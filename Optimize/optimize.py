import math

import pulp
import pandas as pd
import numpy as np
from pulp import PULP_CBC_CMD
import matplotlib.pyplot as plt
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
        self.output_L = None
        self.num_engines = 2
        self.engine_min_max = None
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
                    fuel_cost += pulp.lpDot(engine_group, self.output_L.iloc[:, engine])
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
                    total_output += pulp.lpDot(engine_group, self.output_W.iloc[:, engine])
                    # Увеличение целевой функции на затраты на топливо выбранного двигателя
                    prob.objective += pulp.lpDot(engine_group, self.output_L.iloc[:, engine])

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
                    print(f"Дизель {idx+1} включен, его мощность: {self.output_W.iloc[cons_idx, idx]}", end=' ')
                    print(f"его расход: {self.output_L.iloc[cons_idx, idx]}")
                    self.list_dgu.append([idx, self.output_W.iloc[cons_idx, idx], self.output_L.iloc[cons_idx, idx]])
                    b += self.output_L.iloc[cons_idx, idx]
                    p += self.output_W.iloc[cons_idx, idx]
                    d += f'{idx + 1} '
            if self.flag_save:
                column = [b, p, d]
                Util().open_csv(self.name_file, mode='a', data=column)
            print("Суммарный расход:", b)
            print('================================================================================')

    def __bool_optimize(self, target_w):
        if target_w != 0:
            self.target_w = target_w
            return True
        return False

    def init_optimize(self, connect, k):
        if connect:
            cursor = connect.cursor()
            cursor.execute("SELECT * FROM power_dgu")
            power_dgu = cursor.fetchall()
            power_all = pd.DataFrame(power_dgu).set_index('No. of item')
            self.output_W = self.generate_matrix(power_all)
            self.num_points = int((power_all.max(axis=1).iloc[-1] - power_all.min(axis=1).iloc[0]) / k)
            cursor = connect.cursor()
            cursor.execute("SELECT * FROM consumption_dgu")
            power_dgu = cursor.fetchall()
            consumption_all = pd.DataFrame(power_dgu).set_index('No. of item')
            self.output_L = self.generate_matrix(consumption_all)



    @staticmethod
    def generate_matrix(data):
        output = {}
        for c, r in data.items():
            output[c] = []
            for c_1, r_1 in r.items():

                try:
                    if r_1 is None or math.isnan(r_1):
                        output[c].append(data[c].min(axis=0))
                        pass
                    else:
                        output[c].append(r_1)
                except Exception as e:
                    print(e)

        output = pd.DataFrame(output)
        return output

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
                plt.scatter(self.output_W.loc[cons_idx, idx], self.output_L[cons_idx, idx],
                            marker=marker[idx], label=f'ДГУ {idx + 1}: '
                                                      f'b={round(self.output_L[cons_idx, idx], 2)}, '
                                                      f'p={self.output_W.loc[cons_idx, idx]}', s=100)
        plt.legend(fontsize=8)
        plt.xlabel('Мощность [кВт]')
        plt.ylim(225, 400)
        plt.ylabel('Удельный расход [г/кВт*ч]')
        plt.grid()
        plt.savefig(f'{filename}_{self.target_w}.png')
        # plt.show()
