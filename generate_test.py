import argparse # Импортируем модуль для обработки аргументов командной строки
import json # Импортируем модуль для работы с JSON 
import os # Импортируем модуль для работы с файлами
from datetime import datetime # Импортируем модуль для работы с датой и временем
import sys # Импортируем модуль для работы с аргументами командной строки
from pydantic import ValidationError

import config.read_confg as cfg 
 
from utils.log import logging, initialize_log, log_start_program # Импортируем класс для логирования
from utils.generate_utils.parse_scenarios import ScenarioParser # Импортируем класс для парсинга сценариев
from utils.generate_utils.resolve_scheme import ResolveScheme # Импортируем класс для разрешения схемы
from utils.generate_utils.generate_values import GenerateValues # Импортируем класс для генерации значений для аргументов сценария
from utils.generate_utils.make_test import GenerateTests # Импортируем класс для генерации тестов
from utils.generate_utils.generate_structure import StructureGenerator # Импортируем класс для генерации структуры тестов
from utils.check_auth_method import CheckAuthMethod # Импортируем класс для проверки метода авторизации
from utils.http_methods import Http_methods # Импортируем класс методов HTTP
from utils.validation.scenario_models import Scenario

HELP_TEXT = '''Показать это сообщение и выйти.

СИНТАКСИС:
  python generate_tests.py [ОПЦИИ]

ОСНОВНЫЕ ОПЦИИ:
  --verbose, -v          Включить подробный вывод (debug режим)
  --seed, -s SEED        Установить seed для генератора случайных чисел
  --logname, -ln LOG NAME    Указать имя файла лога
  --route, -r DIR        Указать целевую директорию для тестов

РЕЖИМЫ ГЕНЕРАЦИИ (взаимоисключающие):
  --endpoints, -e [ENDPOINTS...]
                        Сгенерировать тесты для указанных endpoint'ов
  --dir, -d DIR         Сгенерировать тесты для всех сценариев в указанной директории
  (без аргументов)      Сгенерировать тесты для всех сценариев

ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ:
  1. Генерация всех тестов:
     python generate_tests.py
  
  2. Генерация с подробным выводом и seed:
     python generate_tests.py -v -s 12345
  
  3. Генерация конкретных endpoint'ов:
     python generate_tests.py -e users_get users_post
  
  4. Генерация всех сценариев в директории:
     python generate_tests.py -d api/v1
  
  5. Указание своей директории для тестов:
     python generate_tests.py --route my_tests
  
  6. Создание лога с определенным именем:
     python generate_tests.py -ln my_test_run

КОНФИГУРАЦИЯ:
  Конфигурационный файл: config/read_confg.py
  Директория сценариев:  {SCENARIOS_DIR}
  Директория тестов:     {TESTS_DIR}
  OpenAPI файл:          {OPENAPI_PATH}
'''


# ASCII-символы для консольных сообщений
OK_SIMBOL = '|  OK  |'
FAIL_SIMBOL = '| FAIL |'

# Объявляем переменную для сохранения итоговых логов
LOGS_EXECUTION_LIST = []


