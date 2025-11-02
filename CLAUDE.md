# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Обзор проекта

Yammy Reports — это гибкая система генерации PDF-отчетов из структурированных JSON данных с использованием Python и WeasyPrint. Система работает на основе конфигурационных файлов JSON, которые определяют структуру отчета, стили и маппинг данных.

## Основные команды

### Генерация отчетов
```bash
python generate_report.py <config_file> <data_file> <output_file> [--save-html]
```

Примеры:
```bash
# Простой инвойс
python generate_report.py configs/invoice_report.json examples/invoice_data.json output/invoice.pdf

# С сохранением HTML для отладки
python generate_report.py configs/sales_report.json examples/sales_data.json output/sales.pdf --save-html

# Комплексный аналитический отчет
python generate_report.py configs/taxi_park_analytics_report.json examples/taxi_park_analytics_data.json output/taxi_park_analytics.pdf
```

### Установка зависимостей
```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
pip install -r requirements.txt
```

## Архитектура системы

### Основные модули

1. **config_schema.py** - Определяет структуры данных конфигурации:
   - `ReportConfig` - корневая конфигурация отчета
   - `PageConfig` - конфигурация отдельной страницы
   - `TextStyle` / `FontConfig` - стили текста
   - `BlockMapping` - маппинг JSON данных на текстовые блоки
   - `ChartMapping` - маппинг JSON данных на графики
   - `BackgroundConfig` - фоны страниц (цвет, градиент, изображение)

2. **pdf_generator.py** - Основной генератор PDF:
   - `PDFGenerator` - главный класс, оркестрирует процесс генерации
   - `load_config_from_file()` / `load_config_from_dict()` - загрузка конфигурации
   - Валидация конфигурации при инициализации
   - Поддержка программного использования через `preview_html()`

3. **page_builder.py** - Построение HTML из JSON:
   - `PageBuilder` - рендерит страницы в HTML
   - `extract_data()` - извлечение данных по JSONPath (dot-notation с поддержкой массивов)
   - Использует Jinja2 для шаблонизации
   - Поддержка полноэкранных градиентных фонов для A4

4. **chart_builder.py** - Генерация графиков:
   - `ChartBuilder` - создание графиков через matplotlib
   - Типы графиков: bar, horizontal_bar, line, multi_line, pie, area, scatter
   - Цветовые схемы: professional, pastel, vibrant, corporate, earth, ocean
   - `extract_chart_data()` - извлечение и валидация данных для графиков
   - Конвертация в base64 PNG для встраивания в PDF

### Поток данных

```
JSON Config + JSON Data
        ↓
load_config_from_file() → ReportConfig
        ↓
PDFGenerator(config)
        ↓
PageBuilder.build_document(data)
        ↓
для каждой страницы:
  - render_block() для текстовых блоков
  - render_chart() для графиков
        ↓
HTML с встроенными base64 изображениями
        ↓
WeasyPrint.HTML → PDF
```

## Важные особенности реализации

### JSONPath синтаксис
- Поддержка dot-notation: `"customer.name"`
- Поддержка массивов: `"items[0].price"`
- **Валидация**: синтаксические ошибки (пустые индексы, нецелые индексы) вызывают ValueError
- **Graceful degradation**: отсутствующие данные или null возвращают None, блок пропускается

### Валидация конфигурации
Происходит при загрузке (`load_config_from_dict`):
- Проверка обязательных полей (name, json_path, style, template, chart_type)
- Проверка типов (font должен быть dict, width/height числовые)
- Проверка положительных значений (width/height > 0)
- Проверка существования стилей, на которые ссылаются блоки
- Ошибки валидации выбрасывают ValueError с детальным описанием

### Валидация данных
Происходит во время обработки (`extract_chart_data`, `ChartBuilder`):
- Данные графиков должны быть list или dict
- Значения графиков должны быть числовыми (автоконвертация строк при возможности)
- Обязательные поля (labels_field, values_field) должны существовать
- Никакие None не передаются в matplotlib

### Градиентные фоны
- Поддержка linear и radial градиентов
- `gradient_direction` для linear: "to bottom", "to right", "45deg", "135deg"
- `gradient_stops` - массив цветов
- Для полноэкранных градиентов на A4:
  - `global_css`: `@page { size: A4; margin: 0; }`
  - `custom_css` страницы: `.page-name { min-height: 297mm !important; height: 297mm !important; }`

### Работа с цветами
ChartBuilder содержит предопределенные цветовые схемы в `COLOR_SCHEMES`. При добавлении новых схем обновлять этот словарь.

## Структура конфигурационного файла

```json
{
  "name": "Report Name",
  "page_size": "A4",
  "orientation": "portrait",
  "text_styles": {
    "style_name": {
      "font": {"family": "Arial", "size": 12, "weight": "bold", "color": "#000"},
      "line_height": 1.5,
      "text_align": "left",
      "margin_top": 0,
      "margin_bottom": 0
    }
  },
  "pages": [
    {
      "name": "page1",
      "background": {
        "color": "#fff",
        "gradient_type": "linear",
        "gradient_direction": "135deg",
        "gradient_stops": ["#color1", "#color2"]
      },
      "padding": {"top": 40, "right": 40, "bottom": 40, "left": 40},
      "blocks": [
        {
          "json_path": "path.to.data",
          "style": "style_name",
          "template": "<p style='{{ style_css }}'>{{ data }}</p>",
          "container_class": "optional-class"
        }
      ],
      "charts": [
        {
          "json_path": "path.to.chart_data",
          "chart_type": "bar",
          "title": "Chart Title",
          "width": 10,
          "height": 5,
          "color_scheme": "professional",
          "labels_field": "label",
          "values_field": "value",
          "xlabel": "X Label",
          "ylabel": "Y Label",
          "show_values": true
        }
      ],
      "custom_css": ".custom { color: red; }",
      "custom_html": "<div>{{ data.field }}</div>"
    }
  ],
  "global_css": "@page { margin: 0; }"
}
```

## Паттерн структурированных метрик

Для аналитических отчетов рекомендуется использовать структурированный формат с метаданными:

```json
{
  "meta": {
    "title": "Report Title",
    "period": "Date Range",
    "generated_date": "YYYY-MM-DD"
  },
  "key_metrics": {
    "metric_name": {
      "label": "Metric Label",
      "value": 12345,
      "change_mom": 5,
      "change_yoy": 120,
      "currency": "₽"
    }
  },
  "monthly_data": [
    {"month": "Jan", "value": 1000}
  ],
  "analysis_sections": [
    {
      "title": "Section",
      "summary": "Brief",
      "details": "Details",
      "monthly_data": [...]
    }
  ]
}
```

## Отладка

- Используйте флаг `--save-html` для сохранения промежуточного HTML
- HTML файл позволяет проверить структуру и стили до рендеринга PDF
- Для проверки JSONPath используйте `PageBuilder.extract_data()` напрямую
- При ошибках графиков проверяйте типы данных и наличие required полей

## Ограничения и соглашения

- Все размеры в конфигурации в пикселях (px) для текста, миллиметрах (mm) для страниц
- WeasyPrint не поддерживает JavaScript и продвинутый CSS
- Графики рендерятся как статичные PNG изображения
- Шрифты должны быть доступны системе или указаны в `fonts` mapping
- Файлы конфигурации в `configs/`, данные в `examples/`, выход в `output/`
