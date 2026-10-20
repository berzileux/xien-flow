# xien-flow

Read a repo and write a Mermaid diagram of it. Every box cites a real file.
One switch turns it on or off.

## Install

Run inside a Claude Code session, as two separate prompts:

    /plugin marketplace add berzileux/xien-flow
    /plugin install xien-flow@xien-flow

Restart the session after installing.

## Use

    /xien-flow:run on                   turn xien-flow on
    /xien-flow:run off                  turn xien-flow off
    /xien-flow:run status               show the mode

    /xien-flow:run                      flow: write mermaid.mmd (flowchart TD)
    /xien-flow:run flow                 same as above
    /xien-flow:run mindmap              write mermaid-mindmap.mmd
    /xien-flow:run classes              write mermaid-classes.mmd (classDiagram)
    /xien-flow:run db                   write mermaid-db.mmd (erDiagram)

    /xien-flow:run classes repo:/abs/path/to/other/repo

    /xien-flow:run drill list           list the areas of schema 0 and write mermaid-index.md
    /xien-flow:run drill A3             write one deeper diagram of area A3
    /xien-flow:run drill all            write a deeper diagram for each area, up to a cap

The default mode is off. Run `/xien-flow:run on` once. The choice is saved on the
machine and stays until you run `/xien-flow:run off`. When the mode is off, every
diagram command stops at once and does nothing. To start with the mode on, set
`XIEN_FLOW_DEFAULT_MODE=on` in your shell.

The command is `/xien-flow:run`. Plugin commands carry the plugin name as a prefix, and
autocomplete inserts it. Type the full name. Shorter forms such as `/xien-flow flow` are
not resolved by Claude Code itself. A model may guess them, so do not rely on them.

### Where it scans and where it writes

- Scan: the folder where you started the session. Add `repo:<absolute-path>` at
  the end to scan another repo. The path must be absolute. Spaces are allowed.
  `repo:` must be the last item.
- Write: always the folder where you started the session. Never the scanned repo,
  unless it is the same folder. The file names do not change, so a new run
  overwrites the old file. Move a file away first if you want to keep it.

### Modes

- `flow`: the system. Entry points, modules, storage, outside services.
- `mindmap`: the same repo as a tree of areas.
- `classes`: classes, structs and interfaces, with members and relations.
- `db`: tables, columns and foreign keys, read from SQL, migrations or ORM models.

If the repo has no classes or no schema, the mode writes no file and says so.

### Schema 0 and drill-down

`flow` writes schema 0: a small overview where each area is one box group. Each area
carries a tag line, for example `%% area: A3 | src/components/properties | Properties UI`.
`drill` reads those tags from the saved `mermaid.mmd` and explodes one area at a time
into its own file, schema 1 to N.

    /xien-flow:run flow                 schema 0: mermaid.mmd
    /xien-flow:run drill list           show areas A1 to An, their drill file names and status
    /xien-flow:run drill A3             schema for one area: mermaid-A3-properties-ui.mmd
    /xien-flow:run drill all            one file per area, up to the cap

- Run `drill` in the same folder as `mermaid.mmd`. The scan root is saved inside
  schema 0, so you do not need to repeat `repo:`. If you add `repo:`, it wins.
- Each drill file shows the area in detail, plus the arrows that enter and leave it.
  Those outside boxes use the same id and label as schema 0 and have a dashed border.
- A drill also checks schema 0 against the code. Dotted or `%% unverified` arrows
  that touch the area are reported as confirmed or not found. Schema 0 is not edited.
  Use that report to correct schema 0 by hand, or run `flow` again.
- `drill all` stops at 8 areas. Raise it with `XIEN_FLOW_DRILL_MAX=12`. The report
  names the skipped areas.
- Each drill is a fresh read of its area. `drill all` costs about as many runs as
  it has areas. Use `drill <id>` on the areas you care about first.
- A drill reads at most 60 files per area, then names the rest in Not explored.
- `drill list` writes `mermaid-index.md`: a table of ids, areas, paths, drill files
  and whether each file exists. Mermaid links between files do not work in most
  viewers, so the index is the map from schema 0 to the drill files.
- A `mermaid.mmd` made before 0.4.0 has no area tags. Run `flow` once more.
- Drill applies to `flow` only. `classes` and `db` are single files.

