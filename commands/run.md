---
description: Xien-flow. Write a Mermaid diagram of a repo. on|off|status, flow|mindmap|classes|db, drill list|<id>|all, repo:<absolute-path>
argument-hint: "[on|off|status|flow|mindmap|classes|db|drill list|drill <id>|drill all] [repo:<absolute-path>]"
allowed-tools: Bash, Read, Glob, Grep, Write
---
!`bash "${CLAUDE_PLUGIN_ROOT}/scripts/xien-flow.sh" $ARGUMENTS`

Read the output above.
If it starts with "XIEN-FLOW RUN" or "XIEN-FLOW DRILL", follow the procedure in it exactly.
Otherwise, do only what the output itself tells you to do, and nothing else.
