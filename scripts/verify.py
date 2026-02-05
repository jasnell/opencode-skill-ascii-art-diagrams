#!/usr/bin/env python3
"""
ASCII Diagram Verifier

Automates Phase 3 (VERIFY) of the ascii-art-diagrams workflow. Reads a diagram
from stdin (or extracts from a markdown fenced code block) and runs all
mechanical verification checks:

  1. Unicode scan       - detects banned box-drawing / fancy characters
  2. Junction audit     - every |/^/v adjacent to a horizontal line has matching +
  3. Box consistency    - detects boxes and checks width/padding consistency
  4. Arrow connectivity - checks that arrows touch lines or box edges

Usage:
    # Verify a raw diagram:
    python3 verify.py < diagram.txt

    # Extract and verify a specific diagram from a markdown file:
    python3 verify.py --extract "State Machine" < file.md

    # Extract the Nth fenced code block (1-based):
    python3 verify.py --block 9 < file.md

    # Show column positions of junctions for a specific line:
    python3 verify.py --columns 5 < diagram.txt

Exit codes:
    0 = all checks passed
    1 = one or more checks failed
"""

import sys
import re
import argparse


# Characters banned from ASCII diagrams (Unicode box-drawing, fancy arrows, etc.)
BANNED_CHARS = set(
    '┌┐└┘─│├┤┬┴┼╔╗╚╝═║╭╮╰╯'
    '▶▼◀▲●○◆◇'
    '→←↑↓↔↕'
    '━┃┏┓┗┛┣┫┳┻╋'
)

# Characters that form horizontal lines
HLINE_CHARS = set('+-')

# Characters that form vertical connections
VLINE_CHARS = set('|^v')


def extract_from_markdown(text, heading=None, block_num=None):
    """Extract a fenced code block from markdown.

    If heading is given, find the first ``` block after a heading containing
    that text. If block_num is given, return the Nth block (1-based).
    Otherwise return all fenced blocks concatenated.
    """
    lines = text.split('\n')
    blocks = []
    in_block = False
    current_block = []
    heading_found = heading is None  # if no heading filter, always match

    for line in lines:
        if heading and not heading_found:
            if line.startswith('#') and heading.lower() in line.lower():
                heading_found = True
            continue

        if line.strip().startswith('```') and not in_block:
            in_block = True
            current_block = []
            continue
        elif line.strip().startswith('```') and in_block:
            in_block = False
            blocks.append('\n'.join(current_block))
            if heading:
                break  # only take first block after heading
            continue

        if in_block:
            current_block.append(line)

    if block_num is not None:
        if 1 <= block_num <= len(blocks):
            return blocks[block_num - 1]
        else:
            print(f"Error: block {block_num} not found (have {len(blocks)} blocks)",
                  file=sys.stderr)
            return ''

    if heading and blocks:
        return blocks[0]

    return '\n'.join(blocks) if blocks else text


def check_unicode(lines):
    """Step 1: Scan for banned Unicode characters."""
    issues = []
    for i, line in enumerate(lines):
        for j, ch in enumerate(line):
            if ch in BANNED_CHARS:
                issues.append(f"  Ln {i+1} col {j+1}: banned char U+{ord(ch):04X} '{ch}'")
    return issues


def _is_structural(ch, row, col, padded, width):
    """Check if a ^/v character at (row, col) is structural (not part of a word).

    Returns True if the character appears to be a diagram connector/arrow,
    False if it appears to be part of label text (surrounded by word characters).
    The | character is always structural.
    """
    if ch == '|':
        return True

    # Check horizontal neighbors for word characters
    left_char = padded[row][col - 1] if col > 0 else ' '
    right_char = padded[row][col + 1] if col + 1 < width else ' '

    # If both horizontal neighbors are word characters (letters, digits),
    # this is likely part of label text like "Server" or "Environment"
    if left_char.isalpha() and right_char.isalpha():
        return False

    # If one neighbor is a letter and the other is a space or line char,
    # it could be at the edge of a word — still likely label text
    if left_char.isalpha() or right_char.isalpha():
        # Check if this looks like it's embedded in a word
        # by scanning for adjacent alphabetic runs
        has_alpha_left = left_char.isalpha()
        has_alpha_right = right_char.isalpha()
        if has_alpha_left and has_alpha_right:
            return False
        # If alpha on one side only, check for longer word context
        if has_alpha_left:
            # Look further left for more alpha chars
            scan = col - 2
            while scan >= 0 and padded[row][scan].isalpha():
                scan -= 1
            if col - 1 - scan >= 2:  # 2+ alpha chars to the left
                return False
        if has_alpha_right:
            scan = col + 2
            while scan < width and padded[row][scan].isalpha():
                scan += 1
            if scan - col - 1 >= 2:  # 2+ alpha chars to the right
                return False

    return True


