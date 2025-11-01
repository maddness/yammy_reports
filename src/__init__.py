"""
Yammy Reports - PDF Generator from Structured JSON Data

A flexible PDF generation system that maps JSON data to styled PDF pages
using configuration-based templates.
"""

from src.pdf_generator import PDFGenerator, load_config_from_dict, load_config_from_file
from src.config_schema import (
    ReportConfig,
    PageConfig,
    BlockMapping,
    TextStyle,
    FontConfig,
    BackgroundConfig,
    PaddingConfig,
    create_default_config
)
from src.page_builder import PageBuilder

__version__ = "1.0.0"

__all__ = [
    'PDFGenerator',
    'load_config_from_dict',
    'load_config_from_file',
    'ReportConfig',
    'PageConfig',
    'BlockMapping',
    'TextStyle',
    'FontConfig',
    'BackgroundConfig',
    'PaddingConfig',
    'PageBuilder',
    'create_default_config',
]
