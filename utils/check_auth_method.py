import logging
import requests
import sys
import urllib3
import config.read_confg as cfg   


# Отключение предупреждений отсутствия сертификата для запроса
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class CheckAuthMethod:
    """Класс для проверки способа аутентификации"""

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
                url=cfg.URL + '/system/platform',
                headers=cfg.TOKEN,
                verify=False,
                timeout=10
            )

            if response.status_code == 200:
                return True
            
            else:
                logging.info("Bearer Token Authentication Error")
                return False
            
        except requests.exceptions.ConnectionError:
            logging.info(f"Connection error: URL 'u{cfg.URL}' unavailable or incorrect.")
            print(f"Connection error: URL '{cfg.TOKEN}' unavailable or incorrect.")
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
                url=cfg.URL + '/system/platform',
                auth=(cfg.USERNAME, cfg.PASSWORD),
                verify=False,
                timeout=10
            )

            if response.status_code == 200:
                return True
            
            else:
                logging.info("Basic Auth authentication error")
                return False
        except requests.exceptions.ConnectionError:
            logging.info(f"Connection error: URL '{cfg.URL}' unavailable or incorrect.")
            print(f"Connection error: URL '{cfg.URL}' unavailable or incorrect.")
            logging.info('=' * 68)
            sys.exit()        
        finally:
            # Восстанавливаем уровни логирования
            requests_logger.setLevel(original_requests_level)
            urllib3_logger.setLevel(original_urllib3_level)

    
    @staticmethod
    def save_auth_method(method):
        """Сохраняем метод аутентификации в config файл"""
        try:
            cfg.config['AUTH']['auth_method'] = method
            with open(cfg.root_to_conf_con, 'w') as configfile:
                cfg.config.write(configfile)
        except Exception as e:
            print(f"Error saving the authentication method:{e}")
    

    @staticmethod
    def get_saved_auth_method():
        """Получаем сохраненный метод аутентификации из config файла"""
        try:
            return cfg.config['AUTH'].get('auth_method', None)
        except:
            return None
    

    @staticmethod
    def reset_auth_method():
        """Сброс сохраненного метода аутентификации"""
        try:
            # Удаляем оба параметра, если они существуют
            if 'auth_method' in cfg.config['AUTH']:
                cfg.config['AUTH']['auth_method'] = ''

                
            with open(cfg.root_to_conf_con, 'w') as configfile:
                cfg.config.write(configfile)

        except Exception as e:
            print(f"Error when resetting the authentication method: {e}")


    # Проверка способа аутентификации по конфигурационному файлу(basic/bearer token)
    @staticmethod
    def check_auth_method() -> str:

        
        # Если нет url, то пишем ошибку в лог       
        if not cfg.URL:
            logging.info('Error: The authorization URL is missing in configs_auth.ini')
            print('Error: The authorization URL is missing in configs_auth.ini')

            sys.exit()

        # Если сохраненного метода нет, определяем его
        if cfg.TOKEN:

            if CheckAuthMethod.try_token():
                logging.info("Successful Bearer Token Authentication")
                logging.info('=' * 68)
                return 'token'
            
            elif cfg.USERNAME and cfg.PASSWORD and CheckAuthMethod.try_basic():
                logging.info("Successful Basic Auth authentication")
                logging.info('=' * 68)
                return 'basic'
            
            else:
                logging.info('=' * 68)
                logging.info("Authentication error!")
                print("Authentication error!")
                logging.info(f"url: {'Installed' if cfg.URL else 'Absent'}")
                logging.info(f"token: {'Installed' if cfg.TOKEN else 'Absent'}")
                logging.info(f"username: {'Installed' if cfg.USERNAME else 'Absent'}")
                logging.info(f"password: {'Installed' if cfg.PASSWORD else 'Absent'}")
                logging.info('=' * 68)
                sys.exit()

        elif cfg.USERNAME and cfg.PASSWORD:

            if CheckAuthMethod.try_basic():
                logging.info("Successful Basic Auth authentication")
                logging.info('=' * 68)
                return 'basic'
            
            elif cfg.TOKEN and CheckAuthMethod.try_token():
                logging.info("Successful Bearer Token authentication")
                logging.info('=' * 68)
                return 'token'
            
            else:
                logging.info('=' * 68)
                logging.info("Authentication error!")
                print("Authentication error!")
                logging.info(f"url: {'Installed' if cfg.URL else 'Absent'}")
                logging.info(f"token: {'Installed' if cfg.TOKEN else 'Absent'}")
                logging.info(f"username: {'Installed' if cfg.USERNAME else 'Absent'}")
                logging.info(f"password: {'Installed' if cfg.PASSWORD else 'Absent'}")
                logging.info('=' * 68)
                sys.exit()

        else:
            print("Authentication parameters are not configured")
            logging.info("Authentication parameters are not configured")
            sys.exit()