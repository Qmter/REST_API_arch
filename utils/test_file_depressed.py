# import rstr

# class GenVal:

#     endpoint = ''
#     name_path = ''
#     arguments_pattern = {}
#     context = {}

#     @staticmethod
#     def generate_values(scenario, arguments_pattern, endpoint):
#         GenVal.endpoint = endpoint
#         GenVal.arguments_pattern = arguments_pattern
#         GenVal.context = {}  # Сбрасываем контекст
        
#         if isinstance(scenario, dict):
#             for endpoint, endpoint_config in scenario.items():
#                 if isinstance(endpoint_config, dict):
#                     for section, section_config in endpoint_config.items():
#                         if section == "PRESET":
#                             # Начинаем путь с endpoint и секции
#                             GenVal.name_path = f"{endpoint}.{section}"
#                             GenVal.gen_test_block(section_config)
#                             GenVal.name_path = ''
#                         if section == "TESTS":
#                             # Начинаем путь с endpoint и секции
#                             GenVal.name_path = f"{endpoint}.{section}"
#                             GenVal.gen_test_block(section_config)
#                             GenVal.name_path = ''
#                         if section == "AFTER-TEST":
#                             # Начинаем путь с endpoint и секции
#                             GenVal.name_path = f"{endpoint}.{section}"
#                             GenVal.gen_test_block(section_config)
#                             GenVal.name_path = ''
#         return scenario

#     @staticmethod
#     def gen_test_block(preset_scenario) -> dict:
#         if isinstance(preset_scenario, dict):
#             for key, value in preset_scenario.items():
#                 # Сохраняем текущий путь
#                 old_path = GenVal.name_path
                
#                 if key == 'parameters':
#                     # Добавляем parameters к пути
#                     GenVal.name_path += f".parameters"
                    
#                     for arg, arg_value in value.items():
#                         if arg_value == 'random':
#                             for i in GenVal.arguments_pattern:
#                                 pattern_string = i[arg]["minimum"]
#                             generated_value = rstr.xeger(pattern_string)
#                             value[arg] = generated_value
                            
#                             # Сохраняем с полным путем включая имя параметра
#                             full_path = f"{GenVal.name_path}.{arg}"
#                             GenVal.context[full_path] = generated_value
                            
#                         elif arg_value == "minimum":
#                             for i in GenVal.arguments_pattern:
#                                 pattern_string = i[arg]["minimum"]
                            
#                             value[arg] = rstr.xeger(pattern_string)
#                         elif arg_value == "maximum":
#                             for i in GenVal.arguments_pattern:
#                                 pattern_string = i[arg]["minimum"]
#                             value[arg] = rstr.xeger(pattern_string)
#                         elif isinstance(arg_value, dict):
#                             for ref_key, ref_arg in arg_value.items():
#                                 value[arg] = GenVal.context[ref_arg.replace('#', f'{GenVal.endpoint}.')]
                            
#                     # Восстанавливаем путь
#                     GenVal.name_path = old_path
                    
#                 else:
#                     # Добавляем ключ к пути и рекурсивно обрабатываем
#                     GenVal.name_path += f".{key}"
#                     GenVal.gen_test_block(value)
#                     # Восстанавливаем путь после рекурсии
#                     GenVal.name_path = old_path
        
#         return preset_scenario






# TODO ЕСЛИ ПОНАДОБИТСЯ ЧИТАТЬСЯ АРГУМЕКНТЫ OneOf AnyOf enum и т.п
    # @staticmethod
    # def find_all_patterns_min_max(schema):
    #     """
    #     Находит ВСЕ pattern, minimum, maximum в УЖЕ РАЗРЕШЕННОЙ схеме.
    #     Если anyOf содержит несколько паттернов, возвращает их как массив.
    #     Если паттерн один, возвращает его как строку.
    #     """
    #     results = {}
        
    #     def _deep_search(obj, field_name=""):
    #         if isinstance(obj, dict):
    #             # Проверяем текущий объект на наличие pattern, min, max
    #             current_rules = {}

    #             # Обработка pattern
    #             if 'pattern' in obj:
    #                 current_rules.setdefault('pattern', []).append(obj['pattern'])
                
    #             # Обработка minimum и maximum
    #             if 'minimum' in obj:
    #                 current_rules['minimum'] = obj['minimum']
    #             if 'maximum' in obj:
    #                 current_rules['maximum'] = obj['maximum']

    #             # Обработка anyOf
    #             if 'anyOf' in obj:
    #                 patterns_from_anyof = []
    #                 for item in obj['anyOf']:
    #                     if isinstance(item, dict) and 'pattern' in item:
    #                         patterns_from_anyof.append(item['pattern'])
                    
    #                 if patterns_from_anyof:
    #                     # Если паттернов несколько, сохраняем как массив
    #                     if len(patterns_from_anyof) > 1:
    #                         current_rules['pattern'] = patterns_from_anyof
    #                     else:
    #                         # Если паттерн один, сохраняем как строку
    #                         current_rules['pattern'] = patterns_from_anyof[0]

    #             # Сохраняем если нашли правила И есть имя поля
    #             if current_rules and field_name:
    #                 results[field_name] = current_rules
                
    #             # Рекурсивно обходим properties - сохраняем имена полей
    #             if 'properties' in obj:
    #                 for prop_name, prop_schema in obj['properties'].items():
    #                     _deep_search(prop_schema, prop_name)
                
    #             # Рекурсивно обходим остальные значения без изменения имени поля
    #             for key, value in obj.items():
    #                 if key not in ['properties', 'anyOf']:  # properties и anyOf уже обработали
    #                     _deep_search(value, field_name)
                        
    #         elif isinstance(obj, list):
    #             for item in obj:
    #                 _deep_search(item, field_name)
        
    #     # Ищем в requestBody схемы
    #     request_body = schema.get('requestBody', {})
    #     if request_body:
    #         content = request_body.get('content', {})
    #         application_json = content.get('application/json', {})
    #         json_schema = application_json.get('schema', {})
    #         _deep_search(json_schema)
        
    #     # Ищем в parameters (query parameters)
    #     parameters = schema.get('parameters', [])
    #     for param in parameters:
    #         param_schema = param.get('schema', {})
    #         param_name = param.get('name', '')
    #         if param_name:
    #             _deep_search(param_schema, param_name)
        
    #     return results