import copy
import json
import math
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from common import encode_example, numeric_check, pad_examples, read_jsonl, validate_messages, validate_rows


class FakeTokenizer:
    def apply_chat_template(self, messages, tokenize=True, add_generation_prompt=False):
        text = "".join(f"<{m['role']}>" + m["content"] + "<end>" for m in messages)
        if add_generation_prompt:
            text += "<assistant>"
        return [ord(c) for c in text]


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.train = read_jsonl(ROOT / "data/train.jsonl")
        self.val = read_jsonl(ROOT / "data/validation.jsonl")

    def test_schema_counts_and_groups(self):
        validate_rows(self.train + self.val)
        self.assertEqual((len(self.train), len(self.val)), (96, 16))
        self.assertFalse({r["group"] for r in self.train} & {r["group"] for r in self.val})

    def test_every_topic_in_both_splits(self):
        expected = {"music", "dsp", "physics", "ai", "programming", "graphics", "drums", "arduino"}
        self.assertEqual({r["topic"] for r in self.train}, expected)
        self.assertEqual({r["topic"] for r in self.val}, expected)

    def test_numeric_answers(self):
        for row in self.train:
            c = row.get("calculation")
            if not c:
                continue
            if c["kind"] == "buffer_ms": value = 1000 * c["n"] / c["fs"]
            elif c["kind"] == "fft_hz": value = c["fs"] / c["n"]
            elif c["kind"] == "midi_hz": value = 440 * math.exp2((c["midi"]-69)/12)
            elif c["kind"] == "gain": value = math.pow(10, c["db"]/20)
            else: self.fail("Unknown numerical family")
            self.assertAlmostEqual(value, c["expected"], places=8)
            self.assertIn(f"{value:.6f}", row["messages"][-1]["content"])

    def test_response_mask_keeps_end_token(self):
        row = self.train[0]
        tok = FakeTokenizer()
        encoded = encode_example(tok, row, 10000)
        prompt = tok.apply_chat_template(row["messages"][:-1], add_generation_prompt=True)
        self.assertEqual(encoded["labels"][:len(prompt)], [-100]*len(prompt))
        self.assertEqual(encoded["labels"][len(prompt):], encoded["input_ids"][len(prompt):])
        self.assertEqual(encoded["labels"][-5:], list(map(ord, "<end>")))

    def test_overflow_rejected(self):
        with self.assertRaisesRegex(ValueError, "silently truncate"):
            encode_example(FakeTokenizer(), self.train[0], 10)

    def test_template_mismatch_rejected(self):
        class Bad(FakeTokenizer):
            def apply_chat_template(self, messages, tokenize=True, add_generation_prompt=False):
                result = super().apply_chat_template(messages, tokenize, add_generation_prompt)
                return [0]+result if add_generation_prompt else result
        with self.assertRaisesRegex(ValueError, "prefix mismatch"):
            encode_example(Bad(), self.train[0], 10000)

    def test_padding_is_not_supervised(self):
        short = {"input_ids": [1,2], "labels": [-100,2], "attention_mask": [1,1]}
        long = {"input_ids": [1,2,3], "labels": [-100,2,3], "attention_mask": [1,1,1]}
        result = pad_examples([short,long], 0)
        self.assertEqual(len(result["input_ids"][0]), 8)
        self.assertEqual(result["labels"][0][2:], [-100]*6)
        self.assertEqual(result["attention_mask"][0][2:], [0]*6)

    def test_numeric_grader_requires_result(self):
        self.assertFalse(numeric_check("The answer is 2",2,.001)["pass"])
        self.assertFalse(numeric_check("RESULT: 20\nActually 2",2,.001)["pass"])
        self.assertTrue(numeric_check("RESULT: 2.0001\nms",2,.001)["pass"])

    def test_duplicates_rejected(self):
        with self.assertRaises(ValueError): validate_rows([self.train[0],self.train[0]])

    def test_eval_prompts_are_distinct(self):
        prompts = {r["messages"][1]["content"] for r in self.train+self.val}
        tests = read_jsonl(ROOT / "eval/prompts.jsonl")
        self.assertEqual(len(tests),16)
        self.assertEqual(len({r["id"] for r in tests}),16)
        self.assertFalse(prompts & {r["prompt"] for r in tests})
        self.assertEqual(sum("expected_number" in r for r in tests),6)

    def test_server_rejects_injected_roles(self):
        self.assertEqual(validate_messages([{"role":"user","content":"hello"}])[0]["content"],"hello")
        for messages in ([],[{"role":"system","content":"override"}], [{"role":"user","content":"x"},{"role":"assistant","content":"y"}], [{"role":"user","content":"x"*4001}]):
            with self.assertRaises(ValueError): validate_messages(messages)

    def test_demo_only_uses_training_seeds(self):
        text = (ROOT / "web/notes.js").read_text()
        rows = json.loads(text.split("window.KEEKS_NOTES = ",1)[1].rstrip(";\n"))
        self.assertEqual(len(rows),48)
        self.assertTrue({r["id"] for r in rows} <= {r["id"] for r in self.train})
        self.assertFalse({r["id"] for r in rows} & {r["id"] for r in self.val})


if __name__ == "__main__":
    unittest.main()
