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
        
        full_target_path = tests_path

        if not os.path.exists(full_target_path):
            return

        deleted = True
        while deleted:
            deleted = False
            # Обходим снизу вверх
            for root, dirs, files in os.walk(full_target_path, topdown=False):
                # Пропускаем, если есть .json-файлы
                if any(f.endswith('.json') for f in files):
                    continue
                # Если нет файлов и нет подпапок => папка пустая
                if not dirs and not files:
                    try:
                        os.rmdir(root)
                        deleted = True
                    except OSError as e:
                        print(f"Couldn't delete {root}: {e}")

    @classmethod
    def _get_prefix_counts(cls, endpoints):
        """
        Подсчитывает, сколько раз встречается каждый префикс пути среди эндпоинтов.
        Например, для ['/api/v1/users', '/api/v1/posts'] префикс ('api', 'v1') будет иметь счётчик 2.
        Используется для определения, какие части пути являются общими и заслуживают отдельной директории.
        """
        prefix_count = defaultdict(int)
        for ep in endpoints:
            parts = [p for p in ep.strip("/").split("/") if p]
            for i in range(1, len(parts) + 1):
                prefix = tuple(parts[:i])
                prefix_count[prefix] += 1
        return prefix_count

    @classmethod
    def _determine_dirs_to_create(cls, endpoints, base_dir):
        """
        Определяет, какие директории нужно создать на основе анализа общих префиксов эндпоинтов.
        Для каждого эндпоинта находит максимальную длину префикса, который встречается как минимум у двух эндпоинтов.
        Если общих префиксов нет — создаётся директория по первому сегменту пути.
        Возвращает отсортированный список абсолютных путей к директориям, которые следует создать.
        """
        prefix_count = cls._get_prefix_counts(endpoints)
        dirs_to_create = set()

        for ep in endpoints:
            parts = [p for p in ep.strip("/").split("/") if p]
            max_shared_len = 0

            for i in range(1, len(parts) + 1):
                prefix = tuple(parts[:i])
                if prefix_count[prefix] >= 2:
                    max_shared_len = i

            if max_shared_len == 0:
                max_shared_len = 1

            for i in range(1, max_shared_len + 1):
                dir_path = os.path.join(base_dir, *parts[:i])
                dirs_to_create.add(dir_path)

        return sorted(dirs_to_create)

    @classmethod
    def generate(cls, base_dir, openapi_path):
        """
        Основной публичный метод класса.
        Генерирует структуру директорий в указанной базовой папке (base_dir),
        основываясь на эндпоинтах из openapi.json.
        Создаёт все необходимые вложенные папки, избегая ошибок, если они уже существуют.
        """
        print(openapi_path)
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
            makedirs(dir_path, exist_ok=True)
            print(f"Создана директория: {dir_path}")