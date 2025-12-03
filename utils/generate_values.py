import rstr
import re
from jsonpath_ng import parse
import random
import json
import datetime

# random.seed(datetime.datetime.now().timestamp())      #TODO для дальнейшей реализации random

class GenerateValues:
    """Класс для генерации значений для аргументов сценария."""

    arguments_pattern = {} # Словарь для хранения всех паттернов для каждого endpoint
    context = {} # Контекст для хранения значений аргументов

    @staticmethod
    def read_scenario(resolved_scenario: dict, arguments_patterns: dict):
        """Функция для чтения сценария и сопостовления аргументов по паттернам"""
        
        GenerateValues.context = {} # Очищаем контекст

        # Сохраняем аргументы и их паттерны
        GenerateValues.arguments_pattern = arguments_patterns

        # Найти все объекты на определенной глубине
        jsonpath_expr = parse('$..*') # Создаем JSONPath-выражение для поиска всех объектов в JSON-структуре
        all_matches = jsonpath_expr.find(resolved_scenario) # Находим все объекты в JSON-структуре
        
        step_objects = [] # Список объектов, которые содержат параметры (parameters) или валидацию (validation)
        
        for match in all_matches: # Получаем все объекты в JSON-структуре
            if isinstance(match.value, dict): # Если это словарь, то это объект
                # Проверяем, содержит ли объект нужные поля
                if 'endpoint' in match.value and ('parameters' in match.value or 'validation' in match.value):
                    step_objects.append(match) # Добавляем объект в список
        
        for match in step_objects:  # Обходим все объекты в списке
            obj = match.value # Получаем объект
            path = match.full_path # Получаем путь к объекту

            print("-" * 40)
            print(f"Путь: {path}")
            print(f"Endpoint: {obj['endpoint']}")
            print(f"Method: {obj.get('method', 'N/A')}")
            print(f"Parameters: {obj.get('parameters', {})}")
            print(f"Validation: {obj.get('validation', {})}")
            print(f"Expected: {obj.get('expected', {})}")
            print("-" * 40)

            endpoint = obj['endpoint']  # Текущий endpoint

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
        
        return resolved_scenario # Возвращаем обработанный сценарий


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

            path_for_func = str(path) + f".{field_type}.{key}" # Чистый путь до аргумента для функции setup_values
            current_path = "#" + '.'.join(str(path).split('.')[1:]) + f".{field_type}.{key}" # Текущий путь да аргумента для сохранения его в контексте для дальнейшего использования

            if value == 'random':  # Если рандом, то генерим по regex
                keys_patterns_arguments = GenerateValues.arguments_pattern[f"{endpoint}"][f"{key}"].keys() # Получаем все паттерны для этого аргумента (Либо pattern, либо minimum, либо maximum)

                if "pattern" in keys_patterns_arguments: # Проверяем, есть ли паттерны для этого аргумента
                    arg_patterns = GenerateValues.arguments_pattern[f"{endpoint}"][f"{key}"]["pattern"] # Получаем список паттернов для аргумента(может быть 1 или больше)
                    selected_pattern = random.choice(arg_patterns) if len(arg_patterns) > 1 else arg_patterns[0] # Если есть несколько паттернов, выбираем случайный
                    arg_value = rstr.xeger(selected_pattern) # Генерируем значение по регулярному выражению

                elif "minimum" in keys_patterns_arguments and "maximum" in keys_patterns_arguments:  # Если есть минимальное и максимальное значение, генерируем случайное значение в этом диапазоне
                    arg_min = GenerateValues.arguments_pattern[f"{endpoint}"][f"{key}"]["minimum"] # Получаем минимальное значение
                    arg_max = GenerateValues.arguments_pattern[f"{endpoint}"][f"{key}"]["maximum"] # Получаем максимальное значение
                    arg_value = random.randint(arg_min, arg_max)  # Генерируем случайное значение в этом диапазоне

                else:
                    arg_value = None  # Если нет конфигурации, оставляем как есть

                if arg_value is not None:  # Если значение не None, то устанавливаем его
                    # Устанавливаем значение
                    GenerateValues.setup_values(
                        scenario_scheme=resolved_scenario,
                        path_to_arg=path_for_func,
                        value=arg_value
                    )
                    GenerateValues.context[f"{current_path}"] = arg_value # Сохраняем значение в контексте для дальнейшего использования
                    print(f"key = {key}, arg_value = {arg_value}") 

            elif value == 'minimum':  # Минимальное значение
                arg_value = GenerateValues.arguments_pattern[f"{endpoint}"][f"{key}"]["minimum"] # Получаем минимальное значение

                # Устанавливаем значение
                GenerateValues.setup_values(
                    scenario_scheme=resolved_scenario,
                    path_to_arg=path_for_func,
                    value=arg_value
                )

                GenerateValues.context[f"{current_path}"] = arg_value # Сохраняем значение в контексте для дальнейшего использования
                print(f"key = {key}, arg_value = {arg_value}")

            elif value == 'maximum':  # Максимальное значение
                arg_value = GenerateValues.arguments_pattern[f"{endpoint}"][f"{key}"]["maximum"] # Получаем максимальное значение

                # Устанавливаем значение
                GenerateValues.setup_values(
                    scenario_scheme=resolved_scenario,
                    path_to_arg=path_for_func,
                    value=arg_value
                )

                GenerateValues.context[f"{current_path}"] = arg_value # Сохраняем значение в контексте для дальнейшего использования
                print(f"key = {key}, arg_value = {arg_value}")

            elif isinstance(value, dict) and "ref" in value.keys():  # Ссылка (ref):
                ref_arg = value['ref']  # Получаем ссылку в формате "TESTS.1.steps.1.parameters.ifname"
                arg_value = GenerateValues.context[f"{ref_arg}"] # Получаем значение из контекста по ссылке
                
                # Устанавливаем значение
                GenerateValues.setup_values(
                    scenario_scheme=resolved_scenario,
                    path_to_arg=path_for_func,
                    value=arg_value
                )
                GenerateValues.context[f"{current_path}"] = arg_value # Сохраняем значение в контексте для дальнейшего использования
                print(f'ref_link = {GenerateValues.context[f'{ref_arg}']}') 

            else:  # Константа: если задали конкретное значение, то его и остваляем
                GenerateValues.context[f"{current_path}"] = value # Устанавливаем значение в контексте для дальнейшего использования


    @staticmethod
    def setup_values(scenario_scheme: dict, path_to_arg: str, value) -> dict:
        """
        Рекурсивно устанавливает значение в указанном пути JSON-структуры.
        
        -scenario_scheme: Исходная JSON-структура (словарь).
        -path_to_arg: Путь к параметру в формате "TESTS.1.steps.1.parameters.ifname".
        -value: Значение, которое нужно установить.
        -return: Обновленная JSON-структура.
        """
        # Разбиваем путь на части
        parts_of_path = path_to_arg.split('.')
        
        def _set_value_recursive(current_level, path_parts):
            """
            Вспомогательная рекурсивная функция для установки значения.
            
            -current_level: Текущий уровень JSON-структуры.
            -path_parts: Оставшиеся части пути.
            """
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
        
        # Вызываем рекурсивную функцию
        _set_value_recursive(scenario_scheme, parts_of_path)
        
        return scenario_scheme # Возвращаем обновленную JSON-структуру
