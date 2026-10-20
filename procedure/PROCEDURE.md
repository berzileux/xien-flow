# Xien Flow procedure

Write one Mermaid file that shows how the repository at `scan_root` works.
The header above gives `scan_root`, `output_dir` and `output_file`.
Read `scan_root`. Change nothing except `output_file`.

## Modes

The header gives the mode. Each mode has one output file name:

- `flow`: `mermaid.mmd`. Type: `flowchart TD`.
- `mindmap`: `mermaid-mindmap.mmd`. Type: `mindmap`.
- `classes`: `mermaid-classes.mmd`. Type: `classDiagram`.
- `db`: `mermaid-db.mmd`. Type: `erDiagram`.

The file goes in `output_dir`. `output_dir` is the folder where the session started.
It can be a different folder than `scan_root`. If the file already exists, overwrite it.
It is a generated file.

## Hard rules

1. Read only. Write only `output_file`. Run no build, install, test or network command.
   Do not write, edit or delete anything inside `scan_root`, except `output_file`
   when `output_dir` is the same folder.
2. Evidence. Every node must name a real file or folder that you opened or listed.
   Put the path in a comment line above the node: `%% src: path/to/file`.
   Write the path relative to `scan_root`.
3. No invention. If you did not read an area, do not draw it.
   Put it in the Not explored list instead.
4. Keep secrets out. Do not open `.env*`, key files or credential files.
   Do not copy any secret value into the diagram.
5. Plain text. No emoji and no icons. Labels use short, plain words.
   Use ASD-STE100 style: simple words, one idea per label, active verbs.
6. Fresh scan. Do not read any `mermaid*.mmd` file as a source.
   An old generated file can be wrong. Draw only from the repo files.
7. Size limit. At most 40 nodes. If the repo is larger, draw the top level and
   name the rest in Not explored.

## Steps

1. List the files in `scan_root`. Use `git -C <scan_root> ls-files` if it is a git repo,
   else list the tree.
   Skip `node_modules`, `vendor`, `dist`, `build`, `.git`, lockfiles and binary files.
2. Find the entry points: main files, CLI scripts, server start files, `package.json`
   scripts, `Makefile` targets, workflow files, hook files, and command files.
3. Read each entry point. Follow its imports or calls one or two levels.
   Note what it reads, what it writes, and what it calls outside the repo.
4. Group files into 4 to 8 areas by purpose (for example: input, logic, storage,
   output, config, tests, tooling).
5. Draw the flow. See the shape rules below.
6. Check the diagram. See the check list below.
7. Write `output_file`. Report the path, the count and the Not explored list.

## Shape rules for `flow`

- Start the file with the front matter title, then `flowchart TD`.
- Use `subgraph` for each area. Give each subgraph a short title.
- Use these node shapes:
  - `[Name]` for code or a module
  - `[(Name)]` for storage (file, database, cache)
  - `([Name])` for an entry point or trigger
  - `{{Name}}` for an outside system (API, service, user)
- Draw an arrow only for a real call, import, read or write that you saw.
  Label an arrow with a verb when the meaning is not clear: `A -->|reads| B`.
- Use node ids that are short and plain: `cli`, `parser`, `db`. No spaces.
- Put a label in double quotes when it has `(`, `)`, `/`, `:` or `<`.
  Example: `cfg["config/app.yaml"]`.
- End the file with a comment block named Not explored.

Template:

```
---
title: <scan_root folder name> flow
---
flowchart TD
    %% src: bin/cli.js
    cli([CLI entry])
    subgraph core[Core logic]
        %% src: src/parse.js
        parse[Parse input]
    end
    %% src: data/store.json
    store[(Store file)]
    cli --> parse
    parse -->|writes| store

%% Not explored:
%% - tests/ (not read)
```

## Shape rules for `mindmap`

