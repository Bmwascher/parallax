"""Parser and classifier for the codex context probe (0.17.0, backlog item 4).

The probe exists because preflight 3 has only ever enumerated the reviewed
tree, while every source that hijacked a review on 2026-07-28 lived on the
reviewer's own machine. These tests lock the parser against fixtures whose
SHAPE is copied from the real CLI, so a shape change is a red, never a
silent empty result.

Fixtures are synthetic on purpose. This repo is public, and a raw
`prompt-input` recording carries the author's global AGENTS.md verbatim
plus the whole layout of their home skills directory.
"""
import hashlib
import json
import os
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
PROBE = REPO_ROOT / "tools" / "codex-context-probe.ps1"
FIXTURES = Path(__file__).parent / "fixtures" / "codex-prompt-input"
STUB = Path(__file__).parent / "fixtures" / "stub-codex" / "stub-codex.ps1"

# The script body past param(), so the tests can dot-source the functions
# without triggering the mandatory-parameter prompt. Same slicing the
# attestation tests use.
BODY_START = "function Get-PromptText"
BODY_END = "$toplevel ="


def ps_host():
    """PARALLAX_PS_HOST selects the interpreter. A green suite on one
    Windows host proves ONE interpreter - 0.16.1 shipped a lock that did
    not lock on pwsh because every local run used powershell.exe."""
    return os.environ.get("PARALLAX_PS_HOST", "powershell.exe")


