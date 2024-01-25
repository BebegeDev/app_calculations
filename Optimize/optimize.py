import pulp
import pandas as pd
import numpy as np
from pulp import PULP_CBC_CMD
import matplotlib.pyplot as plt
import utils
from utils.create_file_and_path import Util


class Optimize:
    """
    Класс предназначен для проведения оптимизации состава ДЭС по целевой мощности, с помощью солвера СВС, работает по
    принципу ЛП с поиском минимума и учетом ограничений.
    """

    def __init__(self):

        # self.flag_test_load = False

        self.name_file = None
        self.flag_save = False
        self.target_w = 0
        self.cons_idx = []
        self.input_L_J = None
        self.num_engines = None
        self.engine_W = None
        self.num_points = None
        self.output_W = None
        self.list_dgu = []

    def optimize(self, excluded_engines, target_w=0):
        """

        Непосредственно метод оптимизации,
        :param excluded_engines: количество доступных дизелей
        :param target_w: целевая мощность
        """
        # ограничение для проверки ручного и автоматического ввода мощности (необязательное)
        if self.__bool_optimize(target_w):

            # вывод в консоль целевую мощность
            print('Мощность для распределения', self.target_w)
            # создание матрицы переменных решения
            assignments = pulp.LpVariable.matrix(
                name='asn', cat=pulp.LpBinary,
                indices=(range(self.num_engines), range(self.num_points)),
            )
            # функция для описания модели минимизации
            prob = pulp.LpProblem(name='diesel_generation', sense=pulp.LpMinimize)
            fuel_cost = pulp.LpAffineExpression()
            for engine, engine_group in enumerate(assignments):
                if excluded_engines[engine] != -1:
                    fuel_cost += pulp.lpDot(engine_group, self.input_L_J[:, engine])
            # prob.objective += fuel_cost
            # функция для создания линейной комбинации
            total_output = pulp.LpAffineExpression()

            # Цикл по двигателям для учета ограничений и добавления их к целевой функции
            for engine, engine_group in enumerate(assignments):
                # Условие проверки исключения двигателя из работы
                if excluded_engines[engine] != -1:
                    # Добавление ограничения на количество выбранных двигателей
                    prob.addConstraint(name=f'engine_excl_{engine}', constraint=pulp.lpSum(engine_group) <= 1)
                    # Увеличение общей выходной мощности на мощность выбранного двигателя
                    total_output += pulp.lpDot(engine_group, self.output_W.loc[:, engine])
                    # Увеличение целевой функции на затраты на топливо выбранного двигателя
                    prob.objective += pulp.lpDot(engine_group, self.input_L_J[:, engine])

            # Добавление ограничения на общую выходную мощность
            prob += total_output == self.target_w

            # Решение задачи оптимизации

            prob.solve(PULP_CBC_CMD(msg=False))
            # prob.solve()
            prob.writeLP("Input_opt.lp")
            prob.writeLP("TaxiAssignmentProblem.lp")
            # Проверка оптимальности решения
            try:
                assert prob.status == pulp.LpStatusOptimal
            except Exception as e:
                print(e)
            # Получение индексов выбранных ДГУ
            self.cons_idx = [
                next((i for i, var in enumerate(engine_group) if var.value() is not None and var.value() > 0.5), None)
                for engine_group in assignments
            ]
            # далее идет программный код для вывода и сохранения информации (не обязателен)
            self.list_dgu = []
            b = 0
            p = 0
            d = ''
            for idx, cons_idx in enumerate(self.cons_idx):

                if cons_idx is not None:
                    print(f"Дизель {idx} включен, его мощность: {self.output_W.loc[cons_idx, idx]}", end=' ')
                    print(f"его расход: {self.input_L_J[cons_idx, idx]}")
                    self.list_dgu.append([idx, self.output_W.loc[cons_idx, idx], self.input_L_J[cons_idx, idx]])
                    b += self.input_L_J[cons_idx, idx]
                    p += self.output_W.loc[cons_idx, idx]
                    d += f'{idx + 1} '
            if self.flag_save:
                column = [b, p, d]
                Util().open_csv(self.name_file, mode='a', data=column)
                print(1)
            print("Суммарный расход:", b)
            print('================================================================================')

    def __bool_optimize(self, target_w):
        if target_w != 0:
            self.target_w = target_w
            return True
        return False

    def init_optimize(self, param_dgu, k):
        """
        Метод init_optimize класса Optimize предназначен для инициализации данных таких как:
            1.внесение параметров ДГУ
            2. создание матриц мощности, расхода
        :param param_dgu: параметры ДГУ
        :param k: коэффициент множитель для изменения количества точек
        """
        # массив с ограничениями по минимальной и максимальной мощности
        engine_data = {
            'power_min': [p_min[1] for p_min in param_dgu.values()],
            'power_max': [p_max[2] for p_max in param_dgu.values()],
        }
        # определяем количество ДГУ
        self.num_engines = len(param_dgu)
        # массив с минимальной и максимальной мощностью каждого ДГУ
        self.engine_W = pd.DataFrame(engine_data, index=pd.RangeIndex(name='engine', start=0, stop=self.num_engines))
        # Извлечение самой минимальной мощности
        min_from_min = self.engine_W['power_min'].min()
        # Извлечение самой максимальной мощности
        max_from_max = self.engine_W['power_max'].max()
        #  определение количества точек
        self.num_points = int((max_from_max - min_from_min) / k + 1)
        # буфер для заполнения мощностями по каждому ДГУ
        self.output_W = pd.DataFrame(np.zeros((self.num_points, self.num_engines)), columns=self.engine_W.index)
        self.old_W = pd.DataFrame(np.zeros((self.num_points, self.num_engines)), columns=self.engine_W.index)
        # циклы для заполнения буфера мощностями
        for e in range(self.num_engines):
            c = 0
            for p in np.linspace(min_from_min, max_from_max, num=self.num_points):
                if self.engine_W['power_min'][e] <= p <= self.engine_W['power_max'][e]:
                    self.output_W.loc[c, e] = p
                    self.old_W.loc[c, e] = p
                else:
                    self.output_W.loc[c, e] = self.engine_W['power_min'][e]
                    self.old_W.loc[c, e] = None
                c += 1
        print(len(self.output_W))
        # буфер для заполнения расхода по каждому ДГУ
        self.input_L_J = np.zeros((self.num_points, self.num_engines))
        self.old_L = np.zeros((self.num_points, self.num_engines))
        # извлечение параметров ДГУ
        param_dgu = [p for p in param_dgu.values()]
        # цикл для заполнения буфера расходами
        for engine, _ in enumerate(range(self.num_engines)):
            # номинальная мощность ДГУ
            N_nom = param_dgu[int(engine)][2]
            # КПД ДГУ
            e_c = param_dgu[int(engine)][0]
            # номинальный расход ДГУ
            b_nom = param_dgu[int(engine)][3]

            b_dg = b_nom / e_c
            # формула для расчета расхода ДГУ
            self.input_L_J[:, engine] = (0.9 + (0.1 / (self.output_W.loc[:, engine] / N_nom))) * b_dg
            self.old_L[:, engine] = (0.9 + (0.1 / (self.old_W.loc[:, engine] / N_nom))) * b_dg

    def save_optimize(self, name_file, column):
        self.name_file = f'{name_file}.csv'
        self.flag_save = True
        Util().open_csv(self.name_file, mode='a', data=column)

    def build_and_save_graph(self, filename):
        self.old_L = pd.DataFrame(self.old_L)
        self.old_W = pd.DataFrame(self.old_W)

        linestyles = ['-', '--', '-.', ':', '--', '--']
        color = ['black', 'red', 'black', 'red', 'black', 'red']
        marker = ['^', 'v', '^', 'v', '^', 'v']

        for i, linestyle in enumerate(linestyles):

            if i % 2 == 0:
                plt.plot(self.old_W[i], self.old_L[i] * 1.005, linestyle=linestyle, label=f'Характеристика ДГУ {i + 1}',
                         color=color[i], linewidth=1)
            else:
                plt.plot(self.old_W[i], self.old_L[i], linestyle=linestyle, label=f'Характеристика ДГУ {i + 1}',
                         color=color[i], linewidth=1)

        for idx, cons_idx in enumerate(self.cons_idx):
            if cons_idx is not None:
                plt.scatter(self.output_W.loc[cons_idx, idx], self.input_L_J[cons_idx, idx],
                            marker=marker[idx], label=f'ДГУ {idx + 1}: '
                                                      f'b={round(self.input_L_J[cons_idx, idx], 2)}, '
                                                      f'p={self.output_W.loc[cons_idx, idx]}', s=100)
        plt.legend(fontsize=8)
        plt.xlabel('Мощность [кВт]')
        plt.ylim(225, 400)
        plt.ylabel('Удельный расход [г/кВт*ч]')
        plt.grid()
        plt.savefig(f'{filename}_{self.target_w}.png')
        # plt.show()
