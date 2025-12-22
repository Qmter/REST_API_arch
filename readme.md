# REST API TEST AUTOMATION

## Описание

REST API Test Generator — это инструмент для автоматической генерации тестов на основе OpenAPI спецификации и JSON сценариев. Система позволяет создавать комплексные тестовые сценарии с поддержкой шаблонов, ссылок между тестами и автоматической валидацией схемы.

## Особенности

- **Автоматическая генерация тестов** на основе OpenAPI спецификации
- **Поддержка сложных сценариев** с шаблонами и ссылками
- **Взаимосвязанные тесты** - возможность ссылаться на значения из других шагов
- **Встроенная валидация** схемы и совместимости с OpenAPI
- **Гибкая структура** с разделением на PRESET, TESTS и AFTER-TEST
- **Конфигурируемая генерация** случайных данных с seed
- **Детальное логирование** всех этапов генерации

## Формат сценариев тестов

### Базовая структура
```json
{
    "<Имя_тестируемого_endpoint>": {
        "PRESET": {
            "1": {
                "description": "Описание теста",
                "steps": {
                    "1": {
                        "endpoint": "<Имя_endpoint>",
                        "method": "<Метод>",
                        "parameters": {"<Параметры>"},
                        "expected": {
                            "errCode": "<Код_ошибки>",
                            "HTTPCode": "<Код_HTTP>"
                        }
                    }
                }
            }
        },
        "TESTS": {},
        "AFTER-TEST": {}
    }
}
```

### Компоненты сценария

| Компонент | Описание |
|-----------|----------|
| **PRESET** | Блок для создания тестовой среды (предварительные настройки) |
| **TESTS** | Основной блок для тестирования функциональности |
| **AFTER-TEST** | Блок для очистки тестовой среды |
| **steps** | Последовательность шагов теста |
| **endpoint** | API endpoint для запроса |
| **method** | HTTP метод (GET, POST) |
| **parameters** | Параметры запроса |
| **expected** | Ожидаемые результаты |

## Поддерживаемые значения параметров

| Значение | Описание | Пример |
|----------|----------|---------|
| `"random"` | Случайное значение из диапазона OpenAPI | `"port": "random"` |
| `"minimum"` | Минимальное значение из схемы OpenAPI | `"age": "minimum"` |
| `"maximum"` | Максимальное значение из схемы OpenAPI | `"count": "maximum"` |
| Константа | Конкретное значение | `"active": true` |
| Ссылка | Значение из другого шага теста | `{"ref": "#PRESET.steps.1.id"}` |

## Структура проекта

```
project/
├── config/
│   └── read_confg.py          # Конфигурация путей и параметров
├── scenarios/                  # JSON сценарии тестов
│   ├── api/
│   │   └── _users_get.json
│   └── system/
│       └── _info_get.json
├── templates/                  # Шаблоны тестов
│   └── _vrf_templates.json
├── tests/                      # Сгенерированные тесты
├── utils/
│   ├── generate_tests/        # Модули генерации тестов
│   ├── log.py                 # Логирование
│   └── http_methods.py        # HTTP методы
└── generate_test.py           # Основной скрипт генерации
```

## Быстрый старт

### Установка зависимостей
```bash
# Убедитесь, что у вас установлен Python 3.8+
python3 --version

# Установите зависимости (если требуется)
pip install -r requirements.txt
```

### Базовая настройка
Перед использованием проверьте файл конфигурации `config/config.ini`:
- `scenarios_dir` -  папка сценариев
- `templates_dir` - папка с шаблонами
- `openapi_dir` - папка к OpenAPI спецификации
- `tests_dir` - директория для сгенерированных тестов

### Примеры использования

#### 1. Генерация всех тестов
```bash
python3 generate_test.py
```

#### 2. Генерация с подробным выводом
```bash
python3 generate_test.py --verbose
```

#### 3. Генерация конкретных endpoint'ов
```bash
python3 generate_test.py -e users_get system_info
```

#### 4. Генерация тестов из директории
```bash
python3 generate_test.py -d api/v1
```

#### 5. Генерация с фиксированным seed
```bash
python3 generate_test.py -s 12345 -e users_post
```

#### 6. Показать справку
```bash
python3 generate_test.py --help
```

## Примеры сценариев

