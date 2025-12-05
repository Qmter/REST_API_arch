import json

class GenerateTests:
    """Класс для генерации тестов"""

    @staticmethod
    def generate_test(scenatio: dict, 
                      scenario_path: str, 
                      scenario_name: str,
                      scenatio_folder: str,
                      test_folder: str):
        """Функция для генерации тестов"""
        
        test_path = scenario_path.replace(scenatio_folder, test_folder)

        json_test = GenerateTests.convert_scenario_to_test(scenatio)

        print(json.dumps(json_test, indent=2, ensure_ascii=False))



        with open(test_path, 'w') as test:
            json.dump(json_test, test, indent=2, ensure_ascii=False)




    @staticmethod
    def convert_scenario_to_test(scenario):
        """
        Преобразует сценарий в новый формат теста.

        :param scenario: Исходный сценарий (словарь).
        :return: Преобразованный тест (словарь).
        """
        test = {}

        # Обработка PRESET (только если есть в исходном сценарии)
        for endpoint, data in scenario.items():
            if "PRESET" in data:
                for preset_id, preset_step in data["PRESET"].items():
                    test_step = {
                        "type": preset_step["method"],
                        "endpoint": preset_step["endpoint"],
                        "schema": preset_step["parameters"],
                        "errCode": preset_step["expected"]["errCode"],
                        "httpCode": preset_step["expected"]["httpCode"]
                    }
                    if "PRESET" not in test:
                        test["PRESET"] = {}
                    test["PRESET"][preset_id] = test_step

        # Обработка TESTS (только если есть в исходном сценарии)
        for endpoint, data in scenario.items():
            if "TESTS" in data:
                for test_id, test_case in data["TESTS"].items():
                    test_key = str(test_id)
                    test[test_key] = {"description": test_case["description"]}

                    for step_id, step in test_case["steps"].items():
                        step_key = f"{test_id}.{step_id}"
                        test_step = {
                            "type": step["method"],
                            "endpoint": step["endpoint"],
                            "schema" if step["method"] == "POST" else "arguments": step.get("parameters", {}),
                            "errCode": step["expected"]["errCode"],
                            "httpCode": step["expected"]["httpCode"]
                        }

                        # Добавляем validation только если метод не POST и validation есть в исходном сценарии
                        if step["method"] != "POST" and "validation" in step:
                            test_step["validation"] = step["validation"]

                        test[test_key][step_key] = test_step

        # Обработка AFTER-TEST (только если есть в исходном сценарии)
        for endpoint, data in scenario.items():
            if "AFTER-TEST" in data:
                for step_id, step in data["AFTER-TEST"]["steps"].items():
                    after_test_step = {
                        "type": step["method"],
                        "endpoint": step["endpoint"],
                        "schema": step["parameters"],
                        "errCode": step["expected"]["errCode"],
                        "httpCode": step["expected"]["httpCode"]
                    }
                    if "AFTER-TEST" not in test:
                        test["AFTER-TEST"] = {}
                    test["AFTER-TEST"][step_id] = after_test_step

        return test