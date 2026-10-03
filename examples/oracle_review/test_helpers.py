"""Failure-boundary tests for the teaching helpers, without network access."""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


bootstrap = load("colab_bootstrap")
metadata = load("audit_croissant")


class HelperTests(unittest.TestCase):
    def test_incompatible_host_selects_managed_interpreter(self):
        self.assertEqual(bootstrap.scientific_python_selector((3, 13), "/host/python"), "3.12")
        self.assertEqual(bootstrap.scientific_python_selector((3, 11), "/host/python"), "3.12")

    def test_compatible_host_keeps_its_interpreter(self):
        self.assertEqual(bootstrap.scientific_python_selector((3, 12), "/host/python"), "/host/python")

    def test_false_is_a_valid_synthetic_data_boolean(self):
        self.assertTrue(metadata.has_content(False))
        self.assertFalse(metadata.has_content(None))

    def test_empty_and_placeholder_answers_are_incomplete(self):
        for value in ([], {}, "", "AUTHOR INPUT: sources", ["TBD"], {"activity": "TODO"}):
            self.assertFalse(metadata.has_content(value), repr(value))

    def test_download_path_cannot_escape_data_root(self):
        with self.assertRaises(ValueError):
            metadata.local_path("/tmp/dataset", "https://huggingface.co/datasets/o/r/resolve/" + "a" * 40 + "/../../secret")

    def test_missing_data_cannot_be_a_complete_pass(self):
        report = metadata.audit(ROOT / "croissant.corrected-example.json")
        self.assertFalse(report["passed"])
        self.assertGreater(report["counts"]["not_evaluated"], 0)


if __name__ == "__main__":
    unittest.main()
