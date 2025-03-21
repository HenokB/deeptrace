import time
import psutil
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn
from rich.panel import Panel
from rich.table import Table

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
        name = pynvml.nvmlDeviceGetName(handle)
        mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        util = pynvml.nvmlDeviceGetUtilizationRates(handle)
        power = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000  
        temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
        driver_version = pynvml.nvmlSystemGetDriverVersion()
        cuda_version = "12.4"  # Hardcoded for now
        
        try:
            fan_speed = pynvml.nvmlDeviceGetFanSpeed(handle)
        except pynvml.NVMLError_NotSupported:
            fan_speed = "N/A"
        
        stats.append({
            "index": i,
            "name": name,
            "memory_used": mem_info.used / (1024 ** 2),  # Convert to MB
            "memory_total": mem_info.total / (1024 ** 2),
            "gpu_util": util.gpu,
            "power": power,
            "temperature": temp,
            "fan_speed": fan_speed,
            "driver_version": driver_version,
            "cuda_version": cuda_version
        })
    
    return stats

def get_cpu_stats():
    return {
        "cpu_usage": psutil.cpu_percent(),
        "cpu_per_core": psutil.cpu_percent(percpu=True),
        "memory_used": psutil.virtual_memory().used / (1024 ** 2),
        "memory_total": psutil.virtual_memory().total / (1024 ** 2)
    }

def render_dashboard():
    cpu_stats = get_cpu_stats()
    gpu_stats = get_gpu_stats()
    
    if NVML_AVAILABLE and gpu_stats:
        console.print(Panel(
            f"[bold]NVIDIA-SMI[/bold] {gpu_stats[0]['driver_version']}  |  CUDA {gpu_stats[0]['cuda_version']}\n"
            "------------------------------------------------------",
            title="[bold blue]System Info[/bold blue]",
            border_style="blue"
        ))
        
        for stat in gpu_stats:
            memory_usage = stat['memory_used'] / stat['memory_total']
            gpu_utilization = stat['gpu_util'] / 100
            fan_speed = stat['fan_speed']
            
            memory_color = "green" if memory_usage < 0.7 else "yellow" if memory_usage < 0.9 else "red"
            gpu_color = "green" if gpu_utilization < 0.7 else "yellow" if gpu_utilization < 0.9 else "red"
            fan_color = "green" if fan_speed != "N/A" and fan_speed < 50 else "yellow" if fan_speed != "N/A" and fan_speed < 80 else "red"
            
            console.print(Panel(f"[bold cyan]{stat['name']}[/bold cyan] (GPU {stat['index']})\n"
                                f"Memory: [bold {memory_color}]{stat['memory_used']:.2f}MB / {stat['memory_total']:.2f}MB[/bold {memory_color}]\n"
                                f"Utilization: [bold {gpu_color}]{stat['gpu_util']}%[/bold {gpu_color}]\n"
                                f"Fan Speed: [bold {fan_color}]{fan_speed if fan_speed != 'N/A' else 'Not Supported'}[/bold {fan_color}]\n"
                                f"Power: [bold]{stat['power']}W[/bold]\n"
                                f"Temperature: [bold]{stat['temperature']}°C[/bold]",
                                title="[bold]GPU Usage[/bold]", border_style="blue"))
    
    cpu_memory_usage = cpu_stats['memory_used'] / cpu_stats['memory_total']
    cpu_memory_color = "green" if cpu_memory_usage < 0.7 else "yellow" if cpu_memory_usage < 0.9 else "red"
    
    console.print(Panel(
        f"[bold yellow]CPU Usage[/bold yellow]: [bold]{cpu_stats['cpu_usage']}%[/bold]\n"
        f"Per-Core Usage: {', '.join([str(core) + '%' for core in cpu_stats['cpu_per_core']])}\n"
        f"Memory: [bold {cpu_memory_color}]{cpu_stats['memory_used']:.2f}MB / {cpu_stats['memory_total']:.2f}MB[/bold {cpu_memory_color}]",
        title="[bold]CPU Stats[/bold]", border_style="yellow"
    ))

def main():
    while True:
        console.clear()
        render_dashboard()
        time.sleep(1)

if __name__ == "__main__":
    main()
