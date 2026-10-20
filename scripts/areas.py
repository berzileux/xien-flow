"""Read area tags from a schema 0 file (mermaid.mmd). Read only, except stdout.
Tag format, one per area:   %% area: A1 | src/a.js, src/b | Short label
Scan root comment:          %% scan_root: /abs/path
Commands:
  root  <schema0>                          print the saved scan root, or nothing
  list  <schema0> <outdir>                 print areas as: id<TAB>label<TAB>paths<TAB>file<TAB>status
  get   <schema0> <id> <scan_root> <outdir>  print validated fields for one area
  index <schema0> <outdir>                 print a markdown index
"""
import os
import re
import sys

TAG = re.compile(r"^\s*%%\s*area:\s*([A-Za-z0-9_-]{1,12})\s*\|\s*(.+?)\s*\|\s*(.+?)\s*$")
ROOT = re.compile(r"^\s*%%\s*scan_root:\s*(\S.*?)\s*$")
CTRL = re.compile(r"[\x00-\x1f\x7f]")


def die(msg, code=1):
    print("ERROR: " + msg)
    sys.exit(code)


def clean(text, limit=80):
    return CTRL.sub(" ", text).strip()[:limit]


def slug(label):
    s = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
    return (s or "area")[:30]


def read_lines(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            return fh.read().splitlines()
    except OSError as exc:
        die("cannot read %s: %s" % (path, exc))


def parse(path):
    areas, seen = [], set()
    for line in read_lines(path):
        m = TAG.match(line)
        if not m:
            continue
        aid, paths, label = m.group(1), m.group(2), m.group(3)
        if aid.lower() in seen:
            die("duplicate area id %s in %s" % (aid, path))
        seen.add(aid.lower())
        plist = [p.strip() for p in paths.split(",") if p.strip()]
        areas.append({"id": aid, "paths": plist, "label": clean(label)})
    return areas


def out_name(area):
    return "mermaid-%s-%s.mmd" % (area["id"], slug(area["label"]))


def check_paths(area, scan_root):
    real_root = os.path.realpath(scan_root)
    good = []
    for p in area["paths"]:
        if CTRL.search(p):
            die("area %s has a path with control characters" % area["id"])
        if os.path.isabs(p) or ".." in p.replace("\\", "/").split("/"):
            die("area %s path is not allowed (absolute or has ..): %s" % (area["id"], p))
        full = os.path.realpath(os.path.join(real_root, p))
        if full != real_root and not full.startswith(real_root + os.sep):
            die("area %s path leaves the scan root: %s" % (area["id"], p))
        if not os.path.exists(full):
            die("area %s path not found under the scan root: %s" % (area["id"], p))
        good.append(p)
    return good


def main():
    if len(sys.argv) < 3:
        die("usage: areas.py root|list|get|index ...", 2)
    cmd, schema0 = sys.argv[1], sys.argv[2]
    if cmd == "root":
        for line in read_lines(schema0):
            m = ROOT.match(line)
            if m:
                print(m.group(1))
                return
        return
    areas = parse(schema0)
    if not areas:
        die("no 'area:' tags in %s. Run /xien-flow:run flow again to rebuild schema 0." % schema0)
    if cmd in ("list", "index"):
        outdir = sys.argv[3]
        rows = []
        for a in areas:
            f = out_name(a)
            status = "written" if os.path.isfile(os.path.join(outdir, f)) else "not yet"
            rows.append((a["id"], a["label"], ", ".join(a["paths"]), f, status))
        if cmd == "list":
            for r in rows:
                print("\t".join(r))
        else:
            print("# Xien-flow index\n")
            print("Schema 0: `mermaid.mmd`. Drill with `/xien-flow:run drill <id>`.\n")
            print("| Id | Area | Paths | Drill file | Status |")
            print("|---|---|---|---|---|")
            for r in rows:
                print("| %s | %s | `%s` | `%s` | %s |" % (r[0], r[1], r[2], r[3], r[4]))
        return
    if cmd == "get":
        want, scan_root, outdir = sys.argv[3].lower(), sys.argv[4], sys.argv[5]
        for a in areas:
            if a["id"].lower() == want:
                paths = check_paths(a, scan_root)
                print("drill_id: " + a["id"])
                print("area_label: " + a["label"])
                print("area_paths: " + ", ".join(paths))
                print("output_file: " + os.path.join(outdir, out_name(a)))
                return
        die("area id '%s' not found. Known ids: %s" % (sys.argv[3], ", ".join(a["id"] for a in areas)))
    die("unknown command " + cmd, 2)


main()
