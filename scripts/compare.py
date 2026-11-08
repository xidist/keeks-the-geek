"""Create a blinded answer sheet and summarize narrow numerical checks."""
import argparse
import csv
import json
import random
from common import ROOT, read_jsonl


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default=ROOT / "outputs/base_eval.jsonl")
    parser.add_argument("--tuned", default=ROOT / "outputs/tuned_eval.jsonl")
    parser.add_argument("--output-dir", default=ROOT / "outputs/comparison")
    args = parser.parse_args()
    from pathlib import Path
    base = {r["id"]: r for r in read_jsonl(args.base)}
    tuned = {r["id"]: r for r in read_jsonl(args.tuned)}
    if base.keys() != tuned.keys():
        raise ValueError("Evaluation IDs differ")
    base_meta = json.loads(Path(args.base).with_suffix(".meta.json").read_text())
    tuned_meta = json.loads(Path(args.tuned).with_suffix(".meta.json").read_text())
    for key in ("base_model", "decoding", "config_sha256", "prompts_sha256"):
        if base_meta[key] != tuned_meta[key]:
            raise ValueError(f"Evaluation conditions differ: {key}")
    output = Path(args.output_dir)
    if output.exists() and any(output.iterdir()):
        raise ValueError("Choose an empty output directory")
    output.mkdir(parents=True, exist_ok=True)
    randomizer = random.Random(3407)
    key, sheet = {}, []
    rubrics = {r["id"]: r["rubric"] for r in read_jsonl(ROOT / "eval/prompts.jsonl")}
    for identifier in base:
        if base[identifier]["prompt"] != tuned[identifier]["prompt"]:
            raise ValueError("Evaluation prompts differ")
        order = ["base", "tuned"]
        randomizer.shuffle(order)
        key[identifier] = {"A": order[0], "B": order[1]}
        answers = {"base": base[identifier]["response"], "tuned": tuned[identifier]["response"]}
        sheet.append({"id": identifier, "prompt": base[identifier]["prompt"], "rubric": " | ".join(rubrics[identifier]),
                      "answer_A": answers[order[0]], "answer_B": answers[order[1]],
                      "accuracy_A_0_to_2": "", "accuracy_B_0_to_2": "", "usefulness_A_0_to_2": "", "usefulness_B_0_to_2": "",
                      "calibration_A_0_to_2": "", "calibration_B_0_to_2": "", "style_A_0_to_2": "", "style_B_0_to_2": "", "notes": ""})
    with (output / "blind_review.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(sheet[0]))
        writer.writeheader(); writer.writerows(sheet)
    (output / "answer_key.json").write_text(json.dumps(key, indent=2) + "\n")
    summary = {"warning": "Scalar checks only, not overall answer accuracy. No results are fabricated."}
    for name, rows in (("base", base), ("tuned", tuned)):
        checks = [r["numeric_check"]["pass"] for r in rows.values() if "numeric_check" in r]
        summary[name] = {"numeric_passes": sum(checks), "numeric_total": len(checks)}
    (output / "numeric_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
