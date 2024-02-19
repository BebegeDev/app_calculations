from Connected.connection_db import add_user
from Optimize.optimize import Optimize
from utils.create_file_and_path import Util

column = ['b', 'p', 'dgu', 'time']
name = 'dgu'
list_power = [10, 9, 7, 6, 12, 14, 14, 17, 30, 40, 50, 5, 20]

data_path = Util()
test = Optimize()
connect = add_user()
test.init_optimize(connect, 0.5)
test.save_optimize(name, column)
for i in list_power:
    test.optimize([1, 1, -1, -1, -1, -1], i)
    test.build_and_save_graph(data_path.get_data_path('graph',
                                                      'C://Users//Александр//app_calculations//images//graph_dgu//'))
