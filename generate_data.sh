#!/bin/bash

# Generate dummy health data and send it to Prometheus exporter
while true; do
    echo "node_health{job=\"node_1\"} $(shuf -i 0-100)" > /tmp/health_data.txt
    cat /tmp/health_data.txt | promtool query local 'up()'
    sleep 5
done
