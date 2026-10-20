---
description: Xien-flow. Write a Mermaid diagram of a repo. Use on|off|status, or flow|mindmap|classes|db [repo:<absolute-path>]
argument-hint: "[on|off|status|flow|mindmap|classes|db] [repo:<absolute-path>]"
allowed-tools: Bash, Read, Glob, Grep, Write
---
!`bash "${CLAUDE_PLUGIN_ROOT}/scripts/xien-flow.sh" $ARGUMENTS`

Read the output above.
If it starts with "XIEN-FLOW RUN", follow the procedure in it exactly.
Otherwise, say the output in one short sentence and do nothing else.
