"""
PDF Generator - Main module for generating PDFs from structured JSON data.

This module provides the main PDFGenerator class that orchestrates the entire
PDF generation process from JSON data and configuration.
"""

import json
from pathlib import Path
from typing import Dict, Any, Union
from weasyprint import HTML, CSS
from src.config_schema import ReportConfig
from src.page_builder import PageBuilder


class PDFGenerator:
    """
    Main PDF generator class.

    Generates PDF documents from structured JSON data using report configurations.
    """

    def __init__(self, config: ReportConfig):
        """
        Initialize PDF generator with a report configuration.

        Args:
            config: Report configuration defining the document structure and styling
        """
        self.config = config
        self.page_builder = PageBuilder(config)

        # Validate configuration
        errors = self.config.validate()
        if errors:
            raise ValueError(f"Invalid configuration: {', '.join(errors)}")

    def generate(
        self,
        data: Union[Dict[str, Any], str, Path],
        output_path: Union[str, Path],
        save_html: bool = False
    ) -> Path:
        """
        Generate PDF from JSON data.

        Args:
            data: JSON data as dict, JSON string, or path to JSON file
            output_path: Path where PDF should be saved
            save_html: If True, also save the intermediate HTML file

        Returns:
            Path to generated PDF file

        Raises:
            ValueError: If data is invalid
            IOError: If file operations fail
        """
        # Load data if needed
        json_data = self._load_data(data)

        # Build HTML document
        html_content = self.page_builder.build_document(json_data)

        # Save HTML if requested
        if save_html:
            html_path = Path(str(output_path).replace('.pdf', '.html'))
            html_path.write_text(html_content, encoding='utf-8')
            print(f"HTML saved to: {html_path}")

        # Generate PDF
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        html = HTML(string=html_content, base_url=str(Path.cwd()))
        html.write_pdf(str(output_path))

        print(f"PDF generated: {output_path}")
        return output_path

    def preview_html(self, data: Union[Dict[str, Any], str, Path]) -> str:
        """
        Generate HTML preview without creating PDF.

        Args:
            data: JSON data as dict, JSON string, or path to JSON file

        Returns:
            HTML content as string
        """
        json_data = self._load_data(data)
        return self.page_builder.build_document(json_data)

    def _load_data(self, data: Union[Dict[str, Any], str, Path]) -> Dict[str, Any]:
        """
        Load JSON data from various sources.

        Args:
            data: Data as dict, JSON string, or file path

        Returns:
            Dictionary containing the data

        Raises:
            ValueError: If data is invalid
            IOError: If file cannot be read
        """
        if isinstance(data, dict):
            return data

        if isinstance(data, (str, Path)):
            # Try as file path first
            path = Path(data)
            if path.exists() and path.is_file():
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON in file '{path}': {e}")
                except IOError as e:
                    raise IOError(f"Cannot read file '{path}': {e}")

            # Try as JSON string (only for str type, not Path)
            if isinstance(data, str):
                try:
                    return json.loads(data)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON string: {e}")

            # If it's a Path object but file doesn't exist
            if isinstance(data, Path):
                raise ValueError(f"File not found: {path}")

            # If it's a string but not valid JSON and not a file
            raise ValueError(f"String is neither a valid file path nor valid JSON: {data}")

        raise ValueError(f"Unsupported data type: {type(data)}")


