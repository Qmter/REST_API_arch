class Validator:

    @staticmethod
    def validate_subset(actual: dict, expected: dict, path: str = ""):
        """
        Проверяет, что expected является подмножеством actual.
        """
        for key, expected_value in expected.items():
            current_path = f"{path}.{key}" if path else key

            if key not in actual:
                raise AssertionError(f"Missing key in response: {current_path}")

            actual_value = actual[key]

            # Рекурсивно проверяем словари
            if isinstance(expected_value, dict):
                if not isinstance(actual_value, dict):
                    raise AssertionError(
                        f"Type mismatch at {current_path}: expected dict, got {type(actual_value)}"
                    )
                Validator.validate_subset(actual_value, expected_value, current_path)

            # Строгая проверка значений
            else:
                if actual_value != expected_value:
                    raise AssertionError(
                        f"Value mismatch at {current_path}: "
                        f"expected {expected_value}, got {actual_value}"
                    )
