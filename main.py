import os
import shutil

from BotFinderConfigs import MainConfig, DataBaseConfig, SamplesConfig
from Samples import ShemaPlayerSamples
from UserDataBase import UserDataBase
from BinaryPlot import drow_3d_plot, plot_local_ouliter_factor


class HTMLreport:
    """класс формирования html отчета"""

    def __init__(self, path:str):
        """
        Args:
            path: путь к папке хранения отчета
        """
        ##путь к папке хранения отчета
        self.path_dir = path
        """путь к папке хранения отчета"""
        ##Количество фотографий в отчете
        self.__count_of_photos = 0
        """Количество фотографий в отчете"""

    def prepare_dir(self):
        """
        Подготовить папку для хранения отчета, в случае если папка отчета уже существует, удаить её и создать новую.
        """
        if os.path.exists(self.path_dir):
            shutil.rmtree(path= self.path_dir)
        os.mkdir(self.path_dir)

    def make_report(self, samples_lable ,ejection_data, other_data, color_other_data):
        """
        Сформировать содержание html отчета

        Args:
            samples_lable: название выборок
            ejection_data: данные точек выброса
            other_data: данные точек выброса линейного анализа
            color_other_data: цвета таблицы точек выброса линейного анализа
            текст html отчета
        """
        htmlrepot = '<html><body>'
        htmlrepot += self.package_title("Отчет о анамалиях в данных пользователей")
        htmlrepot += self.pacage_bloc('графики',
                                      self.package_img_bloc_tuple(0,1) +
                                      self.package_img_bloc_tuple(2,3) +
                                      self.package_img_bloc_tuple(4,5) +
                                      '<div style="display: flex; Justify-content: center;">' +
                                        self.package_img_bloc(6) +
                                      '</div>'
                                      )
        htmlrepot += self.pacage_bloc('Аномальные данные',
                                      self.package_table('аномалии выявленные методом локального уровня вброса',
                                                         samples_lable,
                                                         ejection_data,
                                                         ) +
                                      "".join(self.package_table('аномалии линейного вброса по парпметру "' + samples_lable[sample_index + 1] +'"',
                                                                 samples_lable,
                                                                 other_data[sample_index],
                                                                 color_other_data[sample_index]
                                                             )
                                          for sample_index in range(len(other_data))
                                          )
                                      )

        htmlrepot += '</body></html>'

        return htmlrepot

    def package_title(self, title):
        """
        Упаковать заголовок в html контейнер, с ориентрованием по центру

        Args:
            title: заголовок
            html код
        """
        return '<div style="text-align: center;"><h1>'+ title +'</h1></div>'

    def prepare_all_image(self, names, segments, corupt_points, clear_points):
        """
        Нарисовать графики и сохранить их в папке с отчетом

        Args:
            names: названия выборок
            segments: отезок для увеличенного графика для каждой выборки
            corupt_points: точки выброса данных
            clear_points: точки нормальных данных
        """
        figures = []

        for i in range(len(names) - 1):
            for k in range(i + 1, len(names)):
                figures.append(plot_local_ouliter_factor((names[i],names[k]),
                                                         ((min(corupt_points, key= lambda x: x[i])[i], max(corupt_points, key= lambda x: x[i])[i])
                                                            ,(min(corupt_points, key= lambda x: x[k])[k], max(corupt_points, key= lambda x: x[k])[k])),
                                                         ([value[i] for value in corupt_points], [value[k] for value in corupt_points]),
                                                         ([value[i] for value in clear_points], [value[k] for value in clear_points])
                                                         )
                               )
                figures.append(plot_local_ouliter_factor((names[i],names[k]),
                                                         (segments[i],segments[k]),
                                                         ([value[i] for value in corupt_points], [value[k] for value in corupt_points]),
                                                         ([value[i] for value in clear_points], [value[k] for value in clear_points])
                                                         )
                               )


        figures.append(drow_3d_plot(names, segments, corupt_points, clear_points))

        for figure in figures:
            figure.savefig(self.path_dir + "/" + str(self.__count_of_photos) + '.png')
            self.__count_of_photos += 1

    def package_img_bloc(self, picture_number):
        """
        Упаковать картинку из папки отчета в контейнер, с ориентрованием по центру

        Args:
            picture_number: номер картиники
        Returns:
            html код
        """
        return '<img src = "'+ str(picture_number) +'.png">'

    def pacage_bloc(self, title, content):
        """
        Создать html код блока с заголовком

        Args:
            title: заголовок блока
            content: содержание блока
        Returns:
            html код
        """
        return '<div style="width:100%; border: 1px solid black;"><div style="text-align: center;"><h3>'+ title +'</h1></div> '+content+' </div>'

    def package_img_bloc_tuple(self,picture_number_one,picture_number_two):
        """
        Упаковать две картинки из папки отчета в контейнер в один блок

            picture_number: номер картиники
        Returns:
            html код
        """
        return '<div style="display: flex; Justify-content: space-around;">' + self.package_img_bloc(picture_number_one) + self.package_img_bloc(picture_number_two) + '</div>'

    def package_table(self,title,titles_column, data, color = None):
        """
        Сформировать html код таблицы данных

             title: заголовок таблицы
             titles_column: название колонок таблицы
             data: содкржание таблицы
             color: цвета строк таблицы
        Returns:
            html код
        """
        if color is None:
            color = ['white' for _ in range(len(data))]
        table = '<div style="display: flex; Justify-content: center;"><table>'
        table += '<caption>'+title+'</caption>'
        table += '<tr>'
        for title_column in titles_column:
            table += '<th>' + title_column + '</th>'

        for sting_index in range(len(data)):
            table += '<tr style = "background-color:' + color[sting_index] + ';">'
            for value in data[sting_index]:
                table += '<td>' + str(value) + '</td>'
            table += '</tr>'
        table += '</tr>'
        table += '</table></div>'
        return table


