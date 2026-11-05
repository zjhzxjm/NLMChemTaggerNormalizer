from contextlib import redirect_stdout
import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "CHEM_NORM/src"))
from abbreviations import AbbreviationExpander
from document_processor_PubTator import PubTatorDocumentProcessor


class Lookup:
    unknown_id = "-"
    allowed_ids = {"MESH:TEST"}
    id2name = {"MESH:TEST": "ascorbic acid"}

    def normalize_mention(self, text):
        return {"MESH:TEST"} if text == "ascorbic acid" else set()


class PubTatorContractTests(unittest.TestCase):
    def test_pipes_whitespace_literal_header_marker_and_offsets_survive(self):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            title = "  β | title  "
            abstract = "  AA | B and literal |t| marker remain intact.  "
            start = (title + " " + abstract).index("AA")
            text = (f"a_1|t|{title}\na_1|a|{abstract}\n"
                    f"a_1\t{start}\t{start + 2}\tAA\tChemical\n\n")
            source, output = folder / "input", folder / "output"
            source.write_text(text, encoding="utf-8")
            abbr = AbbreviationExpander()
            abbr.add("a_1", "AA", "ascorbic acid")
            processor = PubTatorDocumentProcessor({"Chemical": Lookup()}, abbr)
            with redirect_stdout(io.StringIO()):
                processor.process_file(str(source), str(output))
            self.assertEqual(output.read_text(encoding="utf-8"),
                             text.replace("AA\tChemical\n", "AA\tChemical\tMESH:TEST\n"))

    def test_empty_pubtator_produces_empty_output(self):
        with tempfile.TemporaryDirectory() as folder:
            source, output = Path(folder) / "input", Path(folder) / "output"
            source.write_text("")
            PubTatorDocumentProcessor({}, AbbreviationExpander()).process_file(str(source), str(output))
            self.assertEqual(output.read_bytes(), b"")


class CliContractTests(unittest.TestCase):
    def invoke(self, exit_code):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            (folder / "bin").mkdir()
            python = folder / "bin/python"
            python.write_text(f"#!/bin/sh\nprintf 'PROBE_CWD=%s\\n' \"$PWD\"\nexit {exit_code}\n")
            python.chmod(0o755)
            source, abbr = folder / "input", folder / "abbr.tsv"
            source.write_text(""); abbr.write_text("")
            env = os.environ.copy()
            env["PATH"] = str(folder / "bin") + os.pathsep + env["PATH"]
            return subprocess.run(
                ["sh", str(ROOT / "run_Chemical_PubTator.sh"), str(source),
                 str(abbr), str(folder / "output"), str(ROOT)],
                cwd=folder, env=env, capture_output=True, text=True,
            )

    def test_installation_directory_works_from_another_working_directory(self):
        result = self.invoke(0)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f"PROBE_CWD={ROOT / 'CHEM_NORM'}", result.stdout)

    def test_python_failure_propagates_through_both_shell_scripts(self):
        result = self.invoke(7)
        self.assertEqual(result.returncode, 7, result.stdout + result.stderr)
        self.assertNotIn("Done.", result.stdout)


if __name__ == "__main__":
    unittest.main()
