"""Small dependency-free data and evaluation helpers."""
import hashlib
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_jsonl(path):
    with Path(path).open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def write_jsonl(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def load_config(path=None):
    return json.loads(Path(path or ROOT / "config.json").read_text(encoding="utf-8"))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate_rows(rows):
    if not rows:
        raise ValueError("Dataset is empty")
    ids, prompts = set(), set()
    for row in rows:
        for field in ("id", "group", "topic", "origin"):
            if not isinstance(row.get(field), str) or not row[field].strip():
                raise ValueError(f"Missing {field}: {row}")
        messages = row.get("messages", [])
        if [m.get("role") for m in messages] != ["system", "user", "assistant"]:
            raise ValueError(f"{row['id']}: expected one system/user/assistant exchange")
        if any(not isinstance(m.get("content"), str) or not m["content"].strip() for m in messages):
            raise ValueError(f"Empty message: {row['id']}")
        key = " ".join(messages[1]["content"].lower().split())
        if row["id"] in ids or key in prompts:
            raise ValueError(f"Duplicate id or prompt: {row['id']}")
        ids.add(row["id"])
        prompts.add(key)


def encode_example(tokenizer, row, max_length):
    """Keep prompt tokens out of loss; keep assistant ending tokens in loss."""
    messages = row["messages"]
    prompt_ids = tokenizer.apply_chat_template(messages[:-1], tokenize=True, add_generation_prompt=True)
    full_ids = tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=False)
    if full_ids[:len(prompt_ids)] != prompt_ids:
        raise ValueError(f"Chat template prefix mismatch for {row['id']}; inspect template before training")
    if len(full_ids) > max_length:
        raise ValueError(f"{row['id']} has {len(full_ids)} tokens > {max_length}; shorten it, do not silently truncate")
    labels = [-100] * len(prompt_ids) + full_ids[len(prompt_ids):]
    if not any(label != -100 for label in labels):
        raise ValueError(f"No supervised response tokens: {row['id']}")
    return {"input_ids": full_ids, "attention_mask": [1] * len(full_ids), "labels": labels}


def pad_examples(features, pad_token_id, multiple=8):
    length = math.ceil(max(len(f["input_ids"]) for f in features) / multiple) * multiple
    return {key: [f[key] + [fill] * (length-len(f[key])) for f in features]
            for key, fill in (("input_ids", pad_token_id), ("attention_mask", 0), ("labels", -100))}


class ResponseCollator:
    def __init__(self, pad_token_id):
        self.pad_token_id = pad_token_id

    def __call__(self, features):
        import torch
        return {key: torch.tensor(value, dtype=torch.long)
                for key, value in pad_examples(features, self.pad_token_id).items()}


def numeric_check(text, expected, tolerance):
    """Only grade a labelled scalar, not arbitrary digits elsewhere in prose."""
    match = re.search(r"(?:^|\n)\s*RESULT\s*:\s*([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?)", text)
    if not match:
        return {"pass": False, "parsed": None, "reason": "Missing RESULT: number"}
    value = float(match.group(1))
    return {"pass": math.isfinite(value) and abs(value-expected) <= tolerance, "parsed": value}


def validate_messages(value):
    if not isinstance(value, list) or not 1 <= len(value) <= 7:
        raise ValueError("Provide 1–7 conversation messages")
    for i, item in enumerate(value):
        expected = "user" if i % 2 == 0 else "assistant"
        if not isinstance(item, dict) or item.get("role") != expected:
            raise ValueError("Messages must alternate user/assistant, starting with user")
        content = item.get("content")
        if not isinstance(content, str) or not content.strip() or len(content) > 4000:
            raise ValueError("Each message must contain 1–4000 characters")
    if value[-1]["role"] != "user":
        raise ValueError("Last message must be from user")
    return [{"role": x["role"], "content": x["content"]} for x in value]
