# DeepTrace

**DeepTrace** is a modern GPU and CPU monitoring tool designed specifically for deep learning workflows. It provides a real-time dashboard that tracks resource usage and maps running processes to popular ML models, serving as a sleek and practical alternative to `nvidia-smi`.

## Features

- Live GPU usage metrics: memory, temperature, utilization, fan speed, ECC errors, and more.
- CPU overview with per-core usage and temperature (where available).
- Tracks which ML models are being run by detecting common model names from process command lines.
- Displays active processes on each GPU, along with the user, model name, and memory usage.
- Uses a terminal-based interactive dashboard powered by the `rich` library.

## Why DeepTrace?

While `nvidia-smi` gives you static metrics and basic process information, **DeepTrace** goes a step further by:
- Providing live updates in a rich-text dashboard
- Enriching process information with model detection
- Offering a more intuitive interface for those monitoring ML training in real-time

## Installation

```bash
pip install -r requirements.txt
```

## Supported Models
DeepTrace can identify processes running the following models (among others):

- LLaMA, Gemma, Mistral, GPT, Vicuna, Alpaca, CodeLLaMA, StarCoder, mT5, NLLB, and many more.

## Security Note

If using this with sensitive codebases, ensure access is restricted as the system scans all process command lines.