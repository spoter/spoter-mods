# mod_mods_gui
### Описание мода:
#### Ядро для моих модов, графические настройки, хуки, ресурсы и т.д.
## Создание графических настроек:
#### Импорт настроек
```python
    from gui.mods.mod_mods_gui import g_gui, inject
```

#### Класс для хранения настроек и доступа к графическим настройкам в ангаре

```python
# -*- coding: utf-8 -*-
from gui.mods.mod_mods_gui import g_gui, inject
import Keys

class Config(object):
    def __init__(self):
        self.ids = 'modsName' # внутренний идентификатор мода, должен быть уникальным
        self.version = 'v4.12 (2021-10-20)' # текстовое описание версии мода, может быть любым
        self.version_id = 412 # идентификатор версии мода, используется для проверки версий конфигов, должен быть int() и уникальным
        self.author = 'by spoter' # поле автора мода, может быть любым
        self.buttons = { #словарь для хранения кнопок по-умолчанию, если понадобится сбросить значение позже
                    'buttonRepair' : [Keys.KEY_SPACE], # пример одной кнопки
                    'buttonChassis': [[Keys.KEY_LALT, Keys.KEY_RALT]] # пример нажатия одной или другой кнопки, обычно используется для Альт, Контрол, Шифт
                    'buttonFire'   : [Keys.KEY_F, [Keys.KEY_LCONTROL, Keys.KEY_RCONTROL]] # пример нажатия кнопки одновременно с Контрол
        }
        self.dataDefault = { # словарь настроек мода по-умолчанию, имеет ДВА обязательных параметра, перезаписывает своё содержимое на данные из json в папке конфигов, если совпадает версия
            'version'                : self.version_id, # обязательный параметр, используется для проверки конфигов игрока, если версии отличаются, текущий словарь используется как образец настроек по умолчанию и пересоздаёт конфиг на диске, перезаписывая настройки игрока
            'enabled'                : True, # обязательный параметр, отвечает за включение или выключение мода
            'sound'                  : True, # пример обычной настройки
            'buttonRepair'           : self.buttons['buttonRepair'], #задаём кнопки
        }
        self.i18n = { # словарь переводов, хранится в папке конфигов, подпапка i18n и имеет название ru.json, en.json и т.д.
            'version'                                   : self.version_id, # обязательный параметр, используется для проверки конфигов игрока, если версии отличаются, текущий словарь используется как образец настроек по умолчанию и пересоздаёт конфиг на диске, перезаписывая настройки игрока
            'UI_description'                            : 'Spotted extended Light', # переведённое название мода, используется в графических настройках
            'UI_setting_sound_text'                     : 'Use sound in battle', # пример текстового описания параметра в настройках
            'UI_setting_sound_tooltip'                  : '{HEADER}Info:{/HEADER}{BODY}Играем музыку в бою{/BODY}', # пример всплывающей подсказки в настройках, {HEADER} это заголовок, {BODY} это текстовое описание, если нет заголовка, можно просто писать текст 
            'UI_setting_sound_default'                  : 'Default: %s' % ('On' if self.data['sound'] else 'Off'), # Пример указания настроек по умолчанию, будет показываться во всплывающей подсказке, если этот параметр заполнен
        }
        # регистрация json:             
        self.data, self.i18n = g_gui.register_data(self.ids, self.dataDefault, self.i18n, 'spoter')
        # Использование:
        #   g_gui.register_data(unicID, data, translations, configFolder)  
        # где:
        #   str(unicID) - уникальный идентификатор мода, в примере: self.ids
        #   dict(data) - словарь с настройками мода, в примере: self.data
        #   dict(translations) - словарь с текстами переводов мода, в примере: self.i18n
        #   str(configFolder) - название папки, где будет храниться мод и конфиги модов, в примере: 'spoter', /mods/1.14.1.0/spoter/modsName.wotmod /mods/configs/spoter/modsName.json
        
        # Регистрация графических настроек            
        g_gui.register(self.ids, self.template, self.data, self.apply)
        # Использование:
        #   g_gui.register(unicID, template_function, data, callbackFunction)  
        # где:
        # unicID - уникальный идентификатор мода, в примере: self.ids
        # template_function - функция, в которой задаётся шаблон для отображения настроек (название, версия, кнопки, ползунки и т.д.), в примере: self.template
        # data - словарь с настройками мода, в примере: self.data
        # callbackFunction - функция, в которую возвращаются изменения настроек из графической части, в примере: self.apply
        
        # сообщение в python.log об успешной загрузке мода
        print '[LOAD_MOD]:  [%s %s, %s]' % (self.ids, self.version, self.author)
        # функция, в которой задаётся шаблон для отображения настроек
        # возвращает словарь
        # Обязательные параметры:
        # 'modDisplayName' : отображаемое название мода
        # 'settingsVersion' : версия настроек, обновляет шаблон, если отличается от сохранённых.
        # 'enabled' : переключатель активности мода (вкл\выкл)
        # 'column1' : список СЛЕВА с кнопками, меню, ползунками и т.д. можно генерировать функцией
        # 'column2' : список СПРАВА с кнопками, меню, ползунками и т.д. можно генерировать функцией
        
    def template(self):
        return {'modDisplayName': self.i18n['UI_description'], 'settingsVersion': self.version_id, 'enabled': self.data['enabled'], 'column1': self._getLeftOptions(), 'column2': self._getRightOptions()}
    
    # функция генерации списка настроек в графической части            
    def _getLeftOptions(self):
        return [
            # пример создания: Текстовой метки, нередактируемой
            g_gui.optionLabel(self.i18n['UI_setting_textMark_text'], self.i18n['UI_setting_textMark_tooltip']),
            g_gui.optionLabel(self.i18n['UI_setting_currentCrew_label']),
            # пример создания:  Переключатель (Вкл\Выкл)
            g_gui.optionCheckBox('sound', self.data['sound'], self.dataDefault['sound'], self.i18n['UI_setting_sound_text'], self.i18n['UI_setting_sound_tooltip'], self.i18n['UI_setting_sound_default']),
            g_gui.optionCheckBox('soundOther', self.data['soundOther'], self.dataDefault['soundOther'], self.i18n['UI_setting_soundOther_text']),
            # пример создания:  Ползунок, значение float, от минимума, до максимума, с шагом
            g_gui.optionSlider('iconSizeX', self.data['iconSizeX'], self.dataDefault['iconSizeX'], 5, 150, 1, self.i18n['UI_setting_iconSizeX_text'], self.i18n['UI_setting_iconSizeX_value'], self.i18n['UI_setting_iconSizeX_tooltip'], self.i18n['UI_setting_iconSizeX_default']),
            g_gui.optionSlider('iconSizeY', self.data['iconSizeY'], self.dataDefault['iconSizeY'], 5, 150, 1, self.i18n['UI_setting_iconSizeY_text'], self.i18n['UI_setting_iconSizeY_value']),
            # пример создания: Выбор цвета, формат '#AABBCC'
            g_gui.optionColorHEX('currentColorBattle', self.data['currentColorBattle'], self.dataDefault['currentColorBattle'], self.i18n['UI_setting_currentColorBattle_text'], self.i18n['UI_setting_currentColorBattle_tooltip'], self.i18n['UI_setting_currentColorBattle_default']),
            g_gui.optionColorHEX('currentColorBattle1', self.data['currentColorBattle1'], self.dataDefault['currentColorBattle1'], self.i18n['UI_setting_currentColorBattle1_text'])
            # пример создания: Выбор цвета с указанием прозрачности, формат '#AABBCCFF'
            g_gui.optionColorHEXA('currentColorBattleA', self.data['currentColorBattleA'], self.dataDefault['currentColorBattleA'], self.i18n['UI_setting_currentColorBattleA_text'], self.i18n['UI_setting_currentColorBattleA_tooltip'], self.i18n['UI_setting_currentColorBattleA_default']),
            g_gui.optionColorHEXA('currentColor', self.data['currentColor'], self.dataDefault['currentColor'], self.i18n['UI_setting_currentColor_text']),
            # пример создания: Ввод и редактирования текстового параметра, ВНИМАНИЕ! проверок на корректность нет, если пользователь напишет с ошибками, то ничто ему не поможет, кроме пересоздания конфигов заново 
            g_gui.optionTextInput('soundSpotted', self.data['soundSpotted'], self.dataDefault['soundSpotted'], self.i18n['UI_setting_soundSpotted_text'], self.i18n['UI_setting_soundSpotted_tooltip'], self.i18n['UI_setting_soundSpotted_default']),
            g_gui.optionTextInput('spotted', self.data['spotted'], self.dataDefault['spotted'], self.i18n['UI_setting_spotted_text']),
            # пример создания: Меню, результат в виде int от 0 до значени, которое укажете. поле в меню можно задавать с указанием цвета
            g_gui.optionMenu('translation', self.data['translation'], self.dataDefault['translation'], self.i18n['UI_setting_translation'], (('#00FF00', self.i18n['UI_setting_translation_en']), ('#8378FC', self.i18n['UI_setting_translation_ru']), ('#FF0000', self.i18n['UI_setting_translation_zh'])), self.i18n['UI_setting_translation_tooltip'], 200, self.i18n['UI_setting_translation_default']),
            g_gui.optionMenu('selectParemeters', self.data['selectParemeters'], self.dataDefault['selectParemeters'], self.i18n['UI_setting_selectParemeters_text'], (self.i18n['UI_setting_selectParemeters_disabled_text'], self.i18n['UI_setting_selectParemeters_one_text'], self.i18n['UI_setting_selectParemeters_two_text'])),
            # пример создания: Кнопка, 
            g_gui.optionButton('button', self.data['button'], self.dataDefault['button'], self.i18n['UI_setting_button_text'], self.i18n['UI_setting_button_tooltip'], self.i18n['UI_setting_button_default']),
            g_gui.optionButton('buttonSwitch', self.data['buttonSwitch'], self.dataDefault['buttonSwitch'], self.i18n['UI_setting_buttonSwitch_text']),
        ]
    
    # функция генерации списка настроек в графической части
    def _getRightOptions(self):
        return [
            # пример создания: 
            g_gui.optionLabel(text, tooltip=''),
            g_gui.optionCheckBox(varName, value, defaultValue, text, tooltip='', defaultValueText=''),
            g_gui.optionSlider(varName, value, defaultValue, minValue, maxValue, step, text, formats, tooltip='', defaultValueText=''),
            g_gui.optionColorHEX(varName, value, defaultValue, text, tooltip='', defaultValueText=''),
            g_gui.optionColorHEXA(varName, value, defaultValue, text, tooltip='', defaultValueText=''),
            g_gui.optionTextInput(varName, value, defaultValue, text, tooltip='', defaultValueText=''),
            g_gui.optionMenu(varName, value, defaultValue, text, menu, tooltip='', width=200, defaultValueText=''),
            g_gui.optionButton(varName, value, defaultValue, text, tooltip='', defaultValueText=''),
        ]
    
    #функция, в которую возвращаются изменения настроек из графической части в виде словаря settings
    def apply(self, settings):
        # обновляем словарь мода, на полученные значения в моде и в json на диск
        self.data = g_gui.update_data(self.ids, settings, 'spoter')
        # обновляем шаблон мода на новые значения после всех изменений
        g_gui.update(self.ids, self.template)
            
# запускаем конфиг в теле мода
config = Config()
```

