# Структурированный вывод для LLM: Pydantic модели для Taxi Park Analytics

Этот документ содержит Pydantic модели и примеры промптов для генерации данных отчетов таксопарка через LLM с использованием Structured Output.

## Pydantic модели

### Модели для аналитики таксопарка

```python
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union


class ReportMeta(BaseModel):
    """Модель для метаданных отчета таксопарка"""
    title: str = Field(..., description="Название отчета")
    period: str = Field(..., description="Период отчета (например, 'Сентябрь 2024 – Август 2025')")
    generated_date: str = Field(..., description="Дата генерации отчета (например, '15 ноября 2025')")
    efficiency_rating: Optional[int] = Field(None, description="Рейтинг эффективности (число от 0 до rating_max)")
    rating_max: Optional[int] = Field(None, description="Максимальный рейтинг (обычно 100)")


class CompactMetric(BaseModel):
    """Модель для компактных метрик"""
    label: str = Field(..., description="Название метрики (например, 'Активные исполнители')")
    value: str = Field(..., description="Значение метрики в виде строки (может содержать единицы измерения, например, '164', '16%', '1341₽')")
    change_text: Optional[str] = Field(None, description="Текст изменения (например, '+1% к августу, +46% год к году')")


class RevenueComparison(BaseModel):
    """Модель для сравнения доходов по месяцам"""
    month: str = Field(..., description="Название месяца в сокращенном формате (например, 'Сент', 'Окт', 'Май')")
    current_year: float = Field(..., description="Значение текущего года")
    previous_year: Optional[float] = Field(None, description="Значение предыдущего года (опционально)")


class MonthlyRevenue(BaseModel):
    """Модель для месячных доходов"""
    month: str = Field(..., description="Название месяца с годом (например, 'Окт 2024', 'Май 2025')")
    revenue: int = Field(..., description="Доход за месяц в рублях (целое число)")


class KeyMetric(BaseModel):
    """Модель для ключевой метрики с изменениями"""
    label: str = Field(..., description="Название метрики")
    value: Union[int, float] = Field(..., description="Значение метрики")
    change_mom: Optional[float] = Field(None, description="Изменение к предыдущему месяцу в процентах (может быть отрицательным)")
    change_yoy: Optional[float] = Field(None, description="Изменение к прошлому году в процентах (может быть отрицательным)")
    currency: Optional[str] = Field(None, description="Валюта (например, '₽') - используется для денежных метрик")
    unit: Optional[str] = Field(None, description="Единица измерения (например, '%', 'чел.') - используется для немонетарных метрик")


class AnalysisSection(BaseModel):
    """Модель для секции анализа (отток, приток и т.д.)"""
    title: str = Field(..., description="Заголовок секции анализа")
    summary: str = Field(..., description="Краткое резюме проблемы или явления")
    details: Optional[str] = Field(None, description="Детальное описание с анализом")
    comparison_data: Optional[List[Dict[str, Any]]] = Field(None, description="Данные для сравнения (массив объектов с полями month, current_year, previous_year)")


class PositivePoint(BaseModel):
    """Модель для позитивного пункта"""
    title: str = Field(..., description="Заголовок позитивного момента")
    content: str = Field(..., description="Развернутое описание позитивного момента")


class RecommendationItem(BaseModel):
    """Модель для рекомендации"""
    title: str = Field(..., description="Название рекомендации")
    content: str = Field(..., description="Развернутое описание рекомендации с деталями реализации")


class TaxiParkAnalyticsData(BaseModel):
    """Основная модель для аналитического отчета таксопарка"""
    meta: ReportMeta = Field(..., description="Метаданные отчета")
    total_revenue_formatted: Optional[str] = Field(None, description="Отформатированный общий доход (строка с валютой, например '157222₽')")
    compact_metrics: Optional[List[CompactMetric]] = Field(None, description="Компактные метрики для быстрого обзора")
    revenue_comparison: Optional[List[RevenueComparison]] = Field(None, description="Сравнение доходов текущего и предыдущего года по месяцам")
    monthly_revenue: Optional[List[MonthlyRevenue]] = Field(None, description="Месячные доходы за период")
    key_metrics: Optional[Dict[str, KeyMetric]] = Field(None, description="Ключевые метрики как словарь (ключи: revenue, active_drivers, churn_rate, revenue_per_driver, profitability)")
    churn_analysis: Optional[AnalysisSection] = Field(None, description="Анализ оттока водителей")
    inflow_analysis: Optional[AnalysisSection] = Field(None, description="Анализ притока новых водителей")
    positive_points: Optional[List[PositivePoint]] = Field(None, description="Позитивные моменты в работе парка")
    recommendations: Optional[List[RecommendationItem]] = Field(None, description="Рекомендации по улучшению")
    warnings: Optional[List[str]] = Field(None, description="Предупреждения и отказы от ответственности")
```

