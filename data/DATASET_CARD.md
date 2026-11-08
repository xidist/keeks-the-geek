# Keeks starter dataset

Updated November 8, 2026. All examples are synthetic: 64 original seed conversations, 45 new documentation-informed conversations, 101 original introductory tool primers, and 48 calculated examples. The total is **233 training rows and 25 validation rows**. `manifest.json` contains exact per-topic counts and hashes. The separate 25-prompt evaluation includes six numerical checks and nine creative-coding transfer tasks.

New domains: TidalCycles, Hydra, TouchDesigner, Gibber, ChucK, sampling, synthesis, live coding, and additional graphics. Source URLs and date checked are in `creative_sources.json`; row-level `source_ids` connect the original explanations to those references. Full documentation text is not included. Sources remain owned/licensed by their authors; the catalog does not claim permission to mirror entire manuals. No recordings, private conversations, patient information or lyrics are used.

The examples were authored and checked against source material by an assistant, without independent human expert review. Code examples have not run in their target creative coding runtimes. JavaScript parsing and retrieval tests are not evidence that ChucK, Tidal, SuperCollider or TouchDesigner examples execute correctly. The model has not trained and no model performance measurements exist.

## Split policy

Explicit exercise groups remain in one split; formula-template variants remain in training. The validation exercises cover different tasks, but concepts and source pages may overlap training. This is not a source-disjoint or comprehensive generalization benchmark. Evaluation prompts are separate from training, validation, and browser notes. Do not tune on evaluation answers; create a new test set if you do.

## Fields and reproducibility

Each training row has `id`, `group`, `topic`, `origin`, and a system/user/assistant `messages` exchange. Creative rows also preserve `source_ids`, `review_status`, and `execution_status`; the assistant response includes reference URLs. Alias phrases are only for the website lookup and are not duplicated as extra training rows. Numerical examples preserve calculation inputs and expected values.

Run `python scripts/build_dataset.py` to regenerate JSONL, manifest and `web/notes.js`. Demo notes include only authored training seeds (185), not validation or evaluation answers. The builder rejects duplicate prompts and group leakage. Training uses the native model chat template and fails instead of silently truncating oversized examples.

This is a small, uneven pilot corpus for an experiment, not a completed documentation-trained expert. DSP numerical templates remain overrepresented. Review domain examples in the real software, expand varied debugging and multi-turn cases, and compare base and trained model outputs before connecting the adapter to the public website.

## Tool primers

`tool_catalog.json` maps all 101 requested entries to one original introductory example each in `tool_seeds.json`. These conceptual examples are not documentation imports and have not been executed in target runtimes. Expert review is pending. The existing validation/evaluation sets do not measure competence on every listed tool; expand held-out tasks before making per-tool quality claims.

