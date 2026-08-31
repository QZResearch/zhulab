#!/usr/bin/env python3
"""
Turn publications.bib into data/publications.yaml.

The point of this script is that it MERGES rather than overwrites: fields you
set by hand in the YAML (featured, tags, code, pdf, and anything else the
importer doesn't produce) are keyed to a paper by its DOI and survive every
re-run. Papers already in the YAML but missing from the .bib are kept and
reported, never silently dropped.

    python3 scripts/sync_publications.py            # write the file
    python3 scripts/sync_publications.py --check    # exit 1 if it would change
    python3 scripts/sync_publications.py --bib other.bib --out other.yaml

Requires PyYAML for reading the existing file:  pip install pyyaml
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("This script needs PyYAML.  Install it with:  pip install pyyaml")


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BIB = ROOT / "publications.bib"
DEFAULT_OUT = ROOT / "data" / "publications.yaml"

# Fields the importer owns. Everything else in an existing YAML entry is
# treated as hand-maintained and copied through untouched.
GENERATED_FIELDS = {"title", "authors", "journal", "volume", "pages", "year", "doi", "url"}

# Order keys appear in the output file.
KEY_ORDER = ["title", "authors", "journal", "volume", "pages", "year",
             "doi", "url", "pdf", "code", "tags", "featured"]


# --------------------------------------------------------------------------
# BibTeX parsing (no third-party dependency, so CI needs no extra install)
# --------------------------------------------------------------------------

def strip_comments(text: str) -> str:
    out = []
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("%"):
            continue
        out.append(line)
    return "\n".join(out)


def find_entries(text: str):
    """Yield (entry_type, citekey, body) for each @type{key, ...} block."""
    i = 0
    n = len(text)
    while True:
        at = text.find("@", i)
        if at == -1:
            return
        m = re.match(r"@([A-Za-z]+)\s*[{(]", text[at:])
        if not m:
            i = at + 1
            continue
        etype = m.group(1).lower()
        open_pos = at + m.end() - 1
        opener = text[open_pos]
        closer = "}" if opener == "{" else ")"
        depth = 0
        j = open_pos
        while j < n:
            c = text[j]
            if c == "\\":
                j += 2
                continue
            if c == opener:
                depth += 1
            elif c == closer:
                depth -= 1
                if depth == 0:
                    break
            j += 1
        body = text[open_pos + 1:j]
        i = j + 1
        if etype in ("comment", "preamble"):
            continue
        key, _, rest = body.partition(",")
        yield etype, key.strip(), rest


def split_top_level(s: str, sep: str) -> list[str]:
    """Split on `sep` only at brace depth 0 and outside quotes."""
    parts, buf, depth, in_q = [], [], 0, False
    i = 0
    while i < len(s):
        c = s[i]
        if c == "\\":
            buf.append(s[i:i + 2])
            i += 2
            continue
        if c == '"' and depth == 0:
            in_q = not in_q
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
        if c == sep and depth == 0 and not in_q:
            parts.append("".join(buf))
            buf = []
        else:
            buf.append(c)
        i += 1
    parts.append("".join(buf))
    return parts


def unwrap(value: str) -> str:
    v = value.strip()
    # concatenation:  {Foo} # " " # {Bar}
    pieces = [p.strip() for p in split_top_level(v, "#")]
    out = []
    for p in pieces:
        if len(p) >= 2 and p[0] == "{" and p[-1] == "}":
            out.append(p[1:-1])
        elif len(p) >= 2 and p[0] == '"' and p[-1] == '"':
            out.append(p[1:-1])
        else:
            out.append(p)
    return "".join(out).strip()


def parse_fields(rest: str) -> dict:
    fields = {}
    for chunk in split_top_level(rest, ","):
        if "=" not in chunk:
            continue
        name, _, value = chunk.partition("=")
        name = name.strip().lower()
        if name:
            fields[name] = unwrap(value)
    return fields


# --------------------------------------------------------------------------
# LaTeX -> plain text
# --------------------------------------------------------------------------

ACCENTS = {
    "`": {"a": "à", "e": "è", "i": "ì", "o": "ò", "u": "ù"},
    "'": {"a": "á", "e": "é", "i": "í", "o": "ó", "u": "ú", "c": "ć", "n": "ń", "s": "ś", "z": "ź"},
    "^": {"a": "â", "e": "ê", "i": "î", "o": "ô", "u": "û"},
    '"': {"a": "ä", "e": "ë", "i": "ï", "o": "ö", "u": "ü", "y": "ÿ"},
    "~": {"a": "ã", "n": "ñ", "o": "õ"},
    "=": {"a": "ā", "e": "ē", "i": "ī", "o": "ō", "u": "ū"},
    ".": {"a": "ȧ", "e": "ė", "z": "ż"},
}
SPECIALS = {
    r"\ss": "ß", r"\o": "ø", r"\O": "Ø", r"\aa": "å", r"\AA": "Å",
    r"\ae": "æ", r"\AE": "Æ", r"\l": "ł", r"\L": "Ł",
    r"\&": "&", r"\%": "%", r"\$": "$", r"\#": "#", r"\_": "_",
}


def _accent(m: re.Match) -> str:
    mark, letter = m.group(1), m.group(2)
    table = ACCENTS.get(mark, {})
    if letter.lower() in table:
        ch = table[letter.lower()]
        return ch.upper() if letter.isupper() else ch
    return letter


def delatex(s: str) -> str:
    if not s:
        return ""
    # Publisher BibTeX often carries HTML markup in titles (<i>...</i> for
    # species names, <sub>/<sup>). Strip the tags, keep the text.
    s = re.sub(r"</?(i|em|b|strong|sub|sup|span|scp)\b[^>]*>", "", s, flags=re.I)
    s = re.sub(r"\\([`'^\"~=.])\s*\{?\s*([A-Za-z])\s*\}?", _accent, s)
    s = re.sub(r"\\c\s*\{?\s*c\s*\}?", "ç", s)
    s = re.sub(r"\\v\s*\{?\s*s\s*\}?", "š", s)
    for k, v in SPECIALS.items():
        s = s.replace(k, v)
    # \textit{...}, \emph{...}, \mbox{...} -> contents
    for _ in range(3):
        s = re.sub(r"\\[a-zA-Z]+\s*\{([^{}]*)\}", r"\1", s)
    s = re.sub(r"\\[a-zA-Z]+\s*", "", s)
    s = s.replace("---", "—").replace("--", "–")
    s = s.replace("~", " ")
    s = s.replace("{", "").replace("}", "")
    return " ".join(s.split())


# --------------------------------------------------------------------------
# Field shaping
# --------------------------------------------------------------------------

PARTICLES = {"van", "von", "de", "der", "den", "di", "da", "del", "della", "le", "la", "du", "dos", "ter"}


def format_author(raw: str) -> str:
    """'Zhu, Qiang' or 'Qiang Zhu' -> 'Q. Zhu'."""
    raw = delatex(raw).strip()
    if not raw:
        return ""
    if raw.lower() == "others":
        return "et al."

    if "," in raw:
        last, _, first = raw.partition(",")
        last, first = last.strip(), first.strip()
    else:
        words = raw.split()
        if len(words) == 1:
            return words[0]
        # pull any lowercase particles into the surname
        idx = len(words) - 1
        for k in range(len(words) - 2, -1, -1):
            if words[k].lower() in PARTICLES:
                idx = k
            else:
                break
        last = " ".join(words[idx:])
        first = " ".join(words[:idx])

    initials = []
    for part in re.split(r"[\s.]+", first):
        part = part.strip("-")
        if not part:
            continue
        if "-" in part:
            initials.append("-".join(p[0].upper() + "." for p in part.split("-") if p))
        else:
            initials.append(part[0].upper() + ".")
    return (" ".join(initials) + " " + last).strip()


def format_authors(raw: str) -> str:
    if not raw:
        return ""
    parts = re.split(r"\s+and\s+", raw)
    return ", ".join(filter(None, (format_author(p) for p in parts)))


def format_pages(raw: str) -> str:
    p = delatex(raw)
    p = p.replace("--", "–").replace("-", "–") if "–" not in p else p
    return p


def extract_year(fields: dict) -> int | None:
    for key in ("year", "date"):
        v = fields.get(key, "")
        m = re.search(r"(19|20)\d{2}", v)
        if m:
            return int(m.group(0))
    return None


def entry_to_record(etype: str, fields: dict) -> dict | None:
    title = delatex(fields.get("title", ""))
    if not title:
        return None

    journal = delatex(
        fields.get("journal")
        or fields.get("journaltitle")
        or fields.get("booktitle")
        or ""
    )

    rec = {"title": title}
    authors = format_authors(fields.get("author", ""))
    if authors:
        rec["authors"] = authors
    if journal:
        rec["journal"] = journal
    if fields.get("volume"):
        rec["volume"] = delatex(fields["volume"])
    if fields.get("pages"):
        rec["pages"] = format_pages(fields["pages"])
    year = extract_year(fields)
    if year:
        rec["year"] = year
    doi = fields.get("doi", "").strip()
    if doi:
        doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi, flags=re.I)
        rec["doi"] = doi
    url = fields.get("url", "").strip()
    if url and not doi:
        rec["url"] = url
    return rec


# --------------------------------------------------------------------------
# Merge + write
# --------------------------------------------------------------------------

def norm_title(t: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (t or "").lower())


def identity(rec: dict) -> str:
    doi = (rec.get("doi") or "").strip().lower()
    return "doi:" + doi if doi else "title:" + norm_title(rec.get("title"))


def merge(existing: list[dict], incoming: list[dict]):
    by_id = {identity(r): dict(r) for r in existing if isinstance(r, dict)}
    added, updated = [], []

    for rec in incoming:
        key = identity(rec)
        if key in by_id:
            old = by_id[key]
            changed = False
            for f in GENERATED_FIELDS:
                new_val = rec.get(f)
                if new_val is None:
                    continue
                if old.get(f) != new_val:
                    old[f] = new_val
                    changed = True
            if changed:
                updated.append(rec["title"])
        else:
            by_id[key] = rec
            added.append(rec["title"])

    incoming_ids = {identity(r) for r in incoming}
    orphans = [r["title"] for k, r in by_id.items()
               if k not in incoming_ids and r.get("title")]

    records = list(by_id.values())
    records.sort(key=lambda r: (-(r.get("year") or 0), (r.get("title") or "").lower()))
    return records, added, updated, orphans


def yaml_scalar(v) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    s = str(v).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{s}"'


HEADER = """\
# Generated from publications.bib by scripts/sync_publications.py
#
# Fields the importer manages: title, authors, journal, volume, pages, year,
# doi, url. Anything else you add here — featured, tags, code, pdf — is yours
# and is preserved on every re-run, so mark up freely.
#
# Set `featured: true` to put a paper on the homepage (the top 4 by year show).
"""


def dump(records: list[dict]) -> str:
    out = [HEADER]
    for rec in records:
        keys = [k for k in KEY_ORDER if k in rec]
        keys += [k for k in rec if k not in KEY_ORDER]
        first = True
        for k in keys:
            v = rec[k]
            prefix = "- " if first else "  "
            first = False
            if isinstance(v, list):
                if not v:
                    out.append(f"{prefix}{k}: []")
                else:
                    inline = ", ".join(yaml_scalar(x) for x in v)
                    out.append(f"{prefix}{k}: [{inline}]")
            else:
                out.append(f"{prefix}{k}: {yaml_scalar(v)}")
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bib", type=Path, default=DEFAULT_BIB)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--check", action="store_true",
                    help="don't write; exit 1 if the file is out of date")
    args = ap.parse_args()

    if not args.bib.exists():
        sys.exit(f"No BibTeX file at {args.bib}")

    text = strip_comments(args.bib.read_text(encoding="utf-8"))
    incoming = []
    for etype, _key, rest in find_entries(text):
        rec = entry_to_record(etype, parse_fields(rest))
        if rec:
            incoming.append(rec)

    if not incoming:
        sys.exit(f"Parsed 0 entries from {args.bib} — is it a BibTeX file?")

    existing = []
    if args.out.exists():
        loaded = yaml.safe_load(args.out.read_text(encoding="utf-8"))
        if isinstance(loaded, list):
            existing = loaded

    records, added, updated, orphans = merge(existing, incoming)
    rendered = dump(records)

    current = args.out.read_text(encoding="utf-8") if args.out.exists() else ""
    changed = rendered != current

    print(f"{len(incoming)} entries in {args.bib.name} -> {len(records)} in {args.out.name}")
    for t in added:
        print(f"  + {t}")
    for t in updated:
        print(f"  ~ {t}")
    for t in orphans:
        print(f"  ! kept (not in the .bib): {t}")

    if args.check:
        print("out of date" if changed else "up to date")
        return 1 if changed else 0

    if changed:
        args.out.write_text(rendered, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        print("no change")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
