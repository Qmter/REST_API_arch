import sys  # Импортируем библиотеку для работы с аргументами командной строки
import os  # Импортируем библиотеку для работы с файловой системой
import argparse  # Вытягивает аргументы из командной строки
from datetime import datetime
import json 

from utils.log import logging, initialize_log, log_start_program
from utils.http_methods import Http_methods
from utils.generate_utils.generate_structure import StructureGenerator
from utils.running_test import RunningTest
from utils.check_auth_method import CheckAuthMethod

import config.read_confg as cfg   


def run_single_test(test_path: str, endpoint_name: str, index_tests: int = None) -> str:
    with open(test_path) as f:
        data = json.load(f)

    logging.debug("=" * 57)
    logging.info(f"Starting the test: {endpoint_name}")
    logging.debug("=" * 57)

    if index_tests is None:
        failed_indexes, test_status = RunningTest.read_test(data)
    else:
        failed_indexes, test_status = RunningTest.read_test(data, test_index=index_tests)

    result_line = (
        f"{endpoint_name.ljust(50, '.')} | {test_status} | "
        + ", ".join(map(str, failed_indexes))
    )

    print(result_line)
    return result_line

def run_tests_endpoints():
    """
    Запуск тестов для указанных endpoint'ов (-e).
    """
    results = []

    # Копия аргументов (НЕ мутируем parser_args)
    requested_endpoints = set(parser_args.endpoints)
    found_endpoints = set()

    for root, _, files in os.walk(TESTS_DIR):
        files.sort()

        for file in files:
            if not file.endswith(".json"):
                continue

            endpoint_key = file[:-5].replace("_", "/")
            endpoint_name = cfg.DICT_ENDPOINTS.get(endpoint_key, endpoint_key)

            if endpoint_name not in requested_endpoints:
                continue

            test_path = os.path.join(root, file)

            results.append(
                run_single_test(test_path, endpoint_name)
            )

            found_endpoints.add(endpoint_name)

    # Определяем, какие endpoint'ы не нашли
    not_found = requested_endpoints - found_endpoints

    if not_found:
        logging.error(
            "No tests found for endpoints: %s",
            ", ".join(sorted(not_found))
        )
        print(f"No tests found for endpoints: {', '.join(sorted(not_found))}")

    return "\n".join(results)
    

def run_tests_all():
    results = []

    for root, _, files in os.walk(TESTS_DIR):
        files.sort()

        for file in files:
            if not file.endswith(".json"):
                continue

            endpoint_key = file[:-5].replace("_", "/")
            endpoint_name = cfg.DICT_ENDPOINTS.get(endpoint_key, endpoint_key)
            test_path = os.path.join(root, file)

            results.append(
                run_single_test(test_path, endpoint_name)
            )

    return "\n".join(results)


def run_tests_dir():
    results = []

    # нормализуем путь аргумента
    target_dir = os.path.normpath(
        os.path.join(TESTS_DIR, parser_args.dir.lstrip("/"))
    )

    if not os.path.isdir(target_dir):
        print(f"The test directory was not found: {parser_args.dir}")
        sys.exit(1)

    for root, _, files in os.walk(target_dir):
        files.sort()

        for file in files:
            if not file.endswith(".json"):
                continue

            endpoint_key = file[:-5].replace("_", "/")
            endpoint_name = cfg.DICT_ENDPOINTS.get(endpoint_key, endpoint_key)
            test_path = os.path.join(root, file)

            results.append(
                run_single_test(test_path, endpoint_name)
            )

    return "\n".join(results)



def run_tests_endpoint_index():
    ...





