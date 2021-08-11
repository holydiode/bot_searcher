from BotFinderConfigs import SamplesConfig
from UserDataBase import UserDataBase
from vptree import VPTree

class Sample(dict):
    """
    Линейная Выборка данных
    """
    def __init__(self, name, data_base_request = None):
        """

        Args:
            name: имя выборки
            data_base_request: запрос базы данных для получения значения выборки по идентификатору пользователя
        """
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

        Returns:
             медана выборки
        """
        return self.quartile(2)

    def quartile(self, number_quartile):
        '''
        Получить квартиь линейной выборки
        Args:
             number_quartile: номер квартили
        Returns:
             значение квартили
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

        Returns:
             межквартильное растояние
        """
        return self.quartile(3) - self.quartile(1)

    def import_from_file(self,path):
        """
        Загрузить выборку из файла
        Args:
             path: путь к файлу
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
        Args:
             path: путь к файлу
        """
        with open(path, 'w') as file:
            for player in self:
                file.write(player + ' '  + str(self[player]) + '\n')

    def try_recover_from_data_base(self, player_id, db:UserDataBase):
        """
        проверить возможность получить элемент выборки из базы данных,
        если это возможно - добавить элемент в выборку
        Args:
             player_id: идентификатор пользователя
             db: объект подключения к базе данных
        Returns:
            True если данные извлеченыу удачно, иначе Else
        """
        try:
            self.append_player_from_data_base(player_id, db)
            return True
        except:
            return False

    def linear_ejection(self):
        '''
        получить id анамальных элементов выборки

        Returns:
             аномальные элементы
        '''
        right_range = self.verified_segment()
        return  [player for player in self.keys() if self[player] < right_range[0] or self[player] > right_range[1]]

    def verified_segment(self):
        """
        интервал, в котором находятся достоверные элементы

        Returns:
             пара значений - начало и канец интервала
        """
        return (max(self.min,
             self.quartile(1) - self.interquartile_range() * 1.5
             )
         ,
         min(self.max,
             self.quartile(3) + self.interquartile_range() * 1.5
             )
         )

    def remissible_segment(self):
        """
        интервал, в которых ожидаймо нохождение некоторого количества элементов

        Returns:
            два числа, начало и конец интервала
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

        Args:
             player_id: id элемента выборки
             db: база данных
        """
        s = db.execute(self.data_base_request.replace( '%player_id%',player_id))
        self[player_id] = float(s[0][0])
        self.max = max(self[player_id], self.max)
        self.min = min(self[player_id], self.min)


class ShemaPlayerSamples():
    """класс для комплексного анализа одномерных выборок"""

    def __init__(self, points, neighbour_count, lip):
        """
        Args:
             points: id данных в выборках
             neighbour_count: количество соседей в методе локального вброса
             lip: порог, за которым данные являются анмальными
        """
        ##id точек, в выборках
        self.points = points
        """id точек, в выборках"""
        ##линейные выборки данных
        self.samples = []
        """линейные выборки данных"""
        ##количество соседей в метоле локального вброса
        self.neighbour_count = neighbour_count
        """количество соседей в метоле локального вброса"""
        ##Дерево точек обзора
        self.vp_tree = None
        """Дерево точек обзора"""
        ##порог, за которым данные являются анмальными
        self.lip = lip
        """порог, за которым данные являются анмальными"""
        ##ближайшие n соседей к точкам
        self.__near_neighbour = {}
        """ближайшие n соседей к точкам"""
        ##локальная дистаниця точек
        self.__pre_distance = {}

    def append_sample(self, name: str, query:str = ""):
        """
        доабвить выборку

        Args:
             name: имя выборки
             name: запрос выборки
        """
        self.samples.append(Sample(name,query))

    def nearest_distance(self, point):
        """
        вернуть растояние к ближайшей n-ой точеке

        Args:
             point: id набора данных (точки)
        Returns:
             список id ближайших данных (точек)
        """
        if point not in self.__near_neighbour:
            self.__near_neighbour[point] = self.VPtree.get_n_nearest_neighbors(point, self.neighbour_count)

        return self.distance(point, self.__near_neighbour[point][-1])

    def distance(self, first_point, second_pont):
        """
        найти нормализированое евклидово растояние между точками

        Args:
             first_point: id первой точки
             second_pont: id второй точки
        Returns:
             расстояние
        """
        return sum(((sample[first_point] - sample[second_pont]) / sample.max) ** 2 for sample in self.samples) ** (1/2)

    def reachability_distance(self, first_point, second_pont):
        """
        найти достижимое растояние между двумя точками

        Args:
             first_point: id первой точки
             second_pont: id второй точки
        Returns:
             расстояние
        """
        return max(self.nearest_distance(second_pont), self.distance(first_point, second_pont))

    def point_on_nearest_distance(self, point):
        """
        Получить точки в области досягаемости заданной точки

        Args:
             point: id заданной точки
        Returns:
             список id точек в области досягаемости
        """
        if point not in self.__near_neighbour:
            self.__near_neighbour[point] = self.VPtree.get_n_nearest_neighbors(point, self.neighbour_count)

        return self.__near_neighbour[point]

    def local_reachability_density(self, point):
        '''
        плотность локальной досягаймости заданной точки

        Args:
             point: id заданной точки
        Returns:
             значение плотности
        '''

        if point not in self.__pre_distance:
            near_points = self.point_on_nearest_distance(point)
            other_sum = sum(self.reachability_distance(point, some_near_point) for some_near_point in near_points)
            if other_sum == 0:
                self.__pre_distance[point] =  float('inf')
            else:
                self.__pre_distance[point] = len(near_points) / other_sum

        return self.__pre_distance[point]

    def local_ouliter_factor(self, point):
        """
        значение локального уровня вброса заданной точки

        Args:
             point: id заданной точки
        Returns:
             локальный уровень вброса
        """
        near_points = self.point_on_nearest_distance(point)
        return sum(self.local_reachability_density(orher_point) for orher_point in near_points) / (
                    len(near_points) * self.local_reachability_density(point))

    def outliers_point(self):
        """
        получить список аномальных данных методом уровня локального вброса

        Returns:
             id аномальных данных
        """

        if len(self.points) < 1:
            raise Exception('отсутствуют данные для анализа')
        if len(self.points) < self.neighbour_count or self.neighbour_count < 1 :
            raise Exception('указано не верное число соседей, или данных слишком мало')

        self.VPtree = VPTree(self.points, self.distance)

        corrupt = []
        for poit in self.points:
            if self.local_ouliter_factor(poit) > self.lip:
                corrupt.append(poit)

        return corrupt

    def __getitem__(self, item):
        """
        преобразовать id данных в координаты соответствующей точки

        Args:
             point: идентификатор точки
        Returns:
            список координат точки
        """
        return [sample[item] for sample in self.samples]

    def clear_from_incomplete(self, is_load_from_data_base = True, db :UserDataBase = None):
        """
        синхронизировать содержание линейных выборок, удалив все элементы, которых нет во всех выборках

        Args:
             is_load_from_data_base: загружать ли данные из базы данныхесли они не были найдены в файлах
             db: база данных для подзагрузки потерянных данных
        Returns:
             id удаленных данных
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