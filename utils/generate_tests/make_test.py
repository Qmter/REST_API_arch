import json
import logging
import os

class GenerateTests:
    """Класс для генерации тестов"""

    @staticmethod
    def generate_test(scenario: dict, 
                      scenario_path: str, 
                      scenario_folder: str,
                      test_folder: str):
        """Функция для генерации тестов"""
        try:
            test_path = scenario_path.replace(scenario_folder, test_folder) # путь к файлу теста
            
            # Проверяем, существует ли директория для тестов
            test_dir = os.path.dirname(test_path)
            if not os.path.exists(test_dir):
                try:
                    os.makedirs(test_dir, exist_ok=True)
                    logging.debug(f"Создана директория для тестов: {test_dir}")
                except OSError as e:
                    logging.debug(f"Ошибка при создании директории {test_dir}: {e}")
                    raise
            
            json_test = GenerateTests.convert_scenario_to_test(scenario) # преобразование сценария в тест

            logging.debug(json.dumps(json_test, indent=2, ensure_ascii=False))

            try:
                with open(test_path, 'w', encoding='utf-8') as test: # запись теста в файл
                    json.dump(json_test, test, indent=2, ensure_ascii=False) # запись в файл
                logging.debug(f"=" * 68)
                logging.debug(f"Тест успешно сохранен: {test_path}")
            except IOError as e:
                logging.debug(f"Ошибка записи в файл {test_path}: {e}")
                raise
            except Exception as e:
                logging.debug(f"Неизвестная ошибка при записи файла {test_path}: {e}")
                raise
                
        except KeyError as e:
            logging.debug(f"Отсутствует ключ в структуре сценария: {e}")
            raise
        except ValueError as e:
            logging.debug(f"Ошибка в данных сценария: {e}")
            raise
        except Exception as e:
            logging.debug(f"Ошибка при генерации теста из {scenario_path}: {e}")
            raise

    @staticmethod
    def convert_scenario_to_test(scenario):
        """
        Преобразует сценарий в новый формат теста.
        """
        test = {}
        
        def create_test_step(step_data, has_expected=True):
            """Создает шаг теста с правильным ключом (schema/arguments)"""
            try:
                # Проверяем обязательные поля
                if "endpoint" not in step_data:
                    raise KeyError(f"Отсутствует обязательное поле 'endpoint' в шаге")
                if "method" not in step_data:
                    raise KeyError(f"Отсутствует обязательное поле 'method' в шаге для endpoint {step_data.get('endpoint', 'unknown')}")
                
                # Дополнительная проверка: POST методы должны иметь parameters
                if step_data["method"] == "POST":
                    if "parameters" not in step_data:
                        raise ValueError(f"POST метод '{step_data['endpoint']}' не имеет параметров (parameters)")
                    elif not step_data["parameters"]:
                        raise ValueError(f"POST метод '{step_data['endpoint']}' имеет пустые параметры")
                
                if has_expected:
                    if "expected" not in step_data:
                        raise KeyError(f"Ожидается поле 'expected' в шаге для endpoint {step_data['endpoint']}")
                    if "errCode" not in step_data["expected"]:
                        raise KeyError(f"Отсутствует 'errCode' в expected для endpoint {step_data['endpoint']}")
                    if "httpCode" not in step_data["expected"]:
                        raise KeyError(f"Отсутствует 'httpCode' в expected для endpoint {step_data['endpoint']}")
                    
                    step = {
                        "endpoint": step_data["endpoint"],
                        "type": step_data["method"],
                        "errCode": step_data["expected"]["errCode"],
                        "httpCode": step_data["expected"]["httpCode"]
                    }
                else:
                    step = {
                        "endpoint": step_data["endpoint"],
                        "type": step_data["method"]
                    }
                
                # Правильный выбор ключа в зависимости от метода
                if step_data["method"] == "POST":
                    step["schema"] = step_data.get("parameters", {})
                else:
                    step["arguments"] = step_data.get("parameters", {})
                    
                # Добавляем validation только для не-POST методов
                if step_data["method"] != "POST" and "validation" in step_data:
                    step["validation"] = step_data["validation"]
                    
                return step
            except KeyError as e:
                logging.debug(f"Ошибка в структуре шага: {e}")
                raise
            except Exception as e:
                logging.debug(f"Неизвестная ошибка при создании шага теста: {e}")
                raise

        try:
            # Обработка PRESET
            for endpoint, data in scenario.items():
                try:
                    if "PRESET" in data:
                        for preset_id, preset_step in data["PRESET"]["steps"].items():
                            try:
                                has_expected = "expected" in preset_step
                                test_step = create_test_step(preset_step, has_expected)
                                
                                if "PRESET" not in test:
                                    test["PRESET"] = {}
                                test["PRESET"][preset_id] = test_step
                            except Exception as e:
                                logging.debug(f"Ошибка при обработке PRESET шага {preset_id} для endpoint {endpoint}: {e}")
                                continue
                except Exception as e:
                    logging.debug(f"Ошибка при обработке endpoint {endpoint} в PRESET: {e}")
                    continue

            # Обработка TESTS
            for endpoint, data in scenario.items():
                try:
                    if "TESTS" in data:
                        for test_id, test_case in data["TESTS"].items():
                            try:
                                test_key = str(test_id)
                                test[test_key] = {}
                                
                                if "description" in test_case:
                                    test[test_key]["description"] = test_case["description"]
                                
                                for step_id, step in test_case["steps"].items():
                                    try:
                                        step_key = f"{test_id}.{step_id}"
                                        has_expected = "expected" in step
                                        test_step = create_test_step(step, has_expected)
                                        test[test_key][step_key] = test_step
                                    except Exception as e:
                                        logging.debug(f"Ошибка при обработке шага {step_id} в тесте {test_id}: {e}")
                                        continue
                            except Exception as e:
                                logging.debug(f"Ошибка при обработке теста {test_id} для endpoint {endpoint}: {e}")
                                continue
                except Exception as e:
                    logging.debug(f"Ошибка при обработке endpoint {endpoint} в TESTS: {e}")
                    continue

            # Обработка AFTER-TEST
            for endpoint, data in scenario.items():
                try:
                    if "AFTER-TEST" in data:
                        for step_id, step in data["AFTER-TEST"]["steps"].items():
                            try:
                                has_expected = "expected" in step
                                test_step = create_test_step(step, has_expected)
                                
                                if "AFTER-TEST" not in test:
                                    test["AFTER-TEST"] = {}
                                test["AFTER-TEST"][step_id] = test_step
                            except Exception as e:
                                logging.debug(f"Ошибка при обработке AFTER-TEST шага {step_id} для endpoint {endpoint}: {e}")
                                continue
                except Exception as e:
                    logging.debug(f"Ошибка при обработке endpoint {endpoint} в AFTER-TEST: {e}")
                    continue

            return test
            
        except Exception as e:
            logging.debug(f"Критическая ошибка при преобразовании сценария в тест: {e}")
            raise