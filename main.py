import argparse
import json
import configparser
import os

from utils.generate_tests.parse_scenarios import ScenarioParser # Импортируем класс для парсинга сценариев
from utils.generate_tests.resolve_scheme import ResolveScheme # Импортируем класс для разрешения схемы
from utils.generate_tests.generate_values import GenerateValues # Импортируем класс для генерации значений для аргументов сценария
from utils.generate_tests.generate_tests import GenerateTests # Импортируем класс для генерации тестов
from utils.generate_tests.generate_structure import StructureGenerator # Импортируем класс для генерации структуры тестов


config = configparser.ConfigParser() # Создаем объект для чтения конфигурационного файла
root_to_conf_con = os.path.join(os.path.join(os.getcwd(), "config"), "config.ini") # Путь к конфигурационному файлу
config.read(root_to_conf_con) # Читаем конфигурационный файл

TESTS_DIR= config["Paths"]["tests_dir"] # Путь к папке с шаблонами
SCENARIOS_DIR = config["Paths"]["scenarios_dir"] # Путь к папке с сценариями
TEMPLATES_DIR= config["Paths"]["templates_dir"] # Путь к папке с шаблонами
OPENAPI_PATH = os.path.join(config["Paths"]["openapi_dir"], "openapi.json") # Путь к файлу с описанием API




def gen_endpoints():
    ...

def gen_dir_endpoints():
    ...

def gen_all_endpoints():
    ...





if __name__ == "__main__": 
    parser = argparse.ArgumentParser() # Создаем парсер аргументов командной строки
    exclusive_group = parser.add_mutually_exclusive_group() # Создаем группу аргументов, которые должны быть выбраны одновременно
    exclusive_group.add_argument('--endpoints', '-e', nargs="*", required=False)  # Аргумент для выбора конкретного ендпоинта
    parser_args = parser.parse_args()  # Парсим аргументы командной строки

    if parser_args.endpoints is not None: # Если выбраны конкретные ендпоинты
        flag = "endpoints"  # Устанавливаем флаг для выбора конкретных ендпоинтов




    scenario_parser = ScenarioParser(SCENARIOS_DIR, TEMPLATES_DIR, OPENAPI_PATH) # Создаем объект для парсинга сценариев

    try:
        endpoint_arg = parser_args.endpoints[0].replace("/", "_") # Получаем первый аргумент, который указывает на конкретный ендпоинт и 
        # print(endpoint)

        # Загрузка сценария
        scenario = scenario_parser.parse_scenario(scenario_name=endpoint_arg) # Парсим сценарий

        print("=" * 50)
        print("Сценарий успешно загружен!")
        print("=" * 50)
        print(json.dumps(scenario, indent=2))
        print("=" * 50)

        # Извлечение всех эндпоинтов которые присутствуют в сценарии
        all_endpoints = scenario_parser.find_all_endpoints(scenario) # Извлекаем все ендпоинты из сценария
        print("=" * 50)
        print(f"Все ендпоинты, присутствующие в сценирии:")
        print("=" * 50)
        [print(f'endpoint: {key}, method: {value}') for key, value in all_endpoints.items()]
        print("=" * 50)


        # Словаь структуры {endpoint: scheme}
        dict_endpoint_scheme = {}

        # Массив со всеми паттернами ендпоинтов для теста. Пример {"endpoint": {patterns}}
        arguments_patterns = {}

        # Проходимся по всем ендпоинтам, разрешшаем схему и собираем паттерны
        for endpoint, method in all_endpoints.items():
            # Разрешение схемы эндпоинта сценария
            resolved_scheme = ResolveScheme.resolve_endpoint(openapi_file=OPENAPI_PATH, endpoint_path=endpoint, method=method)
            print("=" * 50)
            print(f"Разрешенная схема для {endpoint} {method}:")
            print("=" * 50)
            print(json.dumps(resolved_scheme, indent=2))
            dict_endpoint_scheme[f"{endpoint}"] = resolved_scheme
            print("=" * 50)



            # Получение паттернов аргументов
            arguments_patterns[f"{endpoint}"] = ResolveScheme.find_all_patterns_min_max(schema=resolved_scheme)



        print("=" * 50)
        print("Аргументы ендпоинта и его паттерны:")
        print("=" * 50)
        print(json.dumps(arguments_patterns, indent=2))
        print("=" * 50)

        print("=" * 50)
        print("=" * 50)
        print("=" * 50)

        # Генерация значений для аргументов
        ready_scenario = GenerateValues.read_scenario(resolved_scenario=scenario, arguments_patterns=arguments_patterns)
        
        print("=" * 50)
        print("Сценарий с подставленными значениями:")
        print("=" * 50)
        print(json.dumps(ready_scenario, indent=2))
        print("=" * 50)

        # ==Генерация тестов==
        print("=" * 50)
        print("Путь до сценария:")
        print("=" * 50)
        scenario_path = scenario_parser.find_scenario_by_name(scenarios_dir=SCENARIOS_DIR, target_name=endpoint_arg) # Получаем путь к сценарию
        print("=" * 50)


        StructureGenerator.generate(base_dir=TESTS_DIR, openapi_path=OPENAPI_PATH) # Генерируем структуру тестов

        print("=" * 50)
        print("Сгенерированный тест:")
        print("=" * 50)
        GenerateTests.generate_test(scenatio=ready_scenario, 
                                    scenario_path=scenario_path,
                                    scenatio_folder=SCENARIOS_DIR,
                                    test_folder=TESTS_DIR) # Генерируем тесты
        print("=" * 50)
        
        print("=" * 50)
        print("Отчистка пустых папок")
        print("=" * 50)
        StructureGenerator.cleanup_empty_test_dirs(TESTS_DIR) # Очищаем пустые папки


    except FileNotFoundError as e:
        print(e)