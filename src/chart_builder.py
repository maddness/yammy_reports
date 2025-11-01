"""
Chart builder for generating beautiful charts for PDF reports.

This module handles the creation of various chart types using matplotlib
and converts them to base64-encoded images for embedding in PDFs.
"""

import io
import base64
from typing import Dict, Any, List, Optional, Tuple
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server-side rendering
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np


class ChartBuilder:
    """Builds charts from data using matplotlib."""

    # Color schemes
    COLOR_SCHEMES = {
        'professional': ['#3498db', '#2ecc71', '#f39c12', '#e74c3c', '#9b59b6', '#1abc9c'],
        'pastel': ['#a8dadc', '#457b9d', '#f1faee', '#e63946', '#f4a261'],
        'vibrant': ['#ff6b6b', '#4ecdc4', '#45b7d1', '#f9ca24', '#6c5ce7'],
        'corporate': ['#2c3e50', '#34495e', '#7f8c8d', '#95a5a6', '#bdc3c7'],
        'earth': ['#8b4513', '#daa520', '#6b8e23', '#2f4f4f', '#bc8f8f'],
        'ocean': ['#006994', '#0582ca', '#00a6fb', '#7dd3fc', '#bae6fd']
    }

    def __init__(self, color_scheme: str = 'professional'):
        """
        Initialize chart builder.

        Args:
            color_scheme: Name of color scheme to use
        """
        self.color_scheme = color_scheme
        self.colors = self.COLOR_SCHEMES.get(color_scheme, self.COLOR_SCHEMES['professional'])

    def create_chart(
        self,
        chart_type: str,
        data: Dict[str, Any],
        title: Optional[str] = None,
        width: int = 8,
        height: int = 5,
        **kwargs
    ) -> str:
        """
        Create a chart and return it as base64-encoded PNG.

        Args:
            chart_type: Type of chart (bar, line, pie, area, scatter, horizontal_bar)
            data: Chart data
            title: Chart title
            width: Figure width in inches
            height: Figure height in inches
            **kwargs: Additional chart-specific options

        Returns:
            Base64-encoded PNG image string
        """
        fig, ax = plt.subplots(figsize=(width, height))

        # Set style
        plt.style.use('seaborn-v0_8-darkgrid')

        # Create the appropriate chart
        if chart_type == 'bar':
            self._create_bar_chart(ax, data, **kwargs)
        elif chart_type == 'horizontal_bar':
            self._create_horizontal_bar_chart(ax, data, **kwargs)
        elif chart_type == 'line':
            self._create_line_chart(ax, data, **kwargs)
        elif chart_type == 'pie':
            self._create_pie_chart(ax, data, **kwargs)
        elif chart_type == 'area':
            self._create_area_chart(ax, data, **kwargs)
        elif chart_type == 'scatter':
            self._create_scatter_chart(ax, data, **kwargs)
        else:
            raise ValueError(f"Unsupported chart type: {chart_type}")

        # Set title
        if title:
            ax.set_title(title, fontsize=14, fontweight='bold', pad=20)

        # Adjust layout
        plt.tight_layout()

        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close(fig)

        return f"data:image/png;base64,{image_base64}"

    def _create_bar_chart(self, ax, data: Dict[str, Any], **kwargs):
        """Create a vertical bar chart."""
        labels = data.get('labels', [])
        values = data.get('values', [])

        x = np.arange(len(labels))
        width = kwargs.get('bar_width', 0.6)

        bars = ax.bar(x, values, width, color=self.colors[0], alpha=0.8)

        # Add value labels on top of bars
        if kwargs.get('show_values', True):
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:,.0f}',
                       ha='center', va='bottom', fontsize=9)

        ax.set_xlabel(kwargs.get('xlabel', ''), fontsize=11)
        ax.set_ylabel(kwargs.get('ylabel', ''), fontsize=11)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45, ha='right')
        ax.grid(axis='y', alpha=0.3)

    def _create_horizontal_bar_chart(self, ax, data: Dict[str, Any], **kwargs):
        """Create a horizontal bar chart."""
        labels = data.get('labels', [])
        values = data.get('values', [])

        y = np.arange(len(labels))
        height = kwargs.get('bar_height', 0.6)

        bars = ax.barh(y, values, height, color=self.colors[0], alpha=0.8)

        # Add value labels at end of bars
        if kwargs.get('show_values', True):
            for i, bar in enumerate(bars):
                width = bar.get_width()
                ax.text(width, bar.get_y() + bar.get_height()/2.,
                       f' {width:,.0f}',
                       ha='left', va='center', fontsize=9)

        ax.set_ylabel(kwargs.get('ylabel', ''), fontsize=11)
        ax.set_xlabel(kwargs.get('xlabel', ''), fontsize=11)
        ax.set_yticks(y)
        ax.set_yticklabels(labels)
        ax.grid(axis='x', alpha=0.3)

    def _create_line_chart(self, ax, data: Dict[str, Any], **kwargs):
        """Create a line chart."""
        labels = data.get('labels', [])

        # Support multiple series
        series = data.get('series', [])
        if not series and 'values' in data:
            # Single series
            series = [{'name': 'Value', 'values': data['values']}]

        x = np.arange(len(labels))

        for i, s in enumerate(series):
            color = self.colors[i % len(self.colors)]
            ax.plot(x, s['values'], marker='o', linewidth=2,
                   label=s.get('name', f'Series {i+1}'),
                   color=color, markersize=6)

        ax.set_xlabel(kwargs.get('xlabel', ''), fontsize=11)
        ax.set_ylabel(kwargs.get('ylabel', ''), fontsize=11)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45, ha='right')
        ax.grid(True, alpha=0.3)

        if len(series) > 1:
            ax.legend(loc='best', framealpha=0.9)

    def _create_pie_chart(self, ax, data: Dict[str, Any], **kwargs):
        """Create a pie chart."""
        labels = data.get('labels', [])
        values = data.get('values', [])

        # Create pie chart
        wedges, texts, autotexts = ax.pie(
            values,
            labels=labels,
            colors=self.colors[:len(values)],
            autopct='%1.1f%%',
            startangle=90,
            pctdistance=0.85
        )

        # Beautify text
        for text in texts:
            text.set_fontsize(10)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(9)

        ax.axis('equal')

    def _create_area_chart(self, ax, data: Dict[str, Any], **kwargs):
        """Create an area chart."""
        labels = data.get('labels', [])

        # Support multiple series
        series = data.get('series', [])
        if not series and 'values' in data:
            series = [{'name': 'Value', 'values': data['values']}]

        x = np.arange(len(labels))

        # Stack areas if multiple series
        if kwargs.get('stacked', True) and len(series) > 1:
            values_array = [s['values'] for s in series]
            ax.stackplot(x, *values_array,
                        labels=[s.get('name', f'Series {i+1}') for i, s in enumerate(series)],
                        colors=self.colors[:len(series)],
                        alpha=0.7)
        else:
            for i, s in enumerate(series):
                color = self.colors[i % len(self.colors)]
                ax.fill_between(x, s['values'], alpha=0.6, color=color,
                               label=s.get('name', f'Series {i+1}'))

        ax.set_xlabel(kwargs.get('xlabel', ''), fontsize=11)
        ax.set_ylabel(kwargs.get('ylabel', ''), fontsize=11)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45, ha='right')
        ax.grid(True, alpha=0.3)

        if len(series) > 1:
            ax.legend(loc='best', framealpha=0.9)

    def _create_scatter_chart(self, ax, data: Dict[str, Any], **kwargs):
        """Create a scatter plot."""
        x_values = data.get('x_values', [])
        y_values = data.get('y_values', [])

        ax.scatter(x_values, y_values,
                  s=kwargs.get('point_size', 50),
                  c=self.colors[0],
                  alpha=0.6,
                  edgecolors='white',
                  linewidth=1.5)

        ax.set_xlabel(kwargs.get('xlabel', 'X'), fontsize=11)
        ax.set_ylabel(kwargs.get('ylabel', 'Y'), fontsize=11)
        ax.grid(True, alpha=0.3)


