import rstr
import re
from jsonpath_ng import parse
import random
import json
import datetime
import logging

from config.read_confg import (
    NO_USE_SWITCHPORT,
    NO_USE_VLAN,
    NO_USE_ETH,
    NO_USE_VLAN_ID
)

# Список интерфесов которые нельзя использовать
NO_USE_LIST = [NO_USE_VLAN_ID, NO_USE_ETH, NO_USE_SWITCHPORT, NO_USE_VLAN]

class GenerateValues:
    """Класс для генерации значений для аргументов сценария."""

    arguments_pattern = {}  # Словарь для хранения всех паттернов для каждого endpoint
    context = {}  # Контекст для хранения значений аргументов

    @staticmethod
    def read_scenario(resolved_scenario: dict, arguments_patterns: dict, seed: int):
        """Функция для чтения сценария и сопостовления аргументов по паттернам"""

        random.seed(seed)  # Устанавливаем случайное сид для генерации значений

        GenerateValues.context = {}  # Очищаем контекст

        # Сохраняем аргументы и их паттерны
        GenerateValues.arguments_pattern = arguments_patterns

        # Найти все объекты на определенной глубине
        try:
            jsonpath_expr = parse('$..*')  # Создаем JSONPath-выражение для поиска всех объектов в JSON-структуре
            all_matches = jsonpath_expr.find(resolved_scenario)  # Находим все объекты в JSON-структуре
        except Exception as e:
            logging.debug(f"Ошибка при разборе JSONPath: {e}")
            raise

        step_objects = []  # Список объектов, которые содержат параметры (parameters) или валидацию (validation)

        for match in all_matches:  # Получаем все объекты в JSON-структуре
            try:
                if isinstance(match.value, dict):  # Если это словарь, то это объект
                    # Проверяем, содержит ли объект нужные поля
                    if 'endpoint' in match.value and ('parameters' in match.value or 'validation' in match.value):
                        step_objects.append(match)  # Добавляем объект в список
            except Exception as e:
                logging.debug(f"Ошибка при обработке объекта JSONPath: {e}")
                continue

        for match in step_objects:  # Обходим все объекты в списке
            try:
                obj = match.value  # Получаем объект
                path = match.full_path  # Получаем путь к объекту

                logging.debug("=" * 68)
                logging.debug(f"Путь: {path}")
                logging.debug(f"Endpoint: {obj['endpoint']}")
                logging.debug(f"Method: {obj.get('method', 'N/A')}")
                logging.debug(f"Parameters: {obj.get('parameters', {})}")
                logging.debug(f"Validation: {obj.get('validation', {})}")
                if 'expected' in obj:
                    logging.debug(f"Expected: {obj.get('expected', {})}")

                endpoint = obj['endpoint']  # Текущий endpoint

                logging.debug("-" * 68)
                logging.debug("Сгенерированные значения:")
                logging.debug("-" * 68)

                # Обрабатываем параметры (parameters)
                if 'parameters' in obj:
                    GenerateValues.process_fields(
                        resolved_scenario=resolved_scenario,
                        fields=obj['parameters'],
                        path=path,
                        field_type="parameters",
                        endpoint=endpoint
                    )

                # Обрабатываем валидацию (validation)
                if 'validation' in obj:
                    GenerateValues.process_fields(
                        resolved_scenario=resolved_scenario,
                        fields=obj['validation'],
                        path=path,
                        field_type="validation",
                        endpoint=endpoint
                    )
                logging.debug("=" * 68)
            except Exception as e:
                logging.debug(f"Ошибка при обработке шага сценария: {e}")
                continue

        return resolved_scenario  # Возвращаем обработанный сценарий

    @staticmethod
    def process_fields(resolved_scenario: dict, fields: dict, path, field_type: str, endpoint: str):
        """
        Обрабатывает поля parameters или validation.

        -resolved_scenario: Исходная JSON-структура.
        -fields: Словарь с параметрами (parameters или validation).
        -path: Путь к текущему объекту.
        -field_type: Тип полей ("parameters" или "validation").
        -endpoint: Текущий endpoint.
        """
        for key, value in fields.items():
            try:
                path_for_func = str(path) + f".{field_type}.{key}"  # Чистый путь до аргумента для функции setup_values
                current_path = "#" + '.'.join(str(path).split('.')[1:]) + f".{field_type}.{key}"  # Текущий путь да аргумента для сохранения его в контексте для дальнейшего использования

                if value == 'random':  # Если рандом, то генерим по regex
                    try:
                        keys_patterns_arguments = GenerateValues.arguments_pattern[f"{endpoint}"][f"{key}"].keys()  # Получаем все паттерны для этого аргумента (Либо pattern, либо minimum, либо maximum)

                        if "pattern" in keys_patterns_arguments:  # Проверяем, есть ли паттерны для этого аргумента
                            arg_patterns = GenerateValues.arguments_pattern[f"{endpoint}"][f"{key}"]["pattern"]  # Получаем список паттернов для аргумента(может быть 1 или больше)
                            selected_pattern = random.choice(arg_patterns) if len(arg_patterns) > 1 else arg_patterns[0]  # Если есть несколько паттернов, выбираем случайный
                            while True:
                                arg_value = rstr.xeger(selected_pattern)  # Генерируем значение по регулярному выражению
                                if arg_value in NO_USE_LIST:
                                    arg_value = rstr.xeger(selected_pattern)
                                else:
                                    break

                        elif "minimum" in keys_patterns_arguments and "maximum" in keys_patterns_arguments:  # Если есть минимальное и максимальное значение, генерируем случайное значение в этом диапазоне
                            arg_min = GenerateValues.arguments_pattern[f"{endpoint}"][f"{key}"]["minimum"]  # Получаем минимальное значение
                            arg_max = GenerateValues.arguments_pattern[f"{endpoint}"][f"{key}"]["maximum"]  # Получаем максимальное значение
                            while True:
                                if arg_value in NO_USE_LIST:
                                    arg_value = random.randint(arg_min, arg_max)  # Генерируем случайное значение в этом диапазоне
                                else:
                                    break

                        else:
                            arg_value = None  # Если нет конфигурации, оставляем как есть

                        if arg_value is not None:  # Если значение не None, то устанавливаем его
                            # Устанавливаем значение
                            GenerateValues.setup_values(
                                scenario_scheme=resolved_scenario,
                                path_to_arg=path_for_func,
                                value=arg_value
                            )
                            GenerateValues.context[f"{current_path}"] = arg_value  # Сохраняем значение в контексте для дальнейшего использования
                            logging.debug(f"key = {key}, arg_value = {arg_value}")

                    except KeyError as e:
                        logging.debug(f"Отсутствует паттерн для аргумента {key} в endpoint {endpoint}: {e}")
                        continue
                    except Exception as e:
                        logging.debug(f"Ошибка при генерации значения для {key}: {e}")
                        continue

                elif value == 'minimum':  # Минимальное значение
                    try:
                        arg_value = GenerateValues.arguments_pattern[f"{endpoint}"][f"{key}"]["minimum"]  # Получаем минимальное значение

                        # Устанавливаем значение
                        GenerateValues.setup_values(
                            scenario_scheme=resolved_scenario,
                            path_to_arg=path_for_func,
                            value=arg_value
                        )

                        GenerateValues.context[f"{current_path}"] = arg_value  # Сохраняем значение в контексте для дальнейшего использования
                        logging.debug(f"key = {key}, arg_value = {arg_value}")
                    except KeyError as e:
                        logging.debug(f"Отсутствует минимальное значение для аргумента {key} в endpoint {endpoint}: {e}")
                        continue
                    except Exception as e:
                        logging.debug(f"Ошибка при установке минимального значения для {key}: {e}")
                        continue

                elif value == 'maximum':  # Максимальное значение
                    try:
                        arg_value = GenerateValues.arguments_pattern[f"{endpoint}"][f"{key}"]["maximum"]  # Получаем максимальное значение

                        # Устанавливаем значение
                        GenerateValues.setup_values(
                            scenario_scheme=resolved_scenario,
                            path_to_arg=path_for_func,
                            value=arg_value
                        )

                        GenerateValues.context[f"{current_path}"] = arg_value  # Сохраняем значение в контексте для дальнейшего использования
                        logging.debug(f"key = {key}, arg_value = {arg_value}")
                    except KeyError as e:
                        logging.debug(f"Отсутствует максимальное значение для аргумента {key} в endpoint {endpoint}: {e}")
                        continue
                    except Exception as e:
                        logging.debug(f"Ошибка при установке максимального значения для {key}: {e}")
                        continue

                elif value == 'gt_max':  # Больше максимального значения
                    try:
                        arg_value = GenerateValues.arguments_pattern[f"{endpoint}"][f"{key}"]["maximum"] + 1  # Получаем максимальное значение

                        # Устанавливаем значение
                        GenerateValues.setup_values(
                            scenario_scheme=resolved_scenario,
                            path_to_arg=path_for_func,
                            value=arg_value
                        )

                        GenerateValues.context[f"{current_path}"] = arg_value  # Сохраняем значение в контексте для дальнейшего использования
                        logging.debug(f"key = {key}, arg_value = {arg_value}")
                    except KeyError as e:
                        logging.debug(f"Отсутствует максимальное значение для аргумента {key} в endpoint {endpoint}: {e}")
                        continue
                    except Exception as e:
                        logging.debug(f"Ошибка при установке значения gt_max для {key}: {e}")
                        continue

                elif value == 'lt_min':  # Меньше минимального значения
                    try:
                        arg_value = GenerateValues.arguments_pattern[f"{endpoint}"][f"{key}"]["minimum"] - 1  # Получаем минимальное значение

                        # Устанавливаем значение
                        GenerateValues.setup_values(
                            scenario_scheme=resolved_scenario,
                            path_to_arg=path_for_func,
                            value=arg_value
                        )

                        GenerateValues.context[f"{current_path}"] = arg_value  # Сохраняем значение в контексте для дальнейшего использования
                        logging.debug(f"key = {key}, arg_value = {arg_value}")
                    except KeyError as e:
                        logging.debug(f"Отсутствует минимальное значение для аргумента {key} в endpoint {endpoint}: {e}")
                        continue
                    except Exception as e:
                        logging.debug(f"Ошибка при установке значения lt_min для {key}: {e}")
                        continue

                elif isinstance(value, dict) and "modify" in value.keys():
                    ...  # Добавить реализацию модификаторов для генерации значений(например: ip_address)

                elif isinstance(value, dict) and "ref" in value.keys():  # Ссылка (ref):
                    try:
                        ref_arg = value['ref']  # Получаем ссылку в формате "TESTS.1.steps.1.parameters.ifname"
                        arg_value = GenerateValues.context[f"{ref_arg}"]  # Получаем значение из контекста по ссылке

                        # Устанавливаем значение
                        GenerateValues.setup_values(
                            scenario_scheme=resolved_scenario,
                            path_to_arg=path_for_func,
                            value=arg_value
                        )

                        GenerateValues.context[f"{current_path}"] = arg_value  # Сохраняем значение в контексте для дальнейшего использования
                        logging.debug(f'ref_link = {GenerateValues.context[ref_arg]}')
                    except KeyError as e:
                        logging.debug(f"Ссылка {value['ref']} не найдена в контексте: {e}")
                        continue
                    except Exception as e:
                        logging.debug(f"Ошибка при обработке ссылки для {key}: {e}")
                        continue

                else:  # Константа: если задали конкретное значение, то его и оставляем
                    GenerateValues.context[f"{current_path}"] = value  # Устанавливаем значение в контексте для дальнейшего использования
                    logging.debug(f"key = {key}, arg_value = {value}")

            except Exception as e:
                logging.debug(f"Ошибка при обработке поля {key}: {e}")
                continue

    @staticmethod
    def setup_values(scenario_scheme: dict, path_to_arg: str, value) -> dict:
        """
        Рекурсивно устанавливает значение в указанном пути JSON-структуры.

        -scenario_scheme: Исходная JSON-структура (словарь).
        -path_to_arg: Путь к параметру в формате "TESTS.1.steps.1.parameters.ifname".
        -value: Значение, которое нужно установить.
        -return: Обновленная JSON-структура.
        """
        try:
            # Разбиваем путь на части
            parts_of_path = path_to_arg.split('.')

            def _set_value_recursive(current_level, path_parts):
                """
                Вспомогательная рекурсивная функция для установки значения.

                -current_level: Текущий уровень JSON-структуры.
                -path_parts: Оставшиеся части пути.
                """
                try:
                    part = path_parts[0]  # Получаем текущий элемент пути

                    # Если это последний элемент пути, устанавливаем значение
                    if len(path_parts) == 1:
                        current_level[part] = value
                        return

                    # Если текущий уровень еще не содержит нужный ключ, создаем его
                    if part not in current_level:
                        current_level[part] = {}

                    # Рекурсивно углубляемся в структуру
                    _set_value_recursive(current_level[part], path_parts[1:])
                except Exception as e:
                    logging.debug(f"Ошибка в _set_value_recursive: {e}")
                    raise

            # Вызываем рекурсивную функцию
            _set_value_recursive(scenario_scheme, parts_of_path)

            return scenario_scheme  # Возвращаем обновленную JSON-структуру
        except Exception as e:
            logging.debug(f"Ошибка в setup_values для пути {path_to_arg}: {e}")
            raise