import json

class ResolveScheme:

    @staticmethod
    def _resolve_ref(obj, components, seen=None):
        if seen is None:
            seen = set()
        
        if isinstance(obj, dict):
            if "$ref" in obj:
                ref = obj["$ref"]
                if ref.startswith("#/components/schemas/"):
                    name = ref.split("/")[-1]
                    key = f"schemas/{name}"
                    if key in seen:
                        return {"type": "object", "x-circular": True}
                    schema = components["schemas"].get(name)
                    if schema:
                        seen.add(key)
                        resolved = ResolveScheme._resolve_ref(schema, components, seen)
                        seen.discard(key)
                        return resolved
                return obj
            return {k: ResolveScheme._resolve_ref(v, components, seen) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [ResolveScheme._resolve_ref(item, components, seen) for item in obj]
        return obj
        
    @staticmethod
    def find_all_patterns_min_max(schema):
        """
        Находит ВСЕ pattern, minimum, maximum в УЖЕ РАЗРЕШЕННОЙ схеме
        """
        results = {}
        
        def _deep_search(obj, field_name=""):
            if isinstance(obj, dict):
                # Проверяем текущий объект на наличие pattern, min, max
                current_rules = {}
                if 'pattern' in obj:
                    current_rules['pattern'] = obj['pattern']
                if 'minimum' in obj:
                    current_rules['minimum'] = obj['minimum']
                if 'maximum' in obj:
                    current_rules['maximum'] = obj['maximum']
                
                # Сохраняем если нашли правила И есть имя поля
                if current_rules and field_name:
                    results[field_name] = current_rules
                
                # Рекурсивно обходим properties - сохраняем имена полей
                if 'properties' in obj:
                    for prop_name, prop_schema in obj['properties'].items():
                        _deep_search(prop_schema, prop_name)
                
                # Рекурсивно обходим остальные значения без изменения имени поля
                for key, value in obj.items():
                    if key != 'properties':  # properties уже обработали
                        _deep_search(value, field_name)
                        
            elif isinstance(obj, list):
                for item in obj:
                    _deep_search(item, field_name)
        
        # Ищем в requestBody схемы
        request_body = schema.get('requestBody', {})
        if request_body:
            content = request_body.get('content', {})
            application_json = content.get('application/json', {})
            json_schema = application_json.get('schema', {})
            _deep_search(json_schema)
        
        # Ищем в parameters (query parameters)
        parameters = schema.get('parameters', [])
        for param in parameters:
            param_schema = param.get('schema', {})
            param_name = param.get('name', '')
            if param_name:
                _deep_search(param_schema, param_name)
        
        return results
    
    
    @staticmethod
    def resolve_endpoint(openapi_file: str, endpoint_path: str, method: str = 'post'):
        with open(openapi_file, 'r') as f:
            schema = json.load(f)
        
        components = schema.get('components', {})

        endpoint = schema['paths'][endpoint_path][method.lower()]

        
        return ResolveScheme._resolve_ref(endpoint, components)