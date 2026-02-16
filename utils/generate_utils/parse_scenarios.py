import os
import json
import logging


class ScenarioParser:
    def __init__(self, scenarios_dir, templates_dir, openapi_file):
        """
        Инициализация парсера сценария.

        :param scenarios_dir: Путь к папке с JSON-сценариями.
        :param templates_dir: Путь к папке с шаблонами.
        :param openapi_file: Путь к файлу OpenAPI-спецификации.
        """
        self.scenarios_dir = scenarios_dir  # Путь к папке с JSON-сценариями
        self.templates_dir = templates_dir  # Путь к папке с шаблонами
        self.openapi_file = openapi_file  # Путь к файлу OpenAPI-спецификации
        self.context = {}  # Контекст для хранения данных между шагами
        self.endpoints_in_scenario = {}  # Словарь для хранения всех endpoint в сценарии

    def find_scenario_by_name(self, scenarios_dir, target_name):
        """
        Рекурсивно перебирает все файлы в папке scenarios и ищет сценарий по имени.
        
        :param scenarios_dir: Путь к папке со сценариями.
        :param target_name: Имя сценария (без расширения .json).
        :return: Путь к найденному файлу или None, если файл не найден.
        """
        try:
            if not os.path.exists(scenarios_dir):
                logging.debug(f"Директория со сценариями не существует: {scenarios_dir}")
                return None
            
            for root, _, files in os.walk(scenarios_dir):
                for file in files:
                    try:
                        # Проверяем, что файл имеет расширение .json
                        if file.endswith(".json"):
                            # Удаляем расширение .json для сравнения
                            file_name_without_ext = os.path.splitext(file)[0]
                            
                            # Если имя файла совпадает с целевым именем
                            if file_name_without_ext == target_name:
                                file_path = os.path.join(root, file)
                                logging.debug(f"Найден сценарий: {file_path}")
                                return file_path
                    except Exception as e:
                        logging.debug(f"Ошибка при обработке файла {file} в директории {root}: {e}")
                        continue
            
            logging.debug(f"Сценарий с именем '{target_name}' не найден.")
            return None
            
        except Exception as e:
            logging.debug(f"Ошибка при поиске сценария '{target_name}': {e}")
            return None

    def parse_scenario(self, scenario_name):
        """
        Парсинг JSON-сценария.

        :param scenario_name: Название файла сценария (без расширения).
        :return: Содержимое сценария в виде словаря.
        """
        try:
            # Формируем полный путь к файлу сценария
            scenario_path = self.find_scenario_by_name(scenarios_dir=self.scenarios_dir, target_name=scenario_name)
            
            if not scenario_path:
                raise FileNotFoundError(f"Сценарий '{scenario_name}' не найден.")

            # Проверяем существование файла
            if not os.path.exists(scenario_path):
                raise FileNotFoundError(f"Файл сценария '{scenario_path}' не найден.")
            
            # Проверяем, что это файл
            if not os.path.isfile(scenario_path):
                raise ValueError(f"Путь '{scenario_path}' не является файлом.")

            # Читаем содержимое файла
            try:
                with open(scenario_path, 'r', encoding='utf-8') as f:
                    scenario = json.load(f)
            except json.JSONDecodeError as e:
                logging.debug(f"Ошибка парсинга JSON в файле '{scenario_path}': {e}")
                raise
            except UnicodeDecodeError as e:
                logging.debug(f"Ошибка декодирования файла '{scenario_path}': {e}")
                raise
            except Exception as e:
                logging.debug(f"Ошибка чтения файла '{scenario_path}': {e}")
                raise

            # Разворачиваем шаблоны
            try:
                self._resolve_templates(scenario)
            except Exception as e:
                logging.debug(f"Ошибка при разворачивании шаблонов: {e}")
                raise

            # Обрабатываем ссылки
            # self._resolve_references(scenario)

            return scenario  # Возвращаем содержимое сценария в виде словаря
            
        except FileNotFoundError as e:
            logging.debug(f"Сценарий не найден: {e}")
            raise
        except json.JSONDecodeError as e:
            logging.debug(f"Ошибка формата JSON в сценарии: {e}")
            raise
        except Exception as e:
            logging.debug(f"Критическая ошибка при парсинге сценария '{scenario_name}': {e}")
            raise

    def _resolve_templates(self, node):
        """
        Рекурсивное разворачивание шаблонов с сохранением параметров.
        """
        try:
            if isinstance(node, dict):
                keys_to_process = list(node.keys())  # Фиксируем список ключей для обработки
                for key in keys_to_process:
                    try:
                        value = node[key]
                        if isinstance(value, dict) and "template" in value:  # Если значение - словарь и есть ключ "template"
                            # Загружаем шаблон
                            template_ref = value["template"]
                            resolved_template = self._load_template(template_ref)  # Загружаем шаблон
                            logging.debug(f"Шаблон: {template_ref} успешно загружен!")  # Отладочная информация
                            
                            # Если в исходном узле есть дополнительные параметры, объединяем их
                            if "parameters" in value and "parameters" in resolved_template:
                                try:
                                    # Объединяем параметры (параметры из шаблона имеют приоритет)
                                    resolved_template["parameters"] = {
                                        **resolved_template["parameters"],
                                        **value["parameters"]
                                    }
                                except Exception as e:
                                    logging.debug(f"Ошибка при объединении параметров шаблона {template_ref}: {e}")
                            
                            # Заменяем узел на развернутый шаблон
                            node[key] = resolved_template

                            # Рекурсивно обрабатываем развернутый шаблон
                            self._resolve_templates(node[key])
                        else:
                            # Продолжаем обработку других узлов
                            self._resolve_templates(value)
                    except Exception as e:
                        logging.debug(f"Ошибка при обработке ключа '{key}': {e}")
                        continue
            
            elif isinstance(node, list):  # Обработка списков
                for item in node:  # Обходим каждый элемент списка
                    try:
                        self._resolve_templates(item)  # Рекурсивно обрабатываем элемент списка
                    except Exception as e:
                        logging.debug(f"Ошибка при обработке элемента списка: {e}")
                        continue
                        
        except Exception as e:
            logging.debug(f"Критическая ошибка в _resolve_templates: {e}")
            raise

    def _load_template(self, template_ref):
        """
        Загрузка шаблона по ссылке.

        :param template_ref: Ссылка на шаблон (например, "#TEMPLATES./vrf.TESTS.ADD").
        :return: Содержимое шаблона.
        """
        try:
            if not template_ref.startswith("#TEMPLATES."):
                raise ValueError(f"Некорректный формат ссылки на шаблон: {template_ref}")
            
            parts = template_ref.split(".")[1:]  # Пропускаем "#TEMPLATES"
            if not parts:
                raise ValueError(f"Пустая ссылка на шаблон: {template_ref}")
            
            template_name = parts[0]  # Имя шаблона
            if not template_name:
                raise ValueError(f"Имя шаблона пустое в ссылке: {template_ref}")

            # Формируем путь к файлу шаблона
            template_path = os.path.join(self.templates_dir, f"{template_name.replace('/', '_')}_templates.json")

            # Проверяем существование файла
            if not os.path.exists(template_path):
                raise FileNotFoundError(f"Шаблон '{template_name}' не найден по пути: {template_path}")

            # Читаем содержимое шаблона
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    template = json.load(f)
            except json.JSONDecodeError as e:
                logging.debug(f"Ошибка парсинга JSON в шаблоне '{template_path}': {e}")
                raise
            except Exception as e:
                logging.debug(f"Ошибка чтения файла шаблона '{template_path}': {e}")
                raise

            # Извлекаем нужную часть шаблона
            current = template
            for part in parts:
                try:
                    if isinstance(current, dict) and part in current:
                        current = current[part]  # Переходим к следующему уровню в словаре
                    else:
                        raise KeyError(f"Ключ '{part}' не найден в шаблоне '{template_name}'.")
                except Exception as e:
                    logging.debug(f"Ошибка при доступе к ключу '{part}' в шаблоне '{template_name}': {e}")
                    raise

            return current  # Возвращаем содержимое шаблона
            
        except FileNotFoundError as e:
            logging.debug(f"Файл шаблона не найден: {e}")
            raise
        except json.JSONDecodeError as e:
            logging.debug(f"Ошибка формата JSON в шаблоне: {e}")
            raise
        except Exception as e:
            logging.debug(f"Ошибка при загрузке шаблона '{template_ref}': {e}")
            raise

    def find_all_endpoints(self, resolved_scenario, dict_endpoints) -> dict:
        try:
            def _find_endpoints_recursive(data):
                if isinstance(data, dict):
                    for key, value in data.items():

                        if key == 'endpoint' and isinstance(value, str):
                            method = data.get('method', 'post').upper()

                            # теперь endpoint хранит МНОЖЕСТВО методов
                            self.endpoints_in_scenario \
                                .setdefault(value, set()) \
                                .add(method)

                        _find_endpoints_recursive(value)

                elif isinstance(data, list):
                    for item in data:
                        _find_endpoints_recursive(item)

            self.endpoints_in_scenario = {}
            _find_endpoints_recursive(resolved_scenario)

            # ВАЛИДАЦИЯ
            validation_errors = []
            for endpoint in self.endpoints_in_scenario.keys():
                if endpoint not in dict_endpoints and \
                endpoint not in dict_endpoints.values():
                    validation_errors.append(
                        f"Endpoint '{endpoint}' не найден в словаре endpoints_dict"
                    )

            if validation_errors:
                raise ValueError(
                    "Ошибки валидации endpoints:\n" +
                    "\n".join(validation_errors[:10])
                )

            return self.endpoints_in_scenario

        except Exception as e:
            logging.debug(f"Ошибка при поиске endpoints: {e}")
            raise
