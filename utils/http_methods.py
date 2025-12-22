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
    def get():
        """Универсальный метод GET"""
        

        # Отправляем запрос. Если токен, то header, а если basic, то auth
        try:

            if AUTH_METHOD == 'token':
                result_get = requests.get(url=URL,
                                        headers=TOKEN,
                                        verify=False
                                        )

                # Логгируем в каждый запрос полный URL+endpoint, входную схему
                logging.debug(f"Request URL")
                logging.debug(URL)
                logging.debug(f"Response")
                logging.debug(json.dumps(result_get.json(),
                            indent=2, ensure_ascii=False))

                return result_get
            
            elif AUTH_METHOD == 'basic':
                result_get = requests.get(url=URL,
                        auth=(USERNAME, PASSWORD),
                        verify=False
                        )

                # Логгируем в каждый запрос полный URL+endpoint, входную схему
                logging.debug(f"Request URL")
                logging.debug(URL)
                logging.debug(f"Response")
                logging.debug(json.dumps(result_get.json(),
                            indent=2, ensure_ascii=False))

                return result_get
            
            else:
                print("Incorrect authentication!")
                logging.info("Incorrect authentication!")

        except requests.exceptions.RequestException as e:
            logging.info(e)
        
    @staticmethod
    def post(body):
        """Универсальный метод POST для изменения, добавления и удаления"""
    
        # Отправляем запрос. Если токен, то header, а если basic, то auth
        try:

            if AUTH_METHOD == 'token':
                result_post = requests.post(url=URL,
                                            headers=TOKEN,
                                            json=body,
                                            verify=False
                                            )

                # Логгируем в каждый запрос полный URL+endpoint, входную схему и выходную схему
                logging.debug(f"Request URL")
                logging.debug(URL)
                logging.debug(f"Request")
                logging.debug(json.dumps(body, indent=2, ensure_ascii=False))
                logging.debug(f"Response")
                logging.debug(json.dumps(result_post.json(),
                            indent=2, ensure_ascii=False))

                return result_post
            
            elif AUTH_METHOD == 'basic':
                result_post = requests.post(url=URL,
                                            auth=(USERNAME, PASSWORD),
                                            json=body,
                                            verify=False
                                            )

                # Логгируем в каждый запрос полный URL+endpoint, входную схему и выходную схему
                logging.debug(f"Request URL")
                logging.debug(URL)
                logging.debug(f"Request")
                logging.debug(json.dumps(body, indent=2, ensure_ascii=False))
                logging.debug(f"Response")
                logging.debug(json.dumps(result_post.json(),
                            indent=2, ensure_ascii=False))

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
