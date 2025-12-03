import json

class ResolveScheme:

    @staticmethod
    def _resolve_ref(obj, components, seen=None):
        if seen is None: # Инициализируем множество для отслеживания циклических ссылок
            seen = set() 
        
        if isinstance(obj, dict):
            if "$ref" in obj:  # Если это ссылка на другую схему
                ref = obj["$ref"] # Получаем имя схемы из ссылки
                if ref.startswith("#/components/schemas/"):  # Если это ссылка на схему
                    name = ref.split("/")[-1]  # Извлекаем имя схемы из ссылки
                    key = f"schemas/{name}"  # Создаем ключ для схемы
                    if key in seen:  # Если мы уже видели эту схему
                        return {"type": "object", "x-circular": True}  # Возвращаем объект с типом "object" и меткой "x-circular"
                    schema = components["schemas"].get(name) # Получаем схему из компонентов
                    if schema: # Если схема существует
                        seen.add(key) # Добавляем ключ в множество для отслеживания
                        resolved = ResolveScheme._resolve_ref(schema, components, seen) # Рекурсивно разрешаем схему
                        seen.discard(key) # Удаляем ключ из множества для отслеживания
                        return resolved # Возвращаем разрешенную схему
                return obj # Возвращаем исходный объект, если это не ссылка на другую схему
            return {k: ResolveScheme._resolve_ref(v, components, seen) for k, v in obj.items()} # Рекурсивно разрешаем объекты в словаре
        elif isinstance(obj, list):  # Если это список
            return [ResolveScheme._resolve_ref(item, components, seen) for item in obj]  # Рекурсивно разрешаем элементы списка
        return obj # Возвращаем исходный объект, если это не словарь или список
        
    @staticmethod
    def find_all_patterns_min_max(schema):
        """
        Находит ВСЕ pattern, minimum, maximum в УЖЕ РАЗРЕШЕННОЙ схеме.
        Если anyOf содержит несколько паттернов, возвращает их как массив.
        Если паттерн один, возвращает его как строку.
        """
        results = {} # Инициализируем словарь для хранения результатов
        
        def _deep_search(obj, field_name=""):
            if isinstance(obj, dict):
                # Проверяем текущий объект на наличие pattern, min, max
                current_rules = {} # Инициализируем словарь для хранения результатов

                # Обработка pattern
                if 'pattern' in obj: # Если есть pattern
                    current_rules.setdefault('pattern', []).append(obj['pattern']) # Добавляем pattern в словарь
                
                # Обработка minimum и maximum
                if 'minimum' in obj: # Если есть minimum
                    current_rules['minimum'] = obj['minimum']
                if 'maximum' in obj: # Если есть maximum
                    current_rules['maximum'] = obj['maximum']

                # Обработка anyOf
                if 'anyOf' in obj: # Если есть anyOf
                    patterns_from_anyof = [] # Инициализируем список для хранения паттернов из anyOf
                    for item in obj['anyOf']:  # Обходим каждый элемент в anyOf
                        if isinstance(item, dict) and 'pattern' in item:  # Если это словарь и есть pattern
                            patterns_from_anyof.append(item['pattern']) # Добавляем pattern в список
                    
                    if patterns_from_anyof: # Если есть паттерны из anyOf
                        # Если паттернов несколько, сохраняем как массив
                        if len(patterns_from_anyof) > 1:
                            current_rules['pattern'] = patterns_from_anyof
                        else:
                            # Если паттерн один, сохраняем как строку
                            current_rules['pattern'] = patterns_from_anyof[0]

                # Сохраняем если нашли правила И есть имя поля
                if current_rules and field_name:
                    results[field_name] = current_rules # Сохраняем результаты в словарь
                
                # Рекурсивно обходим properties - сохраняем имена полей
                if 'properties' in obj:
                    for prop_name, prop_schema in obj['properties'].items(): # Обходим свойства
                        _deep_search(prop_schema, prop_name) # Рекурсивно обходим свойства
                
                # Рекурсивно обходим остальные значения без изменения имени поля
                for key, value in obj.items():
                    if key not in ['properties', 'anyOf']:  # properties и anyOf уже обработали
                        _deep_search(value, field_name)  # Рекурсивно обходим остальные значения
                        
            elif isinstance(obj, list): # Если это список
                for item in obj: # Обходим элементы списка
                    _deep_search(item, field_name)  # Рекурсивно обходим элементы списка
        
        # Ищем в requestBody схемы
        request_body = schema.get('requestBody', {})
        if request_body:  # Если есть requestBody
            content = request_body.get('content', {})  # Получаем содержимое
            application_json = content.get('application/json', {})  # Получаем содержимое для application/json
            json_schema = application_json.get('schema', {})  # Получаем схему для application/json
            _deep_search(json_schema)  # Рекурсивно обходим схему для application/json
        
        # Ищем в parameters (query parameters)
        parameters = schema.get('parameters', []) # Получаем параметры
        for param in parameters:  # Обходим параметры
            param_schema = param.get('schema', {})  # Получаем схему
            param_name = param.get('name', '')  # Получаем имя параметра
            if param_name:  # Если есть имя параметра
                _deep_search(param_schema, param_name)  # Рекурсивно обходим схему параметра
        
        return results # Возвращаем словарь с результатами
    
    
    @staticmethod
    def resolve_endpoint(openapi_file: str, endpoint_path: str, method: str = 'post'):
        with open(openapi_file, 'r') as f:
            schema = json.load(f)
        
        components = schema.get('components', {}) # Получаем компоненты

        endpoint = schema['paths'][endpoint_path][method.lower()] # Получаем эндпоинт

        
        return ResolveScheme._resolve_ref(endpoint, components) # Возвращаем разрешенный endpoint