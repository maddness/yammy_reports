#!/usr/bin/env python3
"""
Generate PDF reports from JSON data and configuration.

Usage:
    python generate_report.py <config_file> <data_file> <output_file> [--save-html]

Examples:
    python generate_report.py configs/invoice_report.json examples/invoice_data.json output/invoice.pdf
    python generate_report.py configs/sales_report.json examples/sales_data.json output/sales.pdf --save-html
"""

import sys
import argparse
from pathlib import Path
from src.pdf_generator import PDFGenerator, load_config_from_file


def main():
    parser = argparse.ArgumentParser(
        description='Generate PDF reports from JSON data and configuration'
    )
    parser.add_argument('config', help='Path to report configuration JSON file')
    parser.add_argument('data', help='Path to input data JSON file')
    parser.add_argument('output', help='Path for output PDF file')
    parser.add_argument('--save-html', action='store_true',
                        help='Also save intermediate HTML file')

    args = parser.parse_args()

    try:
        print(f"Loading configuration from: {args.config}")
        config = load_config_from_file(args.config)

        print(f"Initializing PDF generator for: {config.name}")
        generator = PDFGenerator(config)

        print(f"Loading data from: {args.data}")
        print(f"Generating PDF to: {args.output}")

        output_path = generator.generate(
            data=args.data,
            output_path=args.output,
            save_html=args.save_html
        )

        print(f"\n✓ Success! PDF generated at: {output_path}")
        print(f"  File size: {output_path.stat().st_size / 1024:.1f} KB")

    except FileNotFoundError as e:
        print(f"✗ Error: File not found - {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"✗ Error: Invalid data - {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
