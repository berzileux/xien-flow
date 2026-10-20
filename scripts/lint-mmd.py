"""Check a Mermaid file for mistakes that stop it from rendering. Read only.
Checks: node ids that are Mermaid keywords, unbalanced subgraph/end, tab characters,
text before the diagram type that is not front matter or a comment.
Exit 0 when clean, exit 1 when it found a problem. This is not a full parser."""
import re
import sys

RESERVED = {
    "end", "subgraph", "graph", "flowchart", "call", "click", "style", "class",
    "classDef", "linkStyle", "default", "href", "direction", "interpolate",
    "classDiagram", "erDiagram", "mindmap", "title",
}
DEF = re.compile(r"^\s*([A-Za-z_][\w-]*)\s*(?:\[|\(|\{|>)")
SRC = re.compile(r"^\s*([A-Za-z_][\w-]*)\s*(?:&|-->|-\.+->|-\.->|---|==>|--[^>-])")
DST = re.compile(r"(?:-->|-\.+->|-\.->|==>|---)\s*(?:\|[^|]*\|\s*)?([A-Za-z_][\w-]*)")
AMP = re.compile(r"&\s*([A-Za-z_][\w-]*)")
CLS = re.compile(r"^\s*class\s+([\w,\- ]+)\s+\w+\s*$")


def main():
    if len(sys.argv) != 2:
        print("Usage: lint-mmd.py <file>")
        return 2
    try:
        text = open(sys.argv[1], encoding="utf-8", errors="replace").read()
    except OSError as exc:
        print("CANNOT READ: %s" % exc)
        return 2
    problems = []
    lines = text.splitlines()
    in_front = False
    kind = None
    depth = 0
    for n, line in enumerate(lines, 1):
        if "\t" in line:
            problems.append("line %d: tab character. Use spaces." % n)
        s = line.strip()
        if n == 1 and s == "---":
            in_front = True
            continue
        if in_front:
            if s == "---":
                in_front = False
            continue
        if not s or s.startswith("%%"):
            continue
        if kind is None:
            m = re.match(r"^(flowchart|graph|classDiagram|erDiagram|mindmap)\b", s)
            if not m:
                problems.append("line %d: text before the diagram type: %s" % (n, s[:40]))
                break
            kind = m.group(1)
            continue
        if kind not in ("flowchart", "graph"):
            continue
        if re.match(r"^subgraph\b", s):
            depth += 1
            continue
        if s == "end":
            depth -= 1
            if depth < 0:
                problems.append("line %d: 'end' without subgraph." % n)
                depth = 0
            continue
        if re.match(r"^(classDef|class|style|linkStyle|click|direction)\b", s):
            continue
        ids = []
        for rx in (DEF, SRC):
            m = rx.match(line)
            if m:
                ids.append(m.group(1))
        ids += DST.findall(line)
        ids += AMP.findall(line)
        for i in ids:
            if i in RESERVED:
                problems.append("line %d: node id '%s' is a Mermaid keyword. Rename it, for example 'n_%s'." % (n, i, i))
    if depth > 0:
        problems.append("%d subgraph block(s) without 'end'." % depth)
    if kind is None:
        problems.append("no diagram type found (flowchart, classDiagram, erDiagram or mindmap).")
    if problems:
        print("LINT FAILED:")
        for p in sorted(set(problems), key=lambda x: (int(re.search(r"line (\d+)", x).group(1)) if "line " in x else 10**9, x)):
            print("  " + p)
        return 1
    print("LINT OK")
    return 0


sys.exit(main())
