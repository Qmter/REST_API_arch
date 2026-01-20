from utils.http_methods import Http_methods
from utils.log import logging
from utils.validation.validator import Validator


class RunningTest:

    json_log = ''

    @staticmethod
    def read_test(test_schema, test_index=None):
        """ Функция запуска теста по схеме """

        pass_message = "PASS"
        failed_indexes = []
        failed_actions = set()

        list_steps = list(test_schema.keys())

        if test_index is None:
            for action in list_steps:

                if action == "PRESET":
                    logging.debug("PRESET-TEST")

                if action == "AFTER-TEST":
                    logging.debug("AFTER-TEST")

                if action not in ("PRESET", "AFTER-TEST"):
                    if "description" in test_schema[action]:
                        description_dynamic = test_schema[action]["description"]
                        test_schema[action].pop("description")

                        logging.debug("-" * 68)
                        logging.debug(f"TEST: {action} | {description_dynamic}")
                        logging.debug("-" * 68)
                    else:
                        logging.debug("-" * 68)
                        logging.debug(f"TEST: {action}")
                        logging.debug("-" * 68)

                try:
                    RunningTest.execute_test(test_schema[action])
                    logging.debug("")

                except (AssertionError, RuntimeError) as e:  # ← ИЗМЕНЕНО
                    logging.debug(f"An error occurred: {e}")
                    logging.debug("")

                    if action.isdigit():
                        failed_indexes.append(action)
                    else:
                        failed_actions.add(action)

                    pass_message = "FAIL"

                    if "AFTER-TEST" in list_steps:
                        try:
                            logging.debug("AFTER-TEST")
                            RunningTest.execute_test(test_schema["AFTER-TEST"])
                        except (AssertionError, RuntimeError) as e_after:  # ← ИЗМЕНЕНО
                            logging.debug(f"An error occurred: {e_after}")
                            logging.debug("")
                            failed_actions.add("AFTER-TEST")

                    if "PRESET" in list_steps:
                        try:
                            logging.debug("PRESET-TEST")
                            RunningTest.execute_test(test_schema["PRESET"])
                        except (AssertionError, RuntimeError) as e_preset:  # ← ИЗМЕНЕНО
                            logging.debug(f"An error occurred: {e_preset}")
                            logging.debug("")
                            failed_actions.add("PRESET")

        else:
            try:
                if "PRESET" in list_steps:
                    logging.debug("PRESET-TEST")
                    RunningTest.execute_test(test_schema["PRESET"])
            except (AssertionError, RuntimeError) as e:  # ← ИЗМЕНЕНО
                logging.debug(f"An error occurred: {e}")
                logging.debug("")
                failed_actions.add("PRESET")
                pass_message = "FAIL"

            try:
                logging.debug("")
                scenario_index = test_schema[str(test_index)]

                if "description" in scenario_index:
                    description_index = scenario_index["description"]
                    logging.debug("-" * 68)
                    logging.debug(f"TEST: {test_index} | {description_index}")
                    logging.debug("-" * 68)
                    scenario_index.pop("description")
                else:
                    logging.debug(f"TEST: {test_index}")

                RunningTest.execute_test(scenario_index)

            except (AssertionError, RuntimeError) as e:  # ← ИЗМЕНЕНО
                logging.debug(f"An error occurred: {e}")
                logging.debug("")
                failed_indexes.append(test_index)
                pass_message = "FAIL"

            try:
                if "AFTER-TEST" in list_steps:
                    logging.debug("AFTER-TEST")
                    RunningTest.execute_test(test_schema["AFTER-TEST"])
            except (AssertionError, RuntimeError) as e:  # ← ИЗМЕНЕНО
                logging.debug(f"An error occurred: {e}")
                logging.debug("")
                failed_actions.add("AFTER-TEST")
                pass_message = "FAIL"

        return failed_indexes + list(failed_actions), pass_message

    @staticmethod
    def execute_test(input_schema):
        """Выполнение запросов по последовательности схемы"""

        action_indexes = list(input_schema.keys())

        for index in action_indexes:
            logging.debug("-" * 68)
            logging.debug(f"step.{index}")
            logging.debug("-" * 68)

            request_type = input_schema[index]["type"]
            endpoint_value = input_schema[index]["endpoint"]
            keys_in_test = input_schema[index].keys()

            if request_type == "POST":
                request_schema = input_schema[index]["schema"]

                try:
                    post_response = Http_methods.post(
                        endpoint=endpoint_value,
                        body=request_schema
                    )
                except RuntimeError as e:
                    raise AssertionError(str(e))  # ← ИЗМЕНЕНО

                if post_response is None:
                    raise AssertionError("POST response is None")  # ← ИЗМЕНЕНО

                response_json = post_response.json()

                if "errCode" in keys_in_test:
                    errCode_test = input_schema[index]["errCode"]
                    errCode_response = response_json.get("errCode")[0]  # ← ИЗМЕНЕНО
                    if errCode_test != errCode_response:
                        raise AssertionError(
                            f"expected: {errCode_test}, response: {errCode_response}"
                        )

                if "httpCode" in keys_in_test:
                    httpCode_response = post_response.status_code
                    httpCode_test = input_schema[index]["httpCode"]
                    if httpCode_response != httpCode_test:
                        raise AssertionError(
                            f"expected: {httpCode_test}, response: {httpCode_response}"
                        )

            if request_type == "GET":
                request_arguments = input_schema[index].get("arguments")

                try:
                    get_response = Http_methods.get(
                        endpoint=endpoint_value,
                        arguments=request_arguments
                    )
                except RuntimeError as e:
                    raise AssertionError(str(e))  # ← ИЗМЕНЕНО

                if get_response is None:
                    raise AssertionError("GET response is None")  # ← ИЗМЕНЕНО

                response_json = get_response.json()

                if "errCode" in keys_in_test:
                    errCode_test = input_schema[index]["errCode"]
                    errCode_response = response_json.get("errCode")[0] # ← ИЗМЕНЕНО
                    if errCode_test != errCode_response:
                        raise AssertionError(
                            f"expected: {errCode_test}, response: {errCode_response}"
                        )

                if "httpCode" in keys_in_test:
                    httpCode_response = get_response.status_code
                    httpCode_test = input_schema[index]["httpCode"]
                    if httpCode_response != httpCode_test:
                        raise AssertionError(
                            f"expected: {httpCode_test}, response: {httpCode_response}"
                        )

                if "validation" in keys_in_test:
                    response_result = response_json.get("result", {})
                    expected_validation = input_schema[index]["validation"]

                    Validator.validate_subset(
                        actual=response_result,
                        expected=expected_validation
                    )
