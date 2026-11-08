# Keeks starter dataset

Created November 7, 2026 for a small experimental fine-tune. All examples are synthetic: 64 authored question/answer pairs plus 48 formula-generated pairs. No private biography, emails, medical history, copyrighted song lyrics, or scraped documentation is included. The examples have not undergone independent expert review.

There are 96 training rows and 16 validation rows. The training set has 18 music, 42 DSP, and six each of physics, AI, programming, graphics, drums and Arduino. Validation has two examples in each topic. Formula templates remain entirely in training; validation groups are disjoint. The final 16-question evaluation file is not used by the trainer. Evaluation concepts intentionally overlap the domain; prompt separation alone does not establish broad generalization or eliminate semantic similarity.

Each row includes `id`, `group`, `topic`, `origin`, and a `messages` array with one system/user/assistant exchange. Formula examples also include calculation inputs and the expected numeric value. The deterministic builder validates schema and duplicate prompts and emits SHA-256 hashes in `manifest.json`.

The small, uneven dataset demonstrates style and workflow. It does not establish expert competence in electronics or acoustics. Repeated formula templates can dominate behavior. Review answers, add more varied examples, and expand every topic before drawing conclusions. Avoid training on the test prompts, and freeze a new test set if you start tuning against the current one.

To add an example, copy a record in `seeds.json`, give it a unique ID, use the correct topic, and assign related variants the same group and split. Run `python scripts/build_dataset.py` from the repository root. This also rebuilds browser demo notes from training seeds only. If changing dataset size, update the expected-count assertions in the tests deliberately.
