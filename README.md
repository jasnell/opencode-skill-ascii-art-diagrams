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

### Sample outputs

A collection of sample ASCII diagrams demonstrating various diagram types.
All diagrams use only basic ASCII characters: `+`, `-`, `|`, `>`, `<`, `^`, `v`, `/`, `\`.

#### 1. Linear Flowchart

A simple top-to-bottom process flow showing sequential steps.

```
+----------------+
|     Start      |
+-------+--------+
        |
        v
+-------+--------+
|   Read Input   |
+-------+--------+
        |
        v
+-------+--------+
|  Process Data  |
+-------+--------+
        |
        v
+-------+--------+
|  Write Output  |
+-------+--------+
        |
        v
+-------+--------+
|      End       |
+----------------+
```

#### 2. System Architecture

A container diagram showing a web application with three internal components
connected by data-flow arrows.

```
+------------------------------------------------------------+
|  Web Application                                           |
|                                                            |
|  +--------------+    +---------+----+    +--------------+  |
|  |   Frontend   | -> |  API Server  | -> |   Database   |  |
|  +--------------+    +---------+----+    +--------------+  |
|                                                            |
+------------------------------------------------------------+
```

#### 3. Decision Tree

A branching flowchart with a conditional check and two parallel paths.

```
             +--------+--------+
             |    Check Age    |
             +--------+--------+
                      |
   No                 |                Yes
         +------------+------------+
         |                         |
         v                         v
+--------+--------+       +--------+--------+
|   Under 18      |       | 18 or Over      |
+--------+--------+       +--------+--------+
         |                         |
         v                         v
+--------+--------+       +--------+--------+
|  Deny Access    |       | Grant Access    |
+--------+--------+       +--------+--------+
```

#### 4. Sequence Diagram

A message sequence chart showing HTTP request/response flow between
a client, server, and database.

```
+-----------+             +-----+-----+             +-----------+
|  Client   |             |  Server   |             | Database  |
+-----+-----+             +-----+-----+             +-----+-----+
      |                         |                         |
      |-- GET /users ---------->|                         |
      |                         |                         |
      |                         |-- Query --------------->|
      |                         |                         |
      |                         |<------- Results --------|
      |                         |                         |
      |<----------- 200 OK -----|                         |
      |                         |                         |
```

#### 5. Entity Relationship Diagram

Three database entities with their fields, connected by labeled
relationship lines (1:N = one-to-many, N:M = many-to-many).

```
+---------------+        +---------------+        +---------------+
|    Users      |        |    Orders     |        |   Products    |
+---------------+        +---------------+        +---------------+
| PK id         |        | PK id         |        | PK id         |
|    name       +--1:N-->+ FK user_id    +--N:M-->+    name       |
|    email      |        |    total      |        |    price      |
|               |        |    status     |        |               |
+---------------+        +---------------+        +---------------+
```

#### 6. Network Topology (Star/Hub-and-Spoke)

A star network topology with a central router connected to four
peripheral devices.

```
                        +---------+
                        |  PC-1   |
                        +----+----+
                             |
                             |
    +----+----+         +----+----+         +----+----+
    | Server  +---------+ Router  +---------+ Printer |
    +----+----+         +----+----+         +----+----+
                             |
                             |
                        +----+----+
                        |  PC-2   |
                        +---------+
