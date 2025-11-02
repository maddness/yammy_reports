"""
Page builder for rendering JSON data into HTML pages.

This module handles the mapping of JSON data to page elements using Jinja2 templates.
"""

from typing import Any, Dict, List
import json
from jinja2 import Template, Environment, BaseLoader
from src.config_schema import PageConfig, ReportConfig, BlockMapping, ChartMapping
from src.chart_builder import ChartBuilder, extract_chart_data


class PageBuilder:
    """Builds HTML pages from JSON data and configuration."""

    def __init__(self, config: ReportConfig):
        """
        Initialize page builder with report configuration.

        Args:
            config: Report configuration
        """
        self.config = config
        self.jinja_env = Environment(loader=BaseLoader(), autoescape=True)

    def extract_data(self, data: Dict[str, Any], json_path: str) -> Any:
        """
        Extract data from JSON using a simple path expression.

        Args:
            data: Source JSON data
            json_path: Dot-notation path (e.g., "user.name" or "items[0].title")

        Returns:
            Extracted data or None if path not found

        Raises:
            ValueError: If JSONPath syntax is malformed (not for missing/null data)
        """
        # First, validate JSONPath syntax (before attempting navigation)
        parts = json_path.split('.')

        for part in parts:
            if '[' in part or ']' in part:
                # Validate bracket structure (SYNTAX validation - should raise)
                if not ('[' in part and ']' in part):
                    raise ValueError(
                        f"Malformed array index in JSONPath '{json_path}' at segment '{part}': "
                        f"brackets must come in pairs"
                    )

                # Validate bracket order
                open_idx = part.index('[')
                close_idx = part.index(']')

                if open_idx >= close_idx:
                    raise ValueError(
                        f"Malformed array index in JSONPath '{json_path}' at segment '{part}': "
                        f"closing bracket must come after opening bracket"
                    )

                # Check for multiple bracket pairs (not supported)
                if part.count('[') > 1 or part.count(']') > 1:
                    raise ValueError(
                        f"Malformed array index in JSONPath '{json_path}' at segment '{part}': "
                        f"multiple bracket pairs in single segment not supported. "
                        f"Use separate path segments (e.g., 'matrix[0].[1]' instead of 'matrix[0][1]')"
                    )

                index_str = part[open_idx + 1:close_idx]

                # Validate index is not empty
                if not index_str.strip():
                    raise ValueError(
                        f"Malformed array index in JSONPath '{json_path}' at segment '{part}': "
                        f"index cannot be empty"
                    )

                # Validate index is an integer (SYNTAX validation)
                try:
                    int(index_str)
                except ValueError:
                    raise ValueError(
                        f"Malformed array index in JSONPath '{json_path}' at segment '{part}': "
                        f"index '{index_str}' is not a valid integer"
                    )

        # Now navigate the data structure (DATA validation - returns None on mismatch)
        try:
            current = data

            for part in parts:
                # Check if current is None before accessing
                if current is None:
                    return None

                # Handle array indexing
                if '[' in part and ']' in part:
                    open_idx = part.index('[')
                    close_idx = part.index(']')
                    key = part[:open_idx]
                    index = int(part[open_idx + 1:close_idx])

                    if key:
                        # First access dict key, then array index
                        if not isinstance(current, dict):
                            # Data structure mismatch - return None for optional fields
                            return None
                        current = current.get(key)

                        if current is None:
                            return None

                        if not isinstance(current, list):
                            # Expected list but got something else - return None
                            return None

                        # Check if index is in range
                        if index < 0 or index >= len(current):
                            return None

                        current = current[index]
                    else:
                        # Direct array index (no key)
                        if not isinstance(current, list):
                            # Expected list but got something else - return None
                            return None

                        # Check if index is in range
                        if index < 0 or index >= len(current):
                            return None

                        current = current[index]
                else:
                    # Regular key access
                    if not isinstance(current, dict):
                        # Data structure mismatch - return None for optional fields
                        return None

                    current = current.get(part)

            return current
        except (KeyError, IndexError, TypeError):
            # Any unexpected access errors - return None for graceful degradation
            return None

    def render_block(self, block: BlockMapping, data: Dict[str, Any]) -> str:
        """
        Render a single block using its template and data.

        Args:
            block: Block mapping configuration
            data: Source JSON data

        Returns:
            Rendered HTML string
        """
        # Extract data for this block
        block_data = self.extract_data(data, block.json_path)

        if block_data is None:
            return ""

        # Get text style
        style = self.config.get_text_style(block.style)
        if not style:
            raise ValueError(f"Text style '{block.style}' not found")

        # Prepare template context
        context = {
            'data': block_data,
            'style': style,
            'style_css': self._dict_to_inline_css(style.to_css())
        }

        # Render template
        template = self.jinja_env.from_string(block.template)
        rendered = template.render(**context)

        # Wrap in container if specified
        if block.container_class:
            rendered = f'<div class="{block.container_class}">{rendered}</div>'

        return rendered

    def render_chart(self, chart: ChartMapping, data: Dict[str, Any]) -> str:
        """
        Render a chart block.

        Args:
            chart: Chart mapping configuration
            data: Source JSON data

        Returns:
            Rendered HTML string with embedded chart image
        """
        # Extract data for this chart
        chart_data_source = self.extract_data(data, chart.json_path)

        if chart_data_source is None:
            return ""

        # Build chart configuration
        chart_config = {
            'labels_field': chart.labels_field,
            'values_field': chart.values_field,
            'x_field': chart.x_field,
            'y_field': chart.y_field,
            'series': chart.series,
        }

        # Extract and format chart data
        formatted_data = extract_chart_data(chart_data_source, chart_config)

        # Create chart builder
        chart_builder = ChartBuilder(color_scheme=chart.color_scheme)

        # Generate chart as base64 image
        chart_kwargs = {
            'xlabel': chart.xlabel,
            'ylabel': chart.ylabel,
            'show_values': chart.show_values,
        }

        image_data = chart_builder.create_chart(
            chart_type=chart.chart_type,
            data=formatted_data,
            title=chart.title,
            width=chart.width,
            height=chart.height,
            **chart_kwargs
        )

        # Render chart as img tag
        rendered = f'<img src="{image_data}" style="max-width: 100%; height: auto;" />'

        # Wrap in container if specified
        if chart.container_class:
            rendered = f'<div class="{chart.container_class}">{rendered}</div>'

        return rendered

    def render_page(self, page: PageConfig, data: Dict[str, Any]) -> str:
        """
        Render a complete page with all its blocks.

        Args:
            page: Page configuration
            data: Source JSON data

        Returns:
            Rendered HTML string for the page
        """
        # Build page styles
        page_styles = {
            'padding': page.padding.to_css(),
            'min-height': '297mm',  # A4 height in portrait
            'height': '297mm',
            'box-sizing': 'border-box',
            'position': 'relative',
        }
        page_styles.update(page.background.to_css())

        page_style_str = self._dict_to_inline_css(page_styles)

        # Render all blocks
        blocks_html = []
        for block in page.blocks:
            block_html = self.render_block(block, data)
            if block_html:
                blocks_html.append(block_html)

        # Render all charts
        for chart in page.charts:
            chart_html = self.render_chart(chart, data)
            if chart_html:
                blocks_html.append(chart_html)

        # Render custom HTML if provided
        custom_html = ""
        if page.custom_html:
            template = self.jinja_env.from_string(page.custom_html)
            custom_html = template.render(data=data)

        # Build page HTML
        custom_css = page.custom_css or ""
        page_html = f"""
        <div class="page page-{page.name}" style="{page_style_str}">
            <style>
                {custom_css}
            </style>
            {''.join(blocks_html)}
            {custom_html}
        </div>
        """

        return page_html

    def build_document(self, data: Dict[str, Any]) -> str:
        """
        Build complete HTML document from all pages.

        Args:
            data: Source JSON data

        Returns:
            Complete HTML document string
        """
        # Build pages
        pages_html = []
        for page in self.config.pages:
            page_html = self.render_page(page, data)
            pages_html.append(page_html)

        # Build font-face declarations
        font_faces = self._build_font_faces()

        # Build text style classes
        style_classes = self._build_style_classes()

        # Page size and orientation
        page_size = self.config.page_size
        orientation = self.config.orientation

        # Global CSS
        global_css = self.config.global_css or ""

        # Build complete HTML
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{self.config.name}</title>
            <style>
                {font_faces}

                @page {{
                    size: {page_size} {orientation};
                    margin: 0;
                }}

                * {{
                    margin: 0;
                    padding: 0;
                }}

                body {{
                    margin: 0;
                    padding: 0;
                }}

                .page {{
                    page-break-after: always;
                }}

                .page:last-child {{
                    page-break-after: auto;
                }}

                {style_classes}

                {global_css}
            </style>
        </head>
        <body>
            {''.join(pages_html)}
        </body>
        </html>
        """

        return html

    def _build_font_faces(self) -> str:
        """Build @font-face CSS declarations."""
        font_faces = []
        for font_name, font_path in self.config.fonts.items():
            font_faces.append(f"""
                @font-face {{
                    font-family: '{font_name}';
                    src: url('{font_path}');
                }}
            """)
        return '\n'.join(font_faces)

    def _build_style_classes(self) -> str:
        """Build CSS classes for text styles."""
        classes = []
        for style_name, style in self.config.text_styles.items():
            css_props = style.to_css()
            # Format CSS properties with proper indentation
            css_lines = [f"{key}: {value}" for key, value in css_props.items()]
            css_formatted = ';\n                    '.join(css_lines)
            classes.append(f"""
                .style-{style_name} {{
                    {css_formatted}
                }}
            """)
        return '\n'.join(classes)

    def _dict_to_inline_css(self, css_dict: Dict[str, str]) -> str:
        """Convert CSS dictionary to inline style string."""
        return '; '.join(f"{key}: {value}" for key, value in css_dict.items())