def extract_chart_data(source_data: Any, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract and format data for chart creation.

    Args:
        source_data: Source data (list, dict, or simple values)
        config: Chart configuration with data mapping

    Returns:
        Formatted chart data
    """
    chart_data = {}

    # Extract labels
    if 'labels_field' in config:
        if isinstance(source_data, list):
            chart_data['labels'] = [item.get(config['labels_field']) for item in source_data]
        else:
            chart_data['labels'] = list(source_data.keys())
    elif 'labels' in config:
        chart_data['labels'] = config['labels']

    # Extract values
    if 'values_field' in config:
        if isinstance(source_data, list):
            chart_data['values'] = [item.get(config['values_field']) for item in source_data]
        else:
            chart_data['values'] = list(source_data.values())
    elif 'values' in config:
        chart_data['values'] = config['values']

    # Handle series for multi-line charts
    if 'series' in config and config['series'] is not None:
        chart_data['series'] = []
        for series_config in config['series']:
            series_data = {
                'name': series_config.get('name', 'Series'),
                'values': []
            }
            if 'values_field' in series_config and isinstance(source_data, list):
                series_data['values'] = [item.get(series_config['values_field']) for item in source_data]
            chart_data['series'].append(series_data)

    # Handle scatter plot
    if 'x_field' in config and 'y_field' in config:
        if isinstance(source_data, list):
            chart_data['x_values'] = [item.get(config['x_field']) for item in source_data]
            chart_data['y_values'] = [item.get(config['y_field']) for item in source_data]

    return chart_data
