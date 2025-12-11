from os import makedirs
from pathlib import Path
import json
import os
from collections import defaultdict


class StructureGenerator:
    """
    Класс для генерации структуры директорий на основе эндпоинтов из OpenAPI-спецификации.
    Анализирует пути из openapi.json и создаёт папки, группируя эндпоинты по общим префиксам.
    """
    
    DEFAULT_FOLDER = 'tests'
    
    @staticmethod
    def cleanup_empty_test_dirs(tests_path):
        """
        Удаляет ВСЕ пустые директории внутри target_folder,
        включая промежуточные папки, которые становятся пустыми
        после удаления вложенных.
        """
        
        full_target_path = tests_path # путь до папки с тестами

        if not os.path.exists(full_target_path): # если папка не существует, то выходим
            return

        deleted = True  # флаг, что были удалены пустые директории
        while deleted:  # Пока есть пустые директории
            deleted = False # Инициализируем флаг
            # Обходим снизу вверх
            for root, dirs, files in os.walk(full_target_path, topdown=False):
                # Пропускаем, если есть .json-файлы 
                if any(f.endswith('.json') for f in files):
                    continue
                # Если нет файлов и нет подпапок => папка пустая
                if not dirs and not files:
                    try:
                        os.rmdir(root) # Удаляем пустую директорию
                        deleted = True  # Указываем, что были удалены пустые директории
                    except OSError as e:    # Если не удалось удалить пустую директорию
                        print(f"Couldn't delete {root}: {e}")

    @classmethod
    def _get_prefix_counts(cls, endpoints):
        """
        Подсчитывает, сколько раз встречается каждый префикс пути среди эндпоинтов.
        Например, для ['/api/v1/users', '/api/v1/posts'] префикс ('api', 'v1') будет иметь счётчик 2.
        Используется для определения, какие части пути являются общими и заслуживают отдельной директории.
        """
        prefix_count = defaultdict(int)  # Счётчик для каждого префикса
        for ep in endpoints:  # Для каждого эндпоинта
            parts = [p for p in ep.strip("/").split("/") if p]  # Разбиваем на части пути
            for i in range(1, len(parts) + 1):  # Для каждого сегмента пути
                prefix = tuple(parts[:i])  # Получаем префикс
                prefix_count[prefix] += 1  # Увеличиваем счётчик для этого префикса
        return prefix_count 

    @classmethod
    def _determine_dirs_to_create(cls, endpoints, base_dir):
        """
        Определяет, какие директории нужно создать на основе анализа общих префиксов эндпоинтов.
        Для каждого эндпоинта находит максимальную длину префикса, который встречается как минимум у двух эндпоинтов.
        Если общих префиксов нет — создаётся директория по первому сегменту пути.
        Возвращает отсортированный список абсолютных путей к директориям, которые следует создать.
        """
        prefix_count = cls._get_prefix_counts(endpoints)  # Подсчитываем префиксы
        dirs_to_create = set()  # Инициализируем множество для хранения путей к директориям

        for ep in endpoints:  # Для каждого эндпоинта
            parts = [p for p in ep.strip("/").split("/") if p]  # Разбиваем на части пути
            max_shared_len = 0  # Инициализируем максимальную длину общего префикса

            for i in range(1, len(parts) + 1):  # Для каждого сегмента пути
                prefix = tuple(parts[:i])  # Получаем префикс
                if prefix_count[prefix] >= 2:  # Если префикс встречается у двух или более эндпоинтов
                    max_shared_len = i  # Обновляем максимальную длину общего префикса

            if max_shared_len == 0:  # Если общих префиксов нет
                max_shared_len = 1  # Используем первый сегмент пути

            for i in range(1, max_shared_len + 1):  # Для каждого сегмента пути
                dir_path = os.path.join(base_dir, *parts[:i])  # Генерируем путь к директории
                dirs_to_create.add(dir_path)  # Добавляем путь к директории в множество

        return sorted(dirs_to_create)  # Возвращаем отсортированный список путей к директориям

    @classmethod
    def generate(cls, base_dir, openapi_path):
        """
        Основной публичный метод класса.
        Генерирует структуру директорий в указанной базовой папке (base_dir),
        основываясь на эндпоинтах из openapi.json.
        Создаёт все необходимые вложенные папки, избегая ошибок, если они уже существуют.
        """
        print(f'openapi_path: {openapi_path}')
        # Читаем OpenAPI-спецификацию
        with open(openapi_path, 'r', encoding='utf-8') as f: 
            openapi = json.load(f)

        # Извлекаем все пути (эндпоинты) из OpenAPI-спецификации
        all_endpoints = list(openapi.get('paths', {}).keys())

        # Получаем список путей, которые нужно создать
        dirs_to_create = cls._determine_dirs_to_create(
            endpoints=all_endpoints,
            base_dir=base_dir
        )

        # Фактически создаём каждую директорию
        for dir_path in dirs_to_create:
            makedirs(dir_path, exist_ok=True)  # Создаём директорию, если она не существует
            print(f"Создана директория: {dir_path};")