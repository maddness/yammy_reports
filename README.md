# Yammy Reports - PDF Generator from JSON

A flexible, configuration-based PDF generation system that transforms structured JSON data into beautifully styled PDF documents using Python and WeasyPrint.

## Features

- **Configuration-Based**: Define report layouts through JSON configuration files
- **Flexible Styling**: Customize fonts, colors, paddings, backgrounds per page
- **Gradient Backgrounds**: Create beautiful linear or radial gradients for page backgrounds
- **Chart Generation**: Built-in support for bar, line, pie, area, and scatter charts using matplotlib
- **Template Engine**: Use Jinja2 templates to map JSON data to page elements
- **Multi-Page Support**: Generate reports with multiple pages, each with unique styling
- **Reusable Styles**: Define text styles once and reuse across multiple blocks
- **JSON Path Mapping**: Extract data from nested JSON structures using dot notation

## Installation

1. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

Generate a sample invoice PDF:
```bash
python generate_report.py configs/invoice_report.json examples/invoice_data.json output/invoice.pdf
```

Generate a sales report with HTML preview:
```bash
python generate_report.py configs/sales_report.json examples/sales_data.json output/sales.pdf --save-html
```

Generate a Russian taxi park analytics report (5 pages with gradient backgrounds):
```bash
python generate_report.py configs/taxi_park_ru_report.json examples/taxi_park_ru_data.json output/taxi_park_ru.pdf
```

Generate a comprehensive analytics dashboard:
```bash
python generate_report.py configs/analytics_report.json examples/analytics_data.json output/analytics.pdf
```

## Project Structure

```
yammy_reports/
├── src/
│   ├── __init__.py              # Package initialization
│   ├── config_schema.py         # Configuration data structures
│   ├── page_builder.py          # HTML page builder with templates
│   ├── chart_builder.py         # Chart generation with matplotlib
│   └── pdf_generator.py         # Main PDF generator class
├── configs/
│   ├── invoice_report.json      # Invoice report configuration
│   ├── sales_report.json        # Sales report configuration
│   ├── analytics_report.json    # Analytics dashboard configuration
│   └── taxi_park_ru_report.json # Russian taxi park analytics (5 pages)
├── examples/
│   ├── invoice_data.json        # Sample invoice data
│   ├── sales_data.json          # Sample sales data
│   ├── analytics_data.json      # Analytics dashboard data
│   └── taxi_park_ru_data.json   # Russian taxi park data
├── output/                       # Generated PDF files (created automatically)
├── generate_report.py           # CLI tool for generating reports
└── requirements.txt             # Python dependencies
```

## Building Blocks

### 1. Configuration File

Each report type has a JSON configuration that defines:

- **Report Settings**: Name, page size (A4, Letter), orientation
- **Text Styles**: Reusable text formatting (fonts, colors, spacing)
- **Pages**: One or more page configurations
- **Page Layout**: Background, padding, blocks
- **Block Mapping**: How JSON data maps to page elements

Example configuration structure:
```json
{
  "name": "My Report",
  "page_size": "A4",
  "orientation": "portrait",
  "text_styles": {
    "heading1": {
      "font": {"size": 24, "weight": "bold", "color": "#2c3e50"},
      "margin_bottom": 20
    }
  },
  "pages": [
    {
      "name": "page1",
      "background": {"color": "#ffffff"},
      "padding": {"top": 40, "right": 40, "bottom": 40, "left": 40},
      "blocks": [
        {
          "json_path": "title",
          "style": "heading1",
          "template": "<h1 style='{{ style_css }}'>{{ data }}</h1>"
        }
      ]
    }
  ]
}
```

### 2. Input Data (JSON)

Structured JSON data that feeds into the report:

```json
{
  "title": "My Document Title",
  "company": {
    "name": "ACME Corp",
    "address": "123 Main St"
  },
  "items": [
    {"name": "Item 1", "price": 100},
    {"name": "Item 2", "price": 200}
  ]
}
```

### 3. Output (PDF)

The system generates:
- **PDF file**: Final styled document
- **HTML file** (optional): Intermediate HTML for debugging

## Configuration Reference

### Text Styles

Define reusable text formatting:

```json
{
  "style_name": {
    "font": {
      "family": "Arial",
      "size": 12,
      "weight": "normal",  // normal, bold
      "color": "#000000"
    },
    "line_height": 1.5,
    "text_align": "left",  // left, center, right, justify
    "margin_top": 0,
    "margin_bottom": 0
  }
}
```

### Page Configuration

```json
{
  "name": "page_name",
  "background": {
    // Option 1: Solid color
    "color": "#ffffff",

    // Option 2: Gradient background
    "gradient_type": "linear",  // or "radial"
    "gradient_direction": "to bottom",  // for linear: "to bottom", "to right", "45deg", etc.
    "gradient_stops": ["#2ecc71", "#f39c12", "#e74c3c"],  // array of color stops

    // Option 3: Background image
    "image": "path/to/image.png",  // optional
    "image_position": "center",
    "image_size": "cover"
  },
  "padding": {
    "top": 40,
    "right": 40,
    "bottom": 40,
    "left": 40
  },
  "blocks": [],  // Block mappings (see below)
  "charts": [],  // Chart mappings (see below)
  "custom_css": ".my-class { color: red; }"  // optional
}
```

