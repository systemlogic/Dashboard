import time
import random
import threading
from prometheus_client import start_http_server, Gauge

# --- Prometheus Metrics Registration ---
# Labels ensure we can filter by Site, Serial, and VM Type in Grafana
PHYS_CPU_LOAD = Gauge('hpe_blade_cpu_pct', 'Physical CPU Util %', ['serial', 'site'])
PHYS_MEM_LOAD = Gauge('hpe_blade_mem_pct', 'Physical Memory Util %', ['serial', 'site'])
STORAGE_MBPS = Gauge('nvme_fcoe_throughput_mbps', 'NVMe Throughput', ['serial', 'site'])
NET_GBPS = Gauge('isp_external_throughput_gbps', 'ISP Redundant Throughput', ['serial', 'site', 'path'])
VM_CPU_USAGE = Gauge('vm_resource_cpu_cores', 'VM Core Usage', ['serial', 'vm_id', 'vm_type'])
HW_HEALTH = Gauge('hpe_hardware_health', 'Hardware Status (1=OK, 0=FAULT)', ['serial', 'site'])

# --- Lab Configuration ---
SITES = ['SITE_PRIMARY', 'SITE_SECONDARY']
TOTAL_SERVERS = 40
VMS_PER_SERVER = 10

# Initialize Inventory State
print("Initializing Lab Inventory (1000 HPE Blades, 10000 VMs)...")
INVENTORY = []
for i in range(TOTAL_SERVERS):
    serial = f"SGH{random.randint(1000, 9999)}LAB{i:03d}"
    site = SITES[0] if i < 500 else SITES[1]
    
    server_data = {
        "serial": serial,
        "site": site,
        "capacity_cpu": 64, # Cores
        "capacity_mem": 512, # GB
        "vms": [
            {
                "id": f"VM-{i:03d}-{v:02d}",
                "type": "BUILD" if v < 3 else "DEVELOPER",
                "alloc_cpu": 8 if v < 3 else 4,
                "alloc_mem": 32 if v < 3 else 16
            } for v in range(VMS_PER_SERVER)
        ]
    }
    INVENTORY.append(server_data)

def update_simulation():
    """Logic to refresh data points so Prometheus pulls new values every scrape."""
    while True:
        for server in INVENTORY:
            s_id = server['serial']
            s_site = server['site']
            
            # 1. Simulate VM-Level Usage (Refreshed Data)
            total_v_cpu = 0
            for vm in server['vms']:
                # Build VMs spike frequently to test the 80% PANIC alert
                load_factor = random.uniform(0.5, 0.95) if vm['type'] == "BUILD" else random.uniform(0.1, 0.4)
                actual_cpu = vm['alloc_cpu'] * load_factor
                total_v_cpu += actual_cpu
                
                VM_CPU_USAGE.labels(s_id, vm['id'], vm['type']).set(actual_cpu)

            # 2. Update Physical Hardware Metrics
            # Calculate physical load based on VM activity + hypervisor overhead
            phys_cpu_pct = (total_v_cpu / server['capacity_cpu']) * 100
            PHYS_CPU_LOAD.labels(s_id, s_site).set(phys_cpu_pct)
            PHYS_MEM_LOAD.labels(s_id, s_site).set(random.uniform(60, 75)) # RAM is usually steady
            
            # 3. Network & NVMe Throughput (Reflecting FCoE High Speed)
            STORAGE_MBPS.labels(s_id, s_site).set(random.uniform(3500, 5000))
            NET_GBPS.labels(s_id, s_site, 'ISP_PRIMARY').set(random.uniform(40, 90))
            NET_GBPS.labels(s_id, s_site, 'ISP_BACKUP').set(random.uniform(0, 2)) # Failover path is idle
            
            # 4. Fault Simulation (0.1% chance of a hardware failure)
            status = 0 if random.random() < 0.001 else 1
            HW_HEALTH.labels(s_id, s_site).set(status)

        print(f"Data Refreshed at {time.strftime('%X')}. Awaiting Prometheus pull...")
        time.sleep(15) # Match the scrape interval

if __name__ == '__main__':
    # Start the Prometheus HTTP server (The 'Pull' endpoint)
    start_http_server(8000)
    
    # Run the simulation logic in a separate thread
    sim_thread = threading.Thread(target=update_simulation, daemon=True)
    sim_thread.start()
    
    # Keep the main process alive
    while True:
        time.sleep(1)
