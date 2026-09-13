#!/usr/bin/env python3
"""ste_lint.py - the mechanically checkable part of ASD-STE100 Simplified
Technical English, for CHANGELOG.md.

STE has two halves: the writing rules and the approved dictionary. The
dictionary is licensed by ASD and is not redistributable, so this tool
does NOT carry it; a word that is not on the denylist below is not
thereby approved. What this tool enforces is the rule half that a
program can decide, so that a changelog entry cannot ship in the shapes
STE forbids:

- Sentence length: at most 25 words (the STE limit for descriptive
  text; procedures get 20, and a changelog is descriptive).
- Paragraph length: at most 6 sentences.
- Active voice: a form of "be" followed by a past participle is
  refused. STE allows a past participle as an ADJECTIVE that describes
  a state ("the valve is closed"); list such words under `state:` in
  the allowlist, and the tool accepts them after "be".
- Verb forms: no "-ing" form. STE keeps "-ing" only for technical names
  and a few nouns; list those under `ing:` in the allowlist.
- Modals: "should", "would", "might", "may" and "shall" are not
  approved. Use "must" (mandatory), "can" (ability) or "will" (future).
- Contractions: none.
- Unapproved words and phrases with a known STE alternative (the
  denylist). A denylisted word that the project uses as a technical
  name goes under `word:` in the allowlist.

What it cannot decide, and leaves to the writer: noun clusters of more
than three nouns, one approved meaning per word, one topic per sentence,
and whether a word outside the denylist is on the approved list.

Text handling: a `#` heading line is a name and is skipped. Inline code
(backticks) and URLs are technical names and count as ONE word each.
Bold and italic markers are stripped. A list item is one paragraph, and
its continuation lines join it. A bare-word Markdown link keeps its
text and loses its target.

The allowlist file is one entry per line, `<category>: <word>`, `#`
comments allowed, categories `ing`, `state`, `word`. Matching is
case-insensitive.

Library use: `lint_text(text, allow) -> [Finding]`, where `allow` is
the dict `load_allowlist()` returns. Command line: `ste_lint.py <file>
[--allow <file>]`, exit 0 clean, 1 findings, 2 unreadable input.
Python 3 stdlib only.
"""
import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

MAX_SENTENCE_WORDS = 25
MAX_PARAGRAPH_SENTENCES = 6

DEFAULT_ALLOWLIST = Path(__file__).resolve().parent / "ste_allow.txt"

# Known unapproved words and phrases, each with the STE alternative.
# Longest phrases first so "in order to" wins over "in".
DENYLIST = [
    ("in order to", "to"),
    ("prior to", "before"),
    ("in excess of", "more than"),
    ("as well as", "and"),
    ("with regard to", "about"),
    ("in the event of", "if"),
    ("a number of", "some, or the number"),
    ("carry out", "do"),
    ("carries out", "does"),
    ("carried out", "did"),
    ("utilize", "use"),
    ("utilise", "use"),
    ("utilizes", "uses"),
    ("utilized", "used"),
    ("commence", "start"),
    ("commences", "starts"),
    ("commenced", "started"),
    ("initiate", "start"),
    ("initiates", "starts"),
    ("initiated", "started"),
    ("terminate", "stop"),
    ("terminates", "stops"),
    ("terminated", "stopped"),
    ("ensure", "make sure"),
    ("ensures", "makes sure"),
    ("ensured", "made sure"),
    ("perform", "do"),
    ("performs", "does"),
    ("performed", "did"),
    ("obtain", "get"),
    ("obtains", "gets"),
    ("obtained", "got"),
    ("provide", "give or supply"),
    ("provides", "gives or supplies"),
    ("provided", "gave or supplied"),
    ("require", "need"),
    ("requires", "needs"),
    ("required", "needed, or necessary"),
    ("assist", "help"),
    ("assists", "helps"),
    ("facilitate", "help"),
    ("facilitates", "helps"),
    ("attempt", "try"),
    ("attempts", "tries"),
    ("attempted", "tried"),
    ("demonstrate", "show"),
    ("demonstrates", "shows"),
    ("employ", "use"),
    ("employs", "uses"),
    ("subsequently", "then, or after"),
    ("whilst", "while"),
    ("via", "through"),
    ("however", "but"),
    ("therefore", "so, or thus"),
    ("verify", "make sure"),
    ("verifies", "makes sure"),
    ("verified", "made sure"),
]

