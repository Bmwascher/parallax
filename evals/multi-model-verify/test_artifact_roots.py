"""Contract pins and behavioural checks for the round-artifact-roots declaration
(BACKLOG item 100; spec docs/superpowers/specs/2026-09-12-artifact-roots-design.md).

Three groups. DECLARATION: the eight canonical lines sit in one contract
region in model-prompting-notes.md, behind the primary model id, under
one whole-region pin. SWEEP: no path literal in the plugin surface names
a round root the declaration does not, and the sweep prints the shapes
it searched for. WRITERS: the real tools, run in a disposable repository
under whichever host PARALLAX_PS_HOST names, create nothing inside the
repository but the attestation, and a stub writer shows the diff logic
can fail.

WINDOWS ONLY for the resolver and writer groups: they drive
artifact-roots.ps1, new-review-mirror.ps1 and dispatch-round.ps1, which
target the Windows PowerShell hosting model. The declaration and sweep
groups are pure text and run everywhere. A green run on one host proves
ONE interpreter; the powershell-hosts CI job runs both.
"""
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
NOTES = REPO / "skills" / "multi-model-verify" / "references" / "model-prompting-notes.md"
TOOL = REPO / "tools" / "artifact-roots.ps1"
ATTEST = REPO / "tools" / "write-attestation.ps1"
MIRROR_TOOL = REPO / "tools" / "new-review-mirror.ps1"

POWERSHELL = (os.environ.get("PARALLAX_PS_HOST")
              or shutil.which("powershell") or shutil.which("pwsh"))

needs_host = pytest.mark.skipif(
    os.name != "nt" or POWERSHELL is None,
    reason="artifact-roots.ps1 and the writers it covers are Windows "
           "PowerShell tools")


def read(path):
    assert path.is_file(), f"missing file: {path}"
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------
# Group 1: the declaration
# ---------------------------------------------------------------------
def test_declaration_region_is_pinned_whole():
    # ONE pin over the whole region: the coverage checker folds a region
    # into one body, and a pin that stops mid-region locks nothing
    # (test_contract_coverage.py:537-553). Every line must stay on one
    # physical line in the notes, because this is a raw-text pin.
    notes = read(NOTES)
    assert (
        "<!-- contract:start id=round-artifact-roots -->\n"
        "Canonical docs root: `docs/superpowers`\n"
        "Canonical docs root override: `dev/docs/superpowers`\n"
        "Canonical frozen plan path: `<docs-root>/plans/<date>-<topic>.md`\n"
        "Canonical rounds root: `<docs-root>/plans/rounds/<date>-<topic>/`\n"
        "Canonical SDD ledger root: `.superpowers/sdd/<plan-basename>/`\n"
        "Canonical review mirror root: `<TEMP>/<short-name>/`\n"
        "Canonical attestation root: `<git-common-dir>/parallax/attestations/`\n"
        "Canonical checkpoint root: `<git-common-dir>/parallax/application-checkpoints/`\n"
        "<!-- contract:end -->"
    ) in notes


def test_primary_model_declaration_precedes_the_artifact_roots():
    # Two runtime parsers match the FIRST `Canonical model id:` occurrence
    # (model-prompting-notes.md, backup lane block); nothing in this
    # region may sit ahead of it.
    notes = read(NOTES)
    assert notes.index("Canonical model id:") < notes.index(
        "contract:start id=round-artifact-roots")


def test_fixed_rows_state_their_reason_outside_the_region():
    notes = read(NOTES)
    tail = notes[notes.index("contract:start id=round-artifact-roots"):]
    assert "Superpowers owns it" in tail
    assert "never inside the reviewed repository" in tail
    assert "git rev-parse --git-common-dir" in tail