def load_config_from_dict(config_dict: Dict[str, Any]) -> ReportConfig:
    """
    Load report configuration from a dictionary.

    Args:
        config_dict: Configuration as dictionary

    Returns:
        ReportConfig instance

    Raises:
        ValueError: If required fields are missing or invalid types
    """
    from src.config_schema import (
        ReportConfig, PageConfig, BlockMapping, ChartMapping,
        TextStyle, FontConfig, BackgroundConfig, PaddingConfig
    )

    # Validate required top-level field
    if 'name' not in config_dict:
        raise ValueError("Configuration must include 'name' field")

    # Parse text styles
    text_styles = {}
    for style_name, style_data in config_dict.get('text_styles', {}).items():
        font_data = style_data.get('font', {})

        # Validate font_data is a dict if present
        if font_data and not isinstance(font_data, dict):
            raise ValueError(f"Font configuration for style '{style_name}' must be a dictionary, got {type(font_data).__name__}")

        font = FontConfig(**font_data) if font_data else FontConfig()

        text_styles[style_name] = TextStyle(
            name=style_name,
            font=font,
            line_height=style_data.get('line_height', 1.5),
            text_align=style_data.get('text_align', 'left'),
            margin_top=style_data.get('margin_top', 0),
            margin_bottom=style_data.get('margin_bottom', 0),
        )

    # Parse pages
    pages = []
    for page_idx, page_data in enumerate(config_dict.get('pages', [])):
        # Validate required page field
        if 'name' not in page_data:
            raise ValueError(f"Page at index {page_idx} is missing required 'name' field")

        # Parse background
        bg_data = page_data.get('background', {})
        background = BackgroundConfig(**bg_data) if bg_data else BackgroundConfig()

        # Parse padding
        pad_data = page_data.get('padding', {})
        padding = PaddingConfig(**pad_data) if pad_data else PaddingConfig()

        # Parse blocks
        blocks = []
        for block_idx, block_data in enumerate(page_data.get('blocks', [])):
            # Validate required block fields
            missing_fields = []
            for field in ['json_path', 'style', 'template']:
                if field not in block_data:
                    missing_fields.append(field)

            if missing_fields:
                raise ValueError(
                    f"Block at index {block_idx} in page '{page_data['name']}' is missing required fields: {', '.join(missing_fields)}"
                )

            blocks.append(BlockMapping(
                json_path=block_data['json_path'],
                style=block_data['style'],
                template=block_data['template'],
                container_class=block_data.get('container_class')
            ))

        # Parse charts
        charts = []
        for chart_idx, chart_data in enumerate(page_data.get('charts', [])):
            # Validate required chart fields
            missing_fields = []
            for field in ['json_path', 'chart_type']:
                if field not in chart_data:
                    missing_fields.append(field)

            if missing_fields:
                raise ValueError(
                    f"Chart at index {chart_idx} in page '{page_data['name']}' is missing required fields: {', '.join(missing_fields)}"
                )

            # Validate and convert chart dimensions to int
            width = chart_data.get('width', 8)
            height = chart_data.get('height', 5)

            try:
                width = int(width)
                height = int(height)
            except (ValueError, TypeError):
                raise ValueError(
                    f"Chart at index {chart_idx} in page '{page_data['name']}' has invalid width/height: must be numeric"
                )

            if width <= 0 or height <= 0:
                raise ValueError(
                    f"Chart at index {chart_idx} in page '{page_data['name']}' has invalid dimensions: width and height must be positive"
                )

            charts.append(ChartMapping(
                json_path=chart_data['json_path'],
                chart_type=chart_data['chart_type'],
                title=chart_data.get('title'),
                width=width,
                height=height,
                color_scheme=chart_data.get('color_scheme', 'professional'),
                labels_field=chart_data.get('labels_field'),
                values_field=chart_data.get('values_field'),
                x_field=chart_data.get('x_field'),
                y_field=chart_data.get('y_field'),
                series=chart_data.get('series'),
                xlabel=chart_data.get('xlabel', ''),
                ylabel=chart_data.get('ylabel', ''),
                show_values=chart_data.get('show_values', True),
                container_class=chart_data.get('container_class')
            ))

        pages.append(PageConfig(
            name=page_data['name'],
            background=background,
            padding=padding,
            blocks=blocks,
            charts=charts,
            custom_css=page_data.get('custom_css')
        ))

    return ReportConfig(
        name=config_dict['name'],
        page_size=config_dict.get('page_size', 'A4'),
        orientation=config_dict.get('orientation', 'portrait'),
        fonts=config_dict.get('fonts', {}),
        text_styles=text_styles,
        pages=pages,
        global_css=config_dict.get('global_css')
    )


def load_config_from_file(config_path: Union[str, Path]) -> ReportConfig:
    """
    Load report configuration from a JSON file.

    Args:
        config_path: Path to configuration file

    Returns:
        ReportConfig instance
    """
    with open(config_path, 'r', encoding='utf-8') as f:
        config_dict = json.load(f)

    return load_config_from_dict(config_dict)
