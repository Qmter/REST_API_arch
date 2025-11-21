import argparse  # Вытягивает аргументы из командной строки
import json
import configparser  # Для работы с конфигурационным файлом
import os

from utils.parse_scenarios import ScenarioParser

# Переменная для чтения конфиг-файла
config = configparser.ConfigParser()
# Путь до конфига-авторизации
root_to_conf_con = os.path.join(os.path.join(os.getcwd(), "config"), "config.ini")

# Чтение конфиг-файла
config.read(root_to_conf_con)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    exclusive_group = parser.add_mutually_exclusive_group()

    # Объявление допустимого аргумента [--endpoints, -e]
    exclusive_group.add_argument('--endpoints', '-e', nargs="*", required=False)

    # Парсинг введенных аргументов
    parser_args = parser.parse_args()

    # Объявление флаговой переменной для запуска определенных тестов
    if parser_args.endpoints is not None:
        # Объявление флаговой переменной
        flag = "endpoints"

    # Инициализация парсера сценария
    scenarios_dir = config["Paths"]["scenarios_dir"]
    templates_dir = config["Paths"]["templates_dir"]
    openapi_file = os.path.join(config["Paths"]["openapi_dir"], "openapi.json")

    scenario_parser = ScenarioParser(scenarios_dir, templates_dir, openapi_file)

    # Парсинг тестового сценария
    try:
        scenario = scenario_parser.parse_scenario("interfaces_loopback_add")
        
        print("Сценарий успешно загружен:")
        print(json.dumps(scenario, indent=2))
    except FileNotFoundError as e:
        print(e)