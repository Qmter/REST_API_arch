import json

class GenerateTests:
    """Класс для генерации тестов"""

    @staticmethod
    def generate_test(scenatio: dict, 
                      scenario_path: str, 
                      scenatio_folder: str,
                      test_folder: str):
        """Функция для генерации тестов"""
        
        test_path = scenario_path.replace(scenatio_folder, test_folder) # путь к файлу теста

        json_test = GenerateTests.convert_scenario_to_test(scenatio) # преобразование сценария в тест

        print(json.dumps(json_test, indent=2, ensure_ascii=False))



        with open(test_path, 'w') as test: # запись теста в файл
            json.dump(json_test, test, indent=2, ensure_ascii=False) # запись в файл




    @staticmethod
    def convert_scenario_to_test(scenario):
        """
        Преобразует сценарий в новый формат теста.

        :param scenario: Исходный сценарий (словарь).
        :return: Преобразованный тест (словарь).
        """
        test = {} # создание словаря для теста

        # Обработка PRESET (только если есть в исходном сценарии)
        for endpoint, data in scenario.items(): # перебор endpoint в сценарии
            if "PRESET" in data:  # если есть PRESET в текущем endpoint
                for preset_id, preset_step in data["PRESET"].items():  # перебор preset_id в PRESET
                    test_step = { 
                        "type": preset_step["method"], 
                        "endpoint": preset_step["endpoint"],
                        "schema": preset_step["parameters"],
                        "errCode": preset_step["expected"]["errCode"],
                        "httpCode": preset_step["expected"]["httpCode"]
                    }
                    if "PRESET" not in test: # если test не содержит PRESET
                        test["PRESET"] = {}  # создание нового ключа PRESET
                    test["PRESET"][preset_id] = test_step # добавление теста в PRESET

        # Обработка TESTS (только если есть в исходном сценарии)
        for endpoint, data in scenario.items():  # перебор endpoint в сценарии
            if "TESTS" in data:  # если есть TESTS в текущем endpoint
                for test_id, test_case in data["TESTS"].items():  # перебор test_id в TESTS
                    test_key = str(test_id)  # создание ключа для теста
                    test[test_key] = {"description": test_case["description"]}  # создание ключа для теста

                    for step_id, step in test_case["steps"].items():  # перебор step_id в TESTS
                        step_key = f"{test_id}.{step_id}"  # создание ключа для шага
                        test_step = {
                            "type": step["method"],
                            "endpoint": step["endpoint"],
                            "schema" if step["method"] == "POST" else "arguments": step.get("parameters", {}),
                            "errCode": step["expected"]["errCode"],
                            "httpCode": step["expected"]["httpCode"]
                        }

                        # Добавляем validation только если метод не POST и validation есть в исходном сценарии
                        if step["method"] != "POST" and "validation" in step: # если метод не POST и validation есть в исходном сценарии
                            test_step["validation"] = step["validation"] # добавление validation в тест

                        test[test_key][step_key] = test_step # добавление теста в тест

        # Обработка AFTER-TEST (только если есть в исходном сценарии)
        for endpoint, data in scenario.items():  # перебор endpoint в сценарии
            if "AFTER-TEST" in data: # если есть AFTER-TEST в текущем endpoint
                for step_id, step in data["AFTER-TEST"]["steps"].items():  # перебор step_id в AFTER-TEST
                    after_test_step = { 
                        "type": step["method"],
                        "endpoint": step["endpoint"],
                        "schema": step["parameters"],
                        "errCode": step["expected"]["errCode"],
                        "httpCode": step["expected"]["httpCode"]
                    }
                    if "AFTER-TEST" not in test: # если test не содержит AFTER-TEST
                        test["AFTER-TEST"] = {} # создание нового ключа AFTER-TEST
                    test["AFTER-TEST"][step_id] = after_test_step # добавление теста в AFTER-TEST

        return test # Возвращаем готовый тест