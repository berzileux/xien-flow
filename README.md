# xien-flow

Read a repo and write a Mermaid diagram of it. Every box cites a real file.
One switch turns it on or off.

## Install

Run inside a Claude Code session, as two separate prompts:

    /plugin marketplace add berzileux/xien-flow
    /plugin install xien-flow@xien-flow

Restart the session after installing.

## Use

    /xien-flow on                   turn xien-flow on
    /xien-flow off                  turn xien-flow off
    /xien-flow status               show the mode

    /xien-flow                      flow: write mermaid.mmd (flowchart TD)
    /xien-flow flow                 same as above
    /xien-flow mindmap              write mermaid-mindmap.mmd
    /xien-flow classes              write mermaid-classes.mmd (classDiagram)
    /xien-flow db                   write mermaid-db.mmd (erDiagram)

    /xien-flow classes repo:/abs/path/to/other/repo

The default mode is off. Run `/xien-flow on` once. The choice is saved on the
machine and stays until you run `/xien-flow off`. When the mode is off, every
diagram command stops at once and does nothing. To start with the mode on, set
`XIEN_FLOW_DEFAULT_MODE=on` in your shell.

If the short form `/xien-flow` does not resolve, use `/xien-flow:xien-flow`.

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

### Which mode to use

Pick the mode by the question you want the diagram to answer.

| Mode | Question | Use it when |
|---|---|---|
| `flow` | How does it run? What calls what? | You are new to the repo, want the big picture, or need to trace a request, a job or a hook from start to finish. |
| `classes` | What are the building blocks and how do they relate? | The code uses classes, structs or interfaces, and you plan a refactor or a design review. |
| `db` | What data is stored and how is it linked? | You need tables, columns and foreign keys before a migration, a query change or a data review. |
| `mindmap` | What is in here, by area? | You want a quick table of contents for a README or a talk. It has no arrows, so it shows no flow and no relations. |

For a repo you do not know, run `flow` first. Then run `classes` or `db` on the
area that `flow` shows is important. `mindmap` and `flow` cover the same ground,
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
- No secrets. It does not open `.env*` or key files. `db` does not connect to a
  database and skips seed data.
- Fresh scan. It does not use an old mermaid file as a source.
- Size limits: 40 nodes, 25 classes or 30 entities.
- Short plain labels (ASD-STE100 style). No icons.

## How it works

`/xien-flow` runs `scripts/xien-flow.sh`. The script checks the mode, parses the
arguments, resolves the scan folder and the output folder, and prints a header and
`procedure/PROCEDURE.md`. Claude then follows that text. The on/off check and the
path checks run in the script, not in the model. There is no hook, no skill and
no auto-trigger, so the plugin adds almost nothing to the context until you run it.

## Tested

Run with the claude CLI, `--plugin-dir` and permissions skipped:

- Default mode is off, and `db` stopped with "xien-flow is off".
- After `on`, `db repo:<path>` wrote `mermaid-db.mmd` in the folder the session
  started in. The scanned repo was byte-identical afterwards (checked with a hash).
- The short form `/xien-flow classes repo:<path>` worked.
- Script cases: relative path, missing folder, `/`, an unknown word, two words,
  `repo:` with `on`, and a path with a space.
- All diagram files render in mermaid-cli 11.16.0 with no parse error.
- `claude plugin validate` passes.

Not tested: install through `/plugin marketplace add`, db mode on ORM models or
migration folders, classes mode on Go, Perl or C# code, repos over 1000 files,
and Windows.

## Limits

- Claude reads and judges. A diagram can be wrong. Check a few arrows against the
  code. Results differ between runs.
- "Read only" is an instruction to Claude. It is not enforced. Use the cathy
  plugin guard if you need enforcement.
- The script path checks stop a bad `repo:` value. They do not stop Claude from
  reading other files if it decides to. Do not point `repo:` at a folder that holds
  secrets, and keep credentials out of the session.
- The arguments are placed into a shell command by Claude Code. Type them
  yourself. Do not paste text you do not trust into the command line.
- Reading a folder outside the session folder may ask for permission in a normal
  session. With permissions skipped it does not ask.
- The on/off state is per machine and shared by all sessions on it.
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

## Layout

    .claude-plugin/
      marketplace.json
      plugin.json
    commands/
      xien-flow.md
    scripts/
      xien-flow.sh      switch, argument parsing, path checks
    procedure/
      PROCEDURE.md      what Claude follows for each diagram
    examples/

## Uninstall

    /plugin uninstall xien-flow@xien-flow
    /plugin marketplace remove xien-flow

Then delete the saved mode: `rm -r ~/.config/xien-flow`.

## Credit

The output style follows the Mermaid samples in
https://rudolfolah.com/cause-and-effect-diagrams/ and the class and system design
samples you supplied. No text or code from them is included.