Drill file names: `mermaid-<id>-<label>.mmd`. A drill overwrites its own file.

### Which mode to use

Pick the mode by the question you want the diagram to answer.

| Mode | Question | Use it when |
|---|---|---|
| `flow` | How does it run? What calls what? | You are new to the repo, want the big picture, or need to trace a request, a job or a hook from start to finish. |
| `classes` | What are the building blocks and how do they relate? | The code uses classes, structs or interfaces, and you plan a refactor or a design review. |
| `db` | What data is stored and how is it linked? | You need tables, columns and foreign keys before a migration, a query change or a data review. |
| `mindmap` | What is in here, by area? | You want a quick table of contents for a README or a talk. It has no arrows, so it shows no flow and no relations. |

For a repo you do not know, run `flow` first. Then run `drill list` and `drill <id>`
on the areas that matter, and `classes` or `db` where they apply. `mindmap` and `flow` cover the same ground,
so you rarely need both.

By repo type:

- Scripts, plugins and config repos: `flow` only. There are no classes and no
  schema, so the other modes write no file.
- Services with a database: `flow` and `db`. Add `classes` for the domain layer.
- Libraries: `classes`, and `flow` for the public entry points.

View a file: paste it into https://mermaid.live, or open it in an editor that
renders Mermaid. GitHub renders Mermaid inside a fenced block in a .md file,
not a bare .mmd file.

## Rules the procedure follows

- Read only. It writes `output_file` and nothing else.
- Evidence. Each node has a `%% src: path` line above it, relative to the scanned repo.
- No invention. Areas it did not read go in a `Not explored` comment block.
- No secrets. It does not open `.env*` or key files. It reads shell, CI, deploy,
  container and config files through `scripts/safe-read.py`, which masks webhook
  URLs, cloud and chat tokens, JWTs, private keys, passwords in URLs and values
  after names like `password`, `token` or `api_key`. `db` does not connect to a
  database and skips seed data.
- No hidden guesses. A solid arrow means the code showed it. A dotted arrow with
  `%% unverified` above it means the link is a guess from names or file lists.
- Fresh scan. It does not use an old mermaid file as a source.
- Size limits: 40 nodes, 25 classes or 30 entities.
- Short plain labels (ASD-STE100 style). No icons.
- Lint. After writing a file, Claude runs `scripts/lint-mmd.py` and fixes what it
  reports, until it prints `LINT OK`. It catches Mermaid keywords used as node ids
  (for example `call` or `end`), unbalanced subgraphs and tab characters.

## How it works

`/xien-flow:run` runs `scripts/xien-flow.sh`. The script checks the mode, parses the
arguments, resolves the scan folder and the output folder, and prints a header and
`procedure/PROCEDURE.md`. For `drill`, `scripts/areas.py` reads the area tags from
schema 0, checks each area path, and the script also prints `procedure/DRILL.md`.
The script writes only the mode file and `mermaid-index.md`. Claude then follows that text. The on/off check and the
path checks run in the script, not in the model. There is no hook, no skill and
no auto-trigger, so the plugin adds almost nothing to the context until you run it.

## Tested

Run with the claude CLI, `--plugin-dir` and permissions skipped:

- Default mode is off, and `db` stopped with "xien-flow is off".
- After `on`, `db repo:<path>` wrote `mermaid-db.mmd` in the folder the session
  started in. The scanned repo was byte-identical afterwards (checked with a hash).
- The full name `/xien-flow:run classes repo:<path>` worked.
- Script cases: relative path, missing folder, `/`, an unknown word, two words,
  `repo:` with `on`, and a path with a space.
- Secret test: a sample repo with a fake Slack webhook, a fake password in a deploy
  script, and a `.env` file. The raw event stream of the run held none of the
  fake values. The model read the deploy script through `safe-read`.
- Drill, on a small React-like sample repo: `flow` wrote schema 0 with 7 area tags and
  the scan root. `drill list` wrote the index. `drill A3` ran with no `repo:` and read
  the saved scan root. `drill all` with a cap of 2 wrote A1 and A2, left A3 alone, and
  named the skipped areas. An unknown id and `../x` were refused.
