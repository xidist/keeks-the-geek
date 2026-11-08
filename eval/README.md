# Evaluation protocol

Freeze `prompts.jsonl` before training. Run the base model and adapter under the same configuration and environment. The script uses deterministic greedy decoding as an experimental comparison setting; it is not a claim about the vendor's preferred conversational sampling settings.

Six cases request `RESULT: number`. The checker only accepts that labelled scalar within a stated absolute tolerance. A passing scalar may still have wrong units or an incorrect explanation. Ten other cases require human judgment. There is no automatic all-purpose quality score.

`compare.py` validates matching IDs, prompts, model IDs, configuration hashes and decoding settings, then randomizes A/B labels per case. Review the CSV before consulting the answer key. For each answer, score these four dimensions from 0 to 2:

| Dimension | 0 | 1 | 2 |
| --- | --- | --- | --- |
| Accuracy | Materially wrong | Partly correct or important omission | Correct within stated scope |
| Usefulness | No usable next step | General suggestion | Concrete, feasible next step |
| Calibration | Invents evidence or certainty | Some assumptions unclear | Honest limits and assumptions |
| Style | Hard to follow | Understandable but unfocused | Clear, concise and engaged |

Report per-case results and the distribution of scores, including regressions. Six numerical tests and one reviewer's judgments are too small to justify a broad accuracy percentage or a meaningful general-purpose confidence interval. If recruiting reviewers, have them score independently and report agreement. Do not inspect the answer key while scoring.

The repository intentionally contains no generated evaluation outputs until a real model run occurs. Unit tests of the evaluation code are not model-performance results.
