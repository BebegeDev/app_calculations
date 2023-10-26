import csv
import pulp
import pandas as pd
import numpy as np
from sys import platform
import CreateJson.create_json_param_DGU


class Optimize:

    def __init__(self):
        self.target_w = 0
        self.cons_idx = []
        self.input_L_J = None
        self.num_engines = None
        self.engine_W = None
        self.num_points = None
        self.output_W = None
        self.power = None



    def optimize(self, power):
        self.target_w = power
        assignments = pulp.LpVariable.matrix(
            name='asn', cat=pulp.LpBinary,
            indices=(range(self.num_engines), range(self.num_points)),
        )
        prob = pulp.LpProblem(name='diesel_generation', sense=pulp.LpMinimize)

        fuel_cost = pulp.LpAffineExpression()


        prob.objective += fuel_cost
        total_output = pulp.LpAffineExpression()

        for engine, engine_group in enumerate(assignments):
            prob.addConstraint(name=f'engine_excl_{engine}', constraint=pulp.lpSum(engine_group) <= 1)
            prob.objective += pulp.lpDot(engine_group, self.input_L_J[:, engine])
            total_output += pulp.lpDot(engine_group, self.output_W.loc[:, engine])

        prob += total_output >= self.target_w - 0.5
        prob += total_output <= self.target_w + 0.5

        prob.solve()
        assert prob.status == pulp.LpStatusOptimal

        self.cons_idx = [
            next((i for i, var in enumerate(engine_group) if var.value() is not None and var.value() > 0.5), None)
            for engine_group in assignments
        ]

        for idx, cons_idx in enumerate(self.cons_idx):
            if cons_idx is not None:
                print(f"Дизель {idx} включен, его мощность: {self.output_W.loc[cons_idx, idx]}")

    def init_optimize(self, param_dgu):

        self.engine_W = pd.DataFrame(
            data={
                'power_min': [p_min[1] for p_min in param_dgu.values()],
                'power_max': [p_max[2] for p_max in param_dgu.values()],
            },
            index=pd.RangeIndex(name='engine', start=0, stop=6),
        )
        self.output_W = pd.DataFrame(
            data=np.linspace(
                start=self.engine_W['power_min'],
                stop=self.engine_W['power_max'],
                num=2001
            ),
            columns=self.engine_W.index,
        )

        self.num_points = 2001
        self.num_engines = len(self.engine_W)

        self.input_L_J = np.zeros((self.num_points, self.num_engines))
        param_dgu = [p for p in param_dgu.values()]
        for engine, _ in enumerate(range(6)):
            N_nom = param_dgu[int(engine)][2]
            e_c = param_dgu[int(engine)][0]
            b_nom = param_dgu[int(engine)][3]
            b_dg = b_nom / e_c
            self.input_L_J[:, engine] = (0.9 + (0.1 / (self.output_W.loc[:, engine] / N_nom))) * b_dg



param_dgu = ''
if platform == 'win32' or platform == 'win64':
    param_dgu = CreateJson.create_json_param_DGU.open_json("\\utils\\param_dgu.json")
elif platform == 'linux' or platform == 'linux2':
    param_dgu = CreateJson.create_json_param_DGU.open_json("/utils/param_dgu.json")

optimize = Optimize()
optimize.init_optimize(param_dgu)
optimize.optimize(999)
