import rstr
import re
from jsonpath_ng import parse
import json



class GenerateValues:

    arguments_pattern = {}
    context = {}

    @staticmethod
    def read_scenario(resolved_scenario: dict, arguments_patterns: dict):

        # Сохраняем аргументы и их паттерны
        GenerateValues.arguments_pattern = arguments_patterns

        # Найти все объекты на определенной глубине
        # Глубина 6 обычно соответствует объектам step
        jsonpath_expr = parse('$..*')
        all_matches = jsonpath_expr.find(resolved_scenario)
        
        step_objects = []
        
        for match in all_matches:
            if isinstance(match.value, dict):
                # Проверяем, содержит ли объект нужные поля
                if 'endpoint' in match.value and 'parameters' in match.value:
                    step_objects.append(match)
        
        for match in step_objects:
            obj = match.value
            path = match.full_path

            # GenerateValues.current_endpoint = obj[и'endpoint']
            # GenerateValues.current_name_path = path
            print("-" * 40)
            print(match.value)
            print("-" * 40)
            print(f"Путь: {path}")
            print(f"Endpoint: {obj['endpoint']}")
            print(f"Method: {obj.get('method', 'N/A')}")
            print(f"Parameters: {obj['parameters']}")
            print(f"Expected: {obj.get('expected', {})}")
            print("-" * 40)

            # for param, value in obj['parameters'].items():
            #     cur_path = path + '.' + param
            #     obj.update(resolved_scenario, '12321321321312321313112321')

            endpoint = obj['endpoint']
            # Проходимс по всем параметрам шага
            for key, value in obj['parameters'].items():
                print(f'key = {key} \t value = {value}')
                if value == 'random': # Если рандом то генерим по regex

                    # Генерируем значение по шаблону
                    arg_value = GenerateValues.arguments_pattern[f"{endpoint}"][f"{key}"]["pattern"]
                    print(f"key = {key}, arg_value = {rstr.xeger(arg_value)}")


                elif value == 'minimum': # Если минимум, то присваиваем минимально возможное значение из схемы
                    ...
                elif value == 'maximum': # Если максимум, то присваиваем максимально возможное значение  из схемы
                    ...
                elif isinstance(value, dict): # Если это словарь и если там есть ref то мы берем значение из context
                    ...
                else: # Если ничего из этого не проходит то мы просто оставляем значение которое мы указали в сценарии
                    ...
                
        return resolved_scenario

            



    # @staticmethod
    # def generate_value(parameters: dict, endpoint: str, path_name: str):
    #     for key, value in parameters.items():


        






















































































































# class GenerateValues:

#     context = {}

#     @staticmethod
#     def generate_values(scenario_scheme, arguments_pattern=None):
#         """
#         Извлекает parameters с полными путями к каждому полю
#         """
#         parameters_with_paths = {}
        
#         def _extract_parameters(obj, current_path=""):
#             if isinstance(obj, dict):
#                 if 'parameters' in obj and isinstance(obj['parameters'], dict):
#                     for param_name, param_value in obj['parameters'].items():
#                         full_path = f"{current_path}.parameters.{param_name}"
#                         parameters_with_paths[full_path] = param_value
                
#                 for key, value in obj.items():
#                     new_path = f"{current_path}.{key}" if current_path else key
#                     _extract_parameters(value, new_path)
                    
#             elif isinstance(obj, list):
#                 for i, item in enumerate(obj):
#                     new_path = f"{current_path}[{i}]" if current_path else f"[{i}]"
#                     _extract_parameters(item, new_path)
        
#         _extract_parameters(scenario_scheme)
#         return parameters_with_paths

#     @staticmethod
#     def process_scenario_sequentially(scenario, arguments_pattern):
#         """
#         Обрабатывает сценарий последовательно: PRESET -> TESTS -> AFTER-TEST
#         """
#         # Создаем копию сценария
#         processed_scenario = json.loads(json.dumps(scenario))
        
#         # Обрабатываем каждый endpoint в сценарии
#         for endpoint, endpoint_config in processed_scenario.items():
#             # 1. Обрабатываем PRESET (генерируем значения и сохраняем в контекст)
#             if 'PRESET' in endpoint_config and 'steps' in endpoint_config['PRESET']:
#                 for step_num, step_config in endpoint_config['PRESET']['steps'].items():
#                     if 'parameters' in step_config:
#                         GenerateValues._generate_step_parameters(step_config, arguments_pattern)
            
#             # 2. Обрабатываем TESTS (используем значения из контекста для ref)
#             if 'TESTS' in endpoint_config:
#                 for test_num, test_config in endpoint_config['TESTS'].items():
#                     if 'steps' in test_config:
#                         for step_num, step_config in test_config['steps'].items():
#                             if 'parameters' in step_config:
#                                 GenerateValues._generate_step_parameters(step_config, arguments_pattern)
            
#             # 3. Обрабатываем AFTER-TEST (используем значения из контекста)
#             if 'AFTER-TEST' in endpoint_config and 'steps' in endpoint_config['AFTER-TEST']:
#                 for step_num, step_config in endpoint_config['AFTER-TEST']['steps'].items():
#                     if 'parameters' in step_config:
#                         GenerateValues._generate_step_parameters(step_config, arguments_pattern)
        
#         return processed_scenario

#     @staticmethod
#     def _generate_step_parameters(step_config, arguments_pattern):
#         """
#         Генерирует параметры для конкретного шага
#         """
#         if 'parameters' not in step_config:
#             return
        
#         for param_name, param_value in step_config['parameters'].items():
#             # Если это ссылка ref - заменяем на значение из контекста
#             if isinstance(param_value, dict) and 'ref' in param_value:
#                 ref_path = param_value['ref']
#                 # Извлекаем путь к значению из ссылки
#                 context_key = GenerateValues._extract_context_key_from_ref(ref_path)
#                 if context_key in GenerateValues.context:
#                     step_config['parameters'][param_name] = GenerateValues.context[context_key]
#                 continue
            
#             # Если значение "random" - генерируем по паттерну
#             if param_value == "random" and param_name in arguments_pattern:
#                 pattern_info = arguments_pattern[param_name]
#                 if 'pattern' in pattern_info:
#                     generated_value = rstr.xeger(pattern_info['pattern'])
#                     step_config['parameters'][param_name] = generated_value
#                     # Сохраняем в контекст для последующего использования
#                     GenerateValues.context[param_name] = generated_value
                
#                 elif 'minimum' in pattern_info and 'maximum' in pattern_info:
#                     import random
#                     min_val = pattern_info['minimum']
#                     max_val = pattern_info['maximum']
#                     generated_value = random.randint(min_val, max_val)
#                     step_config['parameters'][param_name] = generated_value
#                     GenerateValues.context[param_name] = generated_value
            
#             # Если значение уже задано (не "random"), сохраняем его в контекст
#             elif param_value != "random":
#                 GenerateValues.context[param_name] = param_value

#     @staticmethod
#     def _extract_context_key_from_ref(ref_path):
#         """
#         Извлекает ключ контекста из ссылки ref
#         Пример: "#PRESET.steps.1.parameters.vrf_name" -> "vrf_name"
#         """
#         # Разбираем путь ref
#         parts = ref_path.split('.')
        
#         # Ищем часть с parameters и берем следующую за ней (имя параметра)
#         for i, part in enumerate(parts):
#             if part == 'parameters' and i + 1 < len(parts):
#                 return parts[i + 1]
        
#         # Если не нашли, берем последнюю часть
#         return parts[-1] if parts else ref_path