def run_functions(snippet):
    """Dot-source the probe's function block, then run `snippet`."""
    text = PROBE.read_text(encoding="utf-8")
    body = text[text.index(BODY_START):text.index(BODY_END)]
    proc = subprocess.run(
        [ps_host(), "-NoProfile", "-NonInteractive", "-Command",
         body + "\n" + snippet],
        capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    return proc.stdout.strip()


def bucket_counts(fixture, workdir="C:/fixture/repo"):
    path = (FIXTURES / fixture).as_posix()
    out = run_functions(
        f'$t = Get-PromptText (Get-Content -Raw "{path}");'
        ' $r = Get-SkillReport $t;'
        ' $b = @{repo=0;"plugin-cache"=0;home=0;unknown=0};'
        ' foreach ($e in $r.Entries) {'
        f'   $b[(Get-SkillScope $e.Path "{workdir}")] += 1 }};'
        ' "{0} {1} {2} {3} {4} {5}" -f $r.BlockPresent, $r.Entries.Count,'
        ' $b["repo"], $b["plugin-cache"], $b["home"], $b["unknown"]'
    )
    parts = out.split()
    return parts[0], [int(p) for p in parts[1:]]


def test_full_fixture_buckets_are_all_asserted():
    # All four counts are named, not just the total. A re-normalized
    # fixture that shifts entries between buckets while keeping the total
    # would otherwise pass unchanged.
    present, counts = bucket_counts("full.json")
    assert present == "True"
    assert tuple(counts) == (60, 0, 31, 29, 0)


def test_the_two_home_sources_are_counted_separately():
    # The fixture contract fixes 24 user-directory entries and 5 built-in
    # ones. Asserting only `home == 29` would let a 23/6 normalization
    # pass.
    out = run_functions(
        f'$t = Get-PromptText (Get-Content -Raw "{(FIXTURES / "full.json").as_posix()}");'
        ' $r = Get-SkillReport $t;'
        ' $u = 0; $s = 0;'
        ' foreach ($e in $r.Entries) {'
        '   $p = $e.Path.Replace("\\","/");'
        '   if ($p -like "*/.agents/skills/*") { $u += 1 }'
        '   elseif ($p -like "*/.codex/skills/.system/*") { $s += 1 } };'
        ' "{0} {1}" -f $u, $s'
    )
    assert [int(v) for v in out.split()] == [24, 5]


def test_flagged_fixture_has_no_cache_entries():
    present, counts = bucket_counts("flagged.json")
    assert present == "True"
    assert tuple(counts) == (29, 0, 0, 29, 0)


def test_repo_agents_fixture_has_a_repo_scoped_entry():
    _, counts = bucket_counts("repo-agents.json")
    assert counts[1] == 1, "the planted entry must land in the repo bucket"


def test_a_malformed_block_is_present_but_yields_nothing():
    # The false-clean case: BlockPresent True with zero entries. The top
    # level is what must refuse it; here we only prove the parser reports
    # the two facts separately so the caller CAN refuse it.
    present, counts = bucket_counts("malformed-block.json")
    assert present == "True"
    assert counts[0] == 0


def test_suppressed_fixture_has_no_skills_block():
    present, counts = bucket_counts("suppressed.json")
    assert present == "False"
    assert counts[0] == 0


def test_repo_agents_fixture_reports_a_project_doc():
    out = run_functions(
        f'$t = Get-PromptText (Get-Content -Raw "{(FIXTURES / "repo-agents.json").as_posix()}");'
        ' $r = Get-InstructionReport $t;'
        ' "{0} {1}" -f $r.BlockPresent, $r.ProjectDoc'
    )
    assert out.split() == ["True", "True"]


def test_flagged_fixture_reports_no_project_doc():
    # The both-ways proof that ProjectDoc tracks the repo file rather than
    # always reading true.
    out = run_functions(
        f'$t = Get-PromptText (Get-Content -Raw "{(FIXTURES / "flagged.json").as_posix()}");'
        ' $r = Get-InstructionReport $t;'
        ' "{0} {1}" -f $r.BlockPresent, $r.ProjectDoc'
    )
    assert out.split() == ["True", "False"]


@pytest.mark.parametrize("path,workdir,expected", [
    ("C:/Users/x/.codex/plugins/cache/p/p/1.0/skills/s/SKILL.md", "C:/repo", "plugin-cache"),
    ("C:\\Users\\x\\.codex\\plugins\\cache\\p\\p\\1.0\\s\\SKILL.md", "C:/repo", "plugin-cache"),
    ("C:/repo/.agents/skills/planted/SKILL.md", "C:/repo", "repo"),
    ("C:/repo/sub/.agents/skills/deep/SKILL.md", "C:/repo", "repo"),
    ("C:/Users/x/.agents/skills/grilling/SKILL.md", "C:/repo", "home"),
    ("C:/Users/x/.codex/skills/.system/imagegen/SKILL.md", "C:/repo", "home"),
    # Fail closed. A path the classifier cannot place is NOT a benign
    # environment note.
    ("skills/relative/SKILL.md", "C:/repo", "unknown"),
    ("../escape/SKILL.md", "C:/repo", "unknown"),
    ("", "C:/repo", "unknown"),
    ("\\\\server\\share\\skills\\s\\SKILL.md", "C:/repo", "unknown"),
])
def test_scope_classification(path, workdir, expected):
    assert run_functions(f'Get-SkillScope "{path}" "{workdir}"') == expected


def test_repo_scope_wins_over_home_when_the_repo_is_inside_home():
    # A checkout under the user profile is the normal case on Windows. If
    # home matched first, a planted repo skill would be filed as an
    # environment note instead of stopping the gate.
    out = run_functions(
        'Get-SkillScope "C:/Users/x/Documents/repo/.agents/skills/s/SKILL.md"'
        ' "C:/Users/x/Documents/repo"'
    )
    assert out == "repo"


def test_a_sibling_directory_sharing_a_prefix_is_not_repo_scoped():
    out = run_functions(
        'Get-SkillScope "C:/w/repo-old/.agents/skills/s/SKILL.md" "C:/w/repo"'
    )
    assert out == "home"


def test_override_uses_forward_slashes_only():
    out = run_functions(
        '$e = @(@{Name="a";Path="C:\\Users\\x\\.agents\\skills\\a\\SKILL.md"});'
        ' New-SkillDisableOverride $e'
    )
    assert out.startswith("skills.config=[")
    assert "\\" not in out, (
        "backslashes make the value fail TOML parsing; codex then rejects"
        " it with `invalid type: string`"
    )
    assert 'path="C:/Users/x/.agents/skills/a/SKILL.md"' in out
    assert "enabled=false" in out


def test_unparseable_json_raises_rather_than_returning_empty():
    text = PROBE.read_text(encoding="utf-8")
    body = text[text.index(BODY_START):text.index(BODY_END)]
    proc = subprocess.run(
        [ps_host(), "-NoProfile", "-NonInteractive", "-Command",
         body + '\ntry { Get-PromptText "not json" ; "NO-THROW" }'
                ' catch { "THREW" }'],
        capture_output=True, text=True,
    )
    assert "THREW" in proc.stdout, (
        "an unreadable measurement must never return an empty one"
    )


def test_a_known_container_body_is_masked_before_the_unknown_scan():
    # The permitted global AGENTS.md is carried verbatim inside
    # <INSTRUCTIONS>, and a user's own file may contain a line like
    # <role>. Scanning the flattened text would call that a new outer
    # surface and block a review that is fine.
    out = run_functions(
        '$t = "<INSTRUCTIONS>`n<role>x</role>`n</INSTRUCTIONS>";'
        ' (Get-UnknownPromptBlock $t).Count'
    )
    assert out == "0"


@pytest.mark.parametrize("snippet,name", [
    ("<memories_instructions>`nx`n</memories_instructions>", "memories_instructions"),
    ("<agent-context>`nx`n</agent-context>", "agent-context"),
    ("<tool.state>`nx`n</tool.state>", "tool.state"),
    ("<ns:extra>`nx`n</ns:extra>", "ns:extra"),
    ('<beta_block version=`"2`">`nx`n</beta_block>', "beta_block"),
    ("<self_closing/>", "self_closing"),
    ("   <indented_block>`nx`n</indented_block>", "indented_block"),
])
def test_an_unrecognized_outer_block_is_found(snippet, name):
    out = run_functions(f'(Get-UnknownPromptBlock "{snippet}") -join ","')
    assert out == name


@pytest.mark.parametrize("snippet", [
    "<payload text>",
    "<recipient>",
    "Task name: <author>",
])
def test_an_unpaired_tag_in_prose_is_not_a_block(snippet):
    # An opening tag with no matching close is prose, not a surface. The
    # real prompt carries all three of these inside a fenced code block
    # that sits in no container, so requiring the PAIR is what keeps the
    # guard from blocking every genuine review.
    out = run_functions(f'(Get-UnknownPromptBlock "{snippet}").Count')
    assert out == "0"


def test_no_real_fixture_reports_an_unknown_block():
    # `<permissions instructions>` opens with a SPACE, so the grammar
    # reads its name as `permissions` while masking needs the full
    # literal. Two lists, or every real review blocks.
    for fixture in ("full.json", "flagged.json", "suppressed.json",
                    "repo-agents.json", "malformed-block.json"):
        out = run_functions(
            f'$t = Get-PromptText (Get-Content -Raw "{(FIXTURES / fixture).as_posix()}");'
            ' (Get-UnknownPromptBlock $t) -join ","'
        )
        assert out == "", f"{fixture} reported {out!r}"
