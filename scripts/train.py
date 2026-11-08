"""QLoRA training; run from the project root on an NVIDIA GPU."""
import argparse
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

from common import ROOT, ResponseCollator, digest, encode_example, load_config, read_jsonl, validate_rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "config.json")
    parser.add_argument("--max-steps", type=int, default=None, help="Use 2 for a smoke run; omit for full epochs")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--resume-from-checkpoint", type=str)
    args = parser.parse_args()
    cfg = load_config(args.config)
    if args.max_steps is not None and args.max_steps < 1:
        parser.error("--max-steps must be positive")
    output = args.output_dir or ROOT / cfg["output_dir"]
    if output.exists() and any(output.iterdir()) and not args.resume_from_checkpoint:
        parser.error(f"{output} is not empty. Choose a new output directory or explicitly resume a checkpoint.")
    train_rows = read_jsonl(ROOT / "data/train.jsonl")
    val_rows = read_jsonl(ROOT / "data/validation.jsonl")
    validate_rows(train_rows + val_rows)
    if {r["group"] for r in train_rows} & {r["group"] for r in val_rows}:
        raise ValueError("Training and validation groups overlap")
    if any(r["messages"][0]["content"] != cfg["system_prompt"] for r in train_rows + val_rows):
        raise ValueError("System prompt changed: rebuild data first")
    os.environ.setdefault("WANDB_DISABLED", "true")
    os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
    # Unsloth must patch libraries before importing transformers/TRL/PEFT.
    from unsloth import FastLanguageModel, is_bfloat16_supported
    import torch
    from datasets import Dataset
    from trl import SFTConfig, SFTTrainer
    if not torch.cuda.is_available():
        raise SystemExit("This recipe needs an NVIDIA CUDA GPU. Use the included Colab notebook.")
    output.mkdir(parents=True, exist_ok=True)
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=cfg["base_model"], max_seq_length=cfg["max_seq_length"],
        dtype=None, load_in_4bit=True,
    )
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    model = FastLanguageModel.get_peft_model(
        model, r=cfg["lora_rank"], lora_alpha=cfg["lora_alpha"],
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_dropout=0, bias="none", use_gradient_checkpointing="unsloth", random_state=cfg["seed"],
    )
    encoded = {name: [encode_example(tokenizer, row, cfg["max_seq_length"]) for row in rows]
               for name, rows in (("train", train_rows), ("validation", val_rows))}
    bf16 = is_bfloat16_supported()
    training_args = SFTConfig(
        output_dir=str(output / "checkpoints"), max_length=cfg["max_seq_length"],
        per_device_train_batch_size=cfg["batch_size"], per_device_eval_batch_size=1,
        gradient_accumulation_steps=cfg["gradient_accumulation_steps"],
        num_train_epochs=cfg["epochs"], max_steps=args.max_steps or -1,
        learning_rate=cfg["learning_rate"], warmup_ratio=0.1, weight_decay=0.01,
        lr_scheduler_type="linear", optim="adamw_8bit", bf16=bf16, fp16=not bf16,
        logging_steps=1, eval_strategy="epoch", save_strategy="epoch", save_total_limit=2,
        seed=cfg["seed"], data_seed=cfg["seed"], report_to="none", packing=False,
        dataset_kwargs={"skip_prepare_dataset": True},
    )
    trainer = SFTTrainer(
        model=model, processing_class=tokenizer, args=training_args,
        train_dataset=Dataset.from_list(encoded["train"]),
        eval_dataset=Dataset.from_list(encoded["validation"]),
        data_collator=ResponseCollator(tokenizer.pad_token_id),
    )
    # Confirm the collator actually preserves our response-only masks.
    probe = trainer.data_collator([encoded["train"][0]])
    assert (probe["labels"] == -100).any() and (probe["labels"] != -100).any()
    manifest = {
        "config": cfg, "max_steps_override": args.max_steps,
        "status": "started", "python": platform.python_version(),
        "gpu": torch.cuda.get_device_name(0), "cuda": torch.version.cuda,
        "model_commit": getattr(model.config, "_commit_hash", None),
        "tokenizer_commit": tokenizer.init_kwargs.get("_commit_hash"),
        "chat_template_sha256": __import__("hashlib").sha256(tokenizer.chat_template.encode()).hexdigest(),
        "data_sha256": {name: digest(ROOT / f"data/{name}.jsonl") for name in ("train", "validation")},
        "counts": {name: len(rows) for name, rows in encoded.items()},
        "max_tokens": {name: max(len(r["input_ids"]) for r in rows) for name, rows in encoded.items()},
    }
    manifest_path = output / "run_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    freeze = subprocess.run([sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True, check=True)
    (output / "pip-freeze.txt").write_text(freeze.stdout)
    result = trainer.train(resume_from_checkpoint=args.resume_from_checkpoint)
    validation_metrics = trainer.evaluate()
    adapter = output / "adapter"
    model.save_pretrained(str(adapter))
    tokenizer.save_pretrained(str(adapter))
    trainer.save_state()
    manifest.update(status="complete", train_metrics=result.metrics, validation_metrics=validation_metrics)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Saved LoRA adapter: {adapter}")


if __name__ == "__main__":
    main()
