# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project does

A self-contained lab monitoring stack that simulates HPE blade server and VM metrics, scrapes them with Prometheus, and visualizes them in Grafana. Everything runs inside a single Docker container managed by supervisord.

## Running the stack

```bash
# Build and start (all services: Python daemon, Prometheus, Grafana)
docker build -t lab-dashboard .
docker run -p 3000:3000 -p 9090:9090 -p 8000:8000 lab-dashboard
```

- Grafana: http://localhost:3000 (default login: admin/admin)
- Prometheus: http://localhost:9090
- Metrics endpoint (raw): http://localhost:8000

## Architecture

The data flow is: `lab_daemon.py` → Prometheus → Grafana

**`lab_daemon.py`** — the only Python file. Runs a background thread that regenerates random metric values every 15 seconds and exposes them via `prometheus_client.start_http_server` on port 8000. Simulates 25 HPE blade servers (`SGH*LAB*` serial format) × 10 VMs each.

Key metric names (useful when writing PromQL for Grafana panels):
- `hw_server_cpu_pct`, `hw_server_mem_pct`, `hw_server_storage_pct` — labeled by `serial`
- `hw_server_net_pct` — labeled by `serial` + `interface` (`Primary_Path` / `Redundant_Path`)
- `hw_server_vm_occupancy_pct` — VM density per host
- `vm_cpu_util_pct`, `vm_mem_util_pct`, `vm_net_util_pct`, `vm_storage_util_pct` — labeled by `serial` + `vm_id`

**`prometheus.yml`** — scrapes `host.docker.internal:8000` every 15s. `host.docker.internal` resolves to the Docker host; if running the daemon outside Docker, update the target accordingly.

**`supervisord.conf`** — starts all three services as supervised processes. Logs go to `/var/log/`.

**`grafana.ini`** — minimal override (port 3000, root URL). Full Grafana config lives inside the container at `/etc/grafana/grafana.ini`.

## Modifying simulated data

All simulation parameters are in `lab_daemon.py`:
- `TOTAL_SERVERS`, `VMS_PER_SERVER` — scale the inventory
- `random.uniform(min, max)` calls in `update_simulation()` — change metric value ranges
- `time.sleep(15)` — change the refresh cadence (match `scrape_interval` in `prometheus.yml` if changed)

## MCP / Grafana integration

A Grafana MCP server (`MCP_DOCKER`) is available in this environment, exposing tools to query Prometheus, manage dashboards, search panels, and interact with Grafana's API directly from Claude Code. Use tools like `mcp__MCP_DOCKER__query_prometheus`, `mcp__MCP_DOCKER__search_dashboards`, and `mcp__MCP_DOCKER__update_dashboard` when working with live dashboard data.