MODALS = {
    "should": "must, or restructure as a recommendation",
    "would": "restructure in the simple present or simple past",
    "might": "can",
    "may": "can, or 'is permitted'",
    "shall": "must",
}

BE_FORMS = r"(?:am|is|are|was|were|be|been|being)"
IRREGULAR_PARTICIPLES = (
    "built|sent|kept|left|made|put|read|set|shut|cut|hit|let|split|held|"
    "found|bound|wound|told|sold|brought|bought|caught|taught|thought|"
    "fought|sought|written|given|taken|driven|shown|known|thrown|grown|"
    "drawn|seen|done|gone|run|begun|won|spun|lost|hidden|ridden|chosen|"
    "frozen|broken|spoken|stolen|worn|torn|born|sung|hung|struck|stuck|"
    "spent|meant|dealt|felt|fed|led|bled|said|paid|laid|lit|understood|"
    "withdrawn|rebuilt|reread|reset|rerun|overwritten|undone|met|sat|"
    "become|begun|forgotten|got"
)
PASSIVE_RE = re.compile(
    r"\b(" + BE_FORMS + r")\s+(?:(?:not|also|then|now|still|never|only|"
    r"always)\s+)?(\w{2,}ed|" + IRREGULAR_PARTICIPLES + r")\b",
    re.IGNORECASE)
# Words that end in "ed" but are not participles.
NOT_PARTICIPLES = {"indeed", "need", "speed", "seed", "deed", "reed",
                   "weed", "red", "bed", "hundred", "naked", "wicked",
                   "sacred", "wretched", "unified", "hatred"}

ING_RE = re.compile(r"\b(\w{3,}ing)\b", re.IGNORECASE)
# Nouns and function words that end in "ing" and are approved as such.
ING_BUILTIN = {"nothing", "anything", "something", "everything", "during",
               "thing", "things", "string", "strings", "bring", "ring",
               "sing", "king", "wing", "spring", "sting", "swing",
               "morning", "evening", "ceiling"}

CONTRACTION_RE = re.compile(r"\b\w+'(?:t|re|ve|ll|m|d)\b", re.IGNORECASE)

CODE_RE = re.compile(r"`[^`]*`")
URL_RE = re.compile(r"https?://\S+")
LINK_RE = re.compile(r"\[([^\]]*)\]\([^)]*\)")
EMPHASIS_RE = re.compile(r"\*\*|__|(?<!\w)[*_](?!\s)|(?<!\s)[*_](?!\w)")
BULLET_RE = re.compile(r"^\s*(?:[-*+]|\d+\.)\s+")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"'(\[]|CODESPAN|URLSPAN)")
WORD_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9'\-]*")


@dataclass
class Finding:
    line: int
    rule: str
    detail: str

    def __str__(self):
        return "line %d: %s: %s" % (self.line, self.rule, self.detail)


def load_allowlist(path=DEFAULT_ALLOWLIST):
    allow = {"ing": set(), "state": set(), "word": set()}
    if path is None or not Path(path).exists():
        return allow
    for number, raw in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        if ":" not in line:
            raise ValueError("%s line %d: expected '<category>: <word>', got %r"
                             % (path, number, raw))
        category, word = (part.strip().lower() for part in line.split(":", 1))
        if category not in allow:
            raise ValueError("%s line %d: unknown category %r" % (path, number, category))
        allow[category].add(word)
    return allow


