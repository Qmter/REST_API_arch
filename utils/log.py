import logging
import os


def initialize_log(verbose, file_root):
    """Метод для инициализации способа логирования и
        root места записи логов"""

    # Выбор уровня логирования в зависимости от аргумента verbose
    if verbose:
        log_lvl = logging.DEBUG
    else:
        log_lvl = logging.INFO

    # Создание директории для логирования если её не существует
    log_path = os.path.join(os.getcwd(), "logs")
    if not os.path.exists(log_path):
        os.mkdir("logs")

    # Объявление конфигурации и директории логирования
    logging.basicConfig(
        level=log_lvl,
        filename=os.path.join(os.getcwd(), "logs", f"{file_root}.log"),
        filemode='a',
        format='%(message)s',
        encoding="utf-8"
    )

def log_start_program(seed = None,
                       flag = None,
                       launch_command = None,
                       current_log_time = None):
    """Метод для логирования старта программы"""
    
    if current_log_time is not None:
        # Запись в лог текущих времени и даты
        logging.info(msg=f"{current_log_time}")

    if launch_command is not None:
        # Логирование командной строки
        logging.info("Launch Command: " + launch_command)

    if flag is not None:
        # Логирование флага
        logging.info(f"Flag: {flag}")

    if seed is not None:
        # Если seed не None, то логируем его
        if seed != 0:
            logging.info(f"Using seed: {seed}")
        else:
            logging.info(f"The default seed is used: {seed}")