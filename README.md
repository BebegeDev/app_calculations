# app_calculations
Development is underway

# Оптимизатор

### Для использования оптимизатора (можете опираться на `test.py`):
1. Импортируйте модули.
   ```
   from Connected.connection_db import add_user
   from Optimize.optimize import Optimize
   from utils.create_file_and_path import Util
   ```
2. Создайте экземпляр класса `Optimize и Util`, а также создайте подключение к БД
   ```
   data_path = Util()
   test = Optimize()
   connect = add_user()
   ```
3. Запустите метод инициализатор, в качестве аргумента передаются подключение к БД и шаг мощности.
   ```
   test.init_optimize(connect, 0.5)
   ```
4. Необязательный пункт. Если у вас есть подключение к mqtt вы можете использовать метод `optimize_callback_excluded_engines`, которы в качестве параметра принимает объект `mqttc` (как его создать будет описано позже) и `topic` по умолчанию топик `"mpei/DGU/excluded_engines"`.
    + -2 : аварийный режим
    * -1 : выключен
    * 0 : холостой ход
    * 1 : в работе
5. Необязательный пункт. Если у вас есть подключение к mqtt вы можете использовать метод `optimize_callback_power`, которы в качестве параметра принимает объект `mqttc` и `topic` по умолчанию топик `"mpei/Test/Power"`.
6. Вы можете также использовать метод для сохранения результата программы в файл формата .csv. name - имя файла, column - столбцы.
```
column = ['b', 'p', 'dgu', 'time']
test.save_optimize(name, column)
```
7. Запустите метод `optimize` в качестве аргумента принимает кол-во доступных ДГУ и мощность для оптимизации.
```
test.optimize([1, 1, -1, -1, -1, -1], 37)
```
8. Дополнительно можете использовать метод `test.build_and_save_graph` он предназначен для сохранения графиков.
```commandline
    test.build_and_save_graph(data_path.get_data_path('graph',
                                                      'C://Users//Александр//app_calculations//images//graph_dgu//'))
```
### Для настройки параметров ДГУ
ВРЕМЕННО НЕ ФУНКЦИОНИРУЕТ (пока работает только из БД)
Откройте файл и отредактируйте файл `utils\param_dgu.json` (для лучшего отображения нажмите `cntrl + alt + L`).

### Для настройки mqttc
1. Откройте файл и отредактируйте `utils\setting/ini`.
2. Импортируйте MQTT
   ```
   import mqtt.contact_mqtt
   ```
3. Создайте объект mqttc
   ```
   mqttc = mqtt.contact_mqtt.connection()
   ```
