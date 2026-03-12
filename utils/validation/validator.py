class Validator:

    @staticmethod
    def validate_subset(actual, expected, path: str = ""):
        """
        Проверяет, что expected является подмножеством actual.
        """
        # Cловарь
        if isinstance(expected, dict):
            if not isinstance(actual, dict):
                raise AssertionError(
                    f"Type mismatch at {path or '<root>'}: expected dict, got {type(actual)}"
                )

            for key, expected_value in expected.items():
                current_path = f"{path}.{key}" if path else key

                if key not in actual:
                    raise AssertionError(f"Missing key in response: {current_path}")

                actual_value = actual[key]
                Validator.validate_subset(actual_value, expected_value, current_path)

            return

        # Cписок
        if isinstance(expected, list):
            if not isinstance(actual, list):
                raise AssertionError(
                    f"Type mismatch at {path or '<root>'}: expected list, got {type(actual)}"
                )

            for idx, expected_item in enumerate(expected):
                current_path = f"{path}[{idx}]" if path else f"[{idx}]"
                match_found = False

                for actual_item in actual:
                    try:
                        Validator.validate_subset(actual_item, expected_item, current_path)
                        match_found = True
                        break
                    except AssertionError:
                        continue

                if not match_found:
                    raise AssertionError(f"Missing list item at {current_path}: {expected_item}")

            return

        # Примитивные значения
        if actual != expected:
            raise AssertionError(
                f"Value mismatch at {path or '<root>'}: expected {expected}, got {actual}"
            )
