from Connected.connection_db import add_user
from Optimize.optimize import Optimize
from utils.create_file_and_path import Util

column = ['b', 'p', 'dgu']
name = 'dgu'
list_power = [1000, 900, 700, 600, 1200, 1400, 1450, 1700, 300, 400, 500, 532, 2000]

data_path = Util()
test = Optimize()
connect = add_user()
test.init_optimize(connect, 0.5)
# test.save_optimize(name, column)
test.optimize([1, 1], 37)
# test.build_and_save_graph(data_path.get_data_path('graph',
#                                                   'C://Users//Александр//app_calculations//images//graph_dgu//'))
