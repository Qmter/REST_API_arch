import os
import configparser
import requests
import json
import sys
import logging
import urllib3

# Отключение предупреждений отсутствия сертификата для запроса
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Http_methods:
    """Список HTTP методов"""

    @staticmethod
    def get(url, auth_method, username, password, token):
        """Универсальный метод GET"""
        

        # Отправляем запрос. Если токен, то header, а если basic, то auth
        try:

            if auth_method == 'token':
                result_get = requests.get(url=url,
                                        headers=token,
                                        verify=False
                                        )

                # Логгируем в каждый запрос полный URL+endpoint, входную схему
                logging.debug(f"Request URL")
                logging.debug(url)
                logging.debug(f"Response")
                logging.debug(json.dumps(result_get.json(),
                            indent=2, ensure_ascii=False))

                return result_get
            
            elif auth_method == 'basic':
                result_get = requests.get(url=url,
                        auth=(username, password),
                        verify=False
                        )

                # Логгируем в каждый запрос полный URL+endpoint, входную схему
                logging.debug(f"Request URL")
                logging.debug(url)
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
    def post(url, body, auth_method, username, password, token):
        """Универсальный метод POST для изменения, добавления и удаления"""
    
        # Отправляем запрос. Если токен, то header, а если basic, то auth
        try:

            if auth_method == 'token':
                result_post = requests.post(url=url,
                                            headers=token,
                                            json=body,
                                            verify=False
                                            )

                # Логгируем в каждый запрос полный URL+endpoint, входную схему и выходную схему
                logging.debug(f"Request URL")
                logging.debug(url)
                logging.debug(f"Request")
                logging.debug(json.dumps(body, indent=2, ensure_ascii=False))
                logging.debug(f"Response")
                logging.debug(json.dumps(result_post.json(),
                            indent=2, ensure_ascii=False))

                return result_post
            
            elif auth_method == 'basic':
                result_post = requests.post(url=url,
                                            auth=(username, password),
                                            json=body,
                                            verify=False
                                            )

                # Логгируем в каждый запрос полный URL+endpoint, входную схему и выходную схему
                logging.debug(f"Request URL")
                logging.debug(url)
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
    def get_show_platform(auth_method, url, token, username, password):
        """Метод для отправки запроса на /system/platform"""
        logging.info('=' * 68)

        
        # Отправляем запрос. Если токен, то header, а если basic, то auth
        try:

            if auth_method == 'token':
                response = requests.get(
                    url=url + '/system/platform',
                    headers=token,
                    verify=False,
                    timeout=10
                )
                if response.status_code == 200:
                    schema = response.json().get("result")
                    logging.debug(json.dumps(schema, indent=2, ensure_ascii=False))
                    
                else:
                    logging.debug(f'Authentication error: {response.status_code}')
                    sys.exit()

            elif auth_method == 'basic':
                response = requests.get(
                    url=url + '/system/platform',
                    auth=(username, password),
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


        except requests.exceptions.RequestException as e:
            logging.info(e)