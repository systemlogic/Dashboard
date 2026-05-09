FROM ubuntu:22.04

# Prevent interactive prompts during build
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    prometheus \
    gnupg2 \
    curl \
    wget \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Add Grafana Official Repository
RUN mkdir -p /etc/apt/keyrings/ && \
    wget -q -O - https://apt.grafana.com/gpg.key | gpg --dearmor > /etc/apt/keyrings/grafana.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/grafana.gpg] https://apt.grafana.com stable main" | tee /etc/apt/sources.list.d/grafana.list

# Add Prometheus (Standard Ubuntu universe often has it, but we'll ensure it's updated)
RUN apt-get update && apt-get install -y \
    prometheus \
    grafana \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install prometheus_client

RUN mkdir -p /var/lib/grafana /var/log/grafana /etc/grafana && \
    chown -R grafana:grafana /var/lib/grafana /var/log/grafana /etc/grafana

# Setup Configuration Directories
RUN mkdir -p /etc/prometheus /var/lib/prometheus /var/log/supervisor

COPY lab_daemon.py /app/lab_daemon.py
COPY prometheus.yml /etc/prometheus/prometheus.yml
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose ports: 9090 (Prometheus), 3000 (Grafana)
EXPOSE 9090 3000 8000

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
