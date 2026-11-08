# Keeks the Geek — planned adapter

**Status:** training pipeline implemented; no trained weights or measured model-quality results in this initial release.

- Base: `unsloth/Qwen3-4B-Instruct-2507-unsloth-bnb-4bit`.
- Method: Unsloth supervised QLoRA with explicitly masked prompts and padding.
- Intended use: educational creative-technology discussion and project planning.
- Inputs: text only.
- Data: original synthetic starter examples; see `data/DATASET_CARD.md`.
- Training hardware and results: pending actual GPU run.
- Serving: local NVIDIA GPU FastAPI example; no public model service configured.
- Limitations: small synthetic corpus, DSP-heavy topic mix, possible factual and code errors, no direct audio/video perception, no hardware verification.

The upstream Qwen model card lists Apache-2.0 licensing. Review upstream model and dependency licenses before redistributing model artifacts. This file does not grant additional rights to third-party material. Replace the pending fields with actual run details and evaluation evidence when releasing a trained adapter.
