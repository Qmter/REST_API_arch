import requests
import json
import sys
import logging
import urllib3

from config.read_confg import (
    URL,
    USERNAME,
    PASSWORD,
    TOKEN,
    AUTH_METHOD)

# Отключение предупреждений отсутствия сертификата для запроса
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Http_methods:
    """Список HTTP методов"""

    @staticmethod
    def get(endpoint, **kwargs):
        """Универсальный метод GET"""
        
        request_url = URL[:-1] + f"{endpoint}"

        # Объявление arguments = None, при отсутствии аргумента
        if "arguments" not in kwargs:
            kwargs["arguments"] = None

        # Строение ссылки запроса при наличии arguments
        if kwargs["arguments"] is not None:
            arguments = kwargs["arguments"]
            request_url += "?"

            for key, value in arguments.items():
                request_url += str(key) + "=" + str(value) + "&"

            url_arg = request_url[:-1]

        # Отправляем запрос. Если токен, то header, а если basic, то auth
        try:

            if AUTH_METHOD == 'token':
                result_get = requests.get(url=url_arg,
                                        headers=TOKEN,
                                        verify=False
                                        )

                # Логгируем в каждый запрос полный URL+endpoint, входную схему
                logging.debug(f"")
                logging.debug('-' * len(f"Request URL: {url_arg}"))
                logging.debug(f"Request URL: {url_arg}")
                logging.debug('-' * len(f"Request URL: {url_arg}"))
                logging.debug(f"")
                logging.debug("-" * len("Response"))
                logging.debug(f"Response")
                logging.debug("-" * len("Response"))
                logging.debug(json.dumps(result_get.json(),
                            indent=2, ensure_ascii=False))
                logging.debug(f"")

                return result_get
            
            elif AUTH_METHOD == 'basic':
                result_get = requests.get(url=url_arg,
                        auth=(USERNAME, PASSWORD),
                        verify=False
                        )

                # Логгируем в каждый запрос полный URL+endpoint, входную схему
                logging.debug(f"")
                logging.debug('-' * len(f"Request URL: {url_arg}"))
                logging.debug(f"Request URL: {url_arg}")
                logging.debug('-' * len(f"Request URL: {url_arg}"))
                logging.debug(f"")

                logging.debug("-" * len("Response"))
                logging.debug(f"Response")
                logging.debug("-" * len("Response"))
                logging.debug(json.dumps(result_get.json(),
                            indent=2, ensure_ascii=False))
                logging.debug(f"")

                return result_get
            
            else:
                print("Incorrect authentication!")
                logging.info("Incorrect authentication!")

        except requests.exceptions.RequestException as e:
            logging.info(e)
        
    @staticmethod
    def post(body = None, endpoint = None):
        """Универсальный метод POST для изменения, добавления и удаления"""

        if endpoint is not None:
            url_arg = URL[:-1] + endpoint
        else:
            url_arg = URL[:-1]
        
        if body is None:
            body = {}
    
        # Отправляем запрос. Если токен, то header, а если basic, то auth
        try:

            if AUTH_METHOD == 'token':
                result_post = requests.post(url=url_arg,
                                            headers=TOKEN,
                                            json=body,
                                            verify=False
                                            )

                # Логгируем в каждый запрос полный URL+endpoint, входную схему и выходную схему
                logging.debug(f"")
                logging.debug('-' * len(f"Request URL: {url_arg}"))
                logging.debug(f"Request URL: {url_arg}")
                logging.debug('-' * len(f"Request URL: {url_arg}"))

                logging.debug(f"")

                logging.debug("-" * len("Request"))
                logging.debug(f"Request")
                logging.debug("-" * len("Request"))
                logging.debug(json.dumps(body, indent=2, ensure_ascii=False))

                logging.debug(f"")

                logging.debug("-" * len("Response"))
                logging.debug(f"Response")
                logging.debug("-" * len("Response"))
                logging.debug(json.dumps(result_post.json(),
                            indent=2, ensure_ascii=False))
                logging.debug(f"")

                return result_post
            
            elif AUTH_METHOD == 'basic':
                result_post = requests.post(url=url_arg,
                                            auth=(USERNAME, PASSWORD),
                                            json=body,
                                            verify=False
                                            )

                # Логгируем в каждый запрос полный URL+endpoint, входную схему и выходную схему
                logging.debug(f"")
                logging.debug('-' * len(f"Request URL: {url_arg}"))
                logging.debug(f"Request URL: {url_arg}")
                logging.debug('-' * len(f"Request URL: {url_arg}"))

                logging.debug(f"")

                logging.debug("-" * len("Request"))
                logging.debug(f"Request")
                logging.debug("-" * len("Request"))
                logging.debug(json.dumps(body, indent=2, ensure_ascii=False))
                
                logging.debug(f"")
                
                logging.debug("-" * len("Response"))
                logging.debug(f"Response")
                logging.debug("-" * len("Response"))
                logging.debug(json.dumps(result_post.json(),
                            indent=2, ensure_ascii=False))
                logging.debug(f"")

                return result_post
            
            else:
                print("Incorrect authentication!")
                logging.info("Incorrect authentication!")
                

        except requests.exceptions.RequestException as e:
            logging.info(e)
    
    @staticmethod
    def get_show_platform():
        """Метод для отправки запроса на /system/platform"""
        logging.info('=' * 68)

        
        # Отправляем запрос. Если токен, то header, а если basic, то auth
        try:

            if AUTH_METHOD == 'token':
                response = requests.get(
                    url=URL + '/system/platform',
                    headers=TOKEN,
                    verify=False,
                    timeout=10
                )
                if response.status_code == 200:
                    schema = response.json().get("result")
                    logging.debug(json.dumps(schema, indent=2, ensure_ascii=False))
                    
                else:
                    logging.debug(f'Authentication error: {response.status_code}')
                    sys.exit()

            elif AUTH_METHOD == 'basic':
                response = requests.get(
                    url=URL + '/system/platform',
                    auth=(USERNAME, PASSWORD),
                    verify=False,
                    timeout=10
                )
                if response.status_code == 200:
                    schema = response.json().get("result")
                    logging.debug(json.dumps(schema, indent=2, ensure_ascii=False))

                else:
                    logging.debug(f'Authentication error: {response.status_code}')
                    sys.exit()

            else:
                print("Incorrect authentication!")
                logging.info("Incorrect authentication!")
                sys.exit()


        except requests.exceptions.RequestException as e:
            logging.info(e)
            sys.exit()
        finally:
            logging.debug("=" * 68)