- Start with `mindmap`. Use one root: `root((<scan_root folder name>))`.
- Level 1 is an area. Level 2 is a module or file group. Level 3 is a key file or duty.
- Indent with two spaces per level. No arrows in a mindmap.
- Put a `%% src:` comment above each level 2 item.
- Keep labels short. Use the form `file.ext` plus a verb phrase when it helps.
- End with the same Not explored comment block.

Template:

```
mindmap
  root((repo name))
    Input
      %% src: src/cli.js
      cli.js reads arguments
    Logic
      %% src: src/parse.js
      parse.js builds the tree
```

## Shape rules for `classes`

- Start with the front matter title, then `classDiagram`.
- Draw a class for each class, struct, interface, trait or record that you read.
  Other languages: a Go struct, a Perl package with a constructor, a TypeScript
  type or interface, a C# record. Say the kind in the label when it is not a class.
- List only members that you saw in the file. Fields first, then methods.
  Add a type or return type only when the code shows it.
  Show at most 12 members per class. If a class has more, keep the public and
  important ones, and add a comment line `%% more members not shown`.
- Draw a relation only for something that you saw in code:
  - `A <|-- B` B extends or implements A
  - `A *-- B` A owns B and B has no life without A
  - `A o-- B` A holds a B that lives on its own
  - `A --> B` A uses B. Label it: `A --> B : calls`
- Put a `%% src: path` line above each `class` block.
- At most 25 classes. If the repo has more, pick the core ones and name the
  rest in Not explored.
- If the repo has no class-like types (shell scripts, plain functions, config),
  do not invent any. Write no file. Say so in the final report and suggest `flow`.

Template:

```
---
title: <scan_root folder name> classes
---
classDiagram
    %% src: src/store.py
    class Store {
        path
        load()
        save(items)
    }
    %% src: src/app.py
    class App {
        store
        run()
    }
    App --> Store : uses

%% Not explored:
%% - src/legacy/ (not read)
```

## Shape rules for `db`

- Find schema sources: SQL files, migration files, ORM model files, schema
  files (Prisma, GraphQL, Django models, EF Core entities).
  Read the files only. Do not connect to a database. Do not run migrations.
- Start with the front matter title, then `erDiagram`.
- Draw an entity for each table or model. List columns that you saw, with the
  type and the keys: `PK`, `FK`, `UK`.
  Show at most 15 columns per entity. Skip audit columns such as created_at.
- Draw a relation only from a foreign key or an explicit relation field that you saw.
  Use the Mermaid forms: `A ||--o{ B : "has"` (one to many),
  `A ||--|| B : "has"` (one to one), `A }o--o{ B : "links"` (many to many).
  Do not guess a cardinality. If it is not clear, use `A }o--o| B`
  and add a `%% check` comment.
- Put a `%% src: path` line above each entity block.
- Do not copy data values, seed rows, connection strings or passwords.
- At most 30 entities.
- If the repo has no schema source, write no file. Say so in the final report.

Template:

```
---
title: <scan_root folder name> database
---
erDiagram
    %% src: db/001_init.sql
    USERS {
        int id PK
        string email UK
    }
    %% src: db/001_init.sql
    ORDERS {
        int id PK
        int user_id FK
    }
    USERS ||--o{ ORDERS : "places"

%% Not explored:
%% - db/seed.sql (data, skipped on purpose)
```

## Check list before you write

- Each node has a `%% src:` line and the path exists. Check with `ls` or a glob.
- Each arrow matches a call you saw in a file.
- No node id is repeated. No id has a space.
- Labels with special characters are in double quotes.
- The count is within the limit: 40 nodes, 25 classes or 30 entities.
- Every class member and every column was seen in a file.
- Every relation has a code or schema line behind it.
- No secret value appears in the file.
- The Not explored block lists every area you skipped.

If a check fails, fix the diagram, then check again.

## Final report

Say, in short sentences:

- The full output path.
- The node, class or entity count.
- The Not explored list.
- One sentence on how to view it: paste into https://mermaid.live, or open it
  in an editor that renders Mermaid.