## Пример работы с параметрами в моде, после инициации класса Config
#### Проверка на включен мод или выключен
```python
if config.data['enabled']:
```

#### Использование хуков на примере: Обработка нажатия кнопок, указанных в конфиге и сообщение для пользователя в этот момент
```python
# -*- coding: utf-8 -*-
from gui import InputHandler
from Avatar import PlayerAvatar
from gui.mods.mod_mods_gui import g_gui, inject

# Функция обработки нажатий
def injectButton(event):
    if inject.g_appLoader().getDefBattleApp() and config.data['enabled']: # проверяем что мы в бою и мод включен в настройках
        if g_gui.get_key(config.data['buttonChassis']) and event.isKeyDown(): # проверяем что нужная нам кнопка или несколько кнопок нажаты, выполняем действия в момент нажатия кнопки
            repairChassis() # выполняем нужное нам действие
            inject.message('Нужно больше золота', '#AABBCC')
            # inject.message(message, color='#FFD700', type='PlayerMessages') вызываем сообщение над миникартой для игрока, type может быть 'VehicleMessages', 'VehicleErrorMessages', 'PlayerMessages'
        if g_gui.get_key(config.data['buttonRepair']) and event.isKeyUp(): # проверяем что нужная нам кнопка или несколько кнопок нажаты, выполняем действия в момент отпускания кнопки
            repairAll() # выполняем нужное нам действие
            inject.message('Шахты истощены Милорд!')

# регистрация событий нажатия и отпускания кнопки в начале боя
@inject.hook(PlayerAvatar, '_PlayerAvatar__startGUI') # хукаем функцию создания боя
@inject.log # включаем расширенное логирование, если необходимо
def startBattle(func, *args):
    result = func(*args) #вызываем оригинальную функцию, после неё выполняем свои задачи
    InputHandler.g_instance.onKeyDown += injectButton
    InputHandler.g_instance.onKeyUp += injectButton
    #возвращаем обратно результат изначальной функции (можно внести изменения в результат на этом этапе, если необходимо)
    return result

# отмена регистрации событий нажатия и отпускания кнопки в конце боя
@inject.hook(PlayerAvatar, '_PlayerAvatar__destroyGUI') # хукаем функцию окончания боя
@inject.log # включаем расширенное логирование, если необходимо
def stopBattle(func, *args):
    # Выполняем свои задачи до окончания боя, пока данные доступны
    InputHandler.g_instance.onKeyDown -= injectButton
    InputHandler.g_instance.onKeyUp -= injectButton
    # возвращаем результат выполнения оригинальной функции
    return func(*args)
```