import os
import shutil
import time

import matplotlib.pyplot as plt
from BotFinderConfigs import MainConfig, DataBaseConfig, SamplesConfig
from Samples import ShemaPlayerSamples
from UserDataBase import UserDataBase


class HTMLreport:
    """класс формирования html запроса"""
    def __init__(self, path):

        self.path_dir = path
        self.__count_of_photos = 0

    def prepare_dir(self):
        if os.path.exists(self.path_dir):
            shutil.rmtree(path= self.path_dir)
        os.mkdir(self.path_dir)

    def make_report(self, samples_lable ,ejection_data, other_data, color_other_data):

        htmlrepot = '<html><body>'
        htmlrepot += self.package_title("Отчет о анамалиях в данных пользователей")
        htmlrepot += self.pacage_bloc('инфографика',
                                      self.package_img_bloc_tuple(0,3) +
                                      self.package_img_bloc_tuple(1,4) +
                                      self.package_img_bloc_tuple(2,5) +
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
        return '<div style="text-align: center;"><h1>'+ title +'</h1></div>'

    def prepare_all_image(self, figures):
        for figure in figures:
            figure.savefig(self.path_dir + "/" + str(self.__count_of_photos) + '.png')
            self.__count_of_photos += 1

    def package_img_bloc(self, picture_number):
        return '<img src = "'+ str(picture_number) +'.png">'

    def pacage_bloc(self, title, content):
        return '<div style="width:100%; border: 1px solid black;"><div style="text-align: center;"><h3>'+ title +'</h1></div> '+content+' </div>'

    def package_img_bloc_tuple(self,picture_number_one,picture_number_two):
        return '<div style="display: flex; Justify-content: space-around;">' + self.package_img_bloc(picture_number_one) + self.package_img_bloc(picture_number_two) + '</div>'

    def package_table(self,title,titles_column, data, color = None):
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
    def __init__(self):
        self.main_config = MainConfig().load()
        self.data_base = None
        if self.main_config.parse_samples_from_data_base:
            base_config = DataBaseConfig().load(main_config=self.main_config)
            while 1:
                self.data_base = UserDataBase(base_config.host, base_config.database, base_config.user,
                                          base_config.password)
                if self.data_base.connection_is_correct():
                    break
                else:
                    print('данные подключения к базе данных введены не верно')
                    if self.main_config.save_data_base_data:
                        raise Exception('Файл конфигруации базы данных не верный')
        self.samples_config = SamplesConfig().load()

        self.shema = ShemaPlayerSamples([],self.main_config.count_neighbors, self.main_config.eject_lip)
        self.shema.load_sessionf_from_config_file(self.samples_config)
        self.prepare_work_place()

    def prepare_work_place(self):
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

    def drow_all_plot(self, zoom = True):
        figures = []
        bl = self.shema.eject_point
        for i in range(len(self.shema.samples) - 1):
            for k  in range(i + 1, len(self.shema.samples)):
                figures.append(self.plot_local_ouliter_factor(i,k, bl, zoom))
        return figures

    def drow_3d_plot(self, one_number_sample = 0, two_number_sample = 1, free_number_sample = 2, zoom = True):
        bl = self.shema.eject_point
        fig = plt.figure(figsize=(15, 15))
        ax =  fig.add_subplot(111, projection='3d')

        ax.set_xlabel(self.shema.samples[one_number_sample].name)
        ax.set_ylabel(self.shema.samples[two_number_sample].name)
        ax.set_zlabel(self.shema.samples[free_number_sample].name)


        if zoom:
            ax.set_xlim(self.shema.samples[one_number_sample].zoom_range())
            ax.set_ylim(self.shema.samples[two_number_sample].zoom_range())
            ax.set_zlim(self.shema.samples[free_number_sample].zoom_range())

        for player in self.shema.points:
            color = 'b.'
            if player in bl:
                color = 'r.'
            ax.plot(self.shema.samples[one_number_sample][player], self.shema.samples[two_number_sample][player], self.shema.samples[free_number_sample][player], color,  alpha=0.2)
        return fig

    def plot_local_ouliter_factor(self, first_number_sample, second_nuber_sample ,corapt_point, zoom = True):
        fig = plt.figure()
        tuple_plot = plt.subplot2grid((3, 3), (0, 1), rowspan=2, colspan=2)
        cercle_plot = plt.subplot2grid((3, 3), (2, 0) )
        first_boxplot = plt.subplot2grid((3, 3), (0, 0), rowspan=2, sharey = tuple_plot)
        second_bocplot = plt.subplot2grid((3, 3), (2, 1), colspan=2, sharex = tuple_plot)

        plt.setp(tuple_plot.get_xticklabels(), visible=False)
        plt.setp(tuple_plot.get_yticklabels(), visible=False)

        tuple_plot.set_xlabel(self.shema.samples[first_number_sample].name)
        tuple_plot.set_ylabel(self.shema.samples[second_nuber_sample].name)

        if zoom:
            tuple_plot.set_xlim(self.shema.samples[first_number_sample].zoom_range())
            tuple_plot.set_ylim(self.shema.samples[second_nuber_sample].zoom_range())


        cercle_plot.set_xticks([])
        cercle_plot.set_yticks([])

        plt.setp(first_boxplot.get_xticklabels(), visible=False)
        plt.setp(second_bocplot.get_yticklabels(), visible=False)

        cercle_plot.pie( [len(corapt_point), len(self.shema.points) - len(corapt_point)], autopct=lambda pct: str(round(pct, 2)) +'%',
                                          textprops=dict(color="gray"), colors = ['r', 'b'])

        first_boxplot.boxplot(self.shema.samples[second_nuber_sample].values())
        second_bocplot.boxplot(self.shema.samples[first_number_sample].values(), vert = False)

        for dot in self.shema.points:
            color = 'r.'
            if dot not in corapt_point:
                color = 'b.'
            tuple_plot.plot(self.shema.samples[first_number_sample][dot], self.shema.samples[second_nuber_sample][dot], color, alpha=0.2)
        return fig

    def make_report(self):
        report = HTMLreport(self.main_config.report_folder_name)
        report.prepare_dir()
        start_time = time.time()

        report.prepare_all_image(
            bf.drow_all_plot(zoom=False) + bf.drow_all_plot(zoom=True) + [bf.drow_3d_plot(zoom=True)])

        print("--- %s seconds ---" % (time.time() - start_time))

        r = report.make_report(['id пользователя'] + [sample.name for sample in bf.shema.samples],
                               [[player] + list(bf.shema[player]) for player in
                                bf.shema.eject_point],
                               [[[player] + list(bf.shema[player]) for player in
                                 sample.linar_ejection()] for sample in bf.shema.samples],
                               [['pink' if player in bf.shema.eject_point else 'cornflowerblue' for player in
                                 sample.linar_ejection()] for sample in bf.shema.samples])

        with open(self.main_config.report_folder_name + '/отчет.html', 'w') as file:
            file.write(r)


bf = BotFinder()
bf.load_data()
bf.make_report()



