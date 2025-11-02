"""
Configuration schema for PDF report generation.

This module defines the structure and validation for report configurations.
Each report type should have a config that maps JSON blocks to pages with styling.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class FontConfig:
    """Font configuration."""
    family: str = "Arial"
    size: int = 12
    weight: str = "normal"  # normal, bold
    color: str = "#000000"


@dataclass
class PaddingConfig:
    """Padding configuration for pages and blocks."""
    top: int = 20
    right: int = 20
    bottom: int = 20
    left: int = 20

    def to_css(self) -> str:
        """Convert padding to CSS string."""
        return f"{self.top}px {self.right}px {self.bottom}px {self.left}px"


@dataclass
class TextStyle:
    """Text style configuration."""
    name: str
    font: FontConfig = field(default_factory=FontConfig)
    line_height: float = 1.5
    text_align: str = "left"  # left, center, right, justify
    margin_top: int = 0
    margin_bottom: int = 0

    def to_css(self) -> Dict[str, str]:
        """Convert text style to CSS properties."""
        return {
            "font-family": self.font.family,
            "font-size": f"{self.font.size}px",
            "font-weight": self.font.weight,
            "color": self.font.color,
            "line-height": str(self.line_height),
            "text-align": self.text_align,
            "margin-top": f"{self.margin_top}px",
            "margin-bottom": f"{self.margin_bottom}px",
        }


@dataclass
class BackgroundConfig:
    """Background configuration for pages."""
    color: Optional[str] = None
    image: Optional[str] = None
    image_position: str = "center"
    image_size: str = "cover"  # cover, contain, auto
    gradient_type: Optional[str] = None  # linear, radial
    gradient_direction: str = "to bottom"  # for linear: to bottom, to right, 45deg, etc.
    gradient_stops: Optional[List[str]] = None  # list of color stops

    def to_css(self) -> Dict[str, str]:
        """Convert background to CSS properties."""
        css = {}

        # Handle gradient backgrounds
        if self.gradient_type and self.gradient_stops:
            if self.gradient_type == "linear":
                stops = ", ".join(self.gradient_stops)
                css["background"] = f"linear-gradient({self.gradient_direction}, {stops})"
            elif self.gradient_type == "radial":
                stops = ", ".join(self.gradient_stops)
                css["background"] = f"radial-gradient(circle, {stops})"
        # Handle solid color backgrounds (only if no gradient)
        elif self.color:
            css["background-color"] = self.color

        # Handle image backgrounds
        if self.image:
            css["background-image"] = f"url({self.image})"
            css["background-position"] = self.image_position
            css["background-size"] = self.image_size
            css["background-repeat"] = "no-repeat"

        return css


@dataclass
class BlockMapping:
    """Mapping of JSON data block to page element."""
    json_path: str  # JSONPath expression to extract data
    style: str  # Reference to text style name
    template: str  # Jinja2 template for rendering the block
    container_class: Optional[str] = None  # Optional CSS class for container


@dataclass
class ChartMapping:
    """Mapping of JSON data to chart visualization."""
    json_path: str  # JSONPath expression to extract data
    chart_type: str  # Type of chart: bar, line, pie, area, scatter, horizontal_bar
    title: Optional[str] = None  # Chart title
    width: int = 8  # Figure width in inches
    height: int = 5  # Figure height in inches
    color_scheme: str = "professional"  # Color scheme name
    labels_field: Optional[str] = None  # Field name for labels (for list data)
    values_field: Optional[str] = None  # Field name for values (for list data)
    x_field: Optional[str] = None  # Field name for X values (scatter plots)
    y_field: Optional[str] = None  # Field name for Y values (scatter plots)
    series: Optional[List[Dict[str, str]]] = None  # Series config for multi-line charts
    xlabel: str = ""  # X-axis label
    ylabel: str = ""  # Y-axis label
    show_values: bool = True  # Show value labels on bars
    container_class: Optional[str] = None  # Optional CSS class for container


@dataclass
class PageConfig:
    """Configuration for a single page."""
    name: str
    background: BackgroundConfig = field(default_factory=BackgroundConfig)
    padding: PaddingConfig = field(default_factory=PaddingConfig)
    blocks: List[BlockMapping] = field(default_factory=list)
    charts: List[ChartMapping] = field(default_factory=list)
    custom_css: Optional[str] = None  # Additional custom CSS for this page


@dataclass
class ReportConfig:
    """Complete configuration for a report type."""
    name: str
    page_size: str = "A4"  # A4, Letter, etc.
    orientation: str = "portrait"  # portrait, landscape
    fonts: Dict[str, str] = field(default_factory=dict)  # Font name to file path mapping
    text_styles: Dict[str, TextStyle] = field(default_factory=dict)
    pages: List[PageConfig] = field(default_factory=list)
    global_css: Optional[str] = None  # Global CSS for entire document

    def get_text_style(self, name: str) -> Optional[TextStyle]:
        """Get text style by name."""
        return self.text_styles.get(name)

    def validate(self) -> List[str]:
        """Validate configuration and return list of errors."""
        errors = []

        if not self.name:
            errors.append("Report name is required")

        if not self.pages:
            errors.append("At least one page configuration is required")

        # Validate block style references
        for page in self.pages:
            for block in page.blocks:
                if block.style not in self.text_styles:
                    errors.append(
                        f"Page '{page.name}' references undefined style '{block.style}'"
                    )

        return errors


def create_default_config(name: str) -> ReportConfig:
    """Create a default report configuration."""
    return ReportConfig(
        name=name,
        text_styles={
            "heading1": TextStyle(
                name="heading1",
                font=FontConfig(size=24, weight="bold"),
                margin_bottom=20
            ),
            "heading2": TextStyle(
                name="heading2",
                font=FontConfig(size=18, weight="bold"),
                margin_bottom=15
            ),
            "body": TextStyle(
                name="body",
                font=FontConfig(size=12),
                margin_bottom=10
            ),
            "caption": TextStyle(
                name="caption",
                font=FontConfig(size=10, color="#666666"),
                margin_bottom=5
            ),
        }
    )
