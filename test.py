from jsonpath_ng import parse
import json

# Загрузка данных
with open('_interfaces_tunnel_multicast.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Найти все блоки parameters
jsonpath_expr = parse('$..parameters')
matches = jsonpath_expr.find(data)

# Найти все ifname в parameters
jsonpath_expr = parse('$..parameters')
ifname_matches = jsonpath_expr.find(data)

for match in matches:
    print(f"Путь: {match.full_path}")
    print(f"Значение: {match.value}")
    print("-" * 40)