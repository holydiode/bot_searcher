from mysql import connector


class UserDataBase:
    def __init__(self, host = 'localhost', database = None, user = 'root', password = ''):
        """
        Извлечение запросов их базы данных пользователя

        :param host: адрес подключения
        :type host: str
        :param user: полбзователь при подключении
        :type user: str
        :param password: пароль при подключении
        :type password: str
        """
        self.host = host
        #адрес подключения
        self.user = user
        #полбзователь при подключении
        self.password = password
        #пароль при подключении
        self.database = database
        #имя базы данных

    def connection_is_correct(self):
        '''
        проверить возможность полдкючения к базе данных

        :return: True - подключение проходит успешно, False - подключение произощло с ошибкой
        :rtype: bool
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

        :param query: запрос
        :type query: str
        :return: результат выполнения запроса
        :rtype: any
        """
        with connector.connect(host = self.host, user = self.user, password = self.password, database = self.database) as con:
            with con.cursor(buffered=True) as cur:
                cur.execute(query)
                res = cur.fetchall()
        return res

    def find_win_probability_of_player(self, player_id):
        query = 'select sum(f_is_win)/count(f_is_win) from t_participation as p join t_game as g on p.f_game_id = g.f_id where p.f_player_id = '+str(player_id) +' group by cast(f_started_stamp as date) where f_start_stamp != \'0000-00-00 00:00:00\''
        data = self.execute(query)
        return [float(i[0]) for i in data]

    def find_time_session_of_player(self, player_id):
        query = 'SELECT f_end_stamp - f_start_stamp from t_sessions_log WHERE f_player_id = ' + str(player_id)
        data = self.execute(query)
        return [i[0] for i in data]

    def find_avg_bet_of_player(self, player_id):
        query = 'SELECT AVG(f_bet) FROM t_participation WHERE f_player_id =' + str(player_id)
        data = self.execute(query)
        return [i[0] for i in data]

    def list_of_player(self):
        query  = 'select distinct f_player_id from t_participation'
        data = self.execute(query)
        return [d[0] for d in data]
