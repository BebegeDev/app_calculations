# app_calculations
Development is underway

# Оптимизатор

### Для использования оптимизатора:
1. Импортируйте оптимизатор и другие файлы
   ```
   import Optimize.optimize
   from sys import platform
   import CreateJson.create_json_param_DGU

   param_dgu = ''
   if platform == 'win32' or platform == 'win64':
       param_dgu = CreateJson.create_json_param_DGU.open_json("\\utils\\param_dgu.json")
   elif platform == 'linux' or platform == 'linux2':
       param_dgu = CreateJson.create_json_param_DGU.open_json("/utils/param_dgu.json")
   ```
2. Создайте экземпляр класса `Optimize `
   ```
   optimize = Optimize.optimize.Optimize()
   ```
3. Запустите метод инициализатор, в качестве аргумента передаются параметры ДГУ (настройка параметров будет описанная позже).
   ```
   optimize.init_optimize(param_dgu)
   ```
4. Необязательный пункт. Если у вас есть подключение к mqtt вы можете использвать метод `optimize_callback_excluded_engines`, которы в качестве параметра примает объект `mqttc` (как его создать будет описано позже) и `topic` по умолчанию топик `"mpei/DGU/excluded_engines"`.
    + -2 : аварийный режим
    * -1 : выключен
    * 0 : холостой ход
    * 1 : в работе
5. Необязательный пункт. Если у вас есть подключение к mqtt вы можете использвать метод `optimize_callback_power`, которы в качестве параметра примает объект `mqttc` (как его создать будет описано позже) и `topic` по умолчанию топик `"mpei/Test/Power"`.
6. Запустите метод `optimize.optimize` в качестве аргумента принимает мощность для оптимизации, если у вас выполнен пункт №5, то можно ничего не передавать.

### Для настройки параметров ДГУ
Откройте файл и отредоктируйте файл `utils\param_dgu.json` (для лучшего отображения нажмите `cntrl + alt + L`).

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
