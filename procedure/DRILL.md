# Drill procedure

Use this section when the header says `XIEN-FLOW DRILL`. The common rules above apply.
Use only the flow shape rules for the drawing. Ignore the other mode sections.

A drill is one deeper diagram of one area of schema 0. The header lists one `area:`
block, or several when the target is `all`. Make one output file per area block.
Do the areas one after another.

## Steps for each area

1. Read `schema0_file`. Find the area's `subgraph` and the nodes inside it.
   List every arrow that enters or leaves those nodes. These are the boundary arrows.
2. Read the area's `area_paths` in depth. List the files first.
   Read at most 60 files. For a bigger area, read entry files, index files and
   the most imported files first, and name the rest in Not explored.
   Read shell, CI, deploy, container and config files with `safe_read`.
3. Draw the area as `flowchart TD`, with this front matter and first lines:
   ```
   ---
   title: <repo_name> / <area_label> (drill <drill_id>)
   ---
   flowchart TD
       %% scan_root: <scan_root>
       %% drill_of: <drill_id>
   ```
4. Inside the area, draw the real parts: files, components, functions, stores, calls.
   Use the same shape rules, evidence lines (`%% src:`) and limits as for `flow`.
   Make the area itself the detail. Show how its parts call each other, what each part
   reads and writes, and what it calls outside the area. Draw up to 40 nodes.
5. Draw the boundary. For each boundary arrow from step 1, draw the outside node
   with the same id and label that schema 0 uses. Style outside nodes with a dashed edge:
   ```
   classDef ext stroke-dasharray: 4 3
   class mainrt,fetch ext
   ```
   Draw the boundary arrows between the outside nodes and your inner nodes. If you
   cannot match a boundary arrow to a real inner node, draw it to a node named
   `unmatched` with a dotted arrow and `%% unverified`.
6. Check schema 0 against the code. For each dotted or `%% unverified` arrow in
   schema 0 that touches this area, decide from the code: confirmed or not found.
   Do not edit `schema0_file`. Do not draw an arrow that you did not see.
7. End the file with the Not explored block, as for `flow`.
8. Run the check list. Write the file named by `output_file`. Run `lint` from the header on it.
   Fix every problem it lists and write again, until it prints `LINT OK`.

## Report for a drill

For each area, say in short sentences:

- The output path and the node count.
- Schema 0 arrows now confirmed.
- Schema 0 arrows not found in code. Tell the person to check schema 0.
- The Not explored list.

For `all`, also give the skipped areas if the header lists any.
If the area paths hold no code, write no file for that area and say so.
