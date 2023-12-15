import pulp
import pandas as pd
import numpy as np
from pulp import PULP_CBC_CMD
import matplotlib.pyplot as plt
import networkx as nx
import plotly
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
from utils.create_file_and_path import Util
class Optimize:

    def __init__(self):
        self.target_w = 0
        self.cons_idx = []
        self.input_L_J = None
        self.num_engines = None
        self.engine_W = None
        self.num_points = None
        self.output_W = None
        self.list_dgu = []
        self.solution_paths = []

    def optimize(self, excluded_engines, target_w=0):

        if self.__bool_optimize(target_w):
            print('Мощность для распределения', self.target_w)
            self.assignments = pulp.LpVariable.matrix(
                name='asn', cat=pulp.LpBinary,
                indices=(range(self.num_engines), range(self.num_points)),
            )
            prob = pulp.LpProblem(name='diesel_generation', sense=pulp.LpMinimize)
            print(pd.DataFrame(self.assignments))
            fuel_cost = pulp.LpAffineExpression()

            for engine, engine_group in enumerate(self.assignments):
                if excluded_engines[engine] != -1:
                    fuel_cost += pulp.lpDot(engine_group, self.input_L_J[:, engine])

            prob.objective += fuel_cost

            total_output = pulp.LpAffineExpression()

            for engine, engine_group in enumerate(self.assignments):
                if excluded_engines[engine] != -1:
                    prob.addConstraint(name=f'engine_excl_{engine}', constraint=pulp.lpSum(engine_group) <= 1)
                    prob.objective += pulp.lpDot(engine_group, self.input_L_J[:, engine])
                    total_output += pulp.lpDot(engine_group, self.output_W.loc[:, engine])
            print(prob)
            prob += total_output >= self.target_w - 0.5
            prob += total_output <= self.target_w + 0.5
            print(prob)
            # prob.solve(PULP_CBC_CMD(msg=False))
            prob.solve()

            try:
                assert prob.status == pulp.LpStatusOptimal
            except Exception as e:
                print(e)

            self.cons_idx = [
                next((i for i, var in enumerate(engine_group) if var.value() is not None and var.value() > 0.5), None)
                for engine_group in self.assignments
            ]
            r = 0
            self.list_dgu = []
            for idx, cons_idx in enumerate(self.cons_idx):
                if cons_idx is not None:
                    print(f"Дизель {idx + 1} включен, его мощность: {self.output_W.loc[cons_idx, idx]}", end=' ')
                    print(f"его расход: {self.input_L_J[cons_idx, idx]}")
                    self.list_dgu.append([idx, self.output_W.loc[cons_idx, idx], self.input_L_J[cons_idx, idx]])
                    r += self.input_L_J[cons_idx, idx]
            print(r)

    def __bool_optimize(self, target_w):
        if target_w != 0:
            self.target_w = target_w
            return True
        return False

    def init_optimize(self, param_dgu):
        self.engine_W = pd.DataFrame(
            data={
                'power_min': [p_min[1] for p_min in param_dgu.values()],
                'power_max': [p_max[2] for p_max in param_dgu.values()],
            },
            index=pd.RangeIndex(name='engine', start=0, stop=len(param_dgu)),
        )

        self.output_W = pd.DataFrame(
            data=np.linspace(
                start=self.engine_W['power_min'],
                stop=self.engine_W['power_max'],
                num=401
            ),
            columns=self.engine_W.index,
        )

        # print(self.output_W)
        # fig = px.scatter(self.output_W)
        # fig.show()
        self.num_points = 401
        self.num_engines = len(self.engine_W)

        self.input_L_J = np.zeros((self.num_points, self.num_engines))
        param_dgu = [p for p in param_dgu.values()]
        for engine, _ in enumerate(range(len(param_dgu))):
            N_nom = param_dgu[int(engine)][2]
            e_c = param_dgu[int(engine)][0]
            b_nom = param_dgu[int(engine)][3]
            b_dg = b_nom / e_c
            self.input_L_J[:, engine] = (0.9 + (0.1 / (self.output_W.loc[:, engine] / N_nom))) * b_dg
        # Util().open_csv("diesel_12.csv", "w", self.input_L_J[:, 0])

        # fig = px.scatter(self.input_L_J)
        # fig.show()
        print(pd.DataFrame(self.input_L_J))
