from Optimize.optimize import Optimize
from utils.create_file_and_path import Util
import pandas as pd

data_path = Util()
test = Optimize()
test.init_optimize(data_path.open_json("param_dgu.json"))
test.optimize([1, 1], )
matrix = pd.DataFrame(test.input_L_J)
