from BotFinderConfigs import SamplesConfig
from UserDataBase import UserDataBase
from VPTree import VPTreeNode
import time

class Sample(dict):
    """
    Линейная Выборка данных
    """
    def __init__(self, name, data_base_request = None):
        super().__init__()
        self.name = name
        """название выборки"""
        self.min = 0
        """минимум выборки"""
        self.max = 0
        """максимум выборки"""
        self.data_base_request = data_base_request
        """запрос базы данных для получения элемента выборки"""

    def median(self):
        """
        получить мединау выборки

        :return: медана выборки
        :rtype: float
        """
        return self.quartile(2)

    def quartile(self, number_quartile):
        '''
        Получить квартиь линейной выборки

        :param number_quartile: номер квартили
        :type number_quartile: int
        :return: значение квартили
        :rtype: float
        '''
        items = sorted(self.values())
        if number_quartile == 0:
            return items[0]
        if number_quartile == 4:
            return  items[-1]
        if len(self) % 2 == 0:
            return (items[len(self)//4*number_quartile] +items[len(self)//4*number_quartile - 1])/2
        else:
            return items[len((self))//4*number_quartile]

    def interquartile_range(self):
        """
        получить межквартильное растояние

        :return: межквартильное растояние
        :rtype: float
        """
        return self.quartile(3) - self.quartile(1)

    def import_from_file(self,path):
        """
        Загрузить выборку из файла

        :param path: путь к файлу
        :type path: str
        """
        with open(path) as file:
            for string in file:
                self[string.split()[0]] = float(string.split()[1])
        if len(self) != 0:
            self.min = min(self.values())
            self.max = max(self.values())

    def export_to_file(self,path):
        """
        записать выборку в файл

        :param path: путь к файлу
        :type path: str
        """
        with open(path, 'w') as file:
            for player in self:
                file.write(player + ' '  + str(self[player]) + '\n')

    def try_recover_from_data_base(self, player_id, db:UserDataBase):
        """
        проверить возможность получить элемент выборки из базы данных,
        если это возможно - добавить элемент в выборку

        :param player_id:
        :type player_id:
        :param db:
        :type db:
        :return:
        :rtype:
        """
        try:
            self.append_player_from_data_base(player_id, db)
            return True
        except:
            return False

    def linar_ejection(self):
        '''
        получить id анамальных элементов выборки

        :return: аномальные элементы
        :rtype: [str]
        '''
        return [player for player in self.keys() if self[player] < self.right_range()[0] or self[player] > self.right_range()[1]]

    def right_range(self):
        """
        интервал, в котором находятся достоверные элементы

        :return: пара значений - начало и канец интервала
        :rtype: (float,float)
        """
        return (max(self.min,
             self.quartile(1) - self.interquartile_range() * 1.5
             )
         ,
         min(self.max,
             self.quartile(3) + self.interquartile_range() * 1.5
             )
         )

    def zoom_range(self):
        """
        интервал, в которых ожидаймо нохождение некоторого количества элементов

        :return:
        :rtype:
        """
        return (max(self.min,
             self.quartile(1) - self.interquartile_range() * 3
             )
         ,
         min(self.max,
             self.quartile(3) + self.interquartile_range() * 3
             )
         )

    def append_player_from_data_base(self, player_id , db:UserDataBase):
        """
        добавить элемент выборки из базы данных

        :param player_id: id элемента выборки
        :type player_id: int
        :param db: база данных
        :type db: UserDataBase
        """
        s = db.execute(self.data_base_request.replace( '%player_id%',player_id))
        self[player_id] = float(s[0][0])
        if float(s[0][0]) > self.max:
            self.max = float(s[0][0])
        elif float(s[0][0]) < self.min:
            self.min = float(s[0][0])


class ShemaPlayerSamples():
    """класс для комплексного анализа одномерных выборок"""
    def __init__(self, points, neighbour_count, lip):
        """
        :param points: id данных в выборках
        :type points: ['str']
        :param neighbour_count: количество соседей в методе локального вброса
        :type neighbour_count: int
        :param lip: порог, за которым данные являются анмальными
        :type lip: float
        """
        self.points = points
        """id точек, в выборках"""
        self.samples = []
        """линейные выборки данных"""
        self.neighbour_count = neighbour_count
        """количество соседей в метоле локального вброса"""
        self.VPtree = VPTreeNode(self.points, self.distance)
        """Дерево точек обзора"""
        self.lip = lip
        """порог, за которым данные являются анмальными"""
        self.__near_neighbour = {}
        """ближайшие n соседей к точкам"""
        self.__eject_point = None
        """аномальные данные"""



        self.__pre_distance = {}

    @property
    def eject_point(self):
        """
        получить id аномальных данных
        """
        if self.__eject_point is None:
            self.__eject_point = self.corrupt_points_by_local_ouliter_factor()
        return self.__eject_point

    def append_sample(self, sample: Sample):
        """
        доабвить выборку

        :param sample: выборка
        :type sample: Sample
        """
        self.samples.append(sample)

    def near_ditance(self, point):
        return 'boopa'
        """
        вернуть ближайшие n точек к заданной точки

        :param point: id набора данных (точки)
        :type point: str
        :return: список id ближайших данных (точек)
        :rtype: [str]
        """
        if point in self.__near_neighbour:
            return self.distance(point, self.__near_neighbour[point][-1])
        else:
            distances = [(other_point, self.distance(point, other_point)) for other_point in self.points if
                         point != other_point]
            distances.sort(key=lambda x: x[1])
            self.__near_neighbour[point] = [dis[0] for dis in distances[:self.neighbour_count]]
            return distances[self.neighbour_count - 1][1]

    def distance(self, first_point, second_pont):
        """
        DADA
        найти нормализированое евклидово растояние между точками

        :param first_point: id первой точки
        :type first_point: str
        :param second_pont: id второй точки
        :type second_pont: str
        :return: расстояние
        :rtype: float
        """
        return sum(((sample[first_point] - sample[second_pont]) / sample.max) ** 2 for sample in self.samples) ** (1/2)

    def reachability_distance(self, first_point, second_pont):
        """
        найти достижимое растояние между двумя точками

        :param first_point: id первой точки
        :type first_point: str
        :param second_pont: id второй точки
        :type second_pont: str
        :return: расстояние
        :rtype: float
        """
        return max(self.near_ditance(second_pont), self.distance(first_point, second_pont))

    def point_on_zone(self, point):
        """
        Получить точки в области досягаемости заданной точки

        :param point: id заданной точки
        :type point: str
        :return: список id точек в области досягаемости
        :rtype: [str]
        """
        self.near_ditance(point)
        return self.__near_neighbour[point]

    def local_reachability_density(self, point):
        '''
        плотность локальной досягаймости заданной точки

        :param point: id заданной точки
        :type point: 'str'
        :return: значение плотности
        :rtype: float
        '''
        '''
        start_time = time.time()
        near_points = self.point_on_zone(point)
        other_sum = sum(self.reachability_distance(point, some_near_point) for some_near_point in near_points)
        print("--- %s seconds ---" % (time.time() - start_time))
        if other_sum == 0:
            return float('inf')
        else:
            return len(near_points) / other_sum
        '''

        if point not in self.__pre_distance:
            near_points = self.point_on_zone(point)
            other_sum = sum(self.reachability_distance(point, some_near_point) for some_near_point in near_points)
            if other_sum == 0:
                self.__pre_distance[point] =  float('inf')
            else:
                self.__pre_distance[point] = len(near_points) / other_sum

        return self.__pre_distance[point]

    def local_ouliter_factor(self, point):
        """
        значение локального уровня вброса заданной точки

        :param point: id заданной точки
        :type point: 'str'
        :return: локальный уровень вброса
        :rtype: float
        """
        near_points = self.point_on_zone(point)
        return sum(self.local_reachability_density(orher_point) for orher_point in near_points) / (
                    len(near_points) * self.local_reachability_density(point))

    def corrupt_points_by_local_ouliter_factor(self):
        """
        получить список аномальных данных методом уровня локального вброса

        :return: id аномальных данных
        :rtype: [str]
        """
        start_time = time.time()

        corrupt = []
        for poit in self.points:
            if self.local_ouliter_factor(poit) > self.lip:
                corrupt.append(poit)

        print("--- %s seconds ---" % (time.time() - start_time))
        return corrupt

    def load_sessionf_from_config_file(self, cfg: SamplesConfig):
        """
        загрузить данные о выборках из конфигурации

        :param cfg: конфигурация выборок
        :type cfg: SamplesConfig
        """
        for i in cfg.samples_configs:
            self.append_sample(Sample(i['name'],i['data_base_request']))

    def __getitem__(self, item):
        """
        преобразовать id данных в координаты соответствующей точки

        :param point:
        :type point:
        :return:
        :rtype:
        """
        return (sample[item] for sample in self.samples)

    def clear_from_incomplete (self, is_load_from_data_base = True, db :UserDataBase = None):
        """
        синхронизировать содержание линейных выборок, удалив все элементы, которых нет во всех выборках

        :param is_load_from_data_base: загружать ли данные из базы данныхесли они не были найдены в файлах
        :type is_load_from_data_base: bool
        :param db: база данных для подзагрузки потерянных данных
        :type db: UserDataBase
        :return: id удаленных данных
        :rtype: [str]
        """
        incomplete_point = []

        for point in self.points:
            for sample in self.samples:
                if not(point in sample or is_load_from_data_base and sample.try_recover_from_data_base(point, db)):
                    incomplete_point.append(point)
                    break

        for point in incomplete_point:
            self.points.remove(point)
            for sample in self.samples:
                if point in sample:
                    sample.pop(point)

        return incomplete_point