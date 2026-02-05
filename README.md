# ascii-art-diagrams

An OpenCode skill for creating properly aligned ASCII art diagrams in markdown files.

LLMs are remarkably bad at creating ASCII art diagrams, frequently getting alignment
wrong, using banned Unicode box-drawing characters, and producing semantically incorrect
layouts. This skill enforces a mandatory three-phase workflow (PLAN, DRAW, VERIFY) that
produces correct, well-aligned diagrams.

The skill text rather heavily emphasizes the mandated steps because many models see
"You MUST do..." then decide the step is optional and skip it entirely. Repetition is
intentional.

That said, the workflow adds significant time to diagram generation, emphasizing
correctness over speed. If you need a quick rough diagram, say so in your prompt and
the skill should relax the more detailed steps.

## Installation

### Prerequisites

- [OpenCode](https://opencode.ai) installed and configured
- Python 3 (for the helper scripts)

### Install as a global skill

Clone the repo into your OpenCode global skills directory:

```bash
git clone <repo-url> ~/.config/opencode/skills/ascii-art-diagrams
```

Or if you already have it elsewhere, symlink it:

```bash
ln -s /path/to/ascii-art-diagrams ~/.config/opencode/skills/ascii-art-diagrams
```

OpenCode discovers global skills from `~/.config/opencode/skills/*/SKILL.md`.

### Install as a project-local skill

To make the skill available only within a specific project:

```bash
git clone <repo-url> .opencode/skills/ascii-art-diagrams
```

OpenCode also supports `.claude/skills/` and `.agents/skills/` directories.

### Verify installation

Once installed, the skill should appear in OpenCode's available skills list. The agent
loads it automatically when it recognizes a diagram task, or you can request it
explicitly by asking OpenCode to "load the ascii-art-diagrams skill" or by using
the `/skill` tool call.

If the skill doesn't appear, check:

1. The directory is named `ascii-art-diagrams` (must match the `name` in frontmatter)
2. The file is named `SKILL.md` (all caps)
3. The frontmatter contains both `name` and `description` fields

## Files

| File                | Purpose                                                                                                                                                                                                                                                    |
| ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `SKILL.md`          | Main skill definition. Defines the mandatory PLAN/DRAW/VERIFY workflow, character whitelist, junction rules, and all verification steps. This is what OpenCode loads.                                                                                      |
| `REFERENCE.md`      | Reference material: box construction patterns, connection templates, diagram templates (flowcharts, decision trees, sequence diagrams, state machines, etc.), common mistakes, and width references. Consulted by the agent as needed during the workflow. |
| `scripts/grid.py`   | Grid builder library for Phase 2 (DRAW). Provides `Grid` class with precise 1-based column placement to eliminate off-by-one alignment errors. Used as a Python library via `from grid import Grid`.                                                       |
| `scripts/verify.py` | Automated verifier for Phase 3 (VERIFY). Checks for banned Unicode characters, junction alignment, box consistency, and arrow connectivity. Exit code 0 = pass, 1 = fail.                                                                                  |

## How it works

When loaded, the skill instructs the agent to follow three mandatory phases for every
diagram:

1. **PLAN** -- Calculate dimensions, create a column ruler, assign column positions for
   all vertical elements, and verify everything fits within the max width.

2. **DRAW** -- Construct the diagram using only the allowed character set (`+`, `-`,
   `|`, `>`, `<`, `^`, `v`, `/`, `\`). The `grid.py` script is recommended for precise
   column placement.

3. **VERIFY** -- Run `verify.py` to automate checks (Unicode scan, junction audit, box
   consistency, arrow connectivity), then perform a manual read-through. No diagram is
   presented until all checks pass.

## Usage examples

### Using grid.py

```python
import sys
sys.path.insert(0, '/path/to/ascii-art-diagrams/scripts')
from grid import Grid

g = Grid(width=80)
L = g.line()
g.put(L, 1, '+----------+')
g.put(L, 20, '+----------+')
g.emit(L)
```

### Using verify.py

```bash
# Verify piped output
python3 draw.py | python3 /path/to/scripts/verify.py

# Verify a specific diagram from a markdown file by heading
python3 /path/to/scripts/verify.py --extract "State Machine" < doc.md

# Verify the Nth fenced code block (1-based)
python3 /path/to/scripts/verify.py --block 3 < doc.md

# Quiet mode (only print failures)
python3 /path/to/scripts/verify.py --quiet < diagram.txt
```

## License

MIT
