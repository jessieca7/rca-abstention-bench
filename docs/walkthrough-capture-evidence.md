# Walkthrough: scripts/capture_evidence.py

Goal of this file: you can explain every part of the script in an interview.

## The one-sentence version

The script flips the demo into a known state, places a few test orders, then
collects the logs and traces those orders produced and saves them to a file.
Because the cause is known (we set the flag), the saved evidence has a trusted
answer key.

## Imports (top of file)

| Line | Meaning |
|---|---|
| `import argparse` | Reads what you type after the script name (`baseline`, `--orders 5`). |
| `import json` | Converts Python data to and from JSON text. |
| `import subprocess` | Runs other programs, here `docker` and `git`. |
| `import sys` | Used for `sys.exit(...)` to stop with a message. |
| `import time` | `time.sleep(n)` pauses n seconds. |
| `import urllib.request / error / parse` | Python's built-in way to make web requests. We use it instead of `httpx` so nothing needs installing in the Codespace. |
| `import uuid` | Makes random unique ids, one per fake shopper. |
| `from datetime import ...` | Timestamps. Always UTC, so they line up with the logs. |
| `from pathlib import Path` | Reading and writing files and folders. |

## Constants

- `SCENARIOS` is a dictionary mapping each scenario name to a plain-English
  description of the flag state it needs. It is also the list of allowed
  command-line choices.
- `PRODUCT_ID` is a product id copied from the demo's own load generator.
- `NOISE_SERVICE` is the collector's own housekeeping logs. We exclude them
  because they are not evidence about the shop.

## `http(method, url, body, timeout)`

Sends one web request and returns `(status_code, text)`.

- `json.dumps(body).encode()` turns a Python dictionary into JSON bytes, or
  `None` if there is no body.
- `urllib.request.Request(...)` builds the request. `headers=` says "this is JSON".
- `with urlopen(...) as response:` sends it and closes the connection afterward.
- `except HTTPError`: the server answered, but with an error code such as 500.
  That is still useful evidence, so we return the code and the body.
- `except Exception`: the server did not answer at all (refused, timeout).
  We return status `0` and the error text.
- Design choice: this function never crashes. A failed order is data, not a bug.

## `docker_port(container, port)`

`docker port opensearch 9200` prints something like `0.0.0.0:32782`.
`.stdout.splitlines()[0]` takes the first line, and `.rsplit(":", 1)[1]` splits
at the last colon and takes the part after it: `32782`. We look it up every
time because Docker can pick a different port after a restart.

## `place_order(frontend, person)`

1. Makes a new random `user_id`, so each order is a different shopper.
2. `POST /api/cart` adds one item. The body shape came from the demo's own
   load generator (`locustfile.py`).
3. `POST /api/checkout` sends the fake person (from `people.json`) plus the
   user id.
4. Returns a small dictionary with both HTTP status codes and the first 600
   characters of the checkout response (`body[:600]`).

## `fetch_logs(opensearch_url, start, end)`

Builds an OpenSearch query as a Python dictionary:

- `"size": 2000` return at most 2000 records.
- `"sort": [{"@timestamp": "asc"}]` oldest first, so the file reads like a story.
- `"filter"` with `"range"`: only records between `start` and `end`.
- `"must_not"` with `match_phrase`: drop the collector's own logs.

It posts this to `otel-logs-*/_search`. The `*` matches every daily index, so it
still works when the date changes at midnight UTC. If the status is not 200 it
returns the error instead of crashing. Otherwise it loops over `hits` and keeps
only the fields we care about: time, service, severity, body, attributes,
trace id, span id. Field names such as `resource` -> `service.name` came from a
real record we looked at.

## `fetch_traces(jaeger_url, service, start, end)`

Asks Jaeger for up to 20 recent traces for one service in the time window.
This is best effort: we save Jaeger's answer as raw text (capped at 400,000
characters) and its HTTP status, without parsing it, so a format surprise cannot
break the run.

## `demo_commit()`

Runs `git rev-parse HEAD` in the demo folder to record which version of the
demo produced the evidence. A reader can reproduce your setup from that.

## `main()`

1. `argparse` defines the command-line options. `choices=list(SCENARIOS)` makes
   the script reject a misspelled scenario.
2. Finds the OpenSearch and Jaeger ports, and loads the first fake person.
3. Checks the store answers (`GET /api/products`). If not, `sys.exit(...)`
   stops with a clear message instead of producing empty evidence.
4. Prints the flag state you must set, then `input(...)` pauses and waits for
   you. You type the variant you set, which is stored in the evidence file. The
   script cannot verify the flag itself, so it records what you say.
5. `time.sleep(20)` gives the demo time to pick up the new flag.
6. Records `start`, places the orders in a loop, printing each result.
7. `time.sleep(30)` waits for logs and traces to arrive, then records `end`.
8. Fetches logs and traces for the window `start` to `end`.
9. Builds the output file name: `evidence/<scenario>_<timestamp>.json`.
10. The `record` dictionary is the evidence file. It states its provenance
    ("captured from a live run, not constructed or edited"), the scenario, the
    flag variant, the demo commit, the time window, the orders, the logs and the
    traces.
11. Writes the JSON file (`indent=2` for readability) and a plain-text `.txt`
    with one log line per row. `chr(10)` is the newline character, replaced by a
    space so each record stays on one line.
12. Prints a summary: how many checkouts returned 200, how many logs, and how
    many were at error level.

## Last two lines

`if __name__ == "__main__": main()` means "run `main()` only when this file is
run directly, not when it is imported". It is standard Python.

## Questions you should be able to answer

- Why record a baseline? To know what healthy looks like and to build
  false-premise questions.
- Why does the script never crash on a failed order? A failed order is evidence.
- Why does the flag step stay manual? Setting the flag through the demo's UI is
  the documented way, and the script records what you set.
- What are the limits? Ten orders per scenario, one fake shopper, one demo run.
  The evidence shows what happened in these runs and nothing more.
