import argparse
import json
import configparser
import os
from datetime import datetime
import sys
import ast   # Для безопасного преобразования строки в словарь


from utils.log import logging, initialize_log
from utils.generate_tests.parse_scenarios import ScenarioParser # Импортируем класс для парсинга сценариев
from utils.generate_tests.resolve_scheme import ResolveScheme # Импортируем класс для разрешения схемы
from utils.generate_tests.generate_values import GenerateValues # Импортируем класс для генерации значений для аргументов сценария
from utils.generate_tests.make_test import GenerateTests # Импортируем класс для генерации тестов
from utils.generate_tests.generate_structure import StructureGenerator # Импортируем класс для генерации структуры тестов
from utils.check_auth_method import CheckAuthMethod
from utils.http_methods import Http_methods

config = configparser.ConfigParser() # Создаем объект для чтения конфигурационного файла
root_to_conf_con = os.path.join(os.path.join(os.getcwd(), "config"), "config.ini") # Путь к конфигурационному файлу
config.read(root_to_conf_con) # Читаем конфигурационный файл

# PATHS
TESTS_DIR= config["PATHS"]["tests_dir"] # Путь к папке с шаблонами
SCENARIOS_DIR = config["PATHS"]["scenarios_dir"] # Путь к папке с сценариями
TEMPLATES_DIR= config["PATHS"]["templates_dir"] # Путь к папке с шаблонами
OPENAPI_PATH = os.path.join(config["PATHS"]["openapi_dir"], "openapi.json") # Путь к файлу с описанием API

# AUTH
URL = config["AUTH"]["url"] # URL для авторизации
USERNAME = config["AUTH"]["username"] # Имя пользователя для авторизации
PASSWORD = config["AUTH"]["password"] # Пароль для авторизации
if config["AUTH"]["token"] == '':
    TOKEN = ''
else:
    TOKEN = {"Authorization": config["AUTH"]["token"]} # Токен для авторизации

# LOGGIND
LOG_LVL = config["LOGGING"]["log_level"]

DICT_ENDPOINTS = ast.literal_eval(config['ENDPOINTS']['endpoints_dict'])


# ASCII-символы для консольных сообщений
OK_SIMBOL = '|  OK  |'
FAIL_SIMBOL = '| FAIL |'

# Объявляем переменную для сохранения итоговых логов
LOGS_EXECUTION_LIST = []

# Обработчик некорректно переданных данных для [--dir, -d]
class SingleValueAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if len(values) != 1:
            raise argparse.ArgumentError(
                self,
                f"Допустимо указывать только 1 аргумент для '{option_string}', получено {len(values)}"
            )
        # Получаем текущий список значений (если уже есть)
        current = getattr(namespace, self.dest, [])
        if not isinstance(current, list):
            current = []
        # Добавляем новое значение
        current.append(values[0])
        setattr(namespace, self.dest, current)


def gen_endpoints(endpoints_list):
    for endpoint in endpoints_list:
        endpoint_processed = endpoint.replace("/", "_")
        correct_name_endpoint = DICT_ENDPOINTS.get(f'{endpoint}'.replace('_', '/'), endpoint)
        
        try:
            generate_test(endpoint_test=endpoint_processed)
            
            # Сообщение об успехе
            execution_message_d = f"Generated:".ljust(30, ' ') + f"{correct_name_endpoint.ljust(50, '.')}{OK_SIMBOL}"
            LOGS_EXECUTION_LIST.append(execution_message_d)    
            print(execution_message_d)

        except FileNotFoundError as e:
            # Обработка ошибки файла не найден
            error_msg = f"File not found for".ljust(30, ' ') + f"{correct_name_endpoint.ljust(50, '.')}{FAIL_SIMBOL}"
            LOGS_EXECUTION_LIST.append(error_msg)
            print(error_msg)
            logging.debug(f"Файл не найден: {e}")
            
        except Exception as e:
            # Обработка ошибки файла не найден
            error_msg = f"Generated error:".ljust(30, ' ') + f"{correct_name_endpoint.ljust(50, '.')}{FAIL_SIMBOL}"
            LOGS_EXECUTION_LIST.append(error_msg)
            print(error_msg)
            logging.debug(f"Ф{e}")

    

def gen_dir_endpoints():
    ...

def gen_all_endpoints():
    ...

