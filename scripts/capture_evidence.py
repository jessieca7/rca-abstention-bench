#!/usr/bin/env python3
"""Capture real evidence from a running OpenTelemetry demo (docker compose).

Run it from inside the demo folder (the one that contains src/load-generator).

    python3 capture_evidence.py baseline
    python3 capture_evidence.py paymentUnreachable
    python3 capture_evidence.py paymentFailure

What it does, in order:
  1. Asks you to set the feature flag(s) for the scenario, by hand.
  2. Places a few test orders through the store's own web API.
  3. Waits for telemetry to arrive.
  4. Pulls the matching logs (OpenSearch) and traces (Jaeger).
  5. Saves everything to evidence/<scenario>_<time>.json, plus a readable .txt.

It only uses Python's standard library, so nothing needs installing.
"""

import argparse
import json
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCENARIOS = {
    "baseline": "ALL feature flags OFF (healthy system).",
    "paymentUnreachable": "ONLY paymentUnreachable ON (Checkout calls a bad Payment address).",
    "paymentFailure": "ONLY paymentFailure ON, at the highest failure rate offered "
    "(errors generated inside Payment).",
}
PRODUCT_ID = "0PUK6V6EV0"  # a product id taken from the demo's own load generator
NOISE_SERVICE = "otelcol-contrib"  # the collector's own housekeeping logs; not evidence