def check_junctions(lines):
    """Step 2: Junction audit.

    For every |, ^, or v that is vertically adjacent to a horizontal line
    character (+ or -), verify the horizontal line has a + (not -) at that
    exact column. Skips ^/v characters that appear to be part of label text
    (e.g., 'v' in "Server").
    """
    issues = []
    ok_count = 0
    width = max((len(l) for l in lines), default=0)
    padded = [l.ljust(width) for l in lines]

    for row in range(len(padded)):
        for col in range(width):
            ch = padded[row][col]
            if ch not in VLINE_CHARS:
                continue

            # Skip ^/v characters that are part of label text
            if ch in '^v' and not _is_structural(ch, row, col, padded, width):
                continue

            for dr, direction in [(-1, 'above'), (1, 'below')]:
                nr = row + dr
                if 0 <= nr < len(padded):
                    adj = padded[nr][col]
                    if adj in HLINE_CHARS:
                        if adj == '+':
                            ok_count += 1
                        else:
                            issues.append(
                                f"  Ln {row+1} col {col+1}: '{ch}' meets "
                                f"'-' {direction} (Ln {nr+1}) -- needs '+'"
                            )

    return issues, ok_count


def find_boxes(lines):
    """Step 3: Find box borders (patterns like +---+) and check consistency.

    Returns issues and a list of found boxes.

    Only flags width inconsistencies for borders that appear to be part of the
    same box (grouped by column AND requiring at least 2 occurrences of a width
    to establish a "box pattern"). Isolated connector lines at a column are not
    compared against box borders at that same column.
    """
    issues = []
    boxes = []

    # Find horizontal borders: sequences of +---...---+
    border_re = re.compile(r'\+[-+]+\+')

    for i, line in enumerate(lines):
        for m in border_re.finditer(line):
            start_col = m.start() + 1  # 1-based
            end_col = m.end()          # 1-based (inclusive)
            width = end_col - start_col + 1
            text = m.group()
            boxes.append({
                'line': i + 1,
                'col': start_col,
                'width': width,
                'text': text,
            })

    # Check that paired top/bottom borders of the same box have the same outer
    # width. Group by start column. Different internal junction patterns at the
    # same span (e.g., +----+----+ vs +---------+ for UML section separators)
    # are normal and not flagged. Only flag when borders at the same start
    # column have genuinely different outer widths AND both widths appear
    # multiple times (indicating a real mismatch rather than a connector/branch).
    by_col = {}
    for b in boxes:
        by_col.setdefault(b['col'], []).append(b)

    for col, group in sorted(by_col.items()):
        if len(group) < 2:
            continue
        from collections import Counter
        width_counts = Counter(b['width'] for b in group)
        if len(width_counts) <= 1:
            continue
        # Only flag when 2+ distinct widths EACH appear 2+ times
        multi_widths = [w for w, c in width_counts.items() if c >= 2]
        if len(multi_widths) >= 2:
            lines_str = ', '.join(
                f"Ln {b['line']}({b['width']})" for b in group)
            issues.append(
                f"  Col {col}: inconsistent box widths: {lines_str}"
            )

    # Check padding: look for label rows (| ... |) between borders
    # and verify at least 1 space padding on each side of text.
    # Skip arrow patterns commonly used in sequence diagrams (|-- or |<--)
    for i, line in enumerate(lines):
        for m in re.finditer(r'\|([^|]*)\|', line):
            content = m.group(1)
            if content and len(content) >= 2:
                # Skip sequence diagram arrow patterns
                stripped_content = content.lstrip()
                if stripped_content and stripped_content[0] in '-<>':
                    continue  # arrow notation, not a box label
                if content[0] != ' ':
                    col = m.start() + 1
                    issues.append(
                        f"  Ln {i+1} col {col}: missing left padding in box label"
                    )

    return issues, boxes


