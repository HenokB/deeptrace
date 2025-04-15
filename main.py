import time
import psutil
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.align import Align
from rich.columns import Columns
from rich import box
from rich.console import Group

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
    gpu_stats = get_gpu_stats()
    cpu_stats = get_cpu_stats()

    table = Table(title="💻 GPU Stats", expand=True)
    table.add_column("GPU")
    table.add_column("UUID", no_wrap=True)
    table.add_column("Util %")
    table.add_column("Mem Used", justify="right")
    table.add_column("Temp °C")
    table.add_column("Fan %")
    table.add_column("Power (W)")
    table.add_column("Clock (MHz)")
    table.add_column("TX/RX MB/s")
    table.add_column("ECC")

    for g in gpu_stats:
        table.add_row(
            f"{g['index']} - {g['name'].decode()}",
            g["uuid"].decode(),
            f"{g['gpu_util']}%",
            f"{g['memory_used']:.0f}/{g['memory_total']:.0f}MB",
            f"{g['temp']}°C",
            f"{g['fan']}" if g["fan"] != "N/A" else "N/A",
            f"{g['power']:.1f}",
            f"{g['clock_graphics']}/{g['clock_mem']}",
            f"{g['tx']}/{g['rx']}",
            f"{g['ecc']}"
        )

    cpu_panel = Panel(
        f"[bold yellow]CPU Usage:[/bold yellow] {cpu_stats['cpu_usage']}% | [bold yellow]Temp:[/bold yellow] {cpu_stats['cpu_temp']}°C\n"
        f"[bold]Per-core:[/bold] {', '.join([f'{v:.0f}%' for v in cpu_stats['cpu_per_core']])}\n"
        f"[bold]Memory:[/bold] {cpu_stats['mem_used']:.0f}MB / {cpu_stats['mem_total']:.0f}MB",
        title="[bold blue]CPU Stats[/bold blue]"
    )

    return Panel.fit(table, title="[bold green]🚀 DeepTrace Monitor[/bold green]"), cpu_panel

def main():
    with Live(console=console, refresh_per_second=1, screen=True) as live:
        while True:
            gpu_panel, cpu_panel = render_dashboard()
            layout = Group(cpu_panel, gpu_panel)  
            live.update(layout)
            time.sleep(1)

if __name__ == "__main__":
    main()