class BotFinder:
    """Основной класс программы, реализующий запуск чтения/генерации кофигов программы, функциии анализа данных и формировния отчетов"""

    def __init__(self):
        is_first_launch = BotFinder.is_first_start()
        ##оснвая кофигурация программы
        self.main_config = MainConfig().load_or_create()
        ##объект подключение к базе данных
        self.data_base = None
        if not is_first_launch:
            self.try_load_data_base()
        ##конфигурация выборок
        self.samples_config = SamplesConfig().load_or_create()
        ##набор одномерных выборок
        self.shema = ShemaPlayerSamples([],self.main_config.count_neighbors, self.main_config.eject_lip)
        self.load_samples_from_config_file()
        self.prepare_work_place()

    @staticmethod
    def is_first_start():
        """
        проверка на первый запуск программы. Если в папке с программой отсутсвует основной кофигурационный файл она считается впервые запущенной

        Returns: True если программа запущена впервые иначе false
        """
        if os.path.exists(MainConfig().default_path):
            return False
        return True

    def load_samples_from_config_file(self):
        """
        загрузить данные о выборках из конфигурации
        Args:
             cfg: конфигурация выборок
        """
        for i in self.samples_config.samples_configs:
            self.shema.append_sample(i['name'], i['data_base_request'])

    def try_load_data_base(self):
        """
        Загрузить или создать файл конфигурации базы данных и проверить подключение на достоверность.
        В случае если подключение не возможно, заного выполняет процедуру загрузки или выдает исключение

        """
        if self.main_config.parse_samples_from_data_base:
            while 1:
                base_config = DataBaseConfig().load_or_create(self.main_config.save_data_base_data, self.main_config.save_data_base_passwor)
                self.data_base = UserDataBase(base_config.host,
                                              base_config.database,
                                              base_config.user,
                                              base_config.password)
                if self.data_base.connection_is_correct():
                    break
                else:
                    print('данные подключения к базе данных введены не верно')
                    if self.main_config.save_data_base_data:
                        raise Exception('Файл конфигурации базы данных неверный')

    def prepare_work_place(self):
        """
        Подготовить файлы выборок и дерикотрию для их хранения.
        """

        if self.main_config.save_session_data:
            if not os.path.exists(self.main_config.samples_folder_name):
                os.makedirs(self.main_config.samples_folder_name)
            if not os.path.exists(self.main_config.samples_folder_name + '/' +self.main_config.samples_player_name_file) or self.main_config.refresh_player_on_load:
                with open(self.main_config.samples_folder_name + '/' + self.main_config.samples_player_name_file, 'w'):
                    pass
            for sample in self.shema.samples:
                path = self.main_config.samples_folder_name + '/' + sample.name + '.txt'
                if not os.path.exists(path) or self.main_config.refresh_samples_on_load:
                    with open(path, 'w'):
                        pass

    def load_list_of_player(self):
        """
        Загрузить список пользователей из файла или базы данных

        Returns:
             список идентификаторов игроков
        """
        list_of_player = []
        if self.main_config.save_session_data:
            with open(self.main_config.samples_folder_name + '/' +self.main_config.samples_player_name_file, 'r') as file:
                list_of_player = file.read().split()

        if len(list_of_player) == 0:
            if self.main_config.parse_samples_from_data_base:
                list_of_player = [str(i[0]) for i in  self.data_base.execute(self.samples_config.user_query_from_data_base)]
            else:
                raise Exception('выборка пользователей пуста')

        return list_of_player

    def load_data(self):
        """
        Загрузить выборки из файла или из базы данных. После загрузки проверить данные на совместимость загрузить их в файл
        """

        self.shema.points = self.load_list_of_player()

        if self.main_config.save_session_data:
            for sample in self.shema.samples:
                sample.import_from_file(self.main_config.samples_folder_name + '/' + sample.name + '.txt')

        if self.main_config.parse_samples_from_data_base:
            for sample in self.shema.samples:
                if len(sample) == 0:
                    for player in self.shema.points:
                        try:
                            sample.append_player_from_data_base(player,self.data_base)
                        except:
                            if self.main_config.ignore_error_with_session_element_missing:
                                pass
                            else:
                                raise Exception('Ошибка при парсинге данных')

        self.shema.clear_from_incomplete(self.main_config.parse_samples_from_data_base and self.main_config.refresh_single_samples_element_if_missing, self.data_base)

        if self.main_config.save_session_data:
            for sample in self.shema.samples:
                sample.export_to_file(self.main_config.samples_folder_name + '/' + sample.name + '.txt')

            with open(self.main_config.samples_folder_name + '/' + self.main_config.samples_player_name_file,
                      'w') as file:
                file.write(' '.join(self.shema.points))

    def make_report(self):
        """
        Подготовить данные для создания отчета и сохранить отчет в папке
        """
        curupt_name = self.shema.outliers_point()
        curupt_poin = [self.shema[point] for point in curupt_name]
        clear_point = [self.shema[point] for point in self.shema.points if point not in curupt_name]

        report = HTMLreport(self.main_config.report_folder_name)
        report.prepare_dir()

        report.prepare_all_image([sample.name for sample in bf.shema.samples],
                                 [sample.remissible_segment() for sample in bf.shema.samples],
                                 curupt_poin,
                                 clear_point
                                 )

        r = report.make_report(['id пользователя'] + [sample.name for sample in bf.shema.samples],
                               [[player] + list(bf.shema[player]) for player in curupt_name],
                               [[[player] + list(bf.shema[player]) for player in sample.linear_ejection()] for sample in bf.shema.samples],
                               [['pink' if player in curupt_name else 'cornflowerblue' for player in sample.linear_ejection()] for sample in bf.shema.samples])


        with open(self.main_config.report_folder_name + '/отчет.html', 'w') as file:
            file.write(r)

if __name__ == '__main__':

    start_status = BotFinder.is_first_start()
    bf = BotFinder()
    if not start_status:
        bf.load_data()
        bf.make_report()
    else:
        print('конфигурация программы загружена успешно')