### Простой тест
```json
{
  "/interfaces/tunnel/multicast": {
    "TESTS": {
      "1": {
        "description": "Set on multicast",
        "steps": {
          "1": {
            "endpoint": "/interfaces/tunnel/add",
            "method": "POST",
            "parameters": {
              "ifname": "random",
              "source": "random",
              "tos": "maximum",
              "key": "maximum"
            },
            "expected": {
              "errCode": 0,
              "httpCode": 200
            }
          }
        }
      }
    }
  }
}
```

### Шаблоны тестов

Шаблоны хранятся в `/templates` и позволяют переиспользовать общие паттерны тестирования.

#### Пример шаблона (`_vrf_templates.json`):
```json
{
  "/vrf": {
    "TESTS": {
      "ADD": {
        "endpoint": "/vrf",
        "method": "POST",
        "parameters": {
          "action": "add",
          "vrf_name": "random"
        },
        "expected": {"errCode": 0, "httpCode": 200}
      },
      "DELETE": {
        "endpoint": "/vrf",
        "method": "POST",
        "parameters": {
          "action": "delete",
          "vrf_name": "random"
        },
        "expected": {"errCode": 0, "httpCode": 200}
      }
    }
  }
}
```

#### Использование шаблона:
```json
{
  "/interfaces/loopback/add": {
    "PRESET": {
      "steps": {
        "1": {
          "template": "#TEMPLATES./vrf.TESTS.ADD"
        },
        "2": {
          "endpoint": "/interfaces/loopback/add",
          "method": "POST",
          "parameters": {
            "ifname": "random",
            "vrf_name": {"ref": "#PRESET.steps.1.parameters.vrf_name"}
          },
          "expected": {"errCode": 0, "httpCode": 200}
        }
      }
    }
  }
}
```

## Конфигурация

### Основные параметры в `config/read_confg.py`:

```python
# Пути/папки к директориям
SCENARIOS_DIR = "scenarios"
TEMPLATES_DIR = "templates"
TESTS_DIR = "tests"
OPENAPI_PATH = "openapi.json"

# Словарь endpoint'ов для корректного отображения имен
DICT_ENDPOINTS = {
    "users_get": "/api/v1/users",
    "system_info": "/system/info"
}
```

### Настройка через командную строку:

| Аргумент | Описание | Пример |
|----------|----------|---------|
| `--verbose, -v` | Подробный вывод (debug режим) | `-v` |
| `--seed, -s` | Seed для генератора случайных чисел | `-s 12345` |
| `--logname, -ln` | Имя файла лога | `-ln my_test` |
| `--route, -r` | Целевая директория для тестов | `-r custom_tests` |
| `--endpoints, -e` | Конкретные endpoint'ы | `-e users_get` |
| `--dir, -d` | Директория сценариев | `-d api/v1` |

## Детали реализации

### Процесс генерации тестов:
1. **Парсинг сценария** - загрузка и проверка JSON сценария
2. **Валидация структуры** - проверка корректности формата
3. **Разрешение схемы** - анализ OpenAPI спецификации
4. **Генерация значений** - создание тестовых данных
5. **Проверка совместимости** - валидация с OpenAPI
6. **Генерация тестов** - создание готовых тестовых файлов
7. **Очистка** - удаление пустых директорий

### Система ссылок:
- `#PRESET.steps.1.parameters.name` - ссылка на параметр из PRESET
- `#TEMPLATES./vrf.TESTS.ADD` - использование шаблона
- `{"ref": "... "}` - ссылка на значение

## Логирование

Система создает подробные логи выполнения:
- Логи сохраняются в файлы с именем `log_<режим>_<время>.log`
- Режимы логирования: `verbose` (подробный) и `info` (основной)
- Итоговый отчет со статусом генерации каждого endpoint'а

## Расширенные возможности

### Создание собственных шаблонов:
1. Создайте файл в директории `templates/`
2. Имя файла должно начинаться с `_` (например, `_my_template.json`)
3. Определите структуру шаблона с общими паттернами тестирования
4. Используйте в сценариях через `#TEMPLATES.<endpoint>`

### Кастомная генерация значений:
Вы можете расширить класс `GenerateValues` для поддержки:
- Специфичных форматов данных
- Бизнес-логики генерации
- Интеграции с внешними системами
