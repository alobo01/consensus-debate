#!/usr/bin/env python3
"""
clean_markdown.py

This script reads an input text file, removes unwanted ANSI escape sequences
(e.g. "weird characters"), and produces a nicely formatted Markdown output.

Optionally, if the --keep-colors flag is used and the ansi2html package is installed,
ANSI color codes will be converted into inline HTML so that (most) Markdown renderers
that support embedded HTML will show the colors.

Additionally, you can specify the file encoding via the --encoding flag.
If not provided, the script attempts to auto-detect the encoding using chardet
(if installed); otherwise, it defaults to 'utf-8'.

Dependencies:
- ansi2html (if using --keep-colors): install via `pip install ansi2html`
- chardet (optional for auto-detection): install via `pip install chardet`
"""

import re
import sys
import argparse

# Optional: Use chardet for encoding detection
try:
    import chardet
    HAS_CHARDET = True
except ImportError:
    HAS_CHARDET = False

# Try to import ansi2html for color preservation
try:
    from ansi2html import Ansi2HTMLConverter
    HAS_ANSI2HTML = True
except ImportError:
    HAS_ANSI2HTML = False

def remove_ansi_sequences(text):
    """
    Remove ANSI escape sequences from text.
    """
    ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', text)

def convert_ansi_to_html(text):
    """
    Convert ANSI escape codes to inline HTML using ansi2html.
    """
    if not HAS_ANSI2HTML:
        sys.exit("Error: ansi2html is not installed. Please install it via 'pip install ansi2html'")
    conv = Ansi2HTMLConverter(inline=True)
    return conv.convert(text, full=False)

def detect_encoding(file_path):
    """
    Auto-detect the file encoding using chardet (if available).
    """
    try:
        with open(file_path, 'rb') as f:
            rawdata = f.read()
    except Exception as e:
        sys.exit(f"Error reading file in binary mode for encoding detection: {e}")
        
    if HAS_CHARDET:
        result = chardet.detect(rawdata)
        encoding = result.get('encoding', 'utf-8')
        print(f"Detected encoding: {encoding}")
        return encoding
    else:
        print("chardet not installed; defaulting to utf-8")
        return 'utf-8'

def main():
    parser = argparse.ArgumentParser(
        description="Clean ANSI escape sequences from a file and produce formatted Markdown output."
    )
    parser.add_argument("input_file", help="Path to the input file")
    parser.add_argument("output_file", help="Path to the output Markdown file")
    parser.add_argument("--keep-colors", action="store_true",
                        help="Preserve ANSI colors by converting to inline HTML (requires ansi2html)")
    parser.add_argument("--encoding", default=None,
                        help="Specify the file encoding (if not provided, auto-detect or default to utf-8)")
    args = parser.parse_args()

    # Determine encoding: either provided or auto-detect
    if args.encoding:
        encoding = args.encoding
        print(f"Using provided encoding: {encoding}")
    else:
        encoding = detect_encoding(args.input_file)

    # Read the input file using the determined encoding; use errors='replace' to handle bad characters gracefully.
    try:
        with open(args.input_file, 'r', encoding=encoding, errors='replace') as infile:
            content = infile.read()
    except Exception as e:
        sys.exit(f"Error reading file {args.input_file}: {e}")

    # Process content
    if args.keep_colors:
        processed_content = convert_ansi_to_html(content)
        # Wrap in a <div> so that embedded HTML is properly handled in Markdown renderers.
        processed_content = f"<div>\n{processed_content}\n</div>\n"
    else:
        processed_content = remove_ansi_sequences(content)

    # Write to output file (always as UTF-8)
    try:
        with open(args.output_file, 'w', encoding='utf-8') as outfile:
            outfile.write(processed_content)
    except Exception as e:
        sys.exit(f"Error writing file {args.output_file}: {e}")

    print(f"Markdown output written to {args.output_file}")

if __name__ == "__main__":
    main()