## Пример промпта для LLM

### Промпт для аналитики таксопарка

```markdown
Ты - аналитик таксопарка. Создай детальный структурированный JSON отчет на основе предоставленных данных.

Структура должна строго соответствовать следующей схеме:

- meta: метаданные отчета
  - title: название отчета (строка)
  - period: период отчета (строка, например "Сентябрь 2024 – Август 2025")
  - generated_date: дата генерации (строка, например "15 ноября 2025")
  - efficiency_rating: рейтинг эффективности (целое число от 0 до rating_max, опционально)
  - rating_max: максимальный рейтинг (целое число, обычно 100, опционально)

- total_revenue_formatted: отформатированный общий доход (строка с валютой, например "157222₽", опционально)

- compact_metrics: массив компактных метрик
  - label: название метрики (строка)
  - value: значение метрики (строка, может содержать единицы, например "164", "16%", "1341₽")
  - change_text: текст изменения (строка, опционально)

- revenue_comparison: сравнение доходов по месяцам
  - month: название месяца в сокращенном формате (строка, например "Сент", "Окт", "Май")
  - current_year: значение текущего года (число)
  - previous_year: значение предыдущего года (число, опционально)

- monthly_revenue: месячные доходы
  - month: название месяца с годом (строка, например "Окт 2024", "Май 2025")
  - revenue: доход за месяц в рублях (целое число)

- key_metrics: ключевые метрики как словарь (ключи: revenue, active_drivers, churn_rate, revenue_per_driver, profitability)
  Каждая метрика содержит:
  - label: название метрики (строка)
  - value: значение метрики (число)
  - change_mom: изменение к предыдущему месяцу в процентах (число, может быть отрицательным, опционально)
  - change_yoy: изменение к прошлому году в процентах (число, может быть отрицательным, опционально)
  - currency: валюта (строка, например "₽", опционально) - используется для денежных метрик
  - unit: единица измерения (строка, например "%", "чел.", опционально) - используется для немонетарных метрик

- churn_analysis: анализ оттока водителей
  - title: заголовок (строка)
  - summary: краткое резюме (строка)
  - details: детальное описание (строка, опционально)
  - comparison_data: данные для сравнения (массив объектов с полями month, current_year, previous_year, опционально)

- inflow_analysis: анализ притока новых водителей
  - title: заголовок (строка)
  - summary: краткое резюме (строка)
  - details: детальное описание (строка, опционально)
  - comparison_data: данные для сравнения (массив объектов с полями month, current_year, previous_year, опционально)

- positive_points: позитивные моменты (массив объектов)
  - title: заголовок (строка)
  - content: развернутое описание (строка)

- recommendations: рекомендации (массив объектов)
  - title: название рекомендации (строка)
  - content: развернутое описание рекомендации (строка)

- warnings: предупреждения (массив строк, опционально)

ВАЖНО:
1. Все числовые значения должны быть числами (int или float), а не строками
2. Только поля value в compact_metrics и total_revenue_formatted могут быть строками с единицами измерения
3. Месяцы в revenue_comparison должны быть в сокращенном формате на русском языке (Сент, Окт, Ноя, Дек, Янв, Февр, Мар, Апр, Май, Июн, Июл, Авг)
4. Месяцы в monthly_revenue должны быть в формате "Месяц Год" (например, "Окт 2024", "Май 2025")
5. Все обязательные поля должны быть заполнены
6. Опциональные поля можно опустить, если данные отсутствуют

Используй структурированный вывод в формате JSON, соответствующий схеме TaxiParkAnalyticsData.
```

## Использование в коде

### Установка библиотеки

```bash
pip install openai-agents litellm
```

### Пример использования с OpenAI Agents и Anthropic

```python
import asyncio
import os
from agents import Agent, Runner
from agents.extensions.models.litellm_model import LitellmModel

# Создаем агента с использованием Anthropic Claude через LiteLLM
agent = Agent(
    name="Аналитик таксопарка",
    instructions="Ты - аналитик таксопарка. Создай структурированный JSON отчет на основе предоставленных данных.",
    model=LitellmModel(
        model="anthropic/claude-3-5-sonnet-20241022",  # Модель Anthropic Claude
        api_key=os.getenv("ANTHROPIC_API_KEY")  # Используйте переменную окружения для API ключа
    ),
    output_type=TaxiParkAnalyticsData  # Указываем Pydantic модель для structured output
)

async def generate_report(raw_data: str) -> TaxiParkAnalyticsData:
    """Генерирует аналитический отчет таксопарка"""
    result = await Runner.run(agent, f"Создай аналитический отчет таксопарка на основе следующих данных: {raw_data}")
    
    # Получаем структурированный вывод как Pydantic модель
    report = result.final_output_as(TaxiParkAnalyticsData)
    return report

# Использование
async def main():
    raw_data = "..."  # Ваши исходные данные
    report = await generate_report(raw_data)
    print(f"Отчет '{report.meta.title}' успешно создан!")
    print(f"Период: {report.meta.period}")

asyncio.run(main())
```

