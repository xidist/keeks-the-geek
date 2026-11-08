# Keeks the Geek

[LinkedIn announcement](https://lnkd.in/p/giXem6_N)

**A little chatbot for big rabbit holes.** A creative technology project by [Kiki / xidist](https://xidist.xyz), built around music, DSP, FFTs, physics, AI, programming, graphics, creative coding, drum building and Arduino synthesizers.

[Website demo](https://xidist.xyz/keeks/) · [Train in Colab](https://colab.research.google.com/github/xidist/keeks-the-geek/blob/main/notebooks/Keeks_the_Geek_Colab.ipynb) · [Unsloth docs](https://unsloth.ai/docs)

## Current status

The website is an implemented **starter-note chatbot demo**, published on xidist.xyz. It searches 84 authored reference answers in the browser. It is not currently generating answers with a fine-tuned LLM.

This repository implements the fine-tuning, evaluation and serving pipeline. **Training has not run, no trained adapter is included, and no improvement metrics are claimed.** CPU data/pipeline checks and browser checks can run without a GPU; CUDA training and model serving still need a GPU execution test.

## What is here

| Path | Purpose |
| --- | --- |
| `web/` | Responsive chatbot, topic prompts, searchable demo notes, model connection |
| `notebooks/Keeks_the_Geek_Colab.ipynb` | Guided GPU training and download workflow |
| `data/seeds.json` | 64 authored synthetic conversations across eight areas |
| `data/creative_seeds.json` | 45 documentation-informed examples: 36 training + 9 validation |
| `data/creative_sources.json` | 33 official documentation and maintainer reference pages |
| `data/train.jsonl` | 132 examples: 84 authored + 48 calculated numerical examples |
| `data/validation.jsonl` | 25 held-out exercise groups |
| `scripts/train.py` | Unsloth QLoRA, explicit response-only loss, adapter export |
| `scripts/generate.py` | Identical base/adapter evaluation generation or one-question chat |
| `scripts/compare.py` | Blinded human-review sheet and narrow numerical checks |
| `eval/prompts.jsonl` | 25 held-out prompts, including six numeric checks |
| `api/server.py` | GPU-backed FastAPI server requiring a completed adapter run |

## Creative coding expansion — November 8, 2026

The pilot data now covers **TidalCycles, Hydra, TouchDesigner, Gibber, ChucK, drum sampling, synthesis, live coding and p5.js/GLSL graphics**. New examples carry source IDs, review status and execution status. They are original instructional answers informed by the linked docs, not entire manuals copied into training. The corpus is deliberately small and does not yet establish coverage of every API.

The demo recognizes short requests such as `drum synth`, `TD FFT`, `Hydra audio` and `ChucK sample`. Code blocks and documentation links are rendered as inert content. An explicit platform name constrains matching to that platform. It remains authored-note retrieval, not model generation or a live crawl of documentation.

See [the source catalog](docs/CREATIVE_CODING.md), and review the samples before using the notebook. The notebook rebuilds the expanded data automatically. The latest CPU and JavaScript checks are documented in [VALIDATION.md](docs/VALIDATION.md).

## Try the chatbot locally

No installation is needed for demo mode:

```bash
python -m http.server 8000 --directory web
```

Open `http://localhost:8000`. Questions stay in page memory in demo mode; reloading clears them. Demo retrieval is lexical, so it can return an imperfect match and cannot reason over follow-up context. The interface labels returned starter notes and admits when no close note is found.

## Train your model

The included notebook is the simplest route. Select a **GPU runtime** in Colab; an NVIDIA T4 with 16 GB VRAM is the initial target for this 4-bit, 2048-token recipe, not a measured memory guarantee. GPU availability and session limits depend on Colab. This project has not reserved or purchased compute.

The base is `unsloth/Qwen3-4B-Instruct-2507-unsloth-bnb-4bit`, a non-thinking instruction model. It is selected as a manageable starting point, not as a claim that it is the newest or best model. LoRA rank 16, alpha 32, batch size 1, gradient accumulation 8, two epochs and learning rate 1e-4 are editable in `config.json`.

For a fresh Linux NVIDIA environment with compatible CUDA/PyTorch:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/build_dataset.py
python -m unittest discover -s tests -v
# Optional frontend regression suite (requires Node): node tests/test_retrieval.js
python scripts/generate.py --output outputs/base_eval.jsonl
python scripts/train.py --max-steps 2 --output-dir outputs/smoke
python scripts/train.py --output-dir outputs/full
python scripts/generate.py --adapter outputs/full/adapter --output outputs/tuned_eval.jsonl
python scripts/compare.py
```

The two-step run checks integration; it is not the full experiment. Full training starts separately from the base model. Existing output directories are protected against accidental overwriting. Choose a fresh directory for a new experiment, or use `--resume-from-checkpoint` with an existing training checkpoint.

Dependencies are intentionally resolved together using Unsloth's current dependency constraints. There is no fabricated tested lockfile. Each GPU run records `pip-freeze.txt`, model/tokenizer revision where available, chat-template hash, dataset hashes, hyperparameters, GPU and actual metrics. Preserve this environment and the source commit for reproduction. Determinism across different GPUs/stacks is not guaranteed.

The tokenizer's native chat template is used in training and inference. Prompt tokens and padding receive `-100` labels; assistant content and end-of-turn tokens are supervised. Prefix mismatches and overlong samples fail explicitly. Data are not silently truncated or packed. The starter corpus is small and DSP-heavy; review and expand it before expecting robust expertise.

## Evaluate before connecting it

Read `eval/README.md`. Base and tuned outputs use the same system prompt, questions and greedy decoding. Review `outputs/comparison/blind_review.csv` before opening `answer_key.json`. Numerical checks only check a labelled scalar; they do not measure the quality of a complete explanation. Never advertise an accuracy gain from loss curves alone.

To ask the trained model a question:

```bash
python scripts/generate.py --adapter outputs/full/adapter --prompt "Help me design a small Arduino synth experiment."
```

## Serve the trained model

After full training, on the GPU machine:

```bash
python -m pip install -r api/requirements.txt
python -m uvicorn api.server:app --host 127.0.0.1 --port 8000 --workers 1
```

Open `http://localhost:8000`. The same interface now calls `/chat`. Startup requires both adapter files and a completed run manifest; it never quietly substitutes the base model or demo notes. One process loads one GPU model. Prompt size, output length and concurrent work are bounded.

For the public portfolio, keep `web/config.js` blank until a GPU backend is deployed behind HTTPS and an appropriate access/rate-limit layer. Then set `apiUrl` to its public `/chat` endpoint and set the server's `KEEKS_CORS_ORIGINS` to the exact website origins. CORS is not authentication. An optional `KEEKS_API_TOKEN` is for a server-side proxy to forward, never for frontend JavaScript. A local-only server is the provided default; public GPU hosting and its costs are not set up by this repository.

## Extend Keeks

Add reviewed examples to `data/seeds.json`, assign related examples a shared `group`, and rebuild the dataset. Keep validation groups out of training. Do not import private chat history, patient data or credentials. These seed examples were newly written for this project; they are not a dump of personal conversations or third-party books. Source references are in `docs/SOURCES.md`.

Keeks is text-only. It can discuss a provided spectrum or code snippet; it cannot hear a guitar, analyze a video, drive a synth or verify a circuit without those additional components. The waveform on the website is a controllable illustration, not an audio measurement.

## Portfolio description

> Keeks the Geek is my creative-technology chatbot project connecting music, DSP, physics, AI and hands-on instrument building. I built a responsive web demo and an Unsloth QLoRA pipeline with synthetic instruction data, response-only training, held-out evaluation and adapter serving. GPU training and model evaluation are the next experimental milestone.