### Gradient Backgrounds

Create beautiful gradient backgrounds for your pages:

**Linear Gradient (vertical):**
```json
{
  "background": {
    "gradient_type": "linear",
    "gradient_direction": "to bottom",
    "gradient_stops": ["#2ecc71", "#f39c12", "#e74c3c"]
  }
}
```

**Linear Gradient (horizontal):**
```json
{
  "background": {
    "gradient_type": "linear",
    "gradient_direction": "to right",
    "gradient_stops": ["#3498db", "#9b59b6"]
  }
}
```

**Linear Gradient (diagonal):**
```json
{
  "background": {
    "gradient_type": "linear",
    "gradient_direction": "45deg",
    "gradient_stops": ["#1abc9c", "#3498db", "#9b59b6"]
  }
}
```

**Radial Gradient:**
```json
{
  "background": {
    "gradient_type": "radial",
    "gradient_stops": ["#ffffff", "#3498db"]
  }
}
```

### Block Mapping

Map JSON data to page elements:

```json
{
  "json_path": "customer.name",  // Dot notation path to data
  "style": "body_text",          // Reference to text style
  "template": "<p style='{{ style_css }}'>{{ data }}</p>",  // Jinja2 template
  "container_class": "customer-info"  // Optional CSS class
}
```

### Chart Mapping

Generate charts from JSON data:

```json
{
  "json_path": "monthly_revenue",      // Path to chart data
  "chart_type": "bar",                 // bar, line, pie, area, horizontal_bar, scatter
  "title": "Monthly Revenue ($)",      // Chart title
  "width": 10,                         // Figure width in inches
  "height": 5,                         // Figure height in inches
  "color_scheme": "professional",      // professional, ocean, vibrant, earth
  "labels_field": "month",             // Field name for X-axis labels
  "values_field": "revenue",           // Field name for Y-axis values
  "xlabel": "Month",                   // X-axis label
  "ylabel": "Revenue ($)",             // Y-axis label
  "show_values": true,                 // Show value labels on chart
  "container_class": "chart-container" // Optional CSS class
}
```

**Supported Chart Types:**
- `bar` - Vertical bar chart
- `horizontal_bar` - Horizontal bar chart
- `line` - Line chart for trends
- `area` - Area chart (filled line chart)
- `pie` - Pie chart for proportions
- `scatter` - Scatter plot for correlations

**Color Schemes:**
- `professional` - Blue-based professional colors
- `ocean` - Ocean blue tones
- `vibrant` - Bright, vibrant colors
- `earth` - Earthy, natural tones

### JSON Path Examples

- `"title"` - Top-level field
- `"customer.name"` - Nested field
- `"items[0].price"` - Array element
- `"items"` - Entire array (use with Jinja2 loops)

### Jinja2 Templates

Available variables in templates:
- `data` - Extracted JSON data for this block
- `style` - TextStyle object
- `style_css` - Pre-formatted inline CSS string

Template examples:

```html
<!-- Simple text -->
<p style="{{ style_css }}">{{ data }}</p>

<!-- Formatted number -->
<div style="{{ style_css }}">${{ '%.2f'|format(data) }}</div>

<!-- Loop through array -->
{% for item in data %}
  <div>{{ item.name }}: ${{ item.price }}</div>
{% endfor %}

<!-- Conditional -->
{% if data > 1000 %}
  <strong>High Value!</strong>
{% endif %}
```

## Programmatic Usage

You can also use the library programmatically:

```python
from src.pdf_generator import PDFGenerator, load_config_from_file

# Load configuration
config = load_config_from_file('configs/my_report.json')

# Create generator
generator = PDFGenerator(config)

# Generate PDF from file
generator.generate(
    data='examples/my_data.json',
    output_path='output/report.pdf',
    save_html=True
)

# Generate from dictionary
data = {
    "title": "My Report",
    "content": "Report content here"
}
generator.generate(data=data, output_path='output/report2.pdf')

# Get HTML preview without generating PDF
html = generator.preview_html(data)
print(html)
```

## Creating Custom Reports

1. **Define your data structure** - Decide what JSON format your data will use

2. **Create a configuration file** in `configs/`:
   - Define text styles for headings, body text, etc.
   - Configure pages with backgrounds and padding
   - Map JSON fields to blocks using json_path
   - Write Jinja2 templates for rendering

3. **Prepare your data** as JSON file in `examples/`

4. **Generate the PDF**:
   ```bash
   python generate_report.py configs/my_config.json examples/my_data.json output/my_report.pdf
   ```

## Tips

- Start with one of the example configs and modify it
- Use `--save-html` flag to debug layout issues
- Test templates with simple data first
- Use custom_css for page-specific styling
- Use global_css for document-wide styles
- Keep text styles reusable across multiple reports

## Requirements

- Python 3.7+
- WeasyPrint 60.1
- Jinja2 3.1.2
- Pillow 10.1.0

## License

MIT License
