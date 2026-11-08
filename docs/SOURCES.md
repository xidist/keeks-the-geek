# Primary references

Reviewed November 7, 2026. These are implementation and review references, not scraped training material.

- [Unsloth documentation](https://unsloth.ai/docs)
- [Unsloth Core installation](https://unsloth.ai/docs/get-started/install/pip-install)
- [Unsloth notebooks, including Qwen3 4B Instruct](https://unsloth.ai/docs/get-started/unsloth-notebooks)
- [Upstream Qwen3-4B-Instruct-2507 model card](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507)
- [Unsloth 4-bit checkpoint](https://huggingface.co/unsloth/Qwen3-4B-Instruct-2507-unsloth-bnb-4bit)
- [TRL SFTTrainer: pretokenized data, labels, skip_prepare_dataset and max_length](https://huggingface.co/docs/trl/sft_trainer)
- [TRL Unsloth integration](https://huggingface.co/docs/trl/unsloth_integration)
- [NumPy real FFT](https://numpy.org/doc/stable/reference/generated/numpy.fft.rfft.html)
- [SciPy signal processing](https://docs.scipy.org/doc/scipy/reference/signal.html)
- [Arduino analogWrite reference](https://docs.arduino.cc/language-reference/en/functions/analog-io/analogWrite/)
- [Mozzi: synthesis and board-specific output modes](https://sensorium.github.io/Mozzi/)

API compatibility changes over time. The initial project was checked without installing or running the GPU stack. Use the two-step GPU smoke test before a full run; preserve the resulting environment lock and source revision.
