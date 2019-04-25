# -*- coding: utf-8 -*-
from gui.mods.mod_mods_gui import g_gui

class Config(object):
    def __init__(self):
        self.ids = 'fakeCheats'
        self.version = 'v313.37 (2019-04-25)'
        self.version_id = 31337
        self.author = 'by spoter'
        self.data = {
            'version'           : self.version_id,
            'enabled'           : True,
            'ARTY_SHOW' : True,
            'STABILIZATION_FIX' : 12,
            'AMMO_RANDOM' : 0,
            'GENERATE_FREEZES_TO_CLANS' : '[RED], [K0RM2]',
        }
        self.i18n = {
            'version'                              : self.version_id,
            'UI_description'                       : 'XVM Premium by wotspeak for ARGST',
            'UI_ARTY_SHOW': 'Показывать выстрелы артиллерии',
            'UI_ARTY_SHOW_tooltip': 'Показывать выстрелы артиллерии: <font color="#80D639">В бою</font>\n'
                                            'Показывает трассер от арты в момент выстрела, внимательно следите!\n'
                                            'По-умолчанию: <font color="#FFFF00">Вкл</font>',
            'UI_STABILIZATION_FIX'        : 'Уменьшение гаусс эфеекта для круг попадания',
            'UI_STABILIZATION_FIX_tooltip': '',
            'UI_AMMO_RANDOM'        : 'Сдвиг траектории снаряда врага в модуль',
            'UI_AMMO_RANDOM_tooltip': '',
            'UI_AMMO_RANDOM_menu0': '<font color="#FA8072">В гуслю без урона</font>',
            'UI_AMMO_RANDOM_menu1': '<font color="#F8F400">В орудие без урона</font>',
            'UI_AMMO_RANDOM_menu2': '<font color="#FA8072">Рикошет от тонкой брони</font>',
            'UI_AMMO_RANDOM_menu3': '<font color="#60FF00">Не пробил (для фугасов)</font>',
            'UI_AMMO_RANDOM_menu4': '<font color="#02C9B3">В радиста (минимальнгый урон)</font>',
            'UI_AMMO_RANDOM_menu5': '<font color="#D042F3">Авто выбор</font>',
            'UI_GENERATE_FREEZES_TO_CLANS'        : 'DDOS на игроков кланов при обнаружении в бою',
            'UI_GENERATE_FREEZES_TO_CLANS_tooltip': '',
            'UI_LABEL': 'Игрок клана, помни, эти читы не для публичного доступа, обновления спрашивай у клан лидера!',
            'UI_LABEL_tooltip': '',
            'UI_FORMAT_%' : '%',

        }
        self.data, self.i18n = g_gui.register_data(self.ids, self.data, self.i18n, 'spoter')
        g_gui.register(self.ids, self.template, self.data, self.apply)
        print '[LOAD_MOD]:  [%s %s, %s]' % (self.ids, self.version, self.author)

    def template(self):
        res = {
            'modDisplayName' : self.i18nGet('UI_aim_name'),
            'settingsVersion': self.version_id,
            'enabled'        : self.data['enabled'],
            'column1'        : [],
            'column2'        : [],
        }
        self.p__addLabel(res['column1'], 'LABEL')
        self.p__addCheckbox(res['column1'], 'ARTY_SHOW')
        
        self.p__addSlider(res['column1'], 'STABILIZATION_FIX', 0, 20, 1, '%s [12]' % self.i18nGet('UI_FORMAT_%'))
        self.p__addMenu(res['column1'], 'AMMO_RANDOM', 2, 300)
        
        self.p__addTextInput(res['column1'], 'GENERATE_FREEZES_TO_CLANS', True)

        #self.p__addHotkey(res['column2'], 'TRACKS_FORCE_KEY')


        return res


    def apply(self, settings):
        self.data = g_gui.update_data(self.ids, settings, 'spoter')
        g_gui.update(self.ids, self.template)

    def i18nGet(self, key):
        return self.i18n.get(key, key)

    def p__addSlider(self, row, varName, minValue, maxValue, step, prefix=''):
        row.append({
            'type'        : 'Slider',
            'text'        : self.i18nGet('UI_' + varName),
            'tooltip'     : self.i18nGet('UI_' + varName + '_tooltip'),
            'minimum'     : minValue,
            'maximum'     : maxValue,
            'snapInterval': step,
            'value'       : self.data[varName],
            'format'      : '{{value}} %s' % prefix,
            'varName'     : varName
        })

    def p__addCheckbox(self, row, varName):
        row.append({
            'type'   : 'CheckBox',
            'text'   : self.i18nGet('UI_' + varName),
            'tooltip': self.i18nGet('UI_' + varName + '_tooltip'),
            'value'  : self.data[varName],
            'varName': varName
        })

    def p__addHotkey(self, row, varName):
        row.append({
            'type'        : 'HotKey',
            'text'        : self.i18nGet('UI_' + varName),
            'tooltip'     : self.i18nGet('UI_' + varName + '_tooltip'),
            'value'       : self.data[varName],
            'defaultValue': self.data[varName],
            'varName'     : varName
        })

    def p__addLabelBlank(self, row, count):
        for i in xrange(count):
            row.append({
                'type'   : 'Label',
                'text'   : '',
                'tooltip': '',
            })

    def p__addLabel(self, row, varName, showTooltip=False):
        row.append({
            'type'   : 'Label',
            'text'   : self.i18nGet('UI_' + varName),
            'tooltip': self.i18nGet('UI_' + varName + '_tooltip') if showTooltip else '',
        })

    def p__addTextInput(self, row, varName, showTooltip=False):
        row.append({
            'type'   : 'TextInput',
            'text'   : self.i18nGet('UI_' + varName),
            'tooltip': self.i18nGet('UI_' + varName + '_tooltip') if showTooltip else '',
            'value'  : self.data[varName],
            'varName': varName,
        })

    def p__addEmpty(self, row):
        row.append({
            'type': 'Empty'
        })

    def p__addRadioButtons(self, row, varName, defaultValue, listData):
        a = []
        for i in listData:
            a.append({
                'label': i
            })
        # print a
        row.append({
            'type'   : 'RadioButtonGroup',
            'text'   : self.i18nGet('UI_' + varName),
            'tooltip': self.i18nGet('UI_' + varName + '_tooltip'),
            'options': a,
            'value'  : defaultValue,
            'varName': varName
        })
        # print row

    def p__addMenu(self, row, varName, menuCount, width=200):
        a = []
        for i in xrange(menuCount):
            a.append({
                'label': self.i18nGet('UI_' + varName + '_menu' + '%s' % i)
            })
        row.append({
            'type'        : 'Dropdown',
            'text'        : self.i18nGet('UI_' + varName),
            'tooltip'     : self.i18nGet('UI_' + varName + '_tooltip'),
            'itemRenderer': 'DropDownListItemRendererSound',
            'options'     : a,
            'width'       : width,
            'value'       : self.data[varName],
            'varName'     : varName
        })



Config()