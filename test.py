import Optimize.optimize
from sys import platform
import CreateJson.create_json_param_DGU

param_dgu = ''
if platform == 'win32' or platform == 'win64':
    param_dgu = CreateJson.create_json_param_DGU.open_json("\\utils\\param_dgu.json")
elif platform == 'linux' or platform == 'linux2':
    param_dgu = CreateJson.create_json_param_DGU.open_json("/utils/param_dgu.json")


optimize = Optimize.optimize.Optimize()
optimize.init_optimize(param_dgu)
optimize.optimize(1000)
print(optimize.list_dgu)
