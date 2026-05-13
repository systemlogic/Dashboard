import time
import random
import threading
from prometheus_client import start_http_server, Gauge

# --- Prometheus Metrics Registration ---
# Physical Hardware Metrics
HW_CPU_LOAD = Gauge('hw_server_cpu_pct', 'Physical CPU Util %', ['serial'])
HW_MEM_LOAD = Gauge('hw_server_mem_pct', 'Physical Memory Util %', ['serial'])
HW_STORAGE_LOAD = Gauge('hw_server_storage_pct', 'Physical Storage Util %', ['serial'])
HW_NET_LOAD = Gauge('hw_server_net_pct', 'Physical Network Util %', ['serial', 'interface'])

# VM Metrics
VM_COUNT_LOAD = Gauge('hw_server_vm_occupancy_pct', 'VM Capacity Utilization %', ['serial'])
VM_CPU_UTIL = Gauge('vm_cpu_util_pct', 'VM CPU Usage %', ['serial', 'vm_id'])
VM_MEM_UTIL = Gauge('vm_mem_util_pct', 'VM Memory Usage %', ['serial', 'vm_id'])
VM_NET_UTIL = Gauge('vm_net_util_pct', 'VM Network Usage %', ['serial', 'vm_id'])
VM_STORAGE_UTIL = Gauge('vm_storage_util_pct', 'VM Storage Usage %', ['serial', 'vm_id'])

# --- Lab Configuration ---
TOTAL_SERVERS = 25
VMS_PER_SERVER = 10

# Initialize Inventory State (Simplified)
print(f"Initializing Lab Inventory ({TOTAL_SERVERS} HPE Blades, {TOTAL_SERVERS * VMS_PER_SERVER} VMs)...")
INVENTORY = []
for i in range(TOTAL_SERVERS):
    serial = f"SGH{random.randint(1000, 9999)}LAB{i:03d}"
    server_data = {
        "serial": serial,
        "vms": [f"VM-{i:03d}-{v:02d}" for v in range(VMS_PER_SERVER)]
    }
    INVENTORY.append(server_data)

def update_simulation():
    """Mathematical simulation ensuring all workloads stay within requested ranges."""
    while True:
        for server in INVENTORY:
            s_id = server['serial']

            # 1. Hardware Server Metrics (Defined Ranges)
            HW_CPU_LOAD.labels(s_id).set(random.uniform(40, 70))
            HW_MEM_LOAD.labels(s_id).set(random.uniform(40, 70))
            HW_STORAGE_LOAD.labels(s_id).set(random.uniform(30, 50))
            
            # 2. Redundant Network Path Metrics (65% to 80%)
            # Simulating load balancing across two primary/fault-tolerant paths
            HW_NET_LOAD.labels(s_id, 'Primary_Path').set(random.uniform(65, 80))
            HW_NET_LOAD.labels(s_id, 'Redundant_Path').set(random.uniform(65, 80))

            # 3. VM Occupancy/Count Workload (65% to 70%)
            # Represents the density of VMs relative to total host capacity
            VM_COUNT_LOAD.labels(s_id).set(random.uniform(65, 70))

            # 4. Per VM Metrics (40% to 70% range for all resources)
            for vm_id in server['vms']:
                VM_CPU_UTIL.labels(s_id, vm_id).set(random.uniform(40, 70))
                VM_MEM_UTIL.labels(s_id, vm_id).set(random.uniform(40, 70))
                VM_NET_UTIL.labels(s_id, vm_id).set(random.uniform(40, 70))
                VM_STORAGE_UTIL.labels(s_id, vm_id).set(random.uniform(40, 70))

        print(f"Metrics Refreshed at {time.strftime('%X')}. Data pushed to scrape endpoint.")
        time.sleep(15)

if __name__ == '__main__':
    # Start the Prometheus scrape endpoint on port 8000
    start_http_server(8000)

    # Launch simulation thread
    sim_thread = threading.Thread(target=update_simulation, daemon=True)
    sim_thread.start()

    # Maintain main process
    while True:
        time.sleep(1)