# Обработчик ошибок при генерации теста
def handle_generation_error(correct_name_endpoint, e, endpoint_name=""):
    """
    Обрабатывает ошибки при генерации теста.
    Возвращает сообщение об ошибке для вывода.
    """
    if isinstance(e, FileNotFoundError):
        error_msg = f"{correct_name_endpoint.ljust(50, '.')}{FAIL_SIMBOL} File not found"
        logging.debug(f"Файл не найден: {e}")
        
    elif isinstance(e, json.JSONDecodeError):
        error_msg = f"{correct_name_endpoint.ljust(50, '.')}{FAIL_SIMBOL} Invalid JSON"
        logging.debug(f"Ошибка формата JSON: {e}")
        
    elif isinstance(e, KeyError):
        error_msg = f"{correct_name_endpoint.ljust(50, '.')}{FAIL_SIMBOL} Missing key"
        logging.debug(f"Отсутствует ключ: {e}")
        
    elif isinstance(e, ValueError):
        error_msg = f"{correct_name_endpoint.ljust(50, '.')}{FAIL_SIMBOL} Validation error"
        logging.debug(f"Ошибка валидации для {endpoint_name or correct_name_endpoint}: {e}")
        
    else:
        error_msg = f"{correct_name_endpoint.ljust(50, '.')}{FAIL_SIMBOL} Generator error"
        logging.debug(f"Ошибка при генерации теста для {endpoint_name or correct_name_endpoint}: {e}")
    
    return error_msg

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
        correct_name_endpoint = cfg.DICT_ENDPOINTS.get(f'{endpoint}'.replace('_', '/'), endpoint)
        
        try:
            logging.debug("=" * 68)
            logging.debug(f"Генерация теста: {correct_name_endpoint}")
            logging.debug("=" * 68)

            generate_test(endpoint_test=endpoint_processed)

            # Сообщение об успехе
            execution_message_e = f"{correct_name_endpoint.ljust(50, '.')}{OK_SIMBOL}"
            LOGS_EXECUTION_LIST.append(execution_message_e)    
            print(execution_message_e)
            
        except Exception as e:
            error_msg = handle_generation_error(correct_name_endpoint, e, endpoint)
            LOGS_EXECUTION_LIST.append(error_msg)
            print(error_msg)

    

def gen_dir_endpoints():
    target_dir = parser_args.dir[0].strip('/')
    
    # Строим путь к директории
    dir_path = os.path.join(cfg.SCENARIOS_DIR, target_dir.replace('/', os.sep))
    
    if not os.path.exists(dir_path):
        print(f"Директория не найдена: {dir_path}")
        return
    
    # Рекурсивно ищем все JSON файлы
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if file.endswith('.json') and file.startswith('_'):
                # Получаем относительный путь от SCENARIOS_DIR
                rel_path = os.path.relpath(root, cfg.SCENARIOS_DIR)
                
                # Имя файла без _ и .json
                file_base = file[:-5]  # Например: '_fail2ban_enable' -> 'fail2ban_enable'
                
                # ДЕБАГ: выводим информацию
                logging.debug("=" * 68)
                logging.debug(f"Обработка файла: {file}")
                logging.debug(f"rel_path: {rel_path}")
                logging.debug(f"file_base: {file_base}")
                logging.debug("=" * 68)


                correct_name_endpoint = cfg.DICT_ENDPOINTS.get(f'{file_base}'.replace('_', '/'), file_base.replace('_', '/'))
                
                try:
                    generate_test(endpoint_test=file_base)
                    
                    # Сообщение об успехе
                    execution_message = f"{correct_name_endpoint.ljust(50, '.')}{OK_SIMBOL}"
                    LOGS_EXECUTION_LIST.append(execution_message)
                    print(execution_message)
                    
                except Exception as e:
                    error_msg = handle_generation_error(correct_name_endpoint, e, file_base)
                    LOGS_EXECUTION_LIST.append(error_msg)
                    print(error_msg)


def gen_all_endpoints():
    # Строим путь к директории
    dir_path = os.path.join(cfg.SCENARIOS_DIR)
    
    if not os.path.exists(dir_path):
        print(f"Директория не найдена: {dir_path}")
        return
    
    # Рекурсивно ищем все JSON файлы
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if file.endswith('.json') and file.startswith('_'):
                # Получаем относительный путь от SCENARIOS_DIR
                rel_path = os.path.relpath(root, cfg.SCENARIOS_DIR)
                
                # Имя файла без _ и .json
                file_base = file[:-5]  # Например: '_fail2ban_enable' -> 'fail2ban_enable'
                
                # ДЕБАГ: выводим информацию
                logging.debug("=" * 68)
                logging.debug(f"Обработка файла: {file}")
                logging.debug(f"rel_path: {rel_path}")
                logging.debug(f"file_base: {file_base}")
                logging.debug("=" * 68)


                correct_name_endpoint = cfg.DICT_ENDPOINTS.get(f'{file_base}'.replace('_', '/'), file_base.replace('_', '/'))
                
                try:
                    generate_test(endpoint_test=file_base)
                    
                    # Сообщение об успехе
                    execution_message = f"{correct_name_endpoint.ljust(50, '.')}{OK_SIMBOL}"
                    LOGS_EXECUTION_LIST.append(execution_message)
                    print(execution_message)
                    
                except Exception as e:
                    error_msg = handle_generation_error(correct_name_endpoint, e, file_base)
                    LOGS_EXECUTION_LIST.append(error_msg)
                    print(error_msg)

