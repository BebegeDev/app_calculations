import pulp
import pandas as pd
import numpy as np


class Optimize:

    def __init__(self, mqttc):
        self.target_w = None
        self.cons_idx = None
        self.input_L_J = None
        self.num_engines = None
        self.engine_W = None
        self.num_points = None
        self.output_W = None
        self.power = None
        self.mqttc = mqttc
        self.n_old = 1

    def optimize(self, target_w, excluded_engines):
        self.target_w = target_w

        assignments = pulp.LpVariable.matrix(
            name='asn', cat=pulp.LpBinary,
            indices=(range(self.num_engines), range(self.num_points)),
        )
        prob = pulp.LpProblem(name='diesel_generation', sense=pulp.LpMinimize)

        fuel_cost = pulp.LpAffineExpression()
        for engine, engine_group in enumerate(assignments):
            if excluded_engines[engine] != -1:
                fuel_cost += pulp.lpDot(engine_group, self.input_L_J[:, engine])

        prob.objective += fuel_cost
        total_output = pulp.LpAffineExpression()

        for engine, engine_group in enumerate(assignments):
            if excluded_engines[engine] != -1:
                prob.addConstraint(name=f'engine_excl_{engine}', constraint=pulp.lpSum(engine_group) <= 1)
                prob.objective += pulp.lpDot(engine_group, self.input_L_J[:, engine])
                total_output += pulp.lpDot(engine_group, self.output_W.loc[:, engine])

        prob += total_output >= self.target_w - 1
        prob += total_output <= self.target_w + 1

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
        print(self.engine_W)
        self.output_W = pd.DataFrame(
            data=np.linspace(
                start=self.engine_W['power_min'],
                stop=self.engine_W['power_max'],
                num=201,
            ),
            columns=self.engine_W.index,
        )

        self.num_points = 201
        self.num_engines = len(self.engine_W)

        self.input_L_J = np.zeros((self.num_points, self.num_engines))
        param_dgu = [p for p in param_dgu.values()]
        for engine, _ in enumerate(range(6)):
            N_nom = param_dgu[int(engine)][2]
            e_c = param_dgu[int(engine)][0]
            b_nom = param_dgu[int(engine)][3]
            b_dg = b_nom / e_c
            self.input_L_J[:, engine] = (0.9 + (0.1 / (self.output_W.loc[:, engine] / N_nom))) * b_dg



    def optimize_callback(self):
        list_engine = []
        self.power = 0
        for engine, idx in enumerate(self.cons_idx):
            if idx is not None:
                list_engine.append(engine)
                self.power += self.output_W.loc[idx, engine]
                self.mqttc.publish(f"mpei/DGU/{engine+1}/Consuming", self.input_L_J[idx, engine])
                self.mqttc.publish(f"mpei/DGU/{engine+1}/Power/current_generator_power", self.output_W.loc[idx, engine])
                self.mqttc.publish(f"mpei/DGU/{engine+1}/Job_status", 1)
        for engine in range(6):
            if engine not in list_engine:
                self.mqttc.publish(f"mpei/DGU/{engine+1}/Power/current_generator_power", 0)
                self.mqttc.publish(f"mpei/DGU/{engine+1}/Consuming", 0)
                self.mqttc.publish(f"mpei/DGU/{engine+1}/Job_status", 0)

        d_f = ((self.power - self.n_old)/1)*0.1
        d_N = d_f * 120 / self.n_old
        M = round((9550 * self.power / (2200+d_N)), 2)
        self.n_old = self.target_w
        self.mqttc.publish(f"mpei/DGU/Moment", M)
        self.mqttc.publish(f"mpei/DGU/Rotation_speed", 2200+d_N)
        self.mqttc.publish(f"mpei/DGU/Changing_network_frequency", d_f)
        self.mqttc.publish(f"mpei/DGU/Changing_network_frequency_deviation", 50+d_f)
        self.mqttc.publish(f"mpei/DGU/Speed_deviation", d_N)
