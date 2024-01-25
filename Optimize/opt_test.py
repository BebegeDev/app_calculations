# import pulp
# import pandas as pd
# import numpy as np
# from pulp import PULP_CBC_CMD
# import matplotlib.pyplot as plt
# import utils
# from utils.create_file_and_path import Util
#
#
# class Optimize:
#
#     def __init__(self):
#         # self.flag_test_load = False
#
#         self.name_file = None
#         self.flag_save = False
#         self.target_w = 0
#         self.cons_idx = []
#         self.input_L_J = None
#         self.num_engines = None
#         self.engine_W = None
#         self.num_points = None
#         self.output_W = None
#         self.list_dgu = []
#
#     def optimize(self, excluded_engines, target_w=0):
#
#         if self.__bool_optimize(target_w):
#             print('Мощность для распределения', self.target_w)
#             assignments = pulp.LpVariable.matrix(
#                 name='asn', cat=pulp.LpBinary,
#                 indices=(range(self.num_engines), range(self.num_points)),
#             )
#             prob = pulp.LpProblem(name='diesel_generation', sense=pulp.LpMinimize)
#
#             fuel_cost = pulp.LpAffineExpression()
#             for engine, engine_group in enumerate(assignments):
#                 if excluded_engines[engine] != -1:
#                     fuel_cost += pulp.lpDot(engine_group, self.input_L_J[:, engine])
#
#             prob.objective += fuel_cost
#             total_output = pulp.LpAffineExpression()
#
#             for engine, engine_group in enumerate(assignments):
#                 if excluded_engines[engine] != -1:
#                     prob.addConstraint(name=f'engine_excl_{engine}', constraint=pulp.lpSum(engine_group) <= 1)
#                     prob.objective += pulp.lpDot(engine_group, self.input_L_J[:, engine])
#                     total_output += pulp.lpDot(engine_group, self.output_W.loc[:, engine])
#
#             prob += total_output == self.target_w
#
#             prob.solve(PULP_CBC_CMD(msg=False))
#             try:
#                 assert prob.status == pulp.LpStatusOptimal
#             except Exception as e:
#                 print(e)
#             self.cons_idx = [
#                 next((i for i, var in enumerate(engine_group) if var.value() is not None and var.value() > 0.5), None)
#                 for engine_group in assignments
#             ]
#             self.list_dgu = []
#             b = 0
#             p = 0
#             d = ''
#             for idx, cons_idx in enumerate(self.cons_idx):
#
#                 if cons_idx is not None:
#                     print(f"Дизель {idx} включен, его мощность: {self.output_W.loc[cons_idx, idx]}", end=' ')
#                     print(f"его расход: {self.input_L_J[cons_idx, idx]}")
#                     self.list_dgu.append([idx, self.output_W.loc[cons_idx, idx], self.input_L_J[cons_idx, idx]])
#                     b += self.input_L_J[cons_idx, idx]
#                     p += self.output_W.loc[cons_idx, idx]
#                     d += f'{idx + 1} '
#             if self.flag_save:
#                 column = [b, p, d]
#                 Util().open_csv(self.name_file, mode='a', data=column)
#
#             print("Суммарный расход:", b)
#             print('================================================================================')
#
#     def __bool_optimize(self, target_w):
#         if target_w != 0:
#             self.target_w = target_w
#             return True
#         # elif self.flag_test_load:
#         #     # self.flag_test_load = False
#         #     return True
#         return False
#
#     def init_optimize(self, param_dgu, k):
#         """
#         Метод init_optimize класса Optimize предназначен для инициализации данных таких как:
#             1.внесение параметров ДГУ
#             2. создание матриц мощности, расхода
#         :param param_dgu: параметры ДГУ
#         :param k: коэффициент множитель для изменения количества точек
#         """
#         # массив с ограничениями по минимальной и максимальной мощности
#         engine_data = {
#             'power_min': [p_min[1] for p_min in param_dgu.values()],
#             'power_max': [p_max[2] for p_max in param_dgu.values()],
#         }
#         # определяем количество ДГУ
#         self.num_engines = len(param_dgu)
#         # массив с минимальной и максимальной мощностью каждого ДГУ
#         self.engine_W = pd.DataFrame(engine_data, index=pd.RangeIndex(name='engine', start=0, stop=self.num_engines))
#         # Извлечение самой минимальной мощности
#         min_from_min = self.engine_W['power_min'].min()
#         # Извлечение самой максимальной мощности
#         max_from_max = self.engine_W['power_max'].max()
#         #  определение количества точек
#         self.num_points = int(k * (max_from_max - min_from_min) + 1)
#         # буфер для заполнения мощностями по каждому ДГУ
#         self.output_W = pd.DataFrame(np.zeros((self.num_points, self.num_engines)), columns=self.engine_W.index)
#
#         self.old_W = pd.DataFrame(np.zeros((self.num_points, self.num_engines)), columns=self.engine_W.index)
#
#         for e in range(self.num_engines):
#             c = 0
#             for p in np.linspace(min_from_min, max_from_max, num=self.num_points):
#                 if self.engine_W['power_min'][e] <= p <= self.engine_W['power_max'][e]:
#                     self.output_W.loc[c, e] = p
#                     self.old_W.loc[c, e] = p
#                 else:
#                     self.output_W.loc[c, e] = self.engine_W['power_min'][e]
#                     self.old_W.loc[c, e] = None
#                 c += 1
#
#         self.input_L_J = np.zeros((self.num_points, self.num_engines))
#         self.old_L = np.zeros((self.num_points, self.num_engines))
#         param_dgu = [p for p in param_dgu.values()]
#         for engine, _ in enumerate(range(self.num_engines)):
#             N_nom = param_dgu[int(engine)][2]
#             e_c = param_dgu[int(engine)][0]
#             b_nom = param_dgu[int(engine)][3]
#             b_dg = b_nom / e_c
#             self.input_L_J[:, engine] = (0.9 + (0.1 / (self.output_W.loc[:, engine] / N_nom))) * b_dg
#             self.old_L[:, engine] = (0.9 + (0.1 / (self.old_W.loc[:, engine] / N_nom))) * b_dg
#
#         # self.output_W = pd.DataFrame([
#         #     [100, 100, 100, 100, 100, 105, 110, 115, 120, 125, 130, 135, 140, 145, 150, 155, 160, 165, 170, 175, 180,
#         #      185, 190, 195, 200, 205, 210, 215, 220, 225, 230, 235, 240, 245, 250, 255, 260, 265, 270, 275, 280, 285,
#         #      290, 295, 300, 305, 310, 315, 320, 325, 330, 335, 340, 345, 350, 355, 360, 365, 370, 375, 380, 385, 390,
#         #      395, 400, 400, 400, 400, 400, 400, 400, 400, 400, 400, 400, 400, 400, 400, 400, 400, 400, 400, 400, 400,
#         #      400, 400, 400, 400, 400],
#         #     [130, 130, 130, 130, 130, 130, 130, 130, 130, 130, 130, 135, 140, 145, 150, 155, 160, 165, 170, 175, 180,
#         #      185, 190, 195, 200, 205, 210, 215, 220, 225, 230, 235, 240, 245, 250, 255, 260, 265, 270, 275, 280, 285,
#         #      290, 295, 300, 305, 310, 315, 320, 325, 330, 335, 340, 345, 350, 355, 360, 365, 370, 375, 380, 385, 390,
#         #      395, 400, 405, 410, 415, 420, 425, 430, 435, 440, 445, 450, 455, 460, 465, 470, 475, 480, 485, 490, 495,
#         #      500, 505, 510, 515, 520],
#         #     [80, 85, 90, 95, 100, 105, 110, 115, 120, 125, 130, 135, 140, 145, 150, 155, 160, 165, 170, 175, 180, 185,
#         #      190, 195, 200, 205, 210, 215, 220, 225, 230, 235, 240, 245, 250, 255, 260, 265, 270, 275, 280, 285, 290,
#         #      295, 300, 305, 310, 315, 315, 315, 315, 315, 315, 315, 315, 315, 315, 315, 315, 315, 315, 315, 315, 315,
#         #      315, 315, 315, 315, 315, 315, 315, 315, 315, 315, 315, 315, 315, 315, 315, 315, 315, 315, 315, 315, 315,
#         #      315, 315, 315, 315]
#         # ]).T
#         # self.input_L_J = np.array([
#         #     [301.27, 301.27, 301.27, 301.27, 301.27, 296.86, 292.84, 289.18, 285.82, 282.73, 279.88, 277.24, 274.79,
#         #      272.5, 270.37, 268.38, 266.51, 264.75, 263.1, 261.54, 260.07, 260.07, 261.54, 263.1, 264.75, 266.51,
#         #      268.38, 270.37, 272.5, 274.79, 277.24, 279.88, 282.73, 285.82, 289.18, 292.84, 296.86, 301.27, 306.17,
#         #      311.57, 317.57, 323.57, 329.57, 335.57, 341.57, 347.57, 353.57, 359.57, 365.57, 371.57, 377.57, 383.57,
#         #      389.57, 395.57, 401.57, 407.57, 413.57, 419.57, 425.57, 431.57, 437.57, 443.57, 449.57, 455.57, 461.57,
#         #      461.57, 461.57, 461.57, 461.57, 461.57, 461.57, 461.57, 461.57, 461.57, 461.57, 461.57, 461.57, 461.57,
#         #      461.57, 461.57, 461.57, 461.57, 461.57, 461.57, 461.57, 461.57, 461.57, 461.57, 461.57],
#         #     [326.65, 326.65, 326.65, 326.65, 326.65, 326.65, 326.65, 326.65, 326.65, 326.65, 326.65, 322.93, 319.47,
#         #      316.25, 313.25, 310.44, 307.81, 305.33, 303, 300.81, 298.73, 296.77, 294.91, 293.15, 291.47, 289.88,
#         #      288.36, 286.92, 285.53, 284.21, 282.95, 281.74, 280.58, 279.47, 278.41, 277.38, 276.4, 275.45, 274.54,
#         #      273.66, 272.81, 271.99, 271.2, 270.43, 269.7, 268.98, 268.29, 267.62, 268.29, 268.98, 269.7, 270.43, 271.2,
#         #      271.99, 272.81, 273.66, 274.54, 275.45, 276.4, 277.38, 278.41, 279.47, 280.58, 281.74, 282.95, 284.21,
#         #      285.53, 286.92, 288.36, 289.88, 291.47, 293.15, 294.91, 296.77, 298.73, 300.81, 303, 305.33, 307.81,
#         #      310.44, 313.25, 316.25, 319.47, 322.93, 326.65, 330.65, 334.95, 339.55, 344.45],
#         #     [500, 491.6, 483.375, 475.325, 467.45, 459.75, 452.225, 444.875, 437.7, 430.7, 423.875, 417.225, 410.75,
#         #      404.45, 398.325, 392.375, 386.6, 381, 375.575, 370.325, 365.25, 360.35, 355.625, 351.075, 346.7, 342.5,
#         #      338.475, 334.625, 330.95, 327.45, 324.125, 320.975, 318, 315.2, 312.575, 310.125, 307.85, 305.75, 303.825,
#         #      302.075, 300.5, 299.1, 297.875, 296.825, 295.95, 295.25, 294.725, 294.375, 294.375, 294.375, 294.375,
#         #      294.375, 294.375, 294.375, 294.375, 294.375, 294.375, 294.375, 294.375, 294.375, 294.375, 294.375, 294.375,
#         #      294.375, 294.375, 294.375, 294.375, 294.375, 294.375, 294.375, 294.375, 294.375, 294.375, 294.375, 294.375,
#         #      294.375, 294.375, 294.375, 294.375, 294.375, 294.375, 294.375, 294.375, 294.375, 294.375, 294.375, 294.375,
#         #      294.375, 294.375]
#         # ]).T
#         #
#         # self.num_engines = 3
#         # self.num_points = (len(self.output_W[0]))
#
#     def build_and_save_graph(self, filename):
#         self.old_L = pd.DataFrame(self.old_L)
#         self.old_W = pd.DataFrame(self.old_W)
#         # self.old_W = pd.DataFrame([
#         #     [100, 105, 110, 115, 120, 125, 130, 135, 140, 145, 150, 155, 160, 165, 170, 175, 180,
#         #      185, 190, 195, 200, 205, 210, 215, 220, 225, 230, 235, 240, 245, 250, 255, 260, 265, 270, 275, 280, 285,
#         #      290, 295, 300, 305, 310, 315, 320, 325, 330, 335, 340, 345, 350, 355, 360, 365, 370, 375, 380, 385, 390,
#         #      395, 400],
#         #     [130, 135, 140, 145, 150, 155, 160, 165, 170, 175, 180,
#         #      185, 190, 195, 200, 205, 210, 215, 220, 225, 230, 235, 240, 245, 250, 255, 260, 265, 270, 275, 280, 285,
#         #      290, 295, 300, 305, 310, 315, 320, 325, 330, 335, 340, 345, 350, 355, 360, 365, 370, 375, 380, 385, 390,
#         #      395, 400, 405, 410, 415, 420, 425, 430, 435, 440, 445, 450, 455, 460, 465, 470, 475, 480, 485, 490, 495,
#         #      500, 505, 510, 515, 520],
#         #     [80, 85, 90, 95, 100, 105, 110, 115, 120, 125, 130, 135, 140, 145, 150, 155, 160, 165, 170, 175, 180, 185,
#         #      190, 195, 200, 205, 210, 215, 220, 225, 230, 235, 240, 245, 250, 255, 260, 265, 270, 275, 280, 285, 290,
#         #      295, 300, 305, 310, 315]
#         # ]).T
#
#         # self.old_L = pd.DataFrame([
#         #     [301.27, 296.86, 292.84, 289.18, 285.82, 282.73, 279.88, 277.24, 274.79,
#         #      272.5, 270.37, 268.38, 266.51, 264.75, 263.1, 261.54, 260.07, 260.07, 261.54, 263.1, 264.75, 266.51,
#         #      268.38, 270.37, 272.5, 274.79, 277.24, 279.88, 282.73, 285.82, 289.18, 292.84, 296.86, 301.27, 306.17,
#         #      311.57, 317.57, 323.57, 329.57, 335.57, 341.57, 347.57, 353.57, 359.57, 365.57, 371.57, 377.57, 383.57,
#         #      389.57, 395.57, 401.57, 407.57, 413.57, 419.57, 425.57, 431.57, 437.57, 443.57, 449.57, 455.57, 461.57],
#         #     [326.65, 322.93, 319.47,
#         #      316.25, 313.25, 310.44, 307.81, 305.33, 303, 300.81, 298.73, 296.77, 294.91, 293.15, 291.47, 289.88,
#         #      288.36, 286.92, 285.53, 284.21, 282.95, 281.74, 280.58, 279.47, 278.41, 277.38, 276.4, 275.45, 274.54,
#         #      273.66, 272.81, 271.99, 271.2, 270.43, 269.7, 268.98, 268.29, 267.62, 268.29, 268.98, 269.7, 270.43, 271.2,
#         #      271.99, 272.81, 273.66, 274.54, 275.45, 276.4, 277.38, 278.41, 279.47, 280.58, 281.74, 282.95, 284.21,
#         #      285.53, 286.92, 288.36, 289.88, 291.47, 293.15, 294.91, 296.77, 298.73, 300.81, 303, 305.33, 307.81,
#         #      310.44, 313.25, 316.25, 319.47, 322.93, 326.65, 330.65, 334.95, 339.55, 344.45],
#         #     [500, 491.6, 483.375, 475.325, 467.45, 459.75, 452.225, 444.875, 437.7, 430.7, 423.875, 417.225, 410.75,
#         #      404.45, 398.325, 392.375, 386.6, 381, 375.575, 370.325, 365.25, 360.35, 355.625, 351.075, 346.7, 342.5,
#         #      338.475, 334.625, 330.95, 327.45, 324.125, 320.975, 318, 315.2, 312.575, 310.125, 307.85, 305.75, 303.825,
#         #      302.075, 300.5, 299.1, 297.875, 296.825, 295.95, 295.25, 294.725, 294.375]
#         # ]).T
#
#         linestyles = ['-', '--', '-.', ':', '--', '--']
#         marker = ['^', 'v', '^', 'v', '^', 'v']
#         color = ['black', 'red', 'black', 'red', 'black', 'red']
#         # linestyles = ['-', '--', '-.']
#         # marker = ['^', 'v', '^', 'v', '^', 'v']
#         # color = ['black', 'red', 'black', 'red', 'black', 'red']
#
#         for i, linestyle in enumerate(linestyles):
#
#             if i % 2 == 0:
#                 plt.plot(self.old_W[i], self.old_L[i] * 1.005, linestyle=linestyle, label=f'Характеристика ДГУ {i + 1}',
#                          color=color[i], linewidth=1)
#             else:
#                 plt.plot(self.old_W[i], self.old_L[i], linestyle=linestyle, label=f'Характеристика ДГУ {i + 1}',
#                          color=color[i], linewidth=1)
#
#         for idx, cons_idx in enumerate(self.cons_idx):
#             if cons_idx is not None:
#                 plt.scatter(self.output_W.loc[cons_idx, idx], self.input_L_J[cons_idx, idx],
#                             marker=marker[idx], label=f'ДГУ {idx + 1}: '
#                                                       f'b={round(self.input_L_J[cons_idx, idx], 2)}, '
#                                                       f'p={self.output_W.loc[cons_idx, idx]}', s=100)
#         plt.legend(fontsize=8)
#         plt.text(60, 90, f'Мощность ДЭС: {self.target_w}')
#         plt.xlabel('Мощность [кВт]')
#         plt.ylim(225, 400)
#         plt.ylabel('Удельный расход [г/кВт*ч]')
#         plt.grid()
#         plt.savefig(f'{filename}_{self.target_w}.png')
#         plt.show()
#
#     def save_optimize(self, name_file, column):
#         self.name_file = f'{name_file}'
#         self.flag_save = True
#         Util().open_csv(self.name_file, mode='a', data=column)
