import psutil

KNOWN_MODEL_KEYWORDS = {
    "llama": "LLaMA",
    "gemma": "Gemma",
    "mistral": "Mistral",
    "mixtral": "Mixtral",
    "falcon": "Falcon",
    "gpt": "GPT-style",
    "chatgpt": "ChatGPT",
    "gpt-j": "GPT-J",
    "gpt-neox": "GPT-NeoX",
    "bloom": "BLOOM",
    "bloomz": "BLOOMZ",
    "phi": "Phi-2",
    "vicuna": "Vicuna",
    "alpaca": "Alpaca",
    "koala": "Koala",
    "openchat": "OpenChat",
    "airoboros": "Airoboros",
    "dolly": "Dolly",
    "baichuan": "Baichuan",
    "qwen": "Qwen",
    "yi": "Yi",
    "internlm": "InternLM",
    "zephyr": "Zephyr",
    "command-r": "Command-R",
    "orca": "Orca",
    "xwin": "Xwin-LM",
    "starcoder": "StarCoder",
    "codegen": "CodeGen",
    "codellama": "CodeLLaMA",
    "deepseek": "DeepSeek",
    "stablelm": "StableLM",
    "openhermes": "OpenHermes",
    "pandagpt": "PandaGPT",
    "nous": "Nous",
    "mpt": "MPT",
    "replit": "Replit Code Model",
    "rwkv": "RWKV",
    "marian": "MarianMT",
    "opus": "OPUS-MT",
    "mbart": "mBART",
    "mbart50": "mBART-50",
    "mt0": "MT0",
    "mt5": "mT5",
    "t5": "T5",
    "flan": "FLAN-T5",
    "opt": "OPT",
    "xglm": "XGLM",
    "nllb": "NLLB",
    "byT5": "ByT5",
    "glaive": "Glaive",
    "soliloquy": "Soliloquy",
}


def detect_model_from_cmdline(cmdline):
    joined = " ".join(cmdline).lower()
    for keyword, model_name in KNOWN_MODEL_KEYWORDS.items():
        if keyword in joined:
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
