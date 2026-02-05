#!/usr/bin/env python3
"""
ASCII Diagram Grid Builder

A reusable tool for constructing ASCII diagrams with precise column placement.
Eliminates off-by-one errors by using explicit 1-based column positions.

Usage as a library (inline in a python script):
    from grid import Grid

    g = Grid(width=80)
    L = g.line()
    g.put(L, 1, '+------+')
    g.put(L, 10, 'open()')
    g.put(L, 17, '+------+-----+')
    g.emit(L)                       # prints the line

    # Or build multiple lines and print at the end:
    lines = []
    lines.append(g.build(L))        # returns string instead of printing
    for l in lines:
        print(l)

Usage as a standalone script:
    echo '<grid commands>' | python3 grid.py [--width N]

    Commands (one per line, # comments allowed):
        line                          Start a new line
        put <col> <text>              Place text at 1-based column
        fill <col1> <col2> <char>     Fill columns col1..col2 with char
        hline <col1> <col2>           Shortcut for fill with '-'
        box <col> <label>             Draw a box: +--label--+ at col
        emit                          Output the current line
        ruler                         Print a column ruler
        blank                         Output a blank line
        ---                           Output a blank line (separator)
"""

import sys


class Grid:
    """Grid builder for ASCII diagrams with 1-based column placement."""

    def __init__(self, width=80):
        self.width = width

    def line(self):
        """Create a new blank line buffer."""
        return [' '] * self.width

    def put(self, buf, col, text):
        """Place text starting at 1-based column col.

        Characters are placed left-to-right. Characters that fall outside
        the grid width are silently dropped.
        """
        for i, ch in enumerate(text):
            idx = col - 1 + i
            if 0 <= idx < self.width:
                buf[idx] = ch

    def fill(self, buf, col1, col2, ch):
        """Fill 1-based columns col1 through col2 (inclusive) with ch."""
        for c in range(col1, col2 + 1):
            idx = c - 1
            if 0 <= idx < self.width:
                buf[idx] = ch

    def hline(self, buf, col1, col2):
        """Draw a horizontal line from col1 to col2 using '-' with '+' at ends."""
        self.put(buf, col1, '+')
        self.fill(buf, col1 + 1, col2 - 1, '-')
        self.put(buf, col2, '+')

    def box_str(self, label, padding=1):
        """Return a top/bottom border string for a box with the given label.

        Example: box_str("Idle") -> "+------+"  (4 + 2 padding + 2 borders = 8)
        """
        inner = padding * 2 + len(label)
        return '+' + '-' * inner + '+'

    def box_label_str(self, label, width):
        """Return a label row for a box of the given total width.

        Example: box_label_str("Idle", 8) -> "| Idle |"
        The label is left-aligned with 1 space padding.
        """
        inner = width - 2  # subtract the two | chars
        return '|' + (' ' + label).ljust(inner) + '|'

    def build(self, buf):
        """Convert a line buffer to a string (right-stripped)."""
        return ''.join(buf).rstrip()

    def emit(self, buf):
        """Print a line buffer (right-stripped)."""
        print(self.build(buf))

    def ruler(self):
        """Print a column ruler for visual reference."""
        tens = ''
        ones = ''
        for i in range(1, self.width + 1):
            tens += str((i // 10) % 10) if i >= 10 else ' '
            ones += str(i % 10)
        print(tens)
        print(ones)


def _run_commands(commands, width=80):
    """Execute a sequence of grid commands."""
    g = Grid(width=width)
    buf = None

    for raw_line in commands:
        line = raw_line.strip()
        if not line or line.startswith('#'):
            continue

        parts = line.split(None, 2)
        cmd = parts[0].lower()

        if cmd == 'line':
            buf = g.line()
        elif cmd == 'put':
            if buf is None:
                buf = g.line()
            col = int(parts[1])
            text = parts[2] if len(parts) > 2 else ''
            g.put(buf, col, text)
        elif cmd == 'fill':
            if buf is None:
                buf = g.line()
            col1, col2 = int(parts[1]), int(parts[2].split()[0])
            ch = parts[2].split()[1] if len(parts[2].split()) > 1 else '-'
            g.fill(buf, col1, col2, ch)
        elif cmd == 'hline':
            if buf is None:
                buf = g.line()
            col1 = int(parts[1])
            col2 = int(parts[2]) if len(parts) > 2 else col1
            g.hline(buf, col1, col2)
        elif cmd == 'box':
            if buf is None:
                buf = g.line()
            col = int(parts[1])
            label = parts[2] if len(parts) > 2 else ''
            border = g.box_str(label)
            g.put(buf, col, border)
        elif cmd == 'emit':
            if buf is not None:
                g.emit(buf)
                buf = None
        elif cmd == 'ruler':
            g.ruler()
        elif cmd in ('blank', '---'):
            print()
        else:
            print(f"# Unknown command: {cmd}", file=sys.stderr)


def main():
    import argparse
    parser = argparse.ArgumentParser(description='ASCII Diagram Grid Builder')
    parser.add_argument('--width', '-w', type=int, default=80,
                        help='Grid width in characters (default: 80)')
    args = parser.parse_args()

    commands = sys.stdin.readlines()
    _run_commands(commands, width=args.width)


if __name__ == '__main__':
    main()
