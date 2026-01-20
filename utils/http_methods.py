import requests
import json
import sys
import logging
import urllib3

import config.read_confg as cfg   

# Отключение предупреждений отсутствия сертификата для запроса
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Http_methods:
    """Список HTTP методов"""

    @staticmethod
    def get(endpoint, **kwargs):
        """Универсальный метод GET"""
        
        request_url = cfg.URL[:-1] + f"{endpoint}"

        if "arguments" not in kwargs:
            kwargs["arguments"] = None

        if kwargs["arguments"] is not None:
            arguments = kwargs["arguments"]
            request_url += "?"

            for key, value in arguments.items():
                request_url += str(key) + "=" + str(value) + "&"

            url_arg = request_url[:-1]
        else:
            url_arg = request_url  # ← ИЗМЕНЕНО: url_arg гарантирован

        try:
            if cfg.AUTH_METHOD == 'token':
                result_get = requests.get(
                    url=url_arg,
                    headers=cfg.TOKEN,
                    verify=False
                )

            elif cfg.AUTH_METHOD == 'basic':
                result_get = requests.get(
                    url=url_arg,
                    auth=(cfg.USERNAME, cfg.PASSWORD),
                    verify=False
                )

            else:
                raise RuntimeError(
                    f"Incorrect authentication method: {cfg.AUTH_METHOD}"
                )  # ← ИЗМЕНЕНО

            # ← ИЗМЕНЕНО: логируем ТОЛЬКО если JSON валиден
            logging.debug("")
            logging.debug('-' * len(f"Request URL: {url_arg}"))
            logging.debug(f"Request URL: {url_arg}")
            logging.debug('-' * len(f"Request URL: {url_arg}"))
            logging.debug("")

            logging.debug("-" * len("Response"))
            logging.debug("Response")
            logging.debug("-" * len("Response"))

            try:
                logging.debug(json.dumps(
                    result_get.json(),
                    indent=2,
                    ensure_ascii=False
                ))
            except Exception:
                logging.debug("Response is not JSON")  # ← ИЗМЕНЕНО

            logging.debug("")

            return result_get

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"GET request failed: {e}")  # ← ИЗМЕНЕНО

    @staticmethod
    def post(body=None, endpoint=None):
        """Универсальный метод POST для изменения, добавления и удаления"""

        if endpoint is not None:
            url_arg = cfg.URL[:-1] + endpoint
        else:
            url_arg = cfg.URL[:-1]

        if body is None:
            body = {}

        try:
            if cfg.AUTH_METHOD == 'token':
                result_post = requests.post(
                    url=url_arg,
                    headers=cfg.TOKEN,
                    json=body,
                    verify=False
                )

            elif cfg.AUTH_METHOD == 'basic':
                result_post = requests.post(
                    url=url_arg,
                    auth=(cfg.USERNAME, cfg.PASSWORD),
                    json=body,
                    verify=False
                )

            else:
                raise RuntimeError(
                    f"Incorrect authentication method: {cfg.AUTH_METHOD}"
                )  # ← ИЗМЕНЕНО

            logging.debug("")
            logging.debug('-' * len(f"Request URL: {url_arg}"))
            logging.debug(f"Request URL: {url_arg}")
            logging.debug('-' * len(f"Request URL: {url_arg}"))

            logging.debug("")
            logging.debug("-" * len("Request"))
            logging.debug("Request")
            logging.debug("-" * len("Request"))
            logging.debug(json.dumps(body, indent=2, ensure_ascii=False))

            logging.debug("")
            logging.debug("-" * len("Response"))
            logging.debug("Response")
            logging.debug("-" * len("Response"))

            try:
                logging.debug(json.dumps(
                    result_post.json(),
                    indent=2,
                    ensure_ascii=False
                ))
            except Exception:
                logging.debug("Response is not JSON")  # ← ИЗМЕНЕНО

            logging.debug("")

            return result_post

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"POST request failed: {e}")  # ← ИЗМЕНЕНО

    @staticmethod
    def get_show_platform():
        """Метод для отправки запроса на /system/platform"""
        logging.info('=' * 68)

        try:
            if cfg.AUTH_METHOD == 'token':
                response = requests.get(
                    url=cfg.URL + '/system/platform',
                    headers=cfg.TOKEN,
                    verify=False,
                    timeout=10
                )

            elif cfg.AUTH_METHOD == 'basic':
                response = requests.get(
                    url=cfg.URL + '/system/platform',
                    auth=(cfg.USERNAME, cfg.PASSWORD),
                    verify=False,
                    timeout=10
                )

            else:
                raise RuntimeError(
                    f"Incorrect authentication method: {cfg.AUTH_METHOD}"
                )  # ← ИЗМЕНЕНО

            if response.status_code != 200:
                raise RuntimeError(
                    f"Authentication error: {response.status_code}"
                )  # ← ИЗМЕНЕНО

            try:
                schema = response.json().get("result")
                logging.debug(json.dumps(
                    schema,
                    indent=2,
                    ensure_ascii=False
                ))
            except Exception:
                logging.debug("Platform response is not JSON")  # ← ИЗМЕНЕНО

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Platform request failed: {e}")  # ← ИЗМЕНЕНО
        finally:
            logging.debug("=" * 68)