def check_arrows(lines):
    """Step 4: Arrow connectivity check.

    For each arrow character (v, ^, <, >), verify it is adjacent to a
    line character, box edge, or junction. Skips ^/v characters that
    appear to be part of label text (e.g., 'v' in "Server").
    """
    issues = []
    width = max((len(l) for l in lines), default=0)
    padded = [l.ljust(width) for l in lines]

    connecting_chars = set('+-|^v<>')

    for row in range(len(padded)):
        for col in range(width):
            ch = padded[row][col]
            if ch not in '^v<>':
                continue

            # Skip ^/v characters that are part of label text
            if ch in '^v' and not _is_structural(ch, row, col, padded, width):
                continue

            connected = False

            # Check all 4 adjacent cells
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = row + dr, col + dc
                if 0 <= nr < len(padded) and 0 <= nc < width:
                    adj = padded[nr][nc]
                    if adj in connecting_chars:
                        connected = True
                        break

            if not connected:
                issues.append(
                    f"  Ln {row+1} col {col+1}: floating arrow '{ch}' "
                    f"(not connected to any line)"
                )

    return issues


def show_columns(lines, line_num):
    """Show column positions of structural characters on a specific line."""
    if line_num < 1 or line_num > len(lines):
        print(f"Line {line_num} out of range (have {len(lines)} lines)")
        return

    line = lines[line_num - 1]
    structural = set('+-|^v<>')
    print(f"Line {line_num}: {line}")
    print(f"Columns:")
    for i, ch in enumerate(line):
        if ch in structural:
            print(f"  col {i+1}: '{ch}'")


def main():
    parser = argparse.ArgumentParser(description='ASCII Diagram Verifier')
    parser.add_argument('--extract', '-e', metavar='HEADING',
                        help='Extract diagram under this markdown heading')
    parser.add_argument('--block', '-b', type=int, metavar='N',
                        help='Extract the Nth fenced code block (1-based)')
    parser.add_argument('--columns', '-c', type=int, metavar='LINE',
                        help='Show column positions for a specific line number')
    parser.add_argument('--quiet', '-q', action='store_true',
                        help='Only print issues, not OK summaries')
    args = parser.parse_args()

    text = sys.stdin.read()

    # Extract diagram if needed
    if args.extract or args.block:
        text = extract_from_markdown(text, heading=args.extract,
                                     block_num=args.block)

    if not text.strip():
        print("Error: no diagram content found", file=sys.stderr)
        sys.exit(1)

    lines = text.split('\n')
    # Strip trailing empty lines
    while lines and not lines[-1].strip():
        lines.pop()

    # If just showing columns for a line, do that and exit
    if args.columns:
        show_columns(lines, args.columns)
        sys.exit(0)

    all_ok = True

    # Step 1: Unicode scan
    print("=== Step 1: Unicode Scan ===")
    unicode_issues = check_unicode(lines)
    if unicode_issues:
        all_ok = False
        print("FAIL: banned characters found:")
        for issue in unicode_issues:
            print(issue)
    else:
        if not args.quiet:
            print("OK: no banned characters")

    # Step 2: Junction audit
    print("\n=== Step 2: Junction Audit ===")
    junction_issues, junction_ok = check_junctions(lines)
    if junction_issues:
        all_ok = False
        print(f"FAIL: {len(junction_issues)} junction mismatches "
              f"({junction_ok} OK):")
        for issue in junction_issues:
            print(issue)
    else:
        if not args.quiet:
            print(f"OK: {junction_ok} junctions verified")

    # Step 3: Box consistency
    print("\n=== Step 3: Box Consistency ===")
    box_issues, boxes = find_boxes(lines)
    if box_issues:
        all_ok = False
        print(f"FAIL: {len(box_issues)} consistency issues:")
        for issue in box_issues:
            print(issue)
    else:
        if not args.quiet:
            print(f"OK: {len(boxes)} borders found, all consistent")

    # Step 4: Arrow connectivity
    print("\n=== Step 4: Arrow Connectivity ===")
    arrow_issues = check_arrows(lines)
    if arrow_issues:
        all_ok = False
        print(f"FAIL: {len(arrow_issues)} floating arrows:")
        for issue in arrow_issues:
            print(issue)
    else:
        if not args.quiet:
            arrow_count = sum(
                1 for line in lines for ch in line if ch in '^v<>'
            )
            print(f"OK: {arrow_count} arrows, all connected")

    # Step 5 (Final read-through) is manual -- remind the user
    print("\n=== Step 5: Final Read-Through ===")
    print("(Manual step -- read the diagram and check for visual/semantic issues)")

    # Summary
    print()
    if all_ok:
        print("RESULT: All automated checks PASSED")
        sys.exit(0)
    else:
        print("RESULT: Some checks FAILED -- fix issues before presenting")
        sys.exit(1)


if __name__ == '__main__':
    main()
