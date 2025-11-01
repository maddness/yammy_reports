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
        """
        if isinstance(data, dict):
            return data

        if isinstance(data, (str, Path)):
            # Try as file path first
            try:
                path = Path(data)
                if path.exists() and path.is_file():
                    with open(path, 'r', encoding='utf-8') as f:
                        return json.load(f)
            except (IOError, json.JSONDecodeError):
                pass

            # Try as JSON string
            if isinstance(data, str):
                try:
                    return json.loads(data)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON data: {e}")

        raise ValueError(f"Unsupported data type: {type(data)}")


def load_config_from_dict(config_dict: Dict[str, Any]) -> ReportConfig:
    """
    Load report configuration from a dictionary.

    Args:
        config_dict: Configuration as dictionary

    Returns:
        ReportConfig instance
    """
    from src.config_schema import (
        ReportConfig, PageConfig, BlockMapping,
        TextStyle, FontConfig, BackgroundConfig, PaddingConfig
    )

    # Parse text styles
    text_styles = {}
    for style_name, style_data in config_dict.get('text_styles', {}).items():
        font_data = style_data.get('font', {})
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
    for page_data in config_dict.get('pages', []):
        # Parse background
        bg_data = page_data.get('background', {})
        background = BackgroundConfig(**bg_data) if bg_data else BackgroundConfig()

        # Parse padding
        pad_data = page_data.get('padding', {})
        padding = PaddingConfig(**pad_data) if pad_data else PaddingConfig()

        # Parse blocks
        blocks = []
        for block_data in page_data.get('blocks', []):
            blocks.append(BlockMapping(
                json_path=block_data['json_path'],
                style=block_data['style'],
                template=block_data['template'],
                container_class=block_data.get('container_class')
            ))

        pages.append(PageConfig(
            name=page_data['name'],
            background=background,
            padding=padding,
            blocks=blocks,
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