def _paragraphs(text):
    """Yield (first_line_number, joined_text) for each paragraph. A list
    item starts a paragraph; its indented continuation lines join it.
    Heading lines are skipped."""
    current = []
    start = None
    for number, raw in enumerate(text.splitlines(), 1):
        line = raw.rstrip()
        if line.lstrip().startswith("#"):
            if current:
                yield start, " ".join(current)
                current, start = [], None
            continue
        if not line.strip():
            if current:
                yield start, " ".join(current)
                current, start = [], None
            continue
        if BULLET_RE.match(line) and current:
            yield start, " ".join(current)
            current, start = [], None
        if not current:
            start = number
        current.append(BULLET_RE.sub("", line, count=1).strip())
    if current:
        yield start, " ".join(current)


def _normalize(paragraph):
    text = CODE_RE.sub(" CODESPAN ", paragraph)
    text = URL_RE.sub(" URLSPAN ", text)
    text = LINK_RE.sub(r"\1", text)
    text = EMPHASIS_RE.sub("", text)
    return re.sub(r"\s+", " ", text).strip()


def _sentences(text):
    return [s for s in SENTENCE_SPLIT_RE.split(text) if s.strip()]


def _words(sentence):
    return WORD_RE.findall(sentence)


def lint_text(text, allow=None):
    allow = allow or {"ing": set(), "state": set(), "word": set()}
    findings = []
    for line, paragraph in _paragraphs(text):
        text_n = _normalize(paragraph)
        sentences = _sentences(text_n)
        if len(sentences) > MAX_PARAGRAPH_SENTENCES:
            findings.append(Finding(line, "paragraph length",
                                    "%d sentences, the limit is %d"
                                    % (len(sentences), MAX_PARAGRAPH_SENTENCES)))
        for sentence in sentences:
            words = _words(sentence)
            if len(words) > MAX_SENTENCE_WORDS:
                findings.append(Finding(line, "sentence length",
                                        "%d words, the limit is %d: %r"
                                        % (len(words), MAX_SENTENCE_WORDS,
                                           sentence[:60])))
        lowered = text_n.lower()
        for match in PASSIVE_RE.finditer(text_n):
            participle = match.group(2).lower()
            if participle in NOT_PARTICIPLES or participle in allow["state"]:
                continue
            findings.append(Finding(line, "passive voice",
                                    "%r; write who does it, in the active voice, "
                                    "or list %r under 'state:' if it describes a state"
                                    % (match.group(0), participle)))
        for match in ING_RE.finditer(text_n):
            word = match.group(1).lower()
            if word in ING_BUILTIN or word in allow["ing"]:
                continue
            findings.append(Finding(line, "-ing form",
                                    "%r; use the simple present, the infinitive, or a noun"
                                    % match.group(1)))
        for match in CONTRACTION_RE.finditer(text_n):
            findings.append(Finding(line, "contraction",
                                    "%r; write the words in full" % match.group(0)))
        for word in _words(lowered):
            base = word.lower()
            if base in MODALS and base not in allow["word"]:
                findings.append(Finding(line, "unapproved modal",
                                        "%r; use %s" % (base, MODALS[base])))
        for phrase, alternative in DENYLIST:
            if phrase in allow["word"]:
                continue
            for _match in re.finditer(r"\b" + re.escape(phrase) + r"\b", lowered):
                findings.append(Finding(line, "unapproved word",
                                        "%r; use %s" % (phrase, alternative)))
    return findings


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("path")
    parser.add_argument("--allow", default=str(DEFAULT_ALLOWLIST))
    args = parser.parse_args(argv)
    try:
        text = Path(args.path).read_text(encoding="utf-8")
        allow = load_allowlist(args.allow)
    except (OSError, ValueError) as exc:
        print("ste: %s" % exc, file=sys.stderr)
        return 2
    findings = lint_text(text, allow)
    for finding in findings:
        print("ste: %s: %s" % (args.path, finding), file=sys.stderr)
    if findings:
        print("ste: %d finding(s) in %s" % (len(findings), args.path), file=sys.stderr)
        return 1
    print("ste: clean (%s)" % args.path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
