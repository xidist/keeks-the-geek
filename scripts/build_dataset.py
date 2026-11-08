"""Build a reproducible synthetic starter corpus. Standard library only."""
import json
import math
from collections import Counter
from common import ROOT, digest, load_config, validate_rows, write_jsonl


def build():
    cfg = load_config()
    seeds = json.loads((ROOT / "data/seeds.json").read_text())
    creative = json.loads((ROOT / "data/creative_seeds.json").read_text())
    sources = {s["id"]: s for s in json.loads((ROOT / "data/creative_sources.json").read_text())}
    tools = json.loads((ROOT / "data/tool_seeds.json").read_text())
    seeds += creative + tools
    splits = {"train": [], "validation": []}
    def add(split, identifier, group, topic, prompt, answer, origin, calculation=None):
        row = {"id": identifier, "group": group, "topic": topic, "origin": origin,
               "messages": [{"role": "system", "content": cfg["system_prompt"]},
                            {"role": "user", "content": prompt},
                            {"role": "assistant", "content": answer}]}
        if calculation:
            row["calculation"] = calculation
        splits[split].append(row)
    for row in seeds:
        refs = [sources[s] for s in row.get("source_ids", [])]
        answer = row["answer"]
        if refs:
            answer += "\n\nReferences:\n" + "\n".join(s["url"] for s in refs)
        add(row["split"], row["id"], row["group"], row["topic"], row["prompt"], answer, row.get("origin", "synthetic-authored"))
        if row.get("review_status"):
            splits[row["split"]][-1].update(review_status=row["review_status"], execution_status=row.get("execution_status", "not-run"))
        if refs:
            splits[row["split"]][-1].update(source_ids=row["source_ids"],
                review_status=row["review_status"], execution_status=row["execution_status"])
    for i, (sample_rate, size) in enumerate((s, n) for s in (32000, 44100, 48000) for n in (128, 256, 512, 1024)):
        value = size / sample_rate * 1000
        add("train", f"num-buffer-{i:02}", "numeric-buffer", "dsp",
            f"At {sample_rate} samples/s, what duration in ms does a {size}-sample audio block represent?",
            f"Duration = N/fs = {size}/{sample_rate} s = {value:.6f} ms. This is one block's duration, not measured round-trip latency. Input/output buffering, drivers and processing add delay. Measure a loopback to determine total latency.",
            "synthetic-formula", {"kind": "buffer_ms", "fs": sample_rate, "n": size, "expected": value})
    for i, (sample_rate, size) in enumerate((s, n) for s in (16000, 44100, 48000) for n in (512, 1024, 2048, 4096)):
        value = sample_rate / size
        add("train", f"num-fft-{i:02}", "numeric-fft", "dsp",
            f"Find the bin spacing for an N={size} DFT sampled at {sample_rate} Hz.",
            f"Bin spacing is fs/N = {sample_rate}/{size} = {value:.6f} Hz. It is the frequency grid spacing; resolving two nearby tones also depends on window duration, window shape and signal-to-noise ratio. Zero padding makes a denser grid without adding observation time.",
            "synthetic-formula", {"kind": "fft_hz", "fs": sample_rate, "n": size, "expected": value})
    for midi in range(48, 60):
        value = 440 * 2 ** ((midi - 69) / 12)
        add("train", f"num-note-{midi}", "numeric-note", "music",
            f"In 12-tone equal temperament with A4=440 Hz, what frequency is MIDI note {midi}?",
            f"Use f = 440 * 2^((m-69)/12). For m={midi}, f = {value:.6f} Hz. The tuning reference is an assumption; other reference pitches or temperaments change the result.",
            "synthetic-formula", {"kind": "midi_hz", "midi": midi, "expected": value})
    for db in (-24, -18, -12, -9, -6, -3, 0, 3, 6, 9, 12, 18):
        value = 10 ** (db / 20)
        add("train", f"num-gain-{db}", "numeric-gain", "dsp",
            f"What linear amplitude multiplier corresponds to {db} dB?",
            f"For an amplitude ratio, g = 10^(dB/20), so g = {value:.6f}. Power ratios use a denominator of 10 instead. Positive gain can clip signals already near full scale; retain headroom.",
            "synthetic-formula", {"kind": "gain", "db": db, "expected": value})
    validate_rows(splits["train"] + splits["validation"])
    if {r["group"] for r in splits["train"]} & {r["group"] for r in splits["validation"]}:
        raise ValueError("Group leakage")
    for name, rows in splits.items():
        write_jsonl(ROOT / f"data/{name}.jsonl", rows)
    demo = []
    for row in seeds:
        if row["split"] != "train":
            continue
        note = {key: row[key] for key in ("id", "topic", "prompt", "answer")}
        note["aliases"] = row.get("aliases", [])
        note["sources"] = [{k: sources[s][k] for k in ("title", "url")} for s in row.get("source_ids", [])]
        demo.append(note)
    (ROOT / "web/notes.js").write_text("// Synthetic starter notes, not model generations. Built from data/seeds.json.\nwindow.KEEKS_NOTES = " + json.dumps(demo, ensure_ascii=False) + ";\n", encoding="utf-8")
    manifest = {"synthetic": True, "human_expert_reviewed": False, "seed": cfg["seed"],
                "split_policy": "Explicit exercise-group holdout; numerical variants remain in train. Related concepts and source pages may occur in both splits; this is not source-disjoint evaluation.",
                "tool_examples": len(tools), "creative_examples": len(creative), "demo_notes": len(demo), "documentation_sources": len(sources),
                "input_sha256": {p: digest(ROOT / p) for p in ("data/seeds.json", "data/creative_seeds.json", "data/creative_sources.json", "data/tool_seeds.json", "data/tool_catalog.json")},
                "splits": {name: {"count": len(rows), "topics": dict(Counter(r["topic"] for r in rows)),
                                  "sha256": digest(ROOT / f"data/{name}.jsonl")} for name, rows in splits.items()}}
    (ROOT / "data/manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    build()

