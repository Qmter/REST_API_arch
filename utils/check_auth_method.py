import logging
import requests
import sys
import urllib3

# Отключение предупреждений отсутствия сертификата для запроса
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class CheckAuthMethod:

    # Переменные аутентификации
    URL = ''
    USERNAME = ''
    PASSWORD = ''
    TOKEN = ''
    CONFIG = ''

    @staticmethod
    def try_token():
        logging.info('An attempt at the Bearer Token method')
        # Сохраняем уровень логирования для requests и urllib3
        requests_logger = logging.getLogger('requests')
        urllib3_logger = logging.getLogger('urllib3')
        
        original_requests_level = requests_logger.level
        original_urllib3_level = urllib3_logger.level
        
        # Отключаем логирование только для requests и urllib3
        requests_logger.setLevel(logging.CRITICAL)
        urllib3_logger.setLevel(logging.CRITICAL)
        
        try:
            
            response = requests.get(
                url=CheckAuthMethod.URL + '/system/platform',
                headers=CheckAuthMethod.TOKEN,
                verify=False,
                timeout=10
            )

            if response.status_code == 200:
                return True
            
            else:
                logging.info("Bearer Token Authentication Error")
                return False
            
        except requests.exceptions.ConnectionError:
            logging.info(f"Connection error: URL 'u{CheckAuthMethod.URL}' unavailable or incorrect.")
            print(f"Connection error: URL '{CheckAuthMethod.TOKEN}' unavailable or incorrect.")
            logging.info('=' * 68)        
            sys.exit()
        finally:
            # Восстанавливаем уровни логирования
            requests_logger.setLevel(original_requests_level)
            urllib3_logger.setLevel(original_urllib3_level)

    @staticmethod
    def try_basic():
        logging.info('An attempt at the Basic Auth method')
        # Сохраняем уровень логирования для requests и urllib3
        requests_logger = logging.getLogger('requests')
        urllib3_logger = logging.getLogger('urllib3')
        
        original_requests_level = requests_logger.level
        original_urllib3_level = urllib3_logger.level
        
        # Отключаем логирование только для requests и urllib3
        requests_logger.setLevel(logging.CRITICAL)
        urllib3_logger.setLevel(logging.CRITICAL)
        
        try:
            response = requests.get(
                url=CheckAuthMethod.URL + '/system/platform',
                auth=(CheckAuthMethod.USERNAME, CheckAuthMethod.PASSWORD),
                verify=False,
                timeout=10
            )

            if response.status_code == 200:
                return True
            
            else:
                logging.info("Basic Auth authentication error")
                return False
        except requests.exceptions.ConnectionError:
            logging.info(f"Connection error: URL '{CheckAuthMethod.URL}' unavailable or incorrect.")
            print(f"Connection error: URL '{CheckAuthMethod.URL}' unavailable or incorrect.")
            logging.info('=' * 68)
            sys.exit()        
        finally:
            # Восстанавливаем уровни логирования
            requests_logger.setLevel(original_requests_level)
            urllib3_logger.setLevel(original_urllib3_level)

    
    @staticmethod
    def save_auth_method(method, path_config, config):
        """Сохраняем метод аутентификации в config файл"""
        try:
            config['AUTH']['auth_method'] = method
            with open(path_config, 'w') as configfile:
                config.write(configfile)
        except Exception as e:
            print(f"Error saving the authentication method:{e}")
    

    @staticmethod
    def get_saved_auth_method(config):
        """Получаем сохраненный метод аутентификации из config файла"""
        try:
            return config['AUTH'].get('auth_method', None)
        except:
            return None
    

    @staticmethod
    def reset_auth_method(config, path_config):
        """Сброс сохраненного метода аутентификации"""
        try:
            # Удаляем оба параметра, если они существуют
            if 'auth_method' in config['AUTH']:
                del config['AUTH']['auth_method']

                
            with open(path_config, 'w') as configfile:
                config.write(configfile)

        except Exception as e:
            print(f"Error when resetting the authentication method: {e}")


    # Проверка способа аутентификации по конфигурационному файлу(basic/bearer token)
    @staticmethod
    def check_auth_method(url, username, password, token) -> str:

        CheckAuthMethod.URL = url
        CheckAuthMethod.USERNAME = username
        CheckAuthMethod.PASSWORD = password
        CheckAuthMethod.TOKEN = token
        
        # Если нет url, то пишем ошибку в лог       
        if not CheckAuthMethod.URL:
            logging.info('Error: The authorization URL is missing in configs_auth.ini')
            print('Error: The authorization URL is missing in configs_auth.ini')

            sys.exit()

        # Если сохраненного метода нет, определяем его
        if CheckAuthMethod.TOKEN:

            if CheckAuthMethod.try_token():
                logging.info("Successful Bearer Token Authentication")
                logging.info('=' * 68)
                return 'token'
            
            elif CheckAuthMethod.USERNAME and CheckAuthMethod.PASSWORD and CheckAuthMethod.try_basic():
                logging.info("Successful Basic Auth authentication")
                logging.info('=' * 68)
                return 'basic'
            
            else:
                logging.info('=' * 68)
                logging.info("Authentication error!")
                print("Authentication error!")
                logging.info(f"url: {'Installed' if CheckAuthMethod.URL else 'Absent'}")
                logging.info(f"token: {'Installed' if CheckAuthMethod.TOKEN else 'Absent'}")
                logging.info(f"username: {'Installed' if CheckAuthMethod.USERNAME else 'Absent'}")
                logging.info(f"password: {'Installed' if CheckAuthMethod.PASSWORD else 'Absent'}")
                logging.info('=' * 68)
                sys.exit()

        elif CheckAuthMethod.USERNAME and CheckAuthMethod.PASSWORD:

            if CheckAuthMethod.try_basic():
                logging.info("Successful Basic Auth authentication")
                logging.info('=' * 68)
                return 'basic'
            
            elif CheckAuthMethod.TOKEN and CheckAuthMethod.try_token():
                logging.info("Successful Bearer Token authentication")
                logging.info('=' * 68)
                return 'token'
            
            else:
                logging.info('=' * 68)
                logging.info("Authentication error!")
                print("Authentication error!")
                logging.info(f"url: {'Installed' if CheckAuthMethod.URL else 'Absent'}")
                logging.info(f"token: {'Installed' if CheckAuthMethod.TOKEN else 'Absent'}")
                logging.info(f"username: {'Installed' if CheckAuthMethod.USERNAME else 'Absent'}")
                logging.info(f"password: {'Installed' if CheckAuthMethod.PASSWORD else 'Absent'}")
                logging.info('=' * 68)
                sys.exit()

        else:
            print("Authentication parameters are not configured")
            logging.info("Authentication parameters are not configured")
            sys.exit()