"""Print a file with likely secrets masked. Best effort, pattern based.
Use it for shell, CI, deploy, container and config files.
It refuses files that are credentials by name. It never writes anything."""
import os
import re
import sys

REFUSE_NAMES = re.compile(
    r"(^\.env($|\.)|\.pem$|\.key$|\.p12$|\.pfx$|\.jks$|^id_(rsa|dsa|ecdsa|ed25519)|^credentials$|^\.netrc$|^\.npmrc$|\.kdbx$)",
    re.I,
)
MAX_BYTES = 400_000

# Each rule: (pattern, replacement)
RULES = [
    (re.compile(r"https?://[^\s\"'<>]*(hooks\.slack\.com|discord(app)?\.com/api/webhooks|webhook|outlook\.office\.com/webhook)[^\s\"'<>]*", re.I), "<redacted-url>"),
    (re.compile(r"(?<![A-Za-z0-9])(AKIA|ASIA)[A-Z0-9]{16}(?![A-Za-z0-9])"), "<redacted-aws-key>"),
    (re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"), "<redacted-slack-token>"),
    (re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"), "<redacted-github-token>"),
    (re.compile(r"glpat-[A-Za-z0-9_-]{20,}"), "<redacted-gitlab-token>"),
    (re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{5,}"), "<redacted-jwt>"),
    (re.compile(r"(?s)-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----"), "<redacted-private-key>"),
    (re.compile(r"(://[^:/\s@\"']+:)[^@\s\"']+(@)"), r"\1<redacted>\2"),
    (re.compile(
        r"((?:pass(?:word|wd)?|secret|token|api[_-]?key|access[_-]?key|private[_-]?key|auth(?:orization)?|credential)[A-Za-z0-9_]*[\"']?\s*[:=]\s*[\"']?)[^\s\"',;]{4,}",
        re.I,
    ), r"\1<redacted>"),
]


def main():
    if len(sys.argv) != 2:
        print("Usage: safe-read.py <file>")
        return 2
    path = sys.argv[1]
    name = os.path.basename(path)
    if REFUSE_NAMES.search(name):
        print("REFUSED: %s is a credential file by name. Do not read it." % name)
        return 3
    if not os.path.isfile(path):
        print("NOT A FILE: %s" % path)
        return 4
    with open(path, "rb") as fh:
        raw = fh.read(MAX_BYTES)
    text = raw.decode("utf-8", errors="replace")
    count = 0
    for pattern, repl in RULES:
        text, n = pattern.subn(repl, text)
        count += n
    sys.stdout.write(text)
    if count:
        print("\n[safe-read: %d value(s) masked in this file. Name the file in the report. Do not guess the values.]" % count)
    return 0


sys.exit(main())
