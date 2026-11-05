import io
from pathlib import Path
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

sys.path.insert(0, str(Path(__file__).resolve().parents[1] /
    "CHEM_NORM/src"))
from abbreviations import AbbreviationExpander


class ChemicalAbbreviationTests(unittest.TestCase):
    def load(self, text, frequencies=None):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "abbreviations.tsv"
            source.write_text(text, encoding="utf-8")
            expander = AbbreviationExpander(frequencies or {})
            with redirect_stdout(io.StringIO()):
                expander.load(str(source))
        return expander

    def test_same_short_form_keeps_each_documents_definition(self):
        expander = self.load(
            "a_1\tAA\tascorbic acid\nb_1\tAA\tarachidonic acid\n",
            {"AA": {"arachidonic acid": 1000}},
        )
        self.assertEqual(expander.expand("a_1", "AA"), "ascorbic acid")
        self.assertEqual(expander.expand("b_1", "AA"), "arachidonic acid")

    def test_summary_unknown_and_unmapped_mentions_have_no_fallback(self):
        expander = self.load("a_1\tAA\tascorbic acid\n")
        for document_id in ["a", "unknown", "b_1"]:
            with self.subTest(document_id=document_id):
                self.assertEqual(expander.expand(document_id, "AA"), "AA")
        self.assertEqual(expander.expand("a_1", "KGM"), "KGM")

    def test_nested_expansion_cannot_use_another_documents_definition(self):
        expander = self.load("a_1\tABC\tDEF complex\nb_1\tDEF\tdifferent entity\n")
        self.assertEqual(expander.expand("a_1", "ABC"), "DEF complex")

    def test_only_explicit_forms_expand_and_respect_word_boundaries(self):
        expander = self.load("a_1\tFAs\tfatty acids\n")
        self.assertEqual(expander.expand("a_1", "FA"), "FA")
        self.assertEqual(expander.expand("a_1", "FAs"), "fatty acids")
        self.assertEqual(expander.expand("a_1", "FAMILY"), "FAMILY")
        self.assertEqual(expander.expand("other_1", "FA"), "FA")

    def test_plural_inference_cannot_override_explicit_definition(self):
        expander = self.load("a_1\tFAs\tfatty acids\na_1\tFA\tformic acid\n")
        self.assertEqual(expander.expand("a_1", "FA"), "formic acid")

    def test_empty_dictionary_is_success_without_expansion(self):
        self.assertEqual(self.load("").expand("a_1", "AA"), "AA")


if __name__ == "__main__":
    unittest.main()
