#!/usr/bin/env python3
"""
clean_markdown.py

This script reads an input text file, removes unwanted ANSI escape sequences (i.e. weird characters),
and outputs a cleaned-up Markdown file.

Optionally, if the --keep-colors flag is used and the ansi2html package is installed,
ANSI color codes will be converted into inline HTML so that colors are preserved in the Markdown.
(This works best if your Markdown renderer supports embedded HTML.)
"""

import re
import sys
import argparse

# Try to import ansi2html for color preservation
try:
    from ansi2html import Ansi2HTMLConverter
    HAS_ANSI2HTML = True
except ImportError:
    HAS_ANSI2HTML = False

def remove_ansi_sequences(text):
    """
    Remove ANSI escape sequences from the text.
    ANSI escape sequences match the pattern:
      ESC [ ... some characters ...
    """
    ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', text)

def convert_ansi_to_html(text):
    """
    Convert ANSI color codes in the text to inline HTML.
    This function uses the ansi2html library.
    """
    if not HAS_ANSI2HTML:
        sys.exit("Error: ansi2html is not installed. Please install it with: pip install ansi2html")
    conv = Ansi2HTMLConverter(inline=True)
    # The convert() method returns HTML that you can embed in Markdown.
    return conv.convert(text, full=False)

def main():
    parser = argparse.ArgumentParser(
        description="Clean weird (ANSI) characters from a file and produce a nicely formatted Markdown output."
    )
    parser.add_argument("input_file", help="Path to the input file")
    parser.add_argument("output_file", help="Path to the output Markdown file")
    parser.add_argument("--keep-colors", action="store_true",
                        help="Keep colors by converting ANSI codes to HTML (requires ansi2html)")
    args = parser.parse_args()

    # Read the input file
    try:
        with open(args.input_file, 'r', encoding='utf-8', errors='ignore') as infile:
            content = infile.read()
    except Exception as e:
        sys.exit(f"Error reading file {args.input_file}: {e}")

    # Process the file based on the flag
    if args.keep_colors:
        # Convert ANSI color codes to HTML
        processed_content = convert_ansi_to_html(content)
        # Wrap the HTML in a <div> so that it can be embedded in Markdown
        processed_content = f"<div>\n{processed_content}\n</div>\n"
    else:
        # Simply remove ANSI escape sequences
        processed_content = remove_ansi_sequences(content)

    # Write the processed text to the output Markdown file
    try:
        with open(args.output_file, 'w', encoding='utf-8') as outfile:
            outfile.write(processed_content)
    except Exception as e:
        sys.exit(f"Error writing file {args.output_file}: {e}")

    print(f"Markdown output written to {args.output_file}")

if __name__ == "__main__":
    main()