def generate_test(endpoint_test):
    try:
        scenario_parser = ScenarioParser(scenarios_dir=cfg.SCENARIOS_DIR, templates_dir=cfg.TEMPLATES_DIR, openapi_file=cfg.OPENAPI_PATH)
        scenario = scenario_parser.parse_scenario(scenario_name=endpoint_test)
        
        try:
            scenario_model = Scenario.model_validate(scenario)
        except ValidationError as e:
            for err in e.errors():
                logging.debug("=" * 68)
                logging.debug(
                    "Validation error at %s: %s",
                    ".".join(map(str, err["loc"])),
                    err["msg"])
                logging.debug("=" * 68)
                raise
        
        logging.debug("=" * 68)
        logging.debug("Сценарий успешно загружен!")
        logging.debug("=" * 68)
        logging.debug(json.dumps(scenario, indent=2))
        logging.debug("=" * 68)

        
        # Извлечение всех эндпоинтов которые присутствуют в сценарии
        all_endpoints = scenario_parser.find_all_endpoints(resolved_scenario=scenario, dict_endpoints=cfg.DICT_ENDPOINTS)
        logging.debug("=" * 68)
        logging.debug(f"Все endpoint'ы, присутствующие в сценарии:")
        logging.debug("=" * 68)
        [logging.debug(f'endpoint: {key}, method: {value}') for key, value in all_endpoints.items()]
        logging.debug("=" * 68)

        # Словарь структуры {endpoint: scheme}
        dict_endpoint_scheme = {}

        # Массив со всеми паттернами endpoint'ов для теста. Пример {"endpoint": {patterns}}
        arguments_patterns = {}

        # Проходимся по всем endpoint'ам, разрешаем схему и собираем паттерны
        for endpoint, method in all_endpoints.items():
            # Разрешение схемы endpoint'а сценария
            resolved_scheme = ResolveScheme.resolve_endpoint(openapi_file=cfg.OPENAPI_PATH, endpoint_path=endpoint, method=method)
            logging.debug("=" * 68)
            logging.debug(f"Разрешенная схема для {endpoint} {method}:")
            logging.debug("=" * 68)
            logging.debug(json.dumps(resolved_scheme, indent=2))
            dict_endpoint_scheme[f"{endpoint}"] = resolved_scheme
            logging.debug("=" * 68)

            # Получение паттернов аргументов
            arguments_patterns[f"{endpoint}"] = ResolveScheme.find_all_patterns_min_max(schema=resolved_scheme)

        logging.debug("=" * 68)
        logging.debug("Аргументы endpoint'а и его паттерны:")
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
        scenario_path = scenario_parser.find_scenario_by_name(scenarios_dir=cfg.SCENARIOS_DIR, target_name=endpoint_test)
        logging.debug("=" * 68)
        logging.debug("=" * 68)
        logging.debug(f"Путь до сценария: {scenario_path}")
        logging.debug("=" * 68)

        StructureGenerator.generate(base_dir=TESTS_DIR, openapi_path=cfg.OPENAPI_PATH)

        logging.debug("=" * 68)
        logging.debug("Сгенерированный тест:")
        logging.debug("=" * 68)
        GenerateTests.generate_test(scenario=ready_scenario, 
                                    scenario_path=scenario_path,
                                    scenario_folder=cfg.SCENARIOS_DIR,
                                    test_folder=TESTS_DIR)
        logging.debug("=" * 68)

    except ValueError as e:
        # Это ошибки валидации, пробрасываем их наверх
        logging.error(f"Ошибка валидации для {endpoint_test}: {e}")
        raise
    except Exception as e:
        logging.error(f"Критическая ошибка при генерации теста {endpoint_test}: {e}")
        raise





