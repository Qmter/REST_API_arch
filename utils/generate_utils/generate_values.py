import rstr
import re
from jsonpath_ng import parse
import random
import logging

from config.read_confg import (
    NO_USE_SWITCHPORT,
    NO_USE_VLAN,
    NO_USE_ETH,
    NO_USE_VLAN_ID
)

# Список интерфейсов которые нельзя использовать
NO_USE_LIST = [NO_USE_VLAN_ID, NO_USE_ETH, NO_USE_SWITCHPORT, NO_USE_VLAN]


class GenerateValues:
    """Класс для генерации значений для аргументов сценария."""

    arguments_pattern = {}
    context = {}

    @staticmethod
    def read_scenario(resolved_scenario: dict, arguments_patterns: dict, seed: int):
        random.seed(seed)
        GenerateValues.context = {}
        GenerateValues.arguments_pattern = arguments_patterns

        jsonpath_expr = parse('$..*')
        all_matches = jsonpath_expr.find(resolved_scenario)

        step_objects = []
        for match in all_matches:
            if isinstance(match.value, dict):
                if 'endpoint' in match.value and (
                    'parameters' in match.value or 'validation' in match.value
                ):
                    step_objects.append(match)

        for match in step_objects:
            obj = match.value
            path = match.full_path
            endpoint = obj['endpoint']

            if 'parameters' in obj:
                GenerateValues.process_fields(
                    resolved_scenario,
                    obj['parameters'],
                    path,
                    "parameters",
                    endpoint
                )

            if 'validation' in obj:
                GenerateValues.process_fields(
                    resolved_scenario,
                    obj['validation'],
                    path,
                    "validation",
                    endpoint
                )

        return resolved_scenario

    @staticmethod
    def process_fields(resolved_scenario, fields, path, field_type, endpoint):
        for key, value in fields.items():
            try:
                path_for_func = str(path) + f".{field_type}.{key}"
                current_path = (
                    "#" + '.'.join(str(path).split('.')[1:]) +
                    f".{field_type}.{key}"
                )

                # ================= RANDOM =================
                if value == 'random':
                    patterns_info = GenerateValues.arguments_pattern.get(endpoint, {}).get(key, {})
                    arg_value = None

                    if "pattern" in patterns_info:
                        patterns = patterns_info["pattern"]
                        if isinstance(patterns, str):
                            patterns = [patterns]

                        selected_pattern = random.choice(patterns)
                        while True:
                            arg_value = rstr.xeger(selected_pattern)
                            if arg_value not in NO_USE_LIST:
                                break

                    elif "minimum" in patterns_info and "maximum" in patterns_info:
                        arg_min = patterns_info["minimum"]
                        arg_max = patterns_info["maximum"]
                        while True:
                            arg_value = random.randint(arg_min, arg_max)
                            if arg_value not in NO_USE_LIST:
                                break

                    if arg_value is not None:
                        GenerateValues.setup_values(
                            resolved_scenario, path_for_func, arg_value
                        )
                        GenerateValues.context[current_path] = arg_value
                        logging.debug(f"key={key}, arg_value={arg_value}")

                # ================= MIN / MAX =================
                elif value == 'minimum':
                    arg_value = GenerateValues.arguments_pattern[endpoint][key]["minimum"]
                    GenerateValues.setup_values(resolved_scenario, path_for_func, arg_value)
                    GenerateValues.context[current_path] = arg_value

                elif value == 'maximum':
                    arg_value = GenerateValues.arguments_pattern[endpoint][key]["maximum"]
                    GenerateValues.setup_values(resolved_scenario, path_for_func, arg_value)
                    GenerateValues.context[current_path] = arg_value

                elif value == 'gt_max':
                    arg_value = GenerateValues.arguments_pattern[endpoint][key]["maximum"] + 1
                    GenerateValues.setup_values(resolved_scenario, path_for_func, arg_value)
                    GenerateValues.context[current_path] = arg_value

                elif value == 'lt_min':
                    arg_value = GenerateValues.arguments_pattern[endpoint][key]["minimum"] - 1
                    GenerateValues.setup_values(resolved_scenario, path_for_func, arg_value)
                    GenerateValues.context[current_path] = arg_value

                # ================= MODIFY =================
                elif isinstance(value, dict) and "modify" in value:
                    modify = value.get("modify")

                    try:
                        # Получаем паттерны из OpenAPI
                        patterns = (
                            GenerateValues.arguments_pattern
                            .get(endpoint, {})
                            .get(key, {})
                            .get("pattern", [])
                        )

                        # Нормализация
                        if isinstance(patterns, str):
                            patterns = [patterns]

                        if not patterns:
                            raise ValueError("No patterns available")

                        # ================= APPLY MODIFY =================

                        # --- индекс anyOf ---
                        if isinstance(modify, int):
                            if modify < 0 or modify >= len(patterns):
                                raise ValueError(f"modify index out of range: {modify}")
                            selected_patterns = [patterns[modify]]

                        # --- IPv4 ---
                        elif modify == "ipv4":
                            selected_patterns = [
                                p for p in patterns
                                if "25[0-5]" in p or "2[0-4][0-9]" in p or "1[0-9][0-9]" in p
                            ]

                        # --- IFNAME ---
                        elif modify == "ifname":
                            selected_patterns = [
                                p for p in patterns
                                if "eth" in p or "vlan" in p or "tun" in p or "lo" in p
                            ]

                        # --- кастомный regex ---
                        elif modify == "regex":
                            if "regex" not in value:
                                raise ValueError("modify=regex requires 'regex' field")
                            selected_patterns = [value["regex"]]

                        # --- неизвестный modify ---
                        else:
                            raise ValueError(f"Unknown modify type: {modify}")

                        if not selected_patterns:
                            raise ValueError(f"No patterns matched for modify={modify}")

                        # ================= GENERATE VALUE =================
                        selected_pattern = random.choice(selected_patterns)

                        while True:
                            arg_value = rstr.xeger(selected_pattern)
                            if arg_value not in NO_USE_LIST:
                                break

                        GenerateValues.setup_values(
                            resolved_scenario,
                            path_for_func,
                            arg_value
                        )
                        GenerateValues.context[current_path] = arg_value

                        logging.debug(
                            f"key={key}, modify={modify}, "
                            f"pattern={selected_pattern}, value={arg_value}"
                        )

                    except Exception as e:
                        # ================= FALLBACK =================
                        logging.debug(
                            f"modify failed, fallback to random: "
                            f"endpoint={endpoint}, key={key}, modify={modify}, error={e}"
                        )

                        if patterns:
                            selected_pattern = random.choice(patterns)
                            arg_value = rstr.xeger(selected_pattern)

                            GenerateValues.setup_values(
                                resolved_scenario,
                                path_for_func,
                                arg_value
                            )
                            GenerateValues.context[current_path] = arg_value

                        continue


                # ================= REF =================
                elif isinstance(value, dict) and "ref" in value:
                    ref_path = value["ref"]
                    arg_value = GenerateValues.context[ref_path]

                    GenerateValues.setup_values(
                        resolved_scenario, path_for_func, arg_value
                    )
                    GenerateValues.context[current_path] = arg_value
                    logging.debug(f"ref_link={arg_value}")

                # ================= CONST =================
                else:
                    GenerateValues.context[current_path] = value
                    logging.debug(f"key={key}, arg_value={value}")

            except Exception as e:
                logging.debug(f"Ошибка обработки поля {key}: {e}")
                continue

    @staticmethod
    def setup_values(scenario_scheme, path_to_arg, value):
        parts = path_to_arg.split('.')

        def _set(obj, parts_left):
            if len(parts_left) == 1:
                obj[parts_left[0]] = value
                return
            if parts_left[0] not in obj:
                obj[parts_left[0]] = {}
            _set(obj[parts_left[0]], parts_left[1:])

        _set(scenario_scheme, parts)
        return scenario_scheme
