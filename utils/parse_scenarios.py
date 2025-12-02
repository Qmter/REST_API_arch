import os
import json


class ScenarioParser:
    def __init__(self, scenarios_dir, templates_dir, openapi_file):
        """
        Инициализация парсера сценария.

        :param scenarios_dir: Путь к папке с JSON-сценариями.
        :param templates_dir: Путь к папке с шаблонами.
        :param openapi_file: Путь к файлу OpenAPI-спецификации.
        """
        self.scenarios_dir = scenarios_dir
        self.templates_dir = templates_dir
        self.openapi_file = openapi_file
        self.context = {}  # Контекст для хранения данных между шагами
        self.endpoints_in_scenario = {}

    def parse_scenario(self, scenario_name):
        """
        Парсинг JSON-сценария.

        :param scenario_name: Название файла сценария (без расширения).
        :return: Содержимое сценария в виде словаря.
        """
        # Формируем полный путь к файлу сценария
        scenario_path = os.path.join(self.scenarios_dir, f"{scenario_name}.json")

        # Проверяем существование файла
        if not os.path.exists(scenario_path):
            raise FileNotFoundError(f"Сценарий '{scenario_name}' не найден.")

        # Читаем содержимое файла
        with open(scenario_path, 'r') as f:
            scenario = json.load(f)

        # Разворачиваем шаблоны
        self._resolve_templates(scenario)

        # Обрабатываем ссылки
        # self._resolve_references(scenario)

        return scenario

    def _resolve_templates(self, node):
        """
        Рекурсивное разворачивание шаблонов с сохранением параметров.
        """
        if isinstance(node, dict):
            for key, value in list(node.items()):
                if isinstance(value, dict) and "template" in value:
                    # Загружаем шаблон
                    template_ref = value["template"]
                    resolved_template = self._load_template(template_ref)
                    print(f"Шаблон: {template_ref} успешно загружен!")  # Отладочная информация
                    
                    # Если в исходном узле есть дополнительные параметры, объединяем их
                    if "parameters" in value and "parameters" in resolved_template:
                        # Объединяем параметры (параметры из шаблона имеют приоритет)
                        resolved_template["parameters"] = {
                            **resolved_template["parameters"],
                            **value["parameters"]
                        }
                    
                    # Заменяем узел на развернутый шаблон
                    node[key] = resolved_template

                    # Рекурсивно обрабатываем развернутый шаблон
                    self._resolve_templates(node[key])
                
                else:
                    # Продолжаем обработку других узлов
                    self._resolve_templates(value)
        
        elif isinstance(node, list):
            for item in node:
                self._resolve_templates(item)



    def _load_template(self, template_ref):
        """
        Загрузка шаблона по ссылке.

        :param template_ref: Ссылка на шаблон (например, "#TEMPLATES./vrf.TESTS.ADD").
        :return: Содержимое шаблона.
        """
        parts = template_ref.split(".")[1:]  # Пропускаем "#TEMPLATES"
        template_name = parts[0]

        # Формируем путь к файлу шаблона
        template_path = os.path.join(self.templates_dir, f"{template_name.replace('/', '_')}_templates.json")

        print(f"Пытаемся загрузить шаблон из: {template_path}")  # Отладочная информация

        # Проверяем существование файла
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Шаблон '{template_name}' не найден.")

        # Читаем содержимое шаблона
        with open(template_path, 'r') as f:
            template = json.load(f)

        # Извлекаем нужную часть шаблона
        current = template
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                raise KeyError(f"Ключ '{part}' не найден в шаблоне '{template_name}'.")

        return current
    

    def find_all_endpoints(self, resolved_scenario) -> set:

        for key, value in resolved_scenario.items():
            if '/' in key:
                self.endpoints_in_scenario[f'{key}'] = {}
                self.endpoints_in_scenario[f'{key}'] = 'post'
            if key == 'endpoint':
                self.endpoints_in_scenario[f'{value}'] = {}
                self.endpoints_in_scenario[f'{value}'] = resolved_scenario['method']

            
            if isinstance(value, dict):
                self.find_all_endpoints(value)
        
        return self.endpoints_in_scenario