- Area path checks (unit tests): `..`, an absolute path, a missing path, a duplicate id
  and a file without tags are all rejected.
- Lint: a drill file that used `call` as a node id did not render. The lint flagged
  it, the model fixed it after the rule change, and the new file rendered.
- All diagram files render in mermaid-cli 11.16.0 with no parse error.
- `claude plugin validate` passes.

Not tested: drill on a real large repo, drill with an area of more than 60 files,
install through `/plugin marketplace add`, db mode on ORM models or
migration folders, classes mode on Go, Perl or C# code, repos over 1000 files,
and Windows.

## Limits

- Claude reads and judges. A diagram can be wrong. Check a few arrows against the
  code. Results differ between runs.
- "Read only" is an instruction to Claude. It is not enforced. Use the cathy
  plugin guard if you need enforcement.
- `safe-read.py` works by pattern. It can miss a secret, and it covers only the
  files that Claude reads through it. Claude can still use the Read tool on any
  file. If a secret is ever shown, rotate it. The session transcript that Claude
  Code stores on your machine keeps what was printed.
- The script path checks stop a bad `repo:` value. They do not stop Claude from
  reading other files if it decides to. Do not point `repo:` at a folder that holds
  secrets, and keep credentials out of the session.
- The arguments are placed into a shell command by Claude Code. Type them
  yourself. Do not paste text you do not trust into the command line.
- Reading a folder outside the session folder may ask for permission in a normal
  session. With permissions skipped it does not ask.
- The on/off state is per machine and shared by all sessions on it.
- Drill quality depends on schema 0. If an area tag is wrong or too wide, the drill
  is wrong or shallow. Check `mermaid-index.md` before `drill all`.
- A drill can disagree with schema 0, because every run is a fresh read. The drill
  report lists the disagreements. It does not fix schema 0.
- The scan root and area paths are read from `mermaid.mmd`, which Claude wrote. The
  script checks them: the scan root must be an absolute folder, not `/`, and each
  area path must stay inside the scan root. The area label is treated as data.
- The lint is a set of checks, not a full parser. A file can pass it and still fail
  to render. If a viewer shows a parse error, paste the error to Claude and ask for a fix.
- Mermaid has size limits. Very large diagrams render slowly or fail.
- The scripts need bash. Windows needs WSL or Git Bash.

## Update

1. Edit the files.
2. Raise `version` in `.claude-plugin/plugin.json`.
3. Commit and push.
4. On each machine:

       /plugin marketplace update xien-flow
       /plugin update xien-flow@xien-flow

5. Restart the session.

While you develop, add the folder by local path: `/plugin marketplace add ./xien-flow`.

## Testing a local copy

If you installed the live market source, remove it first to avoid issues:

    /plugin uninstall xien-flow@xien-flow
    /plugin marketplace remove xien-flow

Then add the local folder and install it. Use the absolute path of the folder that
contains `.claude-plugin`:

    /plugin marketplace add /abs/path/to/xien-flow
    /plugin install xien-flow@xien-flow

Restart the session after installing.

`marketplace add` only registers the folder. You must still run the install command.

While you develop from the local folder, you do not need to update, reinstall or
raise the version. Edit the files. A new session reads the change. In an open
session, run `/reload-plugins` or restart it.

To go back to the GitHub copy, remove the local one with the two commands above,
then follow the Install section. If you move or rename the folder, remove the
local copy and add it again from the new path.

## Layout

    .claude-plugin/
      marketplace.json
      plugin.json
    commands/
      run.md
    scripts/
      xien-flow.sh      switch, argument parsing, path checks
      areas.py          reads and checks area tags for drill
      lint-mmd.py       checks a written file for common render errors
      safe-read.py      prints a file with likely secrets masked
    procedure/
      PROCEDURE.md      what Claude follows for each diagram
      DRILL.md          extra steps for drill
    examples/

## Uninstall

    /plugin uninstall xien-flow@xien-flow
    /plugin marketplace remove xien-flow

Then delete the saved mode: `rm -r ~/.config/xien-flow`.

## Credit

The output style follows the Mermaid samples in
https://rudolfolah.com/cause-and-effect-diagrams/ and the class and system design
samples you supplied. No text or code from them is included.
