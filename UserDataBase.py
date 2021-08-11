from mysql import connector

class UserDataBase:
    def __init__(self, host = 'localhost', database = None, user = 'root', password = ''):
        """
        Извлечение запросов их базы данных пользователя

        Args:
             host: адрес подключения
             user: полбзователь при подключении
             password: пароль при подключении
        """
        ##адрес подключения
        self.host = host
        #адрес подключения
        ##пользователь при подключении
        self.user = user
        #пользователь при подключении
        ##пароль при подключении
        self.password = password
        #пароль при подключении
        ##пароль при подключении
        self.database = database
        #имя базы данных

    def connection_is_correct(self):
        '''
        проверить возможность полдкючения к базе данных

        Returns:
             True - подключение проходит успешно, False - подключение произощло с ошибкой
        '''
        try:
            with connector.connect(host = self.host, user = self.user, password = self.password, database = self.database):
                pass
            return True
        except connector.Error as e:
            print(e)
            return False

    def execute(self, query):
        """
        выполнить запрос к базе данных

        Args:
             query: запрос
        Returns:
             результат выполнения запроса
        """
        with connector.connect(host = self.host, user = self.user, password = self.password, database = self.database) as con:
            with con.cursor(buffered=True) as cur:
                cur.execute(query)
                res = cur.fetchall()
        return res