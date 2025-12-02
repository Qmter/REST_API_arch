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