if __name__ == '__main__':
    # Объявление переменной текущих даты и времени
    current_log_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Парсер для проверки входящих аргументов:
    # [--verbose | -v] [--test | -t] [--endpoints | -e] [--dir | -d]
    parser = argparse.ArgumentParser()

    # Создание группы для исключения одновременного использования аргументов
    exclusive_group = parser.add_mutually_exclusive_group()

    # Объявление допустимого аргумента [--verbose, -v]
    parser.add_argument('--verbose', '-v', action='store_true')

    # Объявление допустимого аргумента [--dir, -d]
    exclusive_group.add_argument('--dir', '-d', required=False)

    # Объявление допустимого аргумента [--test, -t]
    exclusive_group.add_argument('--test', '-t', nargs=2, required=False)

    # Объявление допустимого аргумента [--endpoints, -e]
    exclusive_group.add_argument('--endpoints', '-e', nargs="*", required=False)

    # Объявление допустимого аргумента [--tag]
    exclusive_group.add_argument("--tag", required=False)

    # Объявление допустимого аргумента [--route, -r]
    parser.add_argument('--route', '-r', required=False)

    # Объявление допустимого аргумента [--logname, -ln]
    parser.add_argument('--logname', '-ln', required=False)

    # Парсинг введенных аргументов
    parser_args = parser.parse_args()

    # Объявление флаговой переменной для обозначения сценария для генераторов
    flag = ''

    # Объявление имени файла с логом
    log_name = ''

    # Объявление флаговой переменной и имени лог-файла для запуска всех тестов
    if (parser_args.dir is None and
            parser_args.test is None and
            parser_args.endpoints is None and
            parser_args.tag is None):
        # Объявление флаговой переменной
        flag = "all"


    # Объявление флаговой переменной и имени лог-файла для запуска определенного теста для эндпоинта
    if parser_args.test is not None:
        # Объявление флаговой переменной
        flag = "test"
        

    # Объявление флаговой переменной для запуска тестов в определенной директории
    if parser_args.dir is not None:
        # Объявление флаговой переменной
        flag = "dir"
        

    # Объявление флаговой переменной для запуска определенных тестов
    if parser_args.endpoints is not None:
        if len(parser_args.endpoints) > 0:
            flag = "endpoints"
        else:
            print("Не указаны тестируесые endpoint'ы ")
            sys.exit()

    # Объявление флаговой переменной для запуска тестов по тегам
    if parser_args.tag is not None:
        # Объявление флаговой переменной
        flag = "tag"


    if parser_args.logname is not None:
        if os.sep in parser_args.logname or '/' in parser_args.logname:
            print("The log name cannot be a path. Try not to use characters like '/' or '\\'.")
            sys.exit()

        log_name = parser_args.logname
    else:
        if flag == 'all':
            # Объявление имени файла с логами
            log_name = f"all_tests__{current_log_time.replace(' ', '__')}"
        if flag == 'test':
            # Объявление имени файла с логами
            log_name = f"{parser_args.test[0].replace('/', '_')[1:]}_{parser_args.test[1]}__{current_log_time.replace(' ', '__').replace('-', '_')}"
        if flag == 'dir':
            # Объявление имени файла с логами
            log_name = f"{parser_args.dir.replace('/', '_')[1:]}__{current_log_time.replace(' ', '__').replace('-', '_')}"
        if flag == "endpoints":
            # Объявление имени файла с логами
            log_name = f"endpoints__{current_log_time.replace(' ', '__').replace('-', '_')}"
        if flag == "tag":
            # Объявление имени файла с логами
            log_name = f"tag__{current_log_time.replace(' ', '__').replace('-', '_')}"

    # Объявление переменной verbose по входному аргументу --verbose
    if parser_args.verbose:
        verbose_arg = True
    else:
        verbose_arg = False

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
    initialize_log(verbose=verbose_arg, file_root=log_name)

    # Логгируем заголовок файла-лога
    log_start_program(flag=flag,
                      launch_command=" ".join(sys.argv),
                      current_log_time=current_log_time)
    
    if cfg.URL == '':
        print("Error: URL is empty")
        logging.info("Error: URL is empty")
        sys.exit()

    

    CheckAuthMethod.reset_auth_method()
    # Проверяем, есть ли сохраненный метод аутентификации
    saved_method = CheckAuthMethod.get_saved_auth_method()
    if saved_method:
        cfg.AUTH_METHOD = saved_method                    # ← ИЗМЕНЕНО
    else:
        cfg.AUTH_METHOD = CheckAuthMethod.check_auth_method()  # ← ИЗМЕНЕНО
        CheckAuthMethod.save_auth_method(method=cfg.AUTH_METHOD)  # ← ИЗМЕНЕНО

    # Вызываем get_show_platform для запроса к /system/platform
    try:
        Http_methods.get_show_platform()
    except RuntimeError as e:
        print("ERROR: API is not reachable")          # ← ИЗМЕНЕНО
        print(f"Reason: {e}")                           # ← ИЗМЕНЕНО
        print("\nTests were not started.\n")            # ← ИЗМЕНЕНО
        sys.exit(1)                                     # ← ИЗМЕНЕНО


    # Создание сообщения-сводки для логов
    last_log_msg = ''

    # Запуск всех тестов по объявленному флагу в зависимости от переданных аргументов
    if flag == "all":
        # Запись результата выполнения тестов в сообщение сводку
        last_log_msg = run_tests_all()
    # Запуск определенного теста по объявленному флагу в зависимости от переданных аргументов
    if flag == "test":
        # Запись результата выполнения тестов в сообщение сводку
        ...

    # Запуск определенной директории с тестами по объявленному флагу в зависимости от переданных аргументов
    if flag == "dir":
        # Запись результата выполнения тестов в сообщение сводку
        last_log_msg = run_tests_dir()

    # Запуск определенных тестов к эндпоинтам по объявленному флагу в зависимости от переданных аргументов
    if flag == "endpoints":
        # Запись результата выполнения тестов в сообщение сводку
        last_log_msg = run_tests_endpoints()
    # Запуск определенных тестов по указанному тегу
    if flag == "tag":
        # Запись результатат выполнения тестов в сообщение сводку
        ...
        


    # Вывод в лог сообщения-сводки выполненных тестов\
    logging.info("=" * 69)
    logging.info("Result")
    logging.info("=" * 69)
    logging.info(last_log_msg)
    logging.info("=" * 69)