def generate_test(endpoint_test):
        scenario_parser = ScenarioParser(scenarios_dir=SCENARIOS_DIR, templates_dir=TEMPLATES_DIR, openapi_file=OPENAPI_PATH) # Создаем объект для парсинга сценариев 

        # Загрузка сценария
        scenario = scenario_parser.parse_scenario(scenario_name=endpoint_test) # Парсим сценарий

        logging.debug("=" * 68)
        logging.debug("Сценарий успешно загружен!")
        logging.debug("=" * 68)
        logging.debug(json.dumps(scenario, indent=2))
        logging.debug("=" * 68)

        # Извлечение всех эндпоинтов которые присутствуют в сценарии
        all_endpoints = scenario_parser.find_all_endpoints(scenario) # Извлекаем все ендпоинты из сценария
        logging.debug("=" * 68)
        logging.debug(f"Все ендпоинты, присутствующие в сценирии:")
        logging.debug("=" * 68)
        [logging.debug(f'endpoint: {key}, method: {value}') for key, value in all_endpoints.items()]
        logging.debug("=" * 68)


        # Словаь структуры {endpoint: scheme}
        dict_endpoint_scheme = {}

        # Массив со всеми паттернами ендпоинтов для теста. Пример {"endpoint": {patterns}}
        arguments_patterns = {}

        # Проходимся по всем ендпоинтам, разрешшаем схему и собираем паттерны
        for endpoint, method in all_endpoints.items():
            # Разрешение схемы эндпоинта сценария
            resolved_scheme = ResolveScheme.resolve_endpoint(openapi_file=OPENAPI_PATH, endpoint_path=endpoint, method=method)
            logging.debug("=" * 68)
            logging.debug(f"Разрешенная схема для {endpoint} {method}:")
            logging.debug("=" * 68)
            logging.debug(json.dumps(resolved_scheme, indent=2))
            dict_endpoint_scheme[f"{endpoint}"] = resolved_scheme
            logging.debug("=" * 68)



            # Получение паттернов аргументов
            arguments_patterns[f"{endpoint}"] = ResolveScheme.find_all_patterns_min_max(schema=resolved_scheme)



        logging.debug("=" * 68)
        logging.debug("Аргументы ендпоинта и его паттерны:")
        logging.debug("=" * 68)
        logging.debug(json.dumps(arguments_patterns, indent=2))
        logging.debug("=" * 68)

        # Генерация значений для аргументов
        ready_scenario = GenerateValues.read_scenario(resolved_scenario=scenario, arguments_patterns=arguments_patterns, seed=seed)
        
        logging.debug("=" * 68)
        logging.debug("Сценарий с подставленными значениями:")
        logging.debug("=" * 68)
        logging.debug(json.dumps(ready_scenario, indent=2))
        logging.debug("=" * 68)

        # ==Генерация тестов==
        scenario_path = scenario_parser.find_scenario_by_name(scenarios_dir=SCENARIOS_DIR, target_name=endpoint_test) # Получаем путь к сценарию
        logging.debug("=" * 68)
        logging.debug("=" * 68)
        logging.debug(f"Путь до сценария: {scenario_path}")
        logging.debug("=" * 68)


        StructureGenerator.generate(base_dir=TESTS_DIR, openapi_path=OPENAPI_PATH) # Генерируем структуру тестов

        logging.debug("=" * 68)
        logging.debug("Сгенерированный тест:")
        logging.debug("=" * 68)
        GenerateTests.generate_test(scenario=ready_scenario, 
                                    scenario_path=scenario_path,
                                    scenario_folder=SCENARIOS_DIR,
                                    test_folder=TESTS_DIR) # Генерируем тесты
        logging.debug("=" * 68)





