import json
import logging
from jsonpath_ng import parse

class SchemaValidator:
    """Класс для валидации JSON-схем сценариев"""
    
    @staticmethod
    def validate_scenario_structure(scenario, scenario_name=""):
        """
        Валидирует базовую структуру сценария.
        Проверяет обязательные поля и корректность структуры.
        """
        errors = []
        
        if not isinstance(scenario, dict):
            errors.append(f"Сценарий должен быть словарем, получен {type(scenario)}")
            return errors
        
        # Проверяем верхнеуровневые ключи
        for endpoint_key, endpoint_data in scenario.items():
            if not isinstance(endpoint_key, str):
                errors.append(f"Ключ endpoint должен быть строкой, получен {type(endpoint_key)}")
                continue
            
            if not endpoint_key.startswith('/'):
                errors.append(f"Endpoint должен начинаться с '/': {endpoint_key}")
            
            if not isinstance(endpoint_data, dict):
                errors.append(f"Данные endpoint '{endpoint_key}' должны быть словарем")
                continue
            
            # Проверяем наличие основных секций
            valid_sections = ['PRESET', 'TESTS', 'AFTER-TEST']
            for section in valid_sections:
                if section in endpoint_data:
                    section_data = endpoint_data[section]
                    if not isinstance(section_data, dict):
                        errors.append(f"Секция '{section}' в '{endpoint_key}' должна быть словарем")
        
        return errors
    
    @staticmethod
    def find_all_steps(scenario):
        """
        Находит все шаги в сценарии.
        Возвращает список кортежей (путь, данные_шага).
        """
        steps = []
        
        try:
            jsonpath_expr = parse('$..*')
            all_matches = jsonpath_expr.find(scenario)
            
            for match in all_matches:
                if isinstance(match.value, dict):
                    if 'endpoint' in match.value:
                        steps.append((match.full_path, match.value))
        except Exception as e:
            logging.debug(f"Ошибка при поиске шагов: {e}")
        
        return steps
    
    @staticmethod
    def validate_step(step_data, step_path="", endpoint_patterns=None):
        """
        Валидирует отдельный шаг сценария.
        
        Args:
            step_data: Данные шага
            step_path: Путь к шагу (для сообщений об ошибках)
            endpoint_patterns: Словарь паттернов endpoint'ов {endpoint: patterns}
        """
        errors = []
        
        if not isinstance(step_data, dict):
            errors.append(f"Шаг должен быть словарем")
            return errors
        
        # Проверяем обязательные поля
        if 'endpoint' not in step_data:
            errors.append("Отсутствует обязательное поле 'endpoint'")
        else:
            endpoint = step_data['endpoint']
            if not isinstance(endpoint, str):
                errors.append(f"Поле 'endpoint' должно быть строкой, получен {type(endpoint)}")
            elif not endpoint.startswith('/'):
                errors.append(f"Endpoint должен начинаться с '/': {endpoint}")
            
            # Если есть паттерны, проверяем что endpoint существует
            if endpoint_patterns and endpoint not in endpoint_patterns:
                errors.append(f"Endpoint '{endpoint}' не найден в паттернах OpenAPI")
        
        if 'method' not in step_data:
            errors.append("Отсутствует обязательное поле 'method'")
        else:
            method = step_data['method'].upper()
            valid_methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS']
            if method not in valid_methods:
                errors.append(f"Некорректный HTTP метод: {method}. Допустимые: {valid_methods}")
        
        # Проверяем parameters
        if 'parameters' in step_data:
            params = step_data['parameters']
            if not isinstance(params, dict):
                errors.append(f"Поле 'parameters' должно быть словарем, получен {type(params)}")
            else:
                # Проверяем только базовую структуру ref, но не их существование
                for param_name, param_value in params.items():
                    if isinstance(param_value, dict) and 'ref' in param_value:
                        ref_value = param_value['ref']
                        if not isinstance(ref_value, str):
                            errors.append(f"Параметр '{param_name}': ref должен быть строкой")
                        elif not ref_value.startswith('#'):
                            errors.append(f"Параметр '{param_name}': ref должен начинаться с '#'")
        
        # Проверяем validation
        if 'validation' in step_data:
            validation = step_data['validation']
            if not isinstance(validation, dict):
                errors.append(f"Поле 'validation' должно быть словарем, получен {type(validation)}")
            else:
                # Проверяем только базовую структуру ref
                for key, value in validation.items():
                    if isinstance(value, dict) and 'ref' in value:
                        ref_value = value['ref']
                        if not isinstance(ref_value, str):
                            errors.append(f"Validation '{key}': ref должен быть строкой")
                        elif not ref_value.startswith('#'):
                            errors.append(f"Validation '{key}': ref должен начинаться с '#'")
        
        # Проверяем expected
        if 'expected' in step_data:
            expected = step_data['expected']
            if not isinstance(expected, dict):
                errors.append(f"Поле 'expected' должно быть словарем, получен {type(expected)}")
            else:
                if 'errCode' not in expected:
                    errors.append("Поле 'expected' должно содержать 'errCode'")
                elif not isinstance(expected['errCode'], (int, float)):
                    errors.append(f"'errCode' должен быть числом, получен {type(expected['errCode'])}")
                
                if 'httpCode' not in expected:
                    errors.append("Поле 'expected' должно содержать 'httpCode'")
                elif not isinstance(expected['httpCode'], int):
                    errors.append(f"'httpCode' должен быть целым числом, получен {type(expected['httpCode'])}")
                
                # Проверяем корректность HTTP кодов
                valid_http_codes = [200, 201, 204, 400, 401, 403, 404, 405, 500]
                if expected.get('httpCode') not in valid_http_codes:
                    errors.append(f"Некорректный HTTP код: {expected.get('httpCode')}. Допустимые: {valid_http_codes}")
        
        # Особые проверки для POST методов
        method = step_data.get('method', '').upper()
        if method == 'POST':
            # POST методы должны иметь parameters (хотя бы пустой словарь)
            if 'parameters' not in step_data:
                errors.append("POST методы должны содержать поле 'parameters'")
            elif not step_data['parameters']:
                errors.append("POST методы не должны иметь пустые 'parameters'")
        
        return errors
    
    @staticmethod
    def validate_scenario_complete(scenario, endpoint_patterns=None):
        """
        Полная валидация сценария БЕЗ проверки существования ref ссылок.
        Проверяет только структуру и синтаксис.
        
        Args:
            scenario: Сценарий для валидации
            endpoint_patterns: Словарь паттернов endpoint'ов {endpoint: patterns}
            
        Returns:
            tuple: (is_valid, errors_list)
        """
        errors = []
        
        # 1. Валидация структуры
        structure_errors = SchemaValidator.validate_scenario_structure(scenario)
        errors.extend(structure_errors)
        
        # 2. Находим и валидируем все шаги
        steps = SchemaValidator.find_all_steps(scenario)
        for step_path, step_data in steps:
            step_errors = SchemaValidator.validate_step(
                step_data, 
                str(step_path), 
                endpoint_patterns
            )
            if step_errors:
                errors.extend([f"{step_path}: {err}" for err in step_errors])
        
        # 3. Проверяем уникальность идентификаторов тестов
        test_id_errors = SchemaValidator._validate_test_ids(scenario)
        errors.extend(test_id_errors)
        
        return len(errors) == 0, errors
    
    @staticmethod
    def _validate_test_ids(scenario):
        """Проверяет уникальность идентификаторов тестов."""
        errors = []
        test_ids = set()
        
        try:
            for endpoint_key, endpoint_data in scenario.items():
                if isinstance(endpoint_data, dict) and 'TESTS' in endpoint_data:
                    tests = endpoint_data['TESTS']
                    if isinstance(tests, dict):
                        for test_id in tests.keys():
                            if test_id in test_ids:
                                errors.append(f"Дублирующийся ID теста: '{test_id}'")
                            test_ids.add(test_id)
        
        except Exception as e:
            logging.debug(f"Ошибка при проверке ID тестов: {e}")
        
        return errors
    
    @staticmethod
    def validate_openapi_compatibility(scenario, openapi_patterns):
        """
        Проверяет совместимость сценария с OpenAPI спецификацией.
        
        Args:
            scenario: Сценарий
            openapi_patterns: Словарь паттернов из OpenAPI {endpoint: {param: pattern}}
            
        Returns:
            tuple: (is_valid, errors_list)
        """
        errors = []
        
        steps = SchemaValidator.find_all_steps(scenario)
        for step_path, step_data in steps:
            endpoint = step_data.get('endpoint')
            method = step_data.get('method', 'post').lower()
            
            if not endpoint or endpoint not in openapi_patterns:
                continue
            
            # Для POST методов: проверяем что есть параметры
            if method == 'post':
                parameters = step_data.get('parameters', {})
                if not parameters:
                    # POST без параметров - проверяем по OpenAPI, есть ли обязательные параметры
                    endpoint_patterns = openapi_patterns.get(endpoint, {})
                    if endpoint_patterns:
                        # Если в OpenAPI есть паттерны для этого endpoint, значит ожидаются параметры
                        errors.append(f"{step_path}: POST метод '{endpoint}' не имеет параметров, но OpenAPI ожидает параметры")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_resolved_scenario(scenario_with_values):
        """
        Валидирует сценарий ПОСЛЕ генерации значений.
        Проверяет, что все ref ссылки разрешились.
        
        Args:
            scenario_with_values: Сценарий с подставленными значениями
            
        Returns:
            tuple: (is_valid, errors_list)
        """
        errors = []
        
        try:
            # Ищем неразрешенные ref ссылки
            jsonpath_expr = parse('$..ref')
            ref_matches = jsonpath_expr.find(scenario_with_values)
            
            for match in ref_matches:
                ref_value = match.value
                # Если после генерации значений остались ref ссылки - это ошибка
                if isinstance(ref_value, dict) and 'ref' in ref_value:
                    errors.append(f"Неразрешенная ссылка: {ref_value['ref']}")
                elif isinstance(ref_value, str) and ref_value.startswith('#'):
                    errors.append(f"Неразрешенная ссылка: {ref_value}")
        
        except Exception as e:
            logging.debug(f"Ошибка при валидации разрешенных ссылок: {e}")
            errors.append(f"Ошибка при валидации разрешенных ссылок: {e}")
        
        return len(errors) == 0, errors