if __name__ == "__main__": 
    parser = argparse.ArgumentParser(
        description='Генератор тестов на основе OpenAPI спецификации и сценариев',
        formatter_class=argparse.RawTextHelpFormatter,
        add_help=False
    )

    parser.add_argument(
        '--help', '-h',
        action='help',
        default=argparse.SUPPRESS,
        help=HELP_TEXT.format(
            SCENARIOS_DIR=cfg.SCENARIOS_DIR,
            TESTS_DIR=cfg.TESTS_DIR,
            OPENAPI_PATH=cfg.OPENAPI_PATH
        )
    )

    # Объявление допустимого аргумента [--verbose, -v]
    parser.add_argument('--verbose', '-v', action='store_true')

    # Объявление допустимого аргумента [--seed, -s]
    parser.add_argument('--seed', '-s', required=False)

    # Объявление допустимого аргумента [--logname, -ln]
    parser.add_argument('--logname', '-ln', required=False)

    # Объявление допустимого аргумента [--route, -r]
    parser.add_argument('--route', '-r', required=False)

    # Создаем группу аргументов, которые должны быть выбраны одновременно
    exclusive_group = parser.add_mutually_exclusive_group()

    # Добавляем аргументы в взаимно исключающую группу
    exclusive_group.add_argument("--dir", "-d", nargs="+", required=False, 
                                action=SingleValueAction)
    
    exclusive_group.add_argument('--endpoints', '-e', nargs="*", required=False)

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
        else:
            print("Не указаны endpoint\'ы для генерации тестов")
            sys.exit()

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
            log_file_name = f"log_{flag}_{parser_args.dir[0].replace('/', '_')}_{current_log_time.replace(' ', '__')}"
        if flag == 'endpoints': # Если запускаем сценарий, то задаем имя лога равное "log_endpoints"
            log_file_name = f"log_endpoints_{current_log_time.replace(' ', '__')}"

    try:
        # Если указана целевая папка для тестов, то генерируем структуру и сохраняем целевую папку во внутреннем конфиге
        if parser_args.route is not None:
            if os.sep in parser_args.route or '/' in parser_args.route:
                print("The folder name cannot be a path. Try not to use characters like '/' or '\\'.")
                sys.exit()
            
            TESTS_DIR = parser_args.route
            StructureGenerator.change_test_folder(TESTS_DIR)
        else:
            TESTS_DIR = 'tests'
            # Дефолтная директория
            StructureGenerator.change_test_folder()

        # Инициализация логирования и места записи логов
        initialize_log(verbose=verbose_arg, file_root=log_file_name)

        # Логгируем заголовок файла-лога
        log_start_program(seed=seed,
                          flag=flag,
                          launch_command=" ".join(sys.argv),
                          current_log_time=current_log_time)

        CheckAuthMethod.reset_auth_method()
        # Проверяем, есть ли сохраненный метод аутентификации
        saved_method = CheckAuthMethod.get_saved_auth_method()
        if saved_method:
            cfg.AUTH_METHOD = saved_method                    # 
        else:
            cfg.AUTH_METHOD = CheckAuthMethod.check_auth_method()  # 
            CheckAuthMethod.save_auth_method(method=cfg.AUTH_METHOD)  # 

        
        # Вызываем get_show_platform для запроса к /system/platform
        try:
            Http_methods.get_show_platform()
        except RuntimeError as e:
            print("ERROR: API is not reachable")          # 
            print(f"Reason: {e}")                           # 
            print("\nTests were not started.\n")            # 
            sys.exit(1)                                     # 



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
        logging.debug("Отчистка пустых папок:")
        logging.debug("=" * 68)
        StructureGenerator.cleanup_empty_test_dirs(TESTS_DIR) # Очищаем пустые папки
        logging.debug("=" * 68)
        logging.debug('\n')
        
        # Логируем суммарный отчет исполнения генераторов
        if len(LOGS_EXECUTION_LIST) > 0:
            logging.info("=" * 68)
            logging.info("Result:")
            logging.info("=" * 68)
            for log in LOGS_EXECUTION_LIST:
                logging.info(log)
            logging.info("=" * 68)