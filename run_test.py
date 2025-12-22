import json
import sys  # Импортируем библиотеку для работы с аргументами командной строки
import os  # Импортируем библиотеку для работы с файловой системой
import argparse  # Вытягивает аргументы из командной строки
import configparser  # Для работы с конфигурационным файлом
import logging  # Запись логов
from datetime import datetime
from pathlib import Path

from config.read_confg import (
    TESTS_DIR,
    SCENARIOS_DIR,
    TEMPLATES_DIR,
    OPENAPI_PATH,
    URL,
    USERNAME,
    PASSWORD,
    TOKEN,
    DICT_ENDPOINTS,
    config,
    root_to_conf_con)

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
        # Объявление флаговой переменной
        flag = "endpoints"


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