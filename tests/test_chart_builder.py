import unittest

from src.chart_builder import extract_chart_data
from src.config_schema import ReportConfig, ChartMapping
from src.page_builder import PageBuilder


class ExtractChartDataTests(unittest.TestCase):
    def test_uses_dictionary_keys_and_values_when_fields_missing(self):
        source = {
            "jan": 1200,
            "feb": 1300,
        }

        result = extract_chart_data(source, {})

        self.assertEqual(result["labels"], ["jan", "feb"])
        self.assertEqual(result["values"], [1200, 1300])

    def test_requires_present_fields_for_list_data(self):
        source = [
            {"value": 10},
            {"value": 20},
        ]

        with self.assertRaisesRegex(ValueError, "label"):
            extract_chart_data(source, {"labels_field": "label", "values_field": "value"})


class RenderChartValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = ReportConfig(name="test")
        self.builder = PageBuilder(self.config)

    def test_render_chart_fails_when_labels_missing(self):
        chart = ChartMapping(
            json_path="items",
            chart_type="bar",
            values_field="value",
        )
        data = {
            "items": [
                {"value": 10},
                {"value": 20},
            ]
        }

        with self.assertRaisesRegex(ValueError, "items"):
            self.builder.render_chart(chart, data)

    def test_render_chart_succeeds_with_valid_fields(self):
        chart = ChartMapping(
            json_path="items",
            chart_type="bar",
            labels_field="month",
            values_field="revenue",
        )
        data = {
            "items": [
                {"month": "Jan", "revenue": 100},
                {"month": "Feb", "revenue": 200},
            ]
        }

        image_data = self.builder.render_chart(chart, data)

        self.assertIn("data:image/png;base64,", image_data)


if __name__ == "__main__":
    unittest.main()
