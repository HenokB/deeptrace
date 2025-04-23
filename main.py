import time
import psutil
from rich import box
from rich.live import Live
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich.align import Align
from rich.console import Group
from rich.layout import Layout
from rich.columns import Columns
from rich.console import Console
from gpu_monitor import find_pids_for_gpu_index
from model_tracker import get_model_usage_by_pid

try:
    import pynvml
    pynvml.nvmlInit()
    NVML_AVAILABLE = True
except:
    NVML_AVAILABLE = False

console = Console()

def get_gpu_stats():
    if not NVML_AVAILABLE:
        return []

    device_count = pynvml.nvmlDeviceGetCount()
    stats = []

    for i in range(device_count):
        handle = pynvml.nvmlDeviceGetHandleByIndex(i)
        mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        util = pynvml.nvmlDeviceGetUtilizationRates(handle)

        try:
            clock_graphics = pynvml.nvmlDeviceGetClockInfo(handle, pynvml.NVML_CLOCK_GRAPHICS)
            clock_mem = pynvml.nvmlDeviceGetClockInfo(handle, pynvml.NVML_CLOCK_MEM)
        except:
            clock_graphics, clock_mem = "N/A", "N/A"

        try:
            tx_bytes = pynvml.nvmlDeviceGetPcieThroughput(handle, pynvml.NVML_PCIE_UTIL_TX_BYTES)
            rx_bytes = pynvml.nvmlDeviceGetPcieThroughput(handle, pynvml.NVML_PCIE_UTIL_RX_BYTES)
        except:
            tx_bytes, rx_bytes = "N/A", "N/A"

        try:
            ecc_errors = pynvml.nvmlDeviceGetTotalEccErrors(handle, pynvml.NVML_MEMORY_ERROR_TYPE_CORRECTED,
                                                            pynvml.NVML_VOLATILE_ECC)
        except:
            ecc_errors = "N/A"

        try:
            fan_speed = pynvml.nvmlDeviceGetFanSpeed(handle)
        except:
            fan_speed = "N/A"

        stats.append({
            "index": i,
            "uuid": pynvml.nvmlDeviceGetUUID(handle),
            "name": pynvml.nvmlDeviceGetName(handle),
            "memory_used": mem_info.used / (1024 ** 2),
            "memory_total": mem_info.total / (1024 ** 2),
            "gpu_util": util.gpu,
            "mem_util": util.memory,
            "power": pynvml.nvmlDeviceGetPowerUsage(handle) / 1000,
            "temp": pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU),
            "driver": pynvml.nvmlSystemGetDriverVersion(),
            "clock_graphics": clock_graphics,
            "clock_mem": clock_mem,
            "tx": tx_bytes,
            "rx": rx_bytes,
            "ecc": ecc_errors,
            "fan": fan_speed
        })

    return stats

def get_cpu_stats():
    try:
        temps = psutil.sensors_temperatures()
        cpu_temp = temps["coretemp"][0].current if "coretemp" in temps else "N/A"
    except:
        cpu_temp = "N/A"

    return {
        "cpu_usage": psutil.cpu_percent(),
        "cpu_per_core": psutil.cpu_percent(percpu=True),
        "cpu_temp": cpu_temp,
        "mem_used": psutil.virtual_memory().used / (1024 ** 2),
        "mem_total": psutil.virtual_memory().total / (1024 ** 2)
    }

def render_dashboard():
    model_map = get_model_usage_by_pid()
    gpu_stats = get_gpu_stats()
    cpu_stats = get_cpu_stats()

    time_str = time.strftime("%a %b %d %H:%M:%S %Y")
    driver = gpu_stats[0]['driver'] if gpu_stats else 'N/A'
    cuda_version = "12.4"

    header = Panel.fit(
        f"{time_str}\n"
        f"[bold cyan]DeepTrace[/bold cyan]    "
        f"[dim]Driver:[/dim] {driver}    [dim]CUDA:[/dim] {cuda_version}",
        border_style="dim", title="DeepTrace"
    )

    gpu_table = Table.grid(padding=(0, 1))
    gpu_table.add_column("GPU Info", width=55)
    gpu_table.add_column("Memory & Util", width=28)
    gpu_table.add_column("ECC / MIG", width=20)

    for g in gpu_stats:
        name = f"{g['index']}  {g['name'].decode()}".ljust(30)
        bus_id = g["uuid"].decode()[:12]
        temp = f"{g['temp']}C"
        power = f"{int(g['power'])}W / 400W"
        mem_used = f"{int(g['memory_used'])}MiB / {int(g['memory_total'])}MiB"
        util = f"{g['gpu_util']}%"
        ecc = f"{g['ecc']}" if g["ecc"] != "N/A" else "N/A"
        mig = "Disabled"

        left = Text(f"{name} | {bus_id} | ECC: {ecc}")
        center = Text(f"Temp: {temp} | Power: {power}\nMem: {mem_used} | Util: {util}")
        right = Text(f"Fan: {g['fan']}%\nMIG: {mig}")

        gpu_table.add_row(left, center, right)

    process_table = Table(
        title="Active GPU Processes",
        show_lines=True,
        box=box.SIMPLE_HEAD,
        expand=True
    )
    process_table.add_column("GPU", style="cyan", width=5)
    process_table.add_column("PID", width=8)
    process_table.add_column("User", style="dim", width=10)
    process_table.add_column("Process", width=30)
    process_table.add_column("Model", width=15)
    process_table.add_column("Mem Used", justify="right", width=12)

    for g in gpu_stats:
        pids = find_pids_for_gpu_index(g["index"])
        for pid in pids:
            try:
                p = psutil.Process(pid)
                user = p.username().split("\\")[-1]
                cmd = " ".join(p.cmdline())[:30]
                mem = f"{p.memory_info().rss // (1024 ** 2)}MiB"
                model = model_map.get(pid, "Unknown")

                process_table.add_row(
                    str(g["index"]), str(pid), user, cmd, model, mem
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

    return Group(header, Panel.fit(gpu_table, title="GPU Overview", border_style="green"), process_table)

def main():
    with Live(console=console, refresh_per_second=1, screen=True) as live:
        while True:
            layout = render_dashboard()
            live.update(layout)
            time.sleep(1)


if __name__ == "__main__":
    main()
