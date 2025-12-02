import argparse
import json
import configparser
import os
from utils.parse_scenarios import ScenarioParser
from utils.resolve_scheme import ResolveScheme
from utils.generate_values import GenerateValues


config = configparser.ConfigParser()
root_to_conf_con = os.path.join(os.path.join(os.getcwd(), "config"), "config.ini")
config.read(root_to_conf_con)

SCENARIOS_DIR = config["Paths"]["scenarios_dir"]
TEMPLATES_DIR= config["Paths"]["templates_dir"]
OPENAPI_PATH = os.path.join(config["Paths"]["openapi_dir"], "openapi.json")



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    exclusive_group = parser.add_mutually_exclusive_group()
    exclusive_group.add_argument('--endpoints', '-e', nargs="*", required=False)
    parser_args = parser.parse_args()

    if parser_args.endpoints is not None:
        flag = "endpoints"



    scenario_parser = ScenarioParser(SCENARIOS_DIR, TEMPLATES_DIR, OPENAPI_PATH)

    try:
        # endpoint = parser_args.endpoints[0]
        # print(endpoint)

        # Загрузка сценария
        scenario = scenario_parser.parse_scenario("_interfaces_tunnel_multicast")
        print("=" * 50)
        print("Сценарий успешно загружен!")
        print(json.dumps(scenario, indent=2))
        print("=" * 50)


        # Извлечение всех эндпоинтов которые присутствуют в сценарии
        all_endpoints = scenario_parser.find_all_endpoints(scenario)
        print("=" * 50)
        print("Все ендпоинты, присутствующие в сценирии:")
        print(all_endpoints)
        print("=" * 50)

        # Словаь структуры {endpoint: scheme}
        dict_endpoint_scheme = {}

        # Массив со всеми паттернами ендпоинтов для теста
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



            # Получение паттернов аргументов
            arguments_patterns[f"{endpoint}"] = ResolveScheme.find_all_patterns_min_max(schema=resolved_scheme)


        print("=" * 50)
        print("Разрешены ссылки для ендпоинтов:")
        print(json.dumps(dict_endpoint_scheme, indent=2))
        print("=" * 50)

        print("=" * 50)
        print("Аргументы ендпоинта и его паттерны:")
        print("=" * 50)
        print(json.dumps(arguments_patterns, indent=2))

        print("=" * 50)
        print("=" * 50)
        print("=" * 50)

        rt = GenerateValues.read_scenario(resolved_scenario=scenario, arguments_patterns=arguments_patterns)

        print(json.dumps(rt, indent=2))


        # # Извлечение параметров сценария
        # parameters_scenario = GenerateValues.generate_values(scenario_scheme=scenario)
        # print("Параметры сценария:")
        # print(json.dumps(parameters_scenario, indent=2))


        # gen_value = GenVal.generate_values(scenario=scenario, arguments_pattern=arguments_patterns, endpoint="/interfaces/tunnel/multicast")
        # print("Сгенерированные значения")
        # print(json.dumps(gen_value, indent=2))



    except FileNotFoundError as e:
        print(e)