```

#### 7. Three-Tier Architecture

A production system with three nested tiers (Presentation, Logic, Data),
each containing three API components. Vertical arrows show the downward
data flow between tiers.

```
+--- Production System -------------------------------------------------+
|                                                                       |
|  +-----------+--------------------+--------------------+-----------+  |
|  |                      Presentation Tier                          |  |
|  |  +--------+--------+  +--------+--------+  +--------+--------+  |  |
|  |  |     Web App     |  |    Mobile API   |  |   Admin Panel   |  |  |
|  |  +--------+--------+  +--------+--------+  +--------+--------+  |  |
|  |           |                    |                    |           |  |
|  +-----------+--------------------+--------------------+-----------+  |
|              |                    |                    |              |
|              v                    v                    v              |
|  +-----------+--------------------+--------------------+-----------+  |
|  |                         Logic Tier                              |  |
|  |  +--------+--------+  +--------+--------+  +--------+--------+  |  |
|  |  |    Auth API     |  |   Order API     |  |   Notify API    |  |  |
|  |  +--------+--------+  +--------+--------+  +--------+--------+  |  |
|  |           |                    |                    |           |  |
|  +-----------+--------------------+--------------------+-----------+  |
|              |                    |                    |              |
|              v                    v                    v              |
|  +-----------+--------------------+--------------------+-----------+  |
|  |                          Data Tier                              |  |
|  |  +--------+--------+  +--------+--------+  +--------+--------+  |  |
|  |  |    PostgreSQL   |  |   Redis Cache   |  |    S3 Storage   |  |  |
|  |  +--------+--------+  +--------+--------+  +--------+--------+  |  |
|  |                                                                 |  |
|  +-----------+--------------------+--------------------+-----------+  |
|                                                                       |
+-----------------------------------------------------------------------+
```

#### 8. Data Pipeline (Fan-Out / Fan-In)

A data processing pipeline that fans out from a single source to four
parallel stages, fans back in to an aggregation step, then splits to
two outputs. All junctions use `+` where pipes meet horizontal branch lines.

```
                                 +-----------+
                                 |  Ingest   |
                                 +-----+-----+
                                       |
                                       v
               +---------------+-------+-------+---------------+
               |               |               |               |
               v               v               v               v
         +-----+-----+   +-----+-----+   +-----+-----+   +-----+-----+
         |   Parse   |   | Validate  |   |  Enrich   |   | Transform |
         +-----+-----+   +-----+-----+   +-----+-----+   +-----+-----+
               |               |               |               |
               v               v               v               v
               +---------------+-------+-------+---------------+
                                       |
                                       v
                                 +-----+-----+
                                 | Aggregate |
                                 +-----+-----+
                                       |
                                       v
                              +--------+--------+
                              |                 |
                              v                 v
                        +-----+-----+     +-----+-----+
                        | Data Lake |     | Dashboard |
                        +-----------+     +-----------+
```

#### 9. State Machine (HTTP Connection Lifecycle)

An HTTP connection state machine with states, labeled transitions,
a loop (Waiting -> Connected via "response"), and multiple paths
to the Closed state (timeout, close, error).

```
                       +-----------------timeout---------------->+
                       |                                         |
+------+ open() +------+-----+  ack   +------------+ close()+----+---+
| Idle |------->| Connecting |------->| Connected  |------->| Closed |
+------+        +------------+        +------+-----+        +----+---+
                                      ^      | send()            ^
                                      |      v                   |
                                      | +----+----+              |
                           response   | | Sending |              |
                                      | +----+----+              |
                                      |      | flush             |
                                      |      v                   |
                                      | +----+----+              |
                                      +-| Waiting +----error-----+
                                        +---------+
```

#### 10. Class Hierarchy (UML-Style)

A UML class diagram showing an `<<interface>>` at the top, two
concrete classes inheriting from it (upward `^` arrows), and a
shared dependency on a Logger class (dashed `- -` lines downward).

```
                            +---------------------+
                            |    <<interface>>    |
                            |     EventEmitter    |
                            +---------------------+
                            | + on()              |
                            | + emit()            |
                            | + off()             |
                            +----+-----------+----+
                                 ^           ^
                                 |           |
                      +----------+           +----------+
                      |                                 |
           +----------+----------+           +----------+----------+
           |    HttpServer       |           |    WebSocket        |
           +---------------------+           +---------------------+
           | - port: number      |           | - url: string       |
           | - host: string      |           | - state: string     |
           +---------------------+           +---------------------+
           | + listen()          |           | + connect()         |
           | + close()           |           | + send()            |
           +----------+----------+           +----------+----------+
                      |                                 |
                      +- - - - - +   uses    +- - - - - +
                                 |           |
                                 v           v
                            +----+-----------+----+
                            |     Logger          |
                            +---------------------+
                            | + info()            |
                            | + error()           |
                            +---------------------+
```

## License

MIT