def http(method, url, body=None, timeout=30):
    """Send one HTTP request. Returns (status_code, response_text).

    Never raises: a failure comes back as status 0 plus the error text, so a
    broken order is recorded as evidence instead of crashing the script.
    """
    data = json.dumps(body).encode() if body is not None else None
    request = urllib.request.Request(
        url, data=data, method=method, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, response.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as error:  # server answered with 4xx/5xx
        return error.code, error.read().decode("utf-8", "replace")
    except Exception as error:  # refused connection, timeout, ...
        return 0, f"{type(error).__name__}: {error}"


def docker_port(container, port):
    """Ask Docker which port on this machine maps to a container's port."""
    result = subprocess.run(
        ["docker", "port", container, str(port)],
        capture_output=True, text=True, check=True,
    )
    return result.stdout.splitlines()[0].rsplit(":", 1)[1]


def place_order(frontend, person):
    """Add one item to a fresh cart, then check out. Records both HTTP results."""
    user_id = str(uuid.uuid4())
    cart_status, _ = http(
        "POST", f"{frontend}/api/cart",
        {"item": {"productId": PRODUCT_ID, "quantity": 1}, "userId": user_id},
    )
    checkout_status, body = http(
        "POST", f"{frontend}/api/checkout", {**person, "userId": user_id}, timeout=60
    )
    return {
        "user_id": user_id,
        "cart_status": cart_status,
        "checkout_status": checkout_status,
        "checkout_response": body[:600],
    }


def fetch_logs(opensearch_url, start, end):
    """Get every log record in [start, end], oldest first, minus collector noise."""
    query = {
        "size": 2000,
        "sort": [{"@timestamp": "asc"}],
        "query": {
            "bool": {
                "filter": [
                    {"range": {"@timestamp": {"gte": start.isoformat(), "lte": end.isoformat()}}}
                ],
                "must_not": [{"match_phrase": {"resource.service.name": NOISE_SERVICE}}],
            }
        },
    }
    status, text = http("POST", f"{opensearch_url}/otel-logs-*/_search", query, timeout=60)
    if status != 200:
        return status, [], text[:300]
    records = []
    for hit in json.loads(text)["hits"]["hits"]:
        source = hit["_source"]
        records.append(
            {
                "time": source.get("@timestamp"),
                "service": source.get("resource", {}).get("service.name", "?"),
                "severity": source.get("severity", {}).get("text", "?"),
                "body": source.get("body"),
                "attributes": source.get("attributes", {}),
                "trace_id": source.get("traceId"),
                "span_id": source.get("spanId"),
            }
        )
    return status, records, ""


def fetch_traces(jaeger_url, service, start, end):
    """Best effort: ask Jaeger for recent traces of one service. Saved raw."""
    params = urllib.parse.urlencode(
        {
            "query.service_name": service,
            "query.start_time_min": start.isoformat().replace("+00:00", "Z"),
            "query.start_time_max": end.isoformat().replace("+00:00", "Z"),
            "query.num_traces": 20,
        }
    )
    status, text = http("GET", f"{jaeger_url}/jaeger/ui/api/v3/traces?{params}", timeout=60)
    return {"service": service, "http_status": status, "raw_response": text[:400_000]}


def demo_commit():
    """Which version of the demo produced this evidence (for reproducibility)."""
    result = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True)
    return result.stdout.strip() or "unknown"


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("scenario", choices=list(SCENARIOS))
    parser.add_argument("--orders", type=int, default=10, help="test orders to place")
    parser.add_argument("--out", default="evidence", help="folder for the saved files")
    parser.add_argument("--frontend", default="http://localhost:8080")
    parser.add_argument("--opensearch-url", default=None)
    parser.add_argument("--jaeger-url", default=None)
    args = parser.parse_args()

    opensearch_url = args.opensearch_url or f"http://localhost:{docker_port('opensearch', 9200)}"
    jaeger_url = args.jaeger_url or f"http://localhost:{docker_port('jaeger', 16686)}"
    person = json.loads(Path("src/load-generator/people.json").read_text())[0]

    status, _ = http("GET", f"{args.frontend}/api/products")
    if status != 200:
        sys.exit(f"The store did not answer (HTTP {status}). Is the demo running?")

    print(f"\nScenario: {args.scenario}")
    print(f"Required flag state: {SCENARIOS[args.scenario]}")
    print(f"Set it now at {args.frontend}/feature, then come back here.")
    variant = input("Type the flag variant you set (e.g. on, 100%, or none): ").strip()
    print("Waiting 20 seconds for the demo to pick up the flag...")
    time.sleep(20)

    start = datetime.now(timezone.utc) - timedelta(seconds=2)
    orders = []
    for number in range(1, args.orders + 1):
        result = place_order(args.frontend, person)
        orders.append(result)
        print(f"  order {number}: cart HTTP {result['cart_status']}, "
              f"checkout HTTP {result['checkout_status']}")
        time.sleep(1)

    print("Waiting 30 seconds for logs and traces to arrive...")
    time.sleep(30)
    end = datetime.now(timezone.utc)

    log_status, logs, log_error = fetch_logs(opensearch_url, start, end)
    traces = [fetch_traces(jaeger_url, name, start, end) for name in ("checkout", "payment")]

    stamp = end.strftime("%Y%m%dT%H%M%SZ")
    out_dir = Path(args.out)
    out_dir.mkdir(exist_ok=True)
    base = out_dir / f"{args.scenario}_{stamp}"
    record = {
        "provenance": "Captured from a live OpenTelemetry demo run. Not constructed or edited.",
        "scenario": args.scenario,
        "flag_state_required": SCENARIOS[args.scenario],
        "flag_variant_set_by_user": variant,
        "demo_git_commit": demo_commit(),
        "window_utc": [start.isoformat(), end.isoformat()],
        "orders": orders,
        "log_query_http_status": log_status,
        "log_query_error": log_error,
        "logs": logs,
        "traces": traces,
    }
    Path(f"{base}.json").write_text(json.dumps(record, indent=2))
    lines = [
        f"{r['time']}  {r['service']:<16} {str(r['severity']):<6} {str(r['body']).replace(chr(10), ' ')}"
        for r in logs
    ]
    Path(f"{base}.txt").write_text("\n".join(lines) + "\n")

    ok = sum(1 for o in orders if o["checkout_status"] == 200)
    errors = [r for r in logs if str(r["severity"]).lower() in ("error", "fatal")]
    print("\nSaved:", f"{base}.json", "and", f"{base}.txt")
    print(f"Orders: {ok} of {len(orders)} checkouts returned HTTP 200.")
    print(f"Logs captured: {len(logs)} ({len(errors)} at error level).")
    if log_status != 200:
        print(f"WARNING: log query failed (HTTP {log_status}): {log_error}")
    for trace in traces:
        print(f"Traces for {trace['service']}: Jaeger HTTP {trace['http_status']}")
    print("Remember to stop the Codespace when you are done for the day.")


if __name__ == "__main__":
    main()
