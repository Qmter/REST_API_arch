import logging
import os.path


def initialize_log(verbose, file_root):
    """Метод для инициализации способа логирования и
        root места записи логов"""

    # Выбор уровня логирования в зависимости от аргумента verbose
    if verbose:
        log_lvl = logging.DEBUG
    else:
        log_lvl = logging.INFO

    # Объявление конфигурации и директории логирования
    logging.basicConfig(
        level=log_lvl,
        filename=os.path.join(os.getcwd(), "logs", f"{file_root}.log"),
        filemode='a',
        format='%(message)s'
    )
