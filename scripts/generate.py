"""Text chat or blindable base/adapter evaluation generations."""
import argparse
import json
from pathlib import Path
from common import ROOT, digest, load_config, numeric_check, read_jsonl, write_jsonl


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--adapter", type=Path, help="Omit to evaluate the original base model")
    parser.add_argument("--prompt", help="Omit to run the held-out evaluation prompts")
    parser.add_argument("--output", type=Path, default=ROOT / "outputs/base_eval.jsonl")
    parser.add_argument("--max-new-tokens", type=int, default=384)
    args = parser.parse_args()
    cfg = load_config()
    if not 1 <= args.max_new_tokens < cfg["max_seq_length"]:
        parser.error("--max-new-tokens must be positive and below the context length")
    if args.adapter and not (args.adapter / "adapter_config.json").is_file():
        parser.error("Adapter directory must contain adapter_config.json from a completed training run")
    if not args.prompt and args.output.exists():
        parser.error("Output already exists; select a new --output to preserve earlier measurements")
    from unsloth import FastLanguageModel
    import torch
    if not torch.cuda.is_available():
        raise SystemExit("Use an NVIDIA CUDA GPU for this inference recipe.")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=str(args.adapter.resolve()) if args.adapter else cfg["base_model"],
        max_seq_length=cfg["max_seq_length"], dtype=None, load_in_4bit=True,
    )
    FastLanguageModel.for_inference(model)
    cases = [{"id": "interactive", "prompt": args.prompt}] if args.prompt else read_jsonl(ROOT / "eval/prompts.jsonl")
    results = []
    for case in cases:
        messages = [{"role": "system", "content": cfg["system_prompt"]}, {"role": "user", "content": case["prompt"]}]
        ids = tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True)
        if len(ids) + args.max_new_tokens > cfg["max_seq_length"]:
            raise ValueError(f"{case['id']}: prompt plus generation exceeds configured context")
        input_ids = torch.tensor([ids], device=model.device)
        with torch.inference_mode():
            output = model.generate(input_ids=input_ids, attention_mask=torch.ones_like(input_ids),
                                    max_new_tokens=args.max_new_tokens, do_sample=False,
                                    pad_token_id=tokenizer.pad_token_id or tokenizer.eos_token_id,
                                    eos_token_id=tokenizer.eos_token_id)
        answer = tokenizer.decode(output[0][len(ids):], skip_special_tokens=True)
        row = {"id": case["id"], "prompt": case["prompt"], "response": answer}
        if "expected_number" in case:
            row["numeric_check"] = numeric_check(answer, case["expected_number"], case["tolerance"])
        results.append(row)
        print(f"\n{case['id']}\n{answer}\n", flush=True)
    if not args.prompt:
        write_jsonl(args.output, results)
        args.output.with_suffix(".meta.json").write_text(json.dumps({
            "base_model": cfg["base_model"], "adapter": str(args.adapter) if args.adapter else None,
            "decoding": {"do_sample": False, "max_new_tokens": args.max_new_tokens},
            "config_sha256": digest(ROOT / "config.json"), "prompts_sha256": digest(ROOT / "eval/prompts.jsonl"),
            "model_commit": getattr(model.config, "_commit_hash", None),
        }, indent=2) + "\n")


if __name__ == "__main__":
    main()
