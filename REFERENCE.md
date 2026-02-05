# REFERENCE MATERIAL

The following sections provide patterns, templates, and examples. Consult as needed but always follow the PLAN, DRAW, VERIFY workflow! These are not shortcuts, but rather resources to help you execute each phase correctly.

As you work, you must confirm that you are following the workflow described above and not skipping any steps.

---

## Box Construction

### Standard Box Pattern

```
+------------+
|   Label    |
+------------+
```

Rules:

- Top and bottom edges: `+` at corners, `-` between
- Side edges: `|`
- Content centered with at least 1 space padding
- Consistent width for related boxes

### Box Width Calculation

For text "Hello World" (11 chars):

- Add 2 for padding: 13
- Add 2 for side borders: 15
- Total: `+-------------+` (13 dashes)

```
+---------------+
|  Hello World  |
+---------------+
```

## Connection Patterns

### Vertical Connections

```
+--------+
| Box A  |
+---+----+
    |
    v
+---+----+
| Box B  |
+--------+
```

The vertical line must align with a `+` in the boxes above and below.

### Horizontal Connections

```
+--------+         +--------+
| Box A  |-------->| Box B  |
+--------+         +--------+
```

### Branching (Decision Points)

```
            +----------+
            | Decision |
            +----+-----+
                 |
            +----+----+
            |         |
           Yes        No
            |         |
            v         v
       +--------+ +--------+
       | Path A | | Path B |
       +--------+ +--------+
```

Key alignment rules:

- The `+` under the decision box aligns with the `|` above
- Branch labels (Yes/No) are centered over their paths
- Child boxes' center `+` align with their branch lines

### Merging Paths

```
   +--------+     +--------+
   | Box A  |     | Box B  |
   +---+----+     +---+----+
       |              |
       +------+-------+
              |
              v
         +----+---+
         | Box C  |
         +--------+
```

## Diagram Templates

### Simple Flowchart

```
      +------------+
      |   Start    |
      +-----+------+
            |
            v
      +-----+------+
      |  Process   |
      +-----+------+
            |
            v
      +-----+------+
      |    End     |
      +------------+
```

### Decision Tree

```
               +------------------+
               |     Decision     |
               +--------+---------+
                        |
                  +-----+-----+
                  |           |
                 Yes          No
                  |           |
                  v           v
             +----+----+ +----+----+
             | Path A  | | Path B  |
             +----+----+ +----+----+
                  |           |
                  +-----+-----+
                        |
                        v
                  +-----+-----+
                  |   Done    |
                  +-----------+
```

### Nested Component Diagram

```
+-------------------------------------------------------------+
|                       Web Application                       |
+-------------------------------------------------------------+
|                                                             |
|  +----------+                      +-----------+            |
|  | Frontend |                      |API Gateway|            |
|  | (React)  |--------------------->|  (nginx)  |            |
|  +----------+                      +-----+-----+            |
|                                          |                  |
|                                          v                  |
|                                    +-----+-----+            |
|                                    |  Backend  |            |
|                                    |  Service  |            |
|                                    +-----+-----+            |
|                                          |                  |
|                            +-------------+------------+     |
|                            |             |            |     |
|                            v             v            v     |
|                      +-----+----+   +----+----+   +---+---+ |
|                      | Database |   |  Cache  |   | Queue | |
|                      +----------+   +---------+   +-------+ |
|                                                             |
+-------------------------------------------------------------+
```

### Sequence Diagram

```
  Client          Server          Database
     |               |               |
     | HTTP Request  |               |
     |-------------->|               |
     |               |               |
     |               |  SQL Query    |
     |               |-------------->|
     |               |               |
     |               |    Results    |
     |               |<--------------|
     |               |               |
     | JSON Response |               |
     |<--------------|               |
     |               |               |
     v               v               v
```

### State Machine

```
              +-------------+
     +------->|    IDLE     |
     |        +------+------+
     |               |
     |           event A
     |               |
     |               v
     |        +------+------+
     |        |   ACTIVE    |
     |        +------+------+
     |               |
     |           event B
     |               |
     |               v
     |        +------+------+
     +--------+    DONE     |
              +-------------+
```

### Tree Structure

```
                     root
                       |
        +--------------+--------------+
        |              |              |
        v              v              v
    child-a        child-b        child-c
        |                              |
   +----+----+                    +----+----+
   |         |                    |         |
   v         v                    v         v
leaf-1    leaf-2               leaf-3    leaf-4
```

### Memory Layout

```
  High Address
  +----------------+
  |     Stack      |
  |       |        |
  |       v        |
  |                |
  |       ^        |
  |       |        |
  |      Heap      |
  +----------------+
  |      BSS       |
  +----------------+
  |      Data      |
  +----------------+
  |      Text      |
  +----------------+
  Low Address
```

### RFC-Style Packet Diagram

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|     Type      |    Length     |            Value              |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                           Payload                             |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

### Git Branch Diagram

```
main     ----*----*-----------*----
                   \         /
feature             *---*---*
```

## Common Mistakes

### Mistake: Junction Misalignment

The junction appears close but is off by one column.

**Wrong** (+ is at column 5, but | is at column 6):

```
      |
  +---+---+
  |       |
```

**Right** (| is at column 6, middle + is at column 6):

```
      |
  +---+---+
      |
```

### Mistake: Missing Junction

When paths branch or merge, every `|` needs a corresponding `+`.

**Wrong:**

```
    |              |
    +--------------+
           |
```

**Right:**

```
    |              |
    +------+-------+
           |
```

### Mistake: Arrow Not Touching Target

**Wrong:**

```
+--------+
| Box A  |
+--------+
    |
    v

+--------+
| Box B  |
+--------+
```

**Right:**

```
+--------+
| Box A  |
+---+----+
    |
    v
+---+----+
| Box B  |
+--------+
```

### Mistake: Inconsistent Box Widths

**Wrong:**

```
+--------+     +----------------+     +-----+
| Short  |     | Medium Label   |     |Tiny |
+--------+     +----------------+     +-----+
```

**Right** (for related boxes at same level):

```
+----------------+  +----------------+  +----------------+
|     Short      |  | Medium Label   |  |      Tiny      |
+----------------+  +----------------+  +----------------+
```

### Mistake: No Padding From Container Edge

**Wrong:**

```
+------------------------+
|  +--------+  +--------+|
|  | Box A  |  | Box B  ||
|  +--------+  +--------+|
+------------------------+
```

**Right:**

```
+----------------------------+
|  +--------+    +--------+  |
|  | Box A  |    | Box B  |  |
|  +--------+    +--------+  |
+----------------------------+
```

## Width Reference

Common box templates:

```
8 chars inner:
+----------+
| 8 chars  |
+----------+

10 chars inner:
+------------+
| 10 chars   |
+------------+

12 chars inner:
+--------------+
|   12 chars   |
+--------------+
```

## Constraints

- Maximum width: 100 characters (prefer 80)
- Maximum boxes: 15-20 (split diagram if more)
- Maximum nesting: 2-3 levels
- Always use spaces, never tabs

## Markdown Usage

Always wrap diagrams in triple-backtick code fences:

````
```
+---------+
| Diagram |
+---------+
```
````

Do NOT use a language identifier (like `text` or `ascii`).
