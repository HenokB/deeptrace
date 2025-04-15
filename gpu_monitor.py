import pynvml

def find_pids_for_gpu_index(index):
    try:
        handle = pynvml.nvmlDeviceGetHandleByIndex(index)
        procs = pynvml.nvmlDeviceGetComputeRunningProcesses(handle)
        return [p.pid for p in procs]
    except pynvml.NVMLError:
        return []
