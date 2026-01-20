from os import makedirs
from pathlib import Path
import json
import os
from collections import defaultdict
import logging

import config.read_confg as cfg   

class StructureGenerator:
    """
    Класс для генерации структуры директорий на основе эндпоинтов из OpenAPI-спецификации.
    Анализирует пути из openapi.json и создаёт папки, группируя эндпоинты по общим префиксам.
    """
    
    DEFAULT_FOLDER = 'tests'
    
    @classmethod
    def change_test_folder(cls, test_folder: str = None):
        try:
            if test_folder is None:
                cfg.config["PATHS"]["tests_dir"] = cls.DEFAULT_FOLDER # Записываем путь к целевой папке в конфиге

            else:
                cfg.config["PATHS"]["tests_dir"] = test_folder # Записываем путь к целевой папке в конфиге
            
            # Перезаписываем конфигурационный файл
            with open(cfg.root_to_conf_con, 'w') as conf_file:
                cfg.config.write(conf_file)
        except Exception as e:
            print(f"Ошибка при изменении пути к папке с тестами: {e}")
            logging.debug(f"Ошибка при изменении пути к папке с тестами: {e}")
            raise e


    @staticmethod
    def cleanup_empty_test_dirs(tests_path):
        """
        Удаляет ВСЕ пустые директории внутри target_folder,
        включая промежуточные папки, которые становятся пустыми
        после удаления вложенных.
        """
        try:
            full_target_path = tests_path  # путь до папки с тестами

            if not os.path.exists(full_target_path):  # если папка не существует, то выходим
                logging.debug(f"Папка {full_target_path} не существует, очистка не требуется")
                return

            deleted = True  # флаг, что были удалены пустые директории
            iteration_count = 0
            
            while deleted and iteration_count < 100:  # Пока есть пустые директории и ограничение на итерации
                deleted = False  # Инициализируем флаг
                iteration_count += 1
                
                # Обходим снизу вверх
                for root, dirs, files in os.walk(full_target_path, topdown=False):
                    try:
                        # Пропускаем, если есть .json-файлы 
                        if any(f.endswith('.json') for f in files):
                            continue
                        # Если нет файлов и нет подпапок => папка пустая
                        if not dirs and not files:
                            try:
                                os.rmdir(root)  # Удаляем пустую директорию
                                deleted = True  # Указываем, что были удалены пустые директории
                                logging.debug(f"Удалена пустая директория: {root}")
                            except OSError as e:
                                logging.debug(f"Не удалось удалить директорию {root}: {e}")
                                continue
                    except Exception as e:
                        logging.debug(f"Ошибка при обходе директории {root}: {e}")
                        continue
                
                if iteration_count >= 100:
                    logging.debug("Достигнут лимит итераций при очистке пустых директорий")
                    
        except Exception as e:
            logging.debug(f"Критическая ошибка при очистке пустых директорий: {e}")
    

    @classmethod
    def _get_prefix_counts(cls, endpoints):
        """
        Подсчитывает, сколько раз встречается каждый префикс пути среди эндпоинтов.
        Например, для ['/api/v1/users', '/api/v1/posts'] префикс ('api', 'v1') будет иметь счётчик 2.
        Используется для определения, какие части пути являются общими и заслуживают отдельной директории.
        """
        try:
            prefix_count = defaultdict(int)  # Счётчик для каждого префикса
            for ep in endpoints:  # Для каждого эндпоинта
                try:
                    if not isinstance(ep, str):
                        logging.debug(f"Эндпоинт не является строкой: {ep}, тип: {type(ep)}")
                        continue
                        
                    parts = [p for p in ep.strip("/").split("/") if p]  # Разбиваем на части пути
                    for i in range(1, len(parts) + 1):  # Для каждого сегмента пути
                        prefix = tuple(parts[:i])  # Получаем префикс
                        prefix_count[prefix] += 1  # Увеличиваем счётчик для этого префикса
                except Exception as e:
                    logging.debug(f"Ошибка при обработке эндпоинта {ep}: {e}")
                    continue
                    
            return prefix_count
        except Exception as e:
            logging.debug(f"Ошибка при подсчете префиксов: {e}")
            return defaultdict(int)

    @classmethod
    def _determine_dirs_to_create(cls, endpoints, base_dir):
        """
        Определяет, какие директории нужно создать на основе анализа общих префиксов эндпоинтов.
        Для каждого эндпоинта находит максимальную длину префикса, который встречается как минимум у двух эндпоинтов.
        Если общих префиксов нет — создаётся директория по первому сегменту пути.
        Возвращает отсортированный список абсолютных путей к директориям, которые следует создать.
        """
        try:
            prefix_count = cls._get_prefix_counts(endpoints)  # Подсчитываем префиксы
            dirs_to_create = set()  # Инициализируем множество для хранения путей к директориям

            for ep in endpoints:  # Для каждого эндпоинта
                try:
                    if not isinstance(ep, str):
                        logging.debug(f"Эндпоинт не является строкой при определении директорий: {ep}")
                        continue
                        
                    parts = [p for p in ep.strip("/").split("/") if p]  # Разбиваем на части пути
                    if not parts:  # Если путь пустой
                        logging.debug(f"Пустой путь в эндпоинте: {ep}")
                        continue
                        
                    max_shared_len = 0  # Инициализируем максимальную длину общего префикса

                    for i in range(1, len(parts) + 1):  # Для каждого сегмента пути
                        prefix = tuple(parts[:i])  # Получаем префикс
                        if prefix in prefix_count and prefix_count[prefix] >= 2:  # Если префикс встречается у двух или более эндпоинтов
                            max_shared_len = i  # Обновляем максимальную длину общего префикса

                    if max_shared_len == 0:  # Если общих префиксов нет
                        max_shared_len = 1  # Используем первый сегмент пути

                    for i in range(1, max_shared_len + 1):  # Для каждого сегмента пути
                        try:
                            dir_path = os.path.join(base_dir, *parts[:i])  # Генерируем путь к директории
                            dirs_to_create.add(dir_path)  # Добавляем путь к директории в множество
                        except Exception as e:
                            logging.debug(f"Ошибка при формировании пути для {ep}: {e}")
                            continue
                except Exception as e:
                    logging.debug(f"Ошибка при обработке эндпоинта {ep} при определении директорий: {e}")
                    continue

            return sorted(dirs_to_create)  # Возвращаем отсортированный список путей к директориям
            
        except Exception as e:
            logging.debug(f"Ошибка при определении директорий для создания: {e}")
            return []

    @classmethod
    def generate(cls, base_dir, openapi_path):
        """
        Основной публичный метод класса.
        Генерирует структуру директорий в указанной базовой папке (base_dir),
        основываясь на эндпоинтах из openapi.json.
        Создаёт все необходимые вложенные папки, избегая ошибок, если они уже существуют.
        """
        try:
            logging.debug("=" * 68)
            logging.debug("Генерируем структуру папок")
            logging.debug("=" * 68)
            
            # Проверяем базовую директорию
            try:
                if not os.path.exists(base_dir):
                    makedirs(base_dir, exist_ok=True)
                    logging.debug(f"Создана базовая директория: {base_dir}")
            except OSError as e:
                logging.debug(f"Не удалось создать базовую директорию {base_dir}: {e}")
                raise
            
            # Проверяем существование файла OpenAPI
            if not os.path.exists(openapi_path):
                logging.debug(f"Файл OpenAPI не найден: {openapi_path}")
                raise FileNotFoundError(f"Файл OpenAPI не найден: {openapi_path}")
            
            if not os.path.isfile(openapi_path):
                logging.error(f"Указанный путь не является файлом: {openapi_path}")
                raise ValueError(f"Указанный путь не является файлом: {openapi_path}")
            
            # Читаем OpenAPI-спецификацию
            try:
                with open(openapi_path, 'r', encoding='utf-8') as f: 
                    openapi = json.load(f)
            except json.JSONDecodeError as e:
                logging.debug(f"Ошибка парсинга JSON в файле {openapi_path}: {e}")
                raise
            except UnicodeDecodeError as e:
                logging.debug(f"Ошибка декодирования файла {openapi_path}: {e}")
                raise
            except Exception as e:
                logging.debug(f"Ошибка чтения файла {openapi_path}: {e}")
                raise
            
            # Извлекаем все пути (эндпоинты) из OpenAPI-спецификации
            try:
                all_endpoints = list(openapi.get('paths', {}).keys())
                if not all_endpoints:
                    logging.debug(f"В файле {openapi_path} не найдены эндпоинты (paths)")
                    return
            except Exception as e:
                logging.debug(f"Ошибка при извлечении эндпоинтов из OpenAPI: {e}")
                raise
            
            # Получаем список путей, которые нужно создать
            dirs_to_create = cls._determine_dirs_to_create(
                endpoints=all_endpoints,
                base_dir=base_dir
            )
            
            if not dirs_to_create:
                logging.debug("Нет директорий для создания")
                return

            # Фактически создаём каждую директорию
            created_count = 0
            for dir_path in dirs_to_create:
                try:
                    makedirs(dir_path, exist_ok=True)  # Создаём директорию, если она не существует
                    created_count += 1
                    logging.debug(f"Создана директория: {dir_path}")
                except OSError as e:
                    logging.debug(f"Не удалось создать директорию {dir_path}: {e}")
                    continue
                except Exception as e:
                    logging.debug(f"Неизвестная ошибка при создании директории {dir_path}: {e}")
                    continue
            
            logging.debug(f"Всего создано {created_count} директорий из {len(dirs_to_create)} запланированных")
            
        except FileNotFoundError as e:
            logging.debug(f"Ошибка: {e}")
            raise
        except json.JSONDecodeError as e:
            logging.debug(f"Ошибка формата JSON: {e}")
            raise
        except Exception as e:
            logging.debug(f"Критическая ошибка при генерации структуры: {e}")
            raise