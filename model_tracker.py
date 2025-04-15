import psutil

KNOWN_MODEL_KEYWORDS = {
    "llama": "LLaMA",
    "gemma": "Gemma",
    "mistral": "Mistral",
    "falcon": "Falcon",
    "gpt": "GPT-style",
    "bloom": "BLOOM",
    "mixtral": "Mixtral",
    "phi": "Phi-2",
    "vicuna": "Vicuna",
}

def detect_model_from_cmdline(cmdline):
    for keyword, model_name in KNOWN_MODEL_KEYWORDS.items():
        if any(keyword in arg.lower() for arg in cmdline):
            return model_name
    return "Unknown"

def get_model_usage_by_pid():
    model_map = {}
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if 'python' in proc.info['name'] or 'python' in " ".join(proc.info['cmdline']):
                model_name = detect_model_from_cmdline(proc.info['cmdline'])
                model_map[proc.info['pid']] = model_name
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return model_map