if __name__ == "__main__": 
    parser = argparse.ArgumentParser() # Создаем парсер аргументов командной строки
    exclusive_group = parser.add_mutually_exclusive_group() # Создаем группу аргументов, которые должны быть выбраны одновременно

    # Объявление допустимого аргумента [--verbose, -v]
    parser.add_argument('--verbose', '-v', action='store_true')

    # Объявление допустимого аргумента [--dir, -d]
    parser.add_argument("--dir", "-d", nargs="+", required=False, action=SingleValueAction)

    # Объявление допустимого аргумента [--seed, -s]
    parser.add_argument('--seed', '-s', required=False)

    # Объявление допустимого аргумента [--endpoints, -e]
    parser.add_argument('--endpoints', '-e', nargs="*", required=False)

    # Объявление допустимого аргумента [--route, -r]
    parser.add_argument('--route', '-r', required=False)

    # Объявление допустимого аргумента [--logname, -ln]
    parser.add_argument('--logname', '-ln', required=False)

    # Парсим аргументы командной строки
    parser_args = parser.parse_args()  

    # Объявление переменной verbose по входному аргументу --verbose
    if parser_args.verbose:
        verbose_arg = True
    else:
        verbose_arg = False

    # Объявление флаговой переменной для обозначения сценария для генераторов
    flag = ''

    # Объявление флага для запуска всех генераторов
    if parser_args.endpoints is None and parser_args.dir is None:
        flag = "all"

    # Объявление флага для запуска директории с генераторами
    if parser_args.dir is not None:
        flag = "dir"

    # Объявление флага для запуска определенных генераторов
    if parser_args.endpoints is not None:
        if len(parser_args.endpoints) > 0:
            flag = "endpoints"

    # Преобразуем seed в str, если передан
    seed = str(parser_args.seed) if parser_args.seed is not None else 0

    # Объявление переменной текущих даты и времени
    current_log_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Формируем имя файла лога
    if parser_args.logname is not None:
        if os.sep in parser_args.logname or '/' in parser_args.logname:
            print("The log name cannot be a path. Try not to use characters like '/' or '\\'.")
            sys.exit()

        log_file_name = parser_args.logname # Если указан аргумент logname, то задаем имя лога равное аргументу
    else:
        if flag == 'all': # Если запускаем все генераторы, то задаем имя лога равное "log_all"
            log_file_name = f"log_{flag}_{current_log_time.replace(' ', '__')}"
        if flag == 'dir': # Если запускаем директорию со сценариями, то задаем имя лога равное "log_dir"
            log_file_name = f"log_{flag}{parser_args.dir[0].replace('/', '_')}_{current_log_time.replace(' ', '__')}"
        if flag == 'endpoints': # Если запускаем сценарий, то задаем имя лога равное "log_endpoints"
            log_file_name = f"log_endpoints_{current_log_time.replace(' ', '__')}"

    try:
        # Если указана целевая папка для тестов, то генерируем структуру и сохраняем целевую папку во внутреннем конфиге
        if parser_args.route is not None:
            if os.sep in parser_args.route or '/' in parser_args.route:
                print("The folder name cannot be a path. Try not to use characters like '/' or '\\'.")
                sys.exit()
            
            TESTS_DIR = parser_args.route
            config["PATHS"]["tests_dir"] = parser_args.route # Записываем путь к целевой папке в конфиге
            # Перезаписываем конфигурационный файл
            with open(root_to_conf_con, 'w') as conf_file:
                config.write(conf_file)
        else:
            TESTS_DIR = 'tests'
            # Дефолтная директория
            config["PATHS"]["tests_dir"] = 'tests' # Записываем путь к целевой папке в конфиге
            # Перезаписываем конфигурационный файл
            with open(root_to_conf_con, 'w') as conf_file:
                config.write(conf_file)

        # Инициализация логирования и места записи логов
        initialize_log(verbose=verbose_arg, file_root=log_file_name)

        # Запись в лог текущих времени и даты
        logging.info(msg=f"{current_log_time}")

        # Логирование командной строки
        logging.info("Launch Command: " + " ".join(sys.argv))

        # Логирование флага
        logging.info(f"Flag: {flag}")

        # Если seed не None, то логируем его
        if seed != 0:
            logging.info(f"Using seed: {seed}")
        else:
            logging.info(f"The default seed is used: {seed}")

        # Проверяем, есть ли сохраненный метод аутентификации
        saved_method = CheckAuthMethod.get_saved_auth_method(config=config)
        if saved_method: # Если есть сохраненный метод аутентификации, то используем его
            AUTH_METHOD =  saved_method 
        else:
            # Определяем метод аутентификации (basic или token)
            AUTH_METHOD = CheckAuthMethod.check_auth_method(url=URL, username=USERNAME, password=PASSWORD, token=TOKEN)

            # Сохраняем метод аутентификации в конфиге
            CheckAuthMethod.save_auth_method(method=AUTH_METHOD, path_config=root_to_conf_con, config=config)
        
        # Вызываем get_show_platform для запроса к /system/platform
        Http_methods.get_show_platform(auth_method=AUTH_METHOD, url=URL, username=USERNAME, password=PASSWORD, token=TOKEN)

        logging.debug("=" * 68)

        # Выполнение сценария запуска всех генераторов
        if flag == "all":
            gen_all_endpoints()

        # Выполнение сценария запуска генераторов из определенной директории
        elif flag == "dir":
            gen_dir_endpoints()
        
        # Выполнение сценария запуска определенных генераторов
        elif flag == 'endpoints':
            endpoints_list = sorted(list(set(parser_args.endpoints)))
            gen_endpoints(endpoints_list=endpoints_list)


    except FileNotFoundError as e:
        StructureGenerator.cleanup_empty_test_dirs(TESTS_DIR) # Очищаем пустые папки
        print(e)
    finally:
        logging.debug("=" * 68)
        logging.debug("Отчистка пустых папок")
        logging.debug("=" * 68)
        StructureGenerator.cleanup_empty_test_dirs(TESTS_DIR) # Очищаем пустые папки
        
    
    # Логируем суммарный отчет исполнения генераторов
    logging.info("=" * 68)
    logging.info("RESULT:")
    logging.info("=" * 68)
    for i in LOGS_EXECUTION_LIST:
        logging.info(i)
    logging.info("=" * 68)