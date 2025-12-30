from utils.http_methods import Http_methods
from utils.log import logging
from utils.validation.validator import Validator


class RunningTest:

    json_log = ''

    @staticmethod
    def read_test(test_schema, test_index = None):
        """ Функция запуска теста по схеме """

        # Аргумент для лога, не изменяется при успешном прохождении теста
        pass_message = "PASS"

        # Аргумент для лога, сохраняет индексы непройденных тестов эндпоинта
        failed_indexes = []

        # Аргумент для лога, сохраняет непройденные действия (preset, after-test) тестов эндпоинта
        failed_actions = set()

        # Получение ключей схемы для запросов
        list_steps = list(test_schema.keys())

        # Запуск всех тестов схемы
        if test_index is None:
            # Перебор схемы-теста по ключам
            for action in list_steps:

                # Запись в лог сообщения о выполнении пресета при наличии
                if action == "PRESET":
                    logging.debug("PRESET-TEST")

                # Запись в лог сообщения о чистке конфига после теста при необходимости
                if action == "AFTER-TEST":
                    logging.debug(f"AFTER-TEST")

                # Запись в лог сообщения о выполнении теста
                if action != "PRESET" and action != "AFTER-TEST":
                    # При наличии указанного description к тесту
                    if "description" in test_schema[action]:
                        # Объявление переменной-description к тесту
                        description_dynamic = test_schema[action]["description"]

                        # Удаление из списка ключей description
                        test_schema[action].pop("description")
                        
                        # Логирование начала исполнения теста с description
                        logging.debug("-" * 68)
                        logging.debug(f"TEST: {action} | {description_dynamic}")
                        logging.debug("-" * 68)
                    else:
                        # Логирование начала исполнения теста без description
                        logging.debug("-" * 68)
                        logging.debug(f"TEST: {action}")
                        logging.debug("-" * 68)
                # Обработка ошибок запросов
                try:
                    # Выполнение тестов
                    RunningTest.execute_test(test_schema[action])
                    # Отступ в логах
                    logging.debug("")
                except AssertionError as e:
                    # Логирование ошибки
                    logging.debug(f"An error occurred: {e}")

                    # Отступ в логах
                    logging.debug("")

                    # Запись в переменную-список индекс непройденного теста
                    if action.isdigit():
                        failed_indexes.append(action)
                    # Запись в переменную-сет непройденного действия теста
                    else:
                        failed_actions.add(action)
                    # Объявление переменной для лога о непройденном тесте
                    pass_message = "FAIL"

                    # Исполнение чистки конфига после теста (в защищённом блоке)
                    if "AFTER-TEST" in list_steps:
                        try:
                            # Логирование сообщения о чистке конфига
                            logging.debug("AFTER-TEST")
                            # Исполнение чистки
                            RunningTest.execute_test(test_schema["AFTER-TEST"])
                        except AssertionError as e_after:
                            # Логирование ошибки очистки
                            logging.debug(f"An error occurred: {e_after}")
                            logging.debug("")
                            # Запись информации о непройденном after-test
                            failed_actions.add("AFTER-TEST")

                    # Повторная настройка окружения для следующих тестов (в защищённом блоке)
                    if "PRESET" in list_steps:
                        try:
                            # Логирование сообщения о настройке конфига
                            logging.debug("PRESET-TEST")
                            # Исполнение настройки конфига
                            RunningTest.execute_test(test_schema["PRESET"])
                        except AssertionError as e_preset:
                            # Логирование ошибки повторной подготовки окружения
                            logging.debug(f"An error occurred: {e_preset}")
                            logging.debug("")
                            failed_actions.add("PRESET")

        # Запуск конкретного теста из схемы при наличии индекса
        else:
            # Обработка ошибок запросов
            try:
                # Выполнение настройки конфига для теста
                if "PRESET" in list_steps:
                    # Логирование сообщения о настройке конфига
                    logging.debug("PRESET-TEST")

                    # Настройка конфига
                    RunningTest.execute_test(test_schema["PRESET"])
            except AssertionError as e:
                # Логирование полученной ошибки
                logging.debug(f"An error occurred: {e}")

                # Отступ в логах
                logging.debug("")

                # Запись в переменную-список информации для лога о непройденном preset
                failed_actions.add("preset")

                # Объявление переменной для лога о непройденном тесте
                pass_message = "FAIL"

            # Обработка ошибок запросов
            try:
                # Выполнение тестов
                logging.debug("")

                # Объявление переменной-сценария конкретного теста
                scenario_index = test_schema[str(test_index)]

                # При наличии description к тесту
                if "description" in scenario_index:
                    # Объявление переменной-description к тесту
                    description_index = scenario_index["description"]

                    # Логирование начала исполнения теста вместе с description
                    logging.debug("-" * 68)
                    logging.debug(f"TEST: {test_index} | {description_index}")
                    logging.debug("-" * 68)

                    # Удаления ключа description из сценария теста
                    scenario_index.pop("description")
                else:
                    # Логирование начала исполнения теста без description
                    logging.debug(f"TEST: {test_index}")
                # Исполнение сценария теста
                RunningTest.execute_test(scenario_index)
            except AssertionError as e:
                # Логирование полученной ошибки
                logging.debug(f"An error occurred: {e}")

                # Отступ в логах
                logging.debug("")

                # Запись в переменную-список индекс непройденного теста
                failed_indexes.append(test_index)

                # Объявление переменной для лога о непройденном тесте
                pass_message = "FAIL"

            # Обработка ошибок запросов
            try:
                # Выполнение запросов для удаления пресета
                if "AFTER-TEST" in list_steps:
                    # Логирование сообщения о чистке конфига
                    logging.debug("AFTER-TEST")

                    # Исполнение чистки
                    RunningTest.execute_test(test_schema["AFTER-TEST"])
            except AssertionError as e:
                # Логирование полученной ошибки
                logging.debug(f"An error occurred: {e}")

                # Отступ в логах
                logging.debug("")

                # Запись в переменную-список информации для лога о непройденном after-test
                failed_actions.add("AFTER-TEST")

                # Объявление переменной для лога о непройденном тесте
                pass_message = "FAIL"

        # Возвращение результатов теста
        return failed_indexes + list(failed_actions), pass_message


    @staticmethod
    def execute_test(input_schema):
        """Выполнение запросов по последовательности схемы"""

        # Список ключей-шагов действия теста
        action_indexes = list(input_schema.keys())

        # Перебор ключей-шагов
        for index in action_indexes:

            # Вывод в лог нумерации запросов
            logging.debug("-" * 68)
            logging.debug(f"step.{index}")
            logging.debug("-" * 68)

            # Объявление типа запроса
            request_type = input_schema[index]["type"]

            # Объявление эндпоинта запроса
            endpoint_value = input_schema[index]["endpoint"]

            # Ключи в тесте
            keys_in_test = input_schema[index].keys()

            # Выполнение POST-запроса
            if request_type == "POST":
                # Получение схемы запроса
                request_schema = input_schema[index]["schema"]

                # Отправка запроса
                post_response = Http_methods.post(endpoint=endpoint_value,
                                                        body=request_schema)


                # errCode
                if "errCode" in keys_in_test:
                    errCode_test = input_schema[index]["errCode"]
                    errCode_response = post_response.json()['errCode'][0]
                    if errCode_test != errCode_response:
                        raise AssertionError(f"expceted: {errCode_test}, response: {errCode_response}")

                # httpCode
                if "httpCode" in keys_in_test:
                    httpCode_response = post_response.status_code
                    httpCode_test = input_schema[index]["httpCode"]
                    if httpCode_response != httpCode_test:
                        raise AssertionError(f"expceted: {httpCode_test}, response: {httpCode_response}")

                

            # Выполнение GET-запроса
            if request_type == "GET":
                # Получение аргументов запроса
                if "arguments" in input_schema[index]:
                    request_arguments = input_schema[index]["arguments"]
                else:
                    request_arguments = None

                # Отправка запроса
                get_response = Http_methods.get(endpoint=endpoint_value,
                                                    arguments=request_arguments)
                
                # errCode
                if "errCode" in keys_in_test:
                    errCode_test = input_schema[index]["errCode"]
                    errCode_response = get_response.json()['errCode'][0]
                    if errCode_test != errCode_response:
                        raise AssertionError(f"expceted: {errCode_test}, response: {errCode_response}")

                # httpCode
                if "httpCode" in keys_in_test:
                    httpCode_response = get_response.status_code
                    httpCode_test = input_schema[index]["httpCode"]
                    if httpCode_response != httpCode_test:
                        raise AssertionError(f"expceted: {httpCode_test}, response: {httpCode_response}")
                
                # validation
                if "validation" in keys_in_test:
                    response_result = get_response.json().get("result", {})
                    expected_validation = input_schema[index]["validation"]

                    Validator.validate_subset(
                        actual=response_result,
                        expected=expected_validation
    )

