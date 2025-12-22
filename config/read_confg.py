import configparser
import os
import ast

config = configparser.ConfigParser() # Создаем объект для чтения конфигурационного файла
root_to_conf_con = os.path.join(os.path.join(os.getcwd(), "config"), "config.ini") # Путь к конфигурационному файлу
config.read(root_to_conf_con) # Читаем конфигурационный файл

# PATHS
TESTS_DIR= config["PATHS"]["tests_dir"] # Путь к папке с шаблонами
SCENARIOS_DIR = config["PATHS"]["scenarios_dir"] # Путь к папке с сценариями
TEMPLATES_DIR= config["PATHS"]["templates_dir"] # Путь к папке с шаблонами
OPENAPI_PATH = os.path.join(config["PATHS"]["openapi_dir"], "openapi.json") # Путь к файлу с описанием API

# AUTH
URL = config["AUTH"]["url"] # URL для авторизации
USERNAME = config["AUTH"]["username"] # Имя пользователя для авторизации
PASSWORD = config["AUTH"]["password"] # Пароль для авторизации
if config["AUTH"]["token"] == '':
    TOKEN = ''
else:
    TOKEN = {"Authorization": config["AUTH"]["token"]} # Токен для авторизации

AUTH_METHOD = config["AUTH"]["auth_method"] # Метод для авторизации

# LOGGIND
LOG_LVL = config["LOGGING"]["log_level"]

# DICT OF ENDPOINTS
DICT_ENDPOINTS = ast.literal_eval(config['ENDPOINTS']['endpoints_dict'])

# NO USE INTERFACES
NO_USE_SWITCHPORT = config["DO_NOT_USE"]["iface_switchport"]
NO_USE_VLAN = config["DO_NOT_USE"]["iface_vlan"]
NO_USE_VLAN_ID = config["DO_NOT_USE"]["vlan_id"]
NO_USE_ETH = config["DO_NOT_USE"]["iface_eth"]