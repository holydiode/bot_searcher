import json
from abc import ABC, abstractmethod

class ProgramConfig(ABC):
    """Абстрактынй класс конфигруационных файлов программы"""
    def config_file_is_available(self, path=None):
        """
        Проверить существует ли файл кофнигурации

        :param path: путь к файлу уонфигурации, если не указано, то брется путь по умочанию
        :type path: str
        :return: True если файл существует, False если файла нет
        :rtype: bool
        """
        if path is None:
            path = self.default_path

        try:
            file = open(path)
            file.close()
            return True
        except:
            return False

    @property
    @abstractmethod
    def default_path(self):
        """
        Путь по умолчнию
        """
        return ""

    def load(self, path=None):
        """
        Закгрузать содержимое файла конфигурации

        :param path: путь к файлу уонфигурации, если не указано, то брется путь по умочанию
        :type path: str
        :return:
        :rtype: ProgramConfig
        """

        if path is None:
            path = self.default_path
        if self.config_file_is_available(path):
            with open(path, 'r') as file:
                self.__dict__ = json.load(file)
        else:
            with open(path, 'w') as file:
                file.write(json.dumps(self.__dict__, indent=2, ensure_ascii=False))
        return self

class MainConfig(ProgramConfig):
    """класс основной конфигруации программы"""
    def __init__(self):
        self.parse_samples_from_data_base = True
        '''импользовать базу данных для получения выборок'''

        self.save_data_base_data = True
        """сохранить данные для входа в базу данных"""
        self.save_data_base_passwor = False
        '''сохранить пороль для входа в базу данных'''

        self.refresh_samples_on_load = False
        '''пересоздавать данные выборки из базы данных при каждом запуске программы'''
        self.refresh_player_on_load = False
        '''пересоздавать данные выборки пользователей из базы данных при каждом запуске программы'''

        self.refresh_single_samples_element_if_missing = True
        '''заново загруить элемент выборки, если он не будет найден в файлах'''
        self.ignore_error_with_session_element_missing = True
        '''игнорировать ошибки связанные с отсутсвием элемента выборки'''

        self.save_session_data = True
        '''сохранять выборки в файлах'''

        self.samples_folder_name = 'Выборки'
        "Название папки для хранения выборок"
        self.samples_player_name_file = 'игроки.txt'
        "Название файла для хранение выборки игроков"
        self.report_folder_name = 'Отчет'
        "название папки для хранения отчета"

        self.count_neighbors = 50
        '''количество соседей в методе локального уровня вброса'''
        self.eject_lip = 1.2
        '''порог выброса в методе локального уровня вброса'''

    @property
    def default_path(self):
        return 'config.json'


class DataBaseConfig(ProgramConfig):
    "класс "
    def __init__(self):
        self.host = 'localhost'
        "адрес базы данных"
        self.database = ''
        "имя базы данных"
        self.user = 'root'
        "пользователь базы данных"
        self.password = ''
        "пароль базы данных"

    @property
    def default_path(self):
        return "database.json"

    def load(self, path=None, main_config: MainConfig = None):
        """
        загрузка файла конфигурации базы данных с диалоговыми опциями

        :param path: путь к файлу конифгурации
        :type path: str
        :param main_config: конфигурация программы
        :type main_config: MainConfig
        :return:
        :rtype: DataBaseConfig
        """
        if main_config is None:
            main_config = MainConfig()

        if not self.config_file_is_available() or not main_config.save_data_base_data:
            self.__dialog_input()
        elif not main_config.save_data_base_passwor:
            super().load(path)
            self.__dialog_input_pass()
        else:
            super().load(path)

        if main_config.save_data_base_data and not self.config_file_is_available():
            save_pass = self.password
            if not main_config.save_data_base_passwor:
                self.password = None
            super().load(path)
            self.password = save_pass

        return self

    def __dialog_input(self):
        """
        диалоговый ввод всех данных подключения
        """
        self.host = input('Адресс базы данных: ')
        self.database = input('Имя базы данных: ')
        self.user = input('Имя пользоваетля: ')
        self.__dialog_input_pass()

    def __dialog_input_pass(self):
        """
        диалоговый ввод пароля
        """
        self.password = input('Пароль базы данных: ')


class SamplesConfig(ProgramConfig):
    """класс кофигурации выборок данных"""

    sample_model = {'name': None, 'data_base_request': None}
    """Конфигурация выборки"""

    def __init__(self):
        self.samples_configs = []
        """выборки"""
        self.user_query_from_data_base = 'select distinct f_player_id from t_participation'
        """запрос к базе данных для получения выборки пользователей"""
        self.default_sample()

    def default_sample(self):
        """
        Заполнить выборки по умочанию
        """
        default_session_config = self.sample_model.copy()
        default_session_config['name'] = "Среднее время сессии"
        default_session_config[
            'data_base_request'] = "SELECT avg(f_end_stamp - f_start_stamp) from t_sessions_log WHERE f_player_id = %player_id%"
        self.samples_configs.append(default_session_config)

    @property
    def default_path(self):
        return "samples.json"