### Альтернативный пример с явной обработкой ошибок

```python
import asyncio
import os
from agents import Agent, Runner
from agents.extensions.models.litellm_model import LitellmModel
from pydantic import ValidationError

def generate_taxi_park_report(raw_data: str) -> TaxiParkAnalyticsData:
    """
    Генерирует аналитический отчет таксопарка на основе предоставленных данных.
    
    Args:
        raw_data: Строка с исходными данными для анализа
        
    Returns:
        TaxiParkAnalyticsData: Валидированный объект отчета
        
    Raises:
        ValidationError: Если данные не соответствуют схеме
        Exception: Если произошла ошибка при обращении к API
    """
    agent = Agent(
        name="Аналитик таксопарка",
        instructions="Ты - аналитик таксопарка. Создай структурированный JSON отчет на основе предоставленных данных.",
        model=LitellmModel(
            model="anthropic/claude-3-5-sonnet-20241022",
            api_key=os.getenv("ANTHROPIC_API_KEY")
        ),
        output_type=TaxiParkAnalyticsData
    )
    
    async def _generate():
        try:
            result = await Runner.run(
                agent,
                f"Создай аналитический отчет таксопарка на основе следующих данных: {raw_data}"
            )
            
            # Получаем структурированный вывод
            report = result.final_output_as(TaxiParkAnalyticsData)
            return report
            
        except ValidationError as e:
            raise ValueError(f"Данные не соответствуют схеме: {e.errors()}")
        except Exception as e:
            raise Exception(f"Ошибка при обращении к API: {e}")
    
    return asyncio.run(_generate())

# Использование
try:
    raw_data = "..."  # Ваши исходные данные
    report = generate_taxi_park_report(raw_data)
    print(f"Отчет '{report.meta.title}' успешно создан!")
    print(f"Период: {report.meta.period}")
except (ValueError, Exception) as e:
    print(f"Ошибка: {e}")
```

**Важные замечания:**

1. **Установка**: Установите библиотеки `openai-agents` и `litellm` через pip
2. **API ключ**: Используйте переменную окружения `ANTHROPIC_API_KEY` для безопасного хранения ключа
3. **Модели**: Доступные модели Anthropic через LiteLLM:
   - `anthropic/claude-3-5-sonnet-20241022` (рекомендуется)
   - `anthropic/claude-3-opus-20240229`
   - `anthropic/claude-3-haiku-20240307`
4. **Structured Output**: Библиотека автоматически обрабатывает structured output через Pydantic модель, указанную в `output_type`
5. **Валидация**: Библиотека автоматически валидирует ответ через Pydantic и возвращает валидированный объект через `final_output_as()`
6. **Асинхронность**: Основной API библиотеки асинхронный, используйте `asyncio.run()` или `await` в async функциях

### Пример валидации данных

```python
from pydantic import ValidationError

def validate_taxi_park_data(data: dict) -> TaxiParkAnalyticsData:
    """Валидирует данные отчета таксопарка и возвращает Pydantic модель"""
    try:
        return TaxiParkAnalyticsData(**data)
    except ValidationError as e:
        print(f"Ошибки валидации: {e.errors()}")
        raise

# Использование
try:
    report = validate_taxi_park_data(json_data)
    print(f"Отчет '{report.meta.title}' успешно создан!")
    print(f"Период: {report.meta.period}")
except ValidationError as e:
    print(f"Данные не соответствуют схеме: {e}")
```

## Рекомендации

1. **Валидация**: Всегда валидируйте данные через Pydantic после получения от LLM.

2. **Типы данных**: Убедитесь, что LLM понимает разницу между:
   - Числовыми значениями (int/float) для метрик и сравнений
   - Строковыми значениями для compact_metrics.value и total_revenue_formatted (могут содержать единицы)

3. **Форматы месяцев**:
   - В `revenue_comparison`: сокращенные названия на русском (Сент, Окт, Май и т.д.)
   - В `monthly_revenue`: полный формат с годом (Окт 2024, Май 2025)

4. **Опциональные поля**: Многие поля помечены как Optional - это нормально, если они не применимы к конкретному отчету.

5. **Ключевые метрики**: Поле `key_metrics` должно быть словарем, где ключи - это названия метрик (revenue, active_drivers, churn_rate, revenue_per_driver, profitability).

6. **Анализ**: Поля `churn_analysis` и `inflow_analysis` содержат `comparison_data` как список словарей - это позволяет гибко добавлять данные для графиков сравнения.
