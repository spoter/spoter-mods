# -*- coding: utf-8 -*-

import Math

import BigWorld
import Keys
import game
from Avatar import PlayerAvatar
from gui import InputHandler
from gui.mods.mod_mods_gui import g_gui, inject
from gui.shared.gui_items import Vehicle
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME
# noinspection PyProtectedMember
from tutorial.control.battle.functional import _StaticObjectMarker3D


class Config(object):
    def __init__(self):
        self.ids = 'spotMarks'
        self.author = 'by spoter'
        self.version = 'v1.12 (2019-09-20)'
        self.version_id = 112
        self.buttons = {
            'buttonShow': [Keys.KEY_P, [Keys.KEY_LALT, Keys.KEY_RALT]],
            'buttonMark': [Keys.KEY_SLASH, [Keys.KEY_LALT, Keys.KEY_RALT]],
        }
        self.data = {
            'version'            : self.version_id,
            'enabled'            : True,
            'showOnStartBattle'  : True,
            'showOnlyLightTanks' : False,
            'showBattleGreetings': True,
            'buttonShow'         : self.buttons['buttonShow'],
        }
        self.i18n = {
            'version'                               : self.version_id,
            'UI_description'                        : 'Passive Spot Marks',
            'UI_setting_buttonShow_text'            : 'Button: Show spot marks',
            'UI_setting_buttonShow_tooltip'         : '',
            'UI_setting_showOnStartBattle_text'     : 'Show on Start Battle',
            'UI_setting_showOnStartBattle_tooltip'  : '',
            'UI_setting_showOnlyLightTanks_text'    : 'Show to Light Tank only',
            'UI_setting_showOnlyLightTanks_tooltip' : '',
            'UI_setting_showBattleGreetings_text'   : 'Show greetings on start battle',
            'UI_setting_showBattleGreetings_tooltip': '',
            'UI_message_on'                         : 'Passive Spot Marks: ON',
            'UI_message_off'                        : 'Passive Spot Marks: OFF',

        }
        if inject.ru:
            self.i18n = {
                'version'                               : self.version_id,
                'UI_description'                        : 'b4it - Точки пассивного засвета',
                'UI_setting_buttonShow_text'            : 'Кнопка: Показать точки',
                'UI_setting_buttonShow_tooltip'         : '',
                'UI_setting_showOnStartBattle_text'     : 'Показывать с начала боя',
                'UI_setting_showOnStartBattle_tooltip'  : '',
                'UI_setting_showOnlyLightTanks_text'    : 'Показывать только для лёгких танков',
                'UI_setting_showOnlyLightTanks_tooltip' : '',
                'UI_setting_showBattleGreetings_text'   : 'Показывать приветствие в начале боя',
                'UI_setting_showBattleGreetings_tooltip': '',
                'UI_message_on'                         : 'Точки пассивного засвета: ВКЛ',
                'UI_message_off'                        : 'Точки пассивного засвета: ВЫКЛ',
            }
        self.data, self.i18n = g_gui.register_data(self.ids, self.data, self.i18n, 'spoter')
        g_gui.register(self.ids, self.template, self.data, self.apply)
        print '[LOAD_MOD]:  [%s %s, %s]' % (self.ids, self.version, self.author)

    def template(self):
        return {
            'modDisplayName' : self.i18n['UI_description'],
            'settingsVersion': self.version_id,
            'enabled'        : self.data['enabled'],
            'column1'        : [{
                'type'        : 'HotKey',
                'text'        : self.i18n['UI_setting_buttonShow_text'],
                'tooltip'     : self.i18n['UI_setting_buttonShow_tooltip'],
                'value'       : self.data['buttonShow'],
                'defaultValue': self.buttons['buttonShow'],
                'varName'     : 'buttonShow'
            }],
            'column2'        : [{
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_setting_showOnStartBattle_text'],
                'value'  : self.data['showOnStartBattle'],
                'tooltip': self.i18n['UI_setting_showOnStartBattle_tooltip'],
                'varName': 'showOnStartBattle'
            }, {
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_setting_showOnlyLightTanks_text'],
                'value'  : self.data['showOnlyLightTanks'],
                'tooltip': self.i18n['UI_setting_showOnlyLightTanks_tooltip'],
                'varName': 'showOnlyLightTanks'
            }, {
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_setting_showBattleGreetings_text'],
                'value'  : self.data['showBattleGreetings'],
                'tooltip': self.i18n['UI_setting_showBattleGreetings_tooltip'],
                'varName': 'showBattleGreetings'
            }]
        }

    def apply(self, settings):
        self.data = g_gui.update_data(self.ids, settings, 'spoter')
        g_gui.update(self.ids, self.template)


class MapsData(object):
    def __init__(self):
        self.ids = 'spotMarksMapsData'
        self.ver = 100
        self.data = {
            'version'               : self.ver,
            '_MapName'              : (
                (['ctf', 'base1', 'coordinates in (x,y,z)', (0.01, 0.01, 0.01)], ['ctf', 'base2', 'coordinates in (x,y,z)', (0.01, 0.01, 0.01)]),
                (['domination', 'base1', 'coordinates in (x,y,z)', (0.01, 0.01, 0.01)], ['domination', 'base2', 'coordinates in (x,y,z)', (0.01, 0.01, 0.01)]),
                (['assault', 'base1', 'coordinates in (x,y,z)', (0.01, 0.01, 0.01)], ['assault', 'base2', 'coordinates in (x,y,z)', (0.01, 0.01, 0.01)]),
            ),
            '01_karelia'            : (
                # 'ctf'
                ([
                     (371.917, 22.0266, -177.35),
                     (493.51, 30.6817, 70.0026),
                     (-233.433, 23.2223, 38.3076),
                     (-62.6051, 19.2882, 199.456),
                     (93.672, 22.0219, 79.9208),
                     (185.491, 39.162, 288.741),
                     (-129.531, 19.2147, 99.3572),
                     (41.7303, 19.8767, 113.237)
                 ],
                 [
                     (105.3, 23.4566, -439.695),
                     (290.918, 26.3094, -415.662),
                     (-35.4793, 21.0322, -122.507),
                     (-158.128, 20.4884, 11.6587),
                     (-318.479, 37.2686, 138.426)
                 ]),
                # ([(371.917, 22.0266, -177.35), (-38.7174, 20.6221, 3.88532), (-62.323, 21.1302, -64.2737), (-484.587, 41.6859, -39.0637), (277.149, 39.0939, 189.29), (287.932, 54.9766, 412.636), (167.194, 41.5668, 351.833)], [(-38.7174, 20.6221, 3.88532), (-62.323, 21.1302, -64.2737), (-484.587, 41.6859, -39.0637), (-485.664, 65.4323, -469.358), (-429.249, 35.6641, -152.877), (277.149, 39.0939, 189.29), (287.932, 54.9766, 412.636), (167.194, 41.5668, 351.833), (-116.654, 20.325, -22.963)]),
                # 'domination'
                ([], []),
                # 'assault'
                ([
                     (-287.143, 32.8441, 53.257),
                     (39.9227, 26.4455, -171.349),
                     (0.919496, 20.3146, 43.3204),
                     (-277.453, 37.7346, -186.563),
                     (-484.533, 40.6582, -33.9339)
                 ],
                 [
                     (-183.915, 39.7661, -283.818),
                     (-165.707, 25.4594, -182.162),
                     (284.984, 37.8261, 183.869)
                 ])
            ),
            '02_malinovka'          : (
                # 'ctf'
                ([
                     (-305.11, 9.37727, -234.568),
                     (-16.1777, 4.78391, 26.5759),
                     (154.91, 16.3431, -37.902),
                     (139.304, 25.3862, 155.417),
                     (3.41607, 21.3172, 174.173),
                     (-27.8981, 25.5284, 255.717)
                 ], [
                     (-249.076, 9.15585, -22.349),
                     (-155.409, 10.4096, 21.397),
                     (-95.3846, 9.49698, 3.06379),
                     (-307.269, 9.35208, -230.241),
                     (-96.0581, 14.8748, 152.325),
                     (136.301, 25.4225, 160.916),
                     (496.736, 60.5611, 394.617),
                     (-27.8981, 25.5284, 255.717)
                 ]),
                # ([(-87.4027, 9.79008, -28.7285), (11.8839, 9.93128, -144.129), (-260.851, 9.77789, -405.307), (158.749, 16.6823, -27.0007), (175.761, 19.4496, 65.8675), (139.739, 25.1161, 149.679), (421.953, 55.5026, 301.764)], [(-124.134, 9.59206, 7.44205), (-90.9091, 9.82202, -27.7949), (-249.638, 9.07871, -22.1089), (-120.229, 14.4694, 157.536), (-314.215, 9.33623, -238.975), (0.0066656, 21.3506, 188.668), (133.746, 25.163, 163.649), (339.175, 55.3964, 380.807)]),
                # 'domination'
                ([
                     (302.796, 27.2025, 49.8634),
                     (139.142, 25.382, 154.773),
                     (-27.8981, 25.5284, 255.717)
                 ], [
                     (135.234, 25.3755, 161.326),
                     (-27.8981, 25.5284, 255.717)
                 ]),
                # 'assault'
                ([], [])
            ),
            '03_campania_big'       : (
                # 'ctf'
                ([], []),
                # 'domination'
                ([], []),
                # 'assault'
                ([], []),
            ),
            '04_himmelsdorf'        : (
                # 'ctf'
                ([], []),
                # 'domination'
                ([], []),
                # 'assault'
                ([], []),
            ),
            '05_prohorovka'         : (
                # 'ctf'
                ([], []),
                # ([(-344.214, 9.90543, 73.9396), (-495.056, 21.9927, 39.8306), (-461.423, 13.7267, 38.0076), (33.3768, 10.228, 39.3744), (31.4288, 10.6367, -6.57884), (326.377, 10.0794, 8.4657), (466.592, 30.7791, -102.303), (472.715, 32.018, -77.1577)], [(-338.711, 10.5767, -96.6661), (-495.83, 18.795, -125.446), (-495.534, 21.9519, 35.8387), (40.3161, 10.1472, -17.019), (208.74, 9.9951, -26.0816), (230.982, 9.70868, -64.6931), (500.084, 37.1061, -196.039)]),
                # 'domination'
                ([], []),
                # 'assault'
                ([], [])
            ),
            '06_ensk'               : (
                # 'ctf'
                ([], []),
                # 'domination'
                ([], []),
                # 'assault'
                ([], []),
            ),
            '07_lakeville'          : (
                # 'ctf'
                ([], []),
                # ([(-80.069, 6.41545, 78.2053), (179.73, -4.8691, 150.418), (141.34, -4.91541, 9.93952), (134.608, -5.00138, -28.1786), (118.469, 14.0239, -367.363), (-317.537, 22.5343, -10.3654), (-344.361, 8.77602, 282.413), (17.7711, 7.2991, 369.066), (-265.335, 15.0933, 326.87)], [(-78.5001, 7.1412, -67.6482), (107.257, -4.84451, -122.466), (139.031, -4.97592, 64.8037), (-17.5822, 6.63461, 293.195), (7.99448, 8.94406, -371.503), (-317.447, 23.3271, -13.9052), (-306.809, 11.7696, -296.899), (147.594, -4.78767, -92.2459)]),
                # 'domination'
                ([], []),
                # 'assault'
                ([], [])
            ),
            '08_ruinberg'           : (
                # 'ctf'
                ([], []),
                # 'domination'
                ([], []),
                # 'assault'
                ([], []),
            ),
            '10_hills'              : (
                # 'ctf'
                ([], []),
                # ([(279.34, 25.2322, 187.455), (180.673, 19.794, 216.029), (-338.968, 7.8405, -207.874), (-326.886, 12.1465, 3.33471), (29.4907, 27.6254, 110.743), (9.95471, 27.8499, 103.174)], [(74.4703, 30.1248, -76.3657), (-309.91, 10.983, -43.5275), (-241.558, 1.54507, -5.77622)]),
                # 'domination'
                ([], []),
                # 'assault'
                ([], [])
            ),
            '11_murovanka'          : (
                # 'ctf'
                ([], []),
                # ([(155.623, 7.50984, 50.7796), (-445.965, 12.3073, 181.356)], [(150.473, 7.47175, 34.13), (-437.529, 14.4005, -190.919)]),
                # 'domination'
                ([], []),
                # 'assault'
                ([], [])
            ),
            '13_erlenberg'          : (
                # 'ctf'
                ([], []),
                # ([(97.0585, 1.73174, -430.833), (282.857, 12.2049, 91.9694), (331.927, 20.4223, 83.8991), (484.342, 29.5171, -40.1278), (368.287, 21.9487, 103.998), (-65.5456, 0.13398, -3.66104), (7.30499, -0.181949, 131.043), (-484.654, 16.7327, -165.991), (73.3182, -0.0491436, 192.941)], [(-492.561, 18.6186, -190.137), (-279.068, 8.99187, -117.066), (199.961, 8.56291, -446.199)], [(-299.465, 11.811, 24.4044), (-41.6205, 0.0402616, 2.57273), (281.108, 12.2053, 97.6094), (309.347, 13.1147, -16.7171), (493.604, 28.479, -12.9697), (-363.021, 12.5469, 192.343), (73.3182, -0.0491436, 192.941)]),
                # 'domination'
                ([], []),
                # 'assault'
                ([], [])

            ),
            '14_siegfried_line'     : (
                # 'ctf'
                ([], []),
                # ([(422.836, -0.536739, -222.759), (-31.5272, -4.01621, -89.9775), (-167.013, -13.3798, -157.023)], [(-239.913, -11.1651, 176.155)]),
                # 'domination'
                ([], []),
                # 'assault'
                ([], [])
            ),
            '17_munchen'            : (
                # 'ctf'
                ([], []),
                # 'domination'
                ([], []),
                # 'assault'
                ([], []),
            ),
            '18_cliff'              : (
                # 'ctf'
                ([], []),
                # 'domination'
                ([], []),
                # 'assault'
                ([], []),
            ),
            '19_monastery'          : (
                # 'ctf'
                ([], []),
                # ([], [(326.01, -4.90546, 111.441), (400.357, 15.8451, 49.8318)]),
                # 'domination'
                ([], []),
                # 'assault'
                ([], [])
            ),
            '22_slough'             : (
                # 'ctf'
                ([], []),
                # ([(177.294, 5.38809, 269.203), (217.984, -3.05096, 95.3409), (-149.134, 5.96888, 109.835), (-304.599, 5.18439, 59.5462), (-94.8094, -0.0841094, -90.335)], [(39.9612, 6.30066, -197.249), (-18.8949, 6.72953, -274.144), (-108.145, -2.36425, -119.928), (199.16, 0.811627, 138.875), (337.705, -4.19894, -79.4721), (-40.4363, -0.287934, -447.344)]),
                ([], []),
                ([], [])
            ),
            '23_westfeld'           : (
                # 'ctf'
                ([], []),
                # 'domination'
                ([], []),
                # 'assault'
                ([], []),
            ),
            '28_desert'             : (
                # 'ctf'
                ([], []),
                # 'domination'
                ([], []),
                # 'assault'
                ([], []),
            ),
            '29_el_hallouf'         : (
                # 'ctf'
                ([], []),
                # ([(-486.017, 61.3318, 497.057), (-328.721, 61.5027, 489.476), (-362.563, 64.425, 494.564), (-32.2327, 7.09785, 11.9004), (-35.7119, 7.16327, 12.3836)], [(-328.721, 61.5027, 489.476), (-362.563, 64.425, 494.564), (5.33137, 21.91, -46.4244), (-162.107, 32.0237, 155.03)]),
                # 'domination'
                ([], []),
                # 'assault'
                ([], [])
            ),
            '31_airfield'           : (
                # 'ctf'
                ([], []),
                # ([(-31.5241, 0.970781, -83.4666), (3.5211, -1.84615, 12.973)], [(-34.295, 0.83001, -83.2242)]),
                # 'domination'
                ([], []),
                # 'assault'
                ([], [])
            ),
            '33_fjord'              : (
                # 'ctf'
                ([], []),
                # ([(135.227, 22.2955, 89.9605), (103.883, 22.457, 189.681), (109.025, 26.6079, 246.806)], [(150.602, 41.8268, 203.492), (8.75892, 19.3056, 304.72), (67.9457, 25.8051, 253.97), (-79.3051, 15.8195, 39.5272)]),
                # 'domination'
                ([], []),
                # 'assault'
                ([], [])
            ),
            '34_redshire'           : (
                # 'ctf'
                ([], []),
                # ([(126.305, 7.31473, 32.6867), (161.712, 15.351, 157.482), (302.918, 21.5731, -62.1638), (322.253, 23.2771, -70.3704), (-466.862, 9.46229, -156.063), (-337.777, 14.8228, 12.9962), (-245.88, 22.7605, 10.1585)], [(102.524, 13.2774, 137.88), (144.298, 14.9232, 106.977), (332.268, 22.6426, 24.1643), (-250.12, 22.4691, 13.0845)]),
                # 'domination'
                ([], []),
                # 'assault'
                ([], [])
            ),
            '35_steppes'            : (
                # 'ctf'
                ([], []),
                # ([(35.6068, 0.0675564, -46.5849), (157.85, 3.73304, 87.4139), (-176.765, 0.660691, -114.414), (242.4, 14.658, -495.36), (210.151, 16.0987, -499.737), (146.787, 16.9983, -476.356), (-12.0513, 8.34863, -368.383)], [(-98.0384, -0.0751553, 62.2948), (157.479, 3.88404, 94), (-177.38, 0.775795, -110.017), (-173.86, 10.8168, 495.924), (-251.634, 10.0065, 486.611), (-474.831, 0.864808, 10.2991)]),
                # 'domination'
                ([], []),
                # 'assault'
                ([], [])
            ),
            '36_fishing_bay'        : (
                # 'ctf'
                ([], []),
                # ([(133.974, 6.85865, 49.459), (411.329, -4.12651, 191.46), (34.2371, 13.9362, 90.92), (-403.763, 19.8049, -80.2957), (-452.331, 19.5812, 164.5), (-249.521, 22.452, -197.189), (-141.295, 15.3926, -177.869)], [(-286.443, 21.6917, -189.973), (-317.546, 15.6169, -46.9166), (24.2669, 16.692, 32.2045), (419.187, -2.86265, 18.0742), (-139.118, 15.1498, -180.467)]),
                # 'domination'
                ([], []),
                # 'assault'
                ([], [])
            ),
            '37_caucasus'           : (
                # 'ctf'
                ([], []),
                # ([(25.5246, 4.4959, 29.9133), (46.303, 4.23922, 38.728), (6.99784, 1.51318, 9.23373)], []),
                # 'domination'
                ([], []),
                # 'assault'
                ([], [])
            ),
            '38_mannerheim_line'    : (
                # 'ctf'
                ([], []),
                # ([(128.296, 1.72147, 125.157), (-69.62, -0.294984, 176.84)], [(43.5662, -0.166392, -111.62)]),
                # 'domination'
                ([], []),
                # 'assault'
                ([], [])
            ),
            '44_north_america'      : (
                # 'ctf'
                ([], []),
                # ([(-0.477468, -8.21883, -119.807), (-218.613, 1.5609, 90.1762), (-468.817, 5.25304, 117.361), (233.642, 3.67883, -298.718), (47.8273, 4.56921, -377.836)], [(78.3206, 8.92147, 250.58), (-84.8534, 1.96668, 198.953), (30.0013, -8.65191, 74.4488), (69.794, -8.0264, 39.9398), (13.7082, -8.88126, 97.9794), (363.354, 3.02559, -224.341), (441.397, -6.41367, -446.634), (484.374, 4.01481, 294.374), (360.324, 4.86011, 451.413), (43.4435, -7.88478, 51.7646)]),
                # 'domination'
                ([], []),
                # 'assault'
                ([], [])
            ),
            '45_north_america'      : (
                # 'ctf'
                ([], []),
                # ([(-55.3425, -12.1103, 104.711), (-136.59, -5.01845, 55.5173), (-249.617, -9.81604, 406.878), (-175.079, -12.493, 380.689), (-153.909, -10.8438, 238.452), (-445.197, 10.5543, 497.272), (-479.813, 17.5762, 110.136), (176.157, 10.0881, -302.609), (218.58, 5.88894, -96.1802), (329.724, 18.3151, 76.5674)], [(-227.16, -2.71393, 49.6255), (-138.595, -5.02132, 52.1804), (-452.208, 10.6209, 496.119), (-116.499, -10.3102, 373.299), (-380.97, 15.3026, -115.127), (195.918, 11.1476, -306.539), (-195.735, 5.60084, -328.22)]),
                # 'domination'
                ([], []),
                # 'assault'
                ([], [])
            ),
            '47_canada_a'           : (
                # 'ctf'
                ([], []),
                # ([(-34.5336, -10.4827, -37.644), (-174.666, -3.94227, -12.6122), (2.15952, -4.98555, -155.264), (332.364, -4.11723, -43.6303), (157.746, -3.54683, -397.114), (-208.535, -6.13352, -6.11681), (-362.545, -2.09773, -179.898), (-288.499, 4.8415, -326.605), (-310.364, 9.22021, -346.111), (-317.357, 9.05777, -362.333), (-142.629, -1.99022, 383.058)], [(198.336, -8.47199, 95.5213), (-94.0136, -4.74729, 228.926), (-311.123, 3.55459, 314.336), (-133.651, -7.25193, 162.553)]),
                # 'domination'
                ([], []),
                # 'assault'
                ([], [])
            ),
            '59_asia_great_wall'    : (
                # 'ctf'
                ([], []),
                # 'domination'
                ([], []),
                # 'assault'
                ([], []),
            ),
            '63_tundra'             : (
                # 'ctf'
                ([], []),
                # 'domination'
                ([], []),
                # 'assault'
                ([], []),
            ),
            '73_asia_korea'         : (
                # 'ctf'
                ([], []),
                # 'domination'
                ([], []),
                # 'assault'
                ([], []),
            ),
            '83_kharkiv'            : (
                # 'ctf'
                ([], []),
                # 'domination'
                ([], []),
                # 'assault'
                ([], []),
            ),
            '84_winter'             : (
                # 'ctf'
                ([], []),
                # ([(12.4407, 6.48786, 132.69)], [(-80.9593, 7.58463, 107.072)]),
                # 'domination'
                ([], []),
                # 'assault'
                ([], [])
            ),
            '86_himmelsdorf_winter' : (
                # 'ctf'
                ([], []),
                # 'domination'
                ([], []),
                # 'assault'
                ([], []),
            ),
            '90_minsk'              : (
                # 'ctf'
                ([], []),
                # 'domination'
                ([], []),
                # 'assault'
                ([], []),
            ),
            '92_stalingrad'         : (
                # 'ctf'
                ([], []),
                # 'domination'
                ([], []),
                # 'assault'
                ([], []),
            ),
            '95_lost_city'          : (
                # 'ctf'
                ([], []),
                # 'domination'
                ([], []),
                # 'assault'
                ([], []),
            ),
            '96_prohorovka_defense' : (
                # 'ctf'
                ([], []),
                # ([(-344.214, 9.90543, 73.9396), (-495.056, 21.9927, 39.8306), (-461.423, 13.7267, 38.0076), (33.3768, 10.228, 39.3744), (31.4288, 10.6367, -6.57884), (326.377, 10.0794, 8.4657), (466.592, 30.7791, -102.303), (472.715, 32.018, -77.1577)], [(-338.711, 10.5767, -96.6661), (-495.83, 18.795, -125.446), (-495.534, 21.9519, 35.8387), (40.3161, 10.1472, -17.019), (208.74, 9.9951, -26.0816), (230.982, 9.70868, -64.6931), (500.084, 37.1061, -196.039)]),
                # 'domination'
                ([], []),
                # 'assault'
                ([], [])
            ),
            '99_poland'             : (
                # 'ctf'
                ([], []),
                # 'domination'
                ([], []),
                # 'assault'
                ([], []),
            ),
            '100_thepit'            : (
                # 'ctf'
                ([], []),
                # 'domination'
                ([], []),
                # 'assault'
                ([], []),
            ),
            '101_dday'              : (
                # 'ctf'
                ([], []),
                # 'domination'
                ([], []),
                # 'assault'
                ([], []),
            ),
            '103_ruinberg_winter'   : (
                # 'ctf'
                ([], []),
                # 'domination'
                ([], []),
                # 'assault'
                ([], []),
            ),
            '112_eiffel_tower_ctf'  : (
                # 'ctf'
                ([], []),
                # ([(-132.88, 6.64391, 216.893), (-228.697, 10.0129, 141.979), (-131.821, 9.18746, 16.7217), (-349.143, 7.48962, 41.3225)], [(117.16, 5.99205, 253.052), (-3.94333, -0.925388, 355.432), (73.5, 9.03571, -14.6004), (320.302, 7.79187, 50.6466), (215.655, 9.8497, 139.428)]),
                # 'domination'
                ([], []),
                # 'assault'
                ([], [])
            ),
            '114_czech'             : (
                # 'ctf'
                ([], []),
                # 'domination'
                ([], []),
                # 'assault'
                ([], []),
            ),
            '115_sweden'            : (
                # 'ctf'
                ([], []),
                # 'domination'
                ([], []),
                # 'assault'
                ([], []),
            ),
            '208_bf_epic_normandy'  : (
                # 'ctf'
                ([], []),
                # 'domination'
                ([], []),
                # 'assault'
                ([], []),
            ),
            '212_epic_random_valley': (
                # 'ctf'
                ([], []),
                # 'domination'
                ([], []),
                # 'assault'
                ([], []),
            ),
            '217_er_alaska'         : (
                # 'ctf'
                ([], []),
                # 'domination'
                ([], []),
                # 'assault'
                ([], []),
            ),
            '222_er_clime'          : (
                # 'ctf'
                ([], []),
                # 'domination'
                ([], []),
                # 'assault'
                ([], []),
            ),

        }
        self.data = g_gui.register_data(self.ids, self.data, {}, 'spoter')[0]


class spotMarks(object):

    def __init__(self):
        self.player = None
        self.battleStarted = False
        self.mapSelected = ''
        self.points = []
        self.status = False
        self.height = 3.0

    def startBattle(self):
        if not config.data['enabled']: return
        self.player = BigWorld.player()
        del self.points[:]
        InputHandler.g_instance.onKeyDown += self.injectButton
        InputHandler.g_instance.onKeyUp += self.injectButton
        vehicle = self.player.arena.vehicles[self.player.playerVehicleID]
        if config.data['showOnlyLightTanks'] and Vehicle.getVehicleClassTag(self.player.getVehicleDescriptor().type.tags) != VEHICLE_CLASS_NAME.LIGHT_TANK: return
        self.height = float((vehicle['vehicleType'].hull.turretPositions[0] + vehicle['vehicleType'].turret.gunPosition + vehicle['vehicleType'].chassis.hullPosition).y)
        # 0 ctf, 1 domination, 2 assault
        # noinspection PyProtectedMember
        gameplayID = self.player.arena.arenaType._ArenaType__gameplayCfg['gameplayID']
        if self.mapSelected and self.mapSelected in mapsData.data and len(mapsData.data[self.mapSelected]) > 2:
            teamBase = self.player.guiSessionProvider.getArenaDP().getNumberOfTeam()
            teamBase -= 1
            if gameplayID < len(mapsData.data[self.mapSelected]) and len(mapsData.data[self.mapSelected][gameplayID]) > 1:
                for position in mapsData.data[self.mapSelected][gameplayID][teamBase]:
                    self.points.append(self.createModel(Math.Vector3(position)))
        if len(self.points):
            self.battleStarted = True
        self.status = config.data['showOnStartBattle']
        self.setVisible(self.status)
        self.checkBattleStarted()

    def checkBattleStarted(self):
        if hasattr(self.player, 'arena') and self.player.arena.period is 3:
            self.status = config.data['showOnStartBattle']
            self.setVisible(self.status)
            if config.data['showBattleGreetings'] and self.battleStarted:
                message = config.i18n['UI_message_on'] if self.status else config.i18n['UI_message_off']
                color = '#84DE40' if self.status else '#FFA500'
                inject.message(message, color)
        else:
            BigWorld.callback(0.5, self.checkBattleStarted)

    def stopBattle(self):
        if not config.data['enabled']: return
        self.battleStarted = False
        InputHandler.g_instance.onKeyDown -= self.injectButton
        InputHandler.g_instance.onKeyUp -= self.injectButton
        self.mapSelected = ''
        for point in self.points:
            for marker in point:
                marker.clear()
        del self.points[:]
        self.status = False

    def getMap(self, path):
        self.mapSelected = '%s' % path.split('/')[-1]

    # noinspection PyProtectedMember
    def createModel(self, position):
        arrow = {'path': 'content/Interface/Arrow/normal/lod0/arrow.model', 'action': 'ArrowAnimAction', 'offset': Math.Vector3(0, self.height + 50.0, 0)}
        ground = {'path': 'content/Interface/CheckPoint/CheckPoint_yellow_black.model'}  # , 'offset': Math.Vector3(0, 0.5,0)
        arrowModel = _StaticObjectMarker3D(arrow, position)
        groundModel = _StaticObjectMarker3D(ground, position)
        arrowModel._StaticObjectMarker3D__model.scale = (1, 10, 1)
        groundModel._StaticObjectMarker3D__model.scale = (0.5, 10, 0.5)
        return arrowModel, groundModel

    def setVisible(self, status):
        for point in self.points:
            for marker in point:
                # noinspection PyProtectedMember
                marker._StaticObjectMarker3D__model.visible = status

    @inject.log
    def injectButton(self, event):
        if not config.data['enabled']: return
        if inject.g_appLoader().getDefBattleApp():
            if g_gui.get_key(config.data['buttonShow']) and event.isKeyDown() and self.battleStarted:
                if config.data['showOnlyLightTanks'] and Vehicle.getVehicleClassTag(self.player.getVehicleDescriptor().type.tags) != VEHICLE_CLASS_NAME.LIGHT_TANK: return
                self.status = not self.status
                message = config.i18n['UI_message_on'] if self.status else config.i18n['UI_message_off']
                color = '#84DE40' if self.status else '#FFA500'
                inject.message(message, color)
                self.setVisible(self.status)
            if g_gui.get_key(config.buttons['buttonMark']) and event.isKeyDown():
                if self.player:
                    teamBase = self.player.guiSessionProvider.getArenaDP().getNumberOfTeam()
                    teamBase -= 1
                    position = self.player.getOwnVehiclePosition()
                    message = 'map: %s, base: %s, pos: %s' % (self.mapSelected, teamBase, position)
                    # noinspection PyProtectedMember
                    gameplayID = self.player.arena.arenaType._ArenaType__gameplayCfg['gameplayID']
                    print '"%s": [%s]([%s], [%s])' % (self.mapSelected, gameplayID, position if not teamBase else '', position if teamBase else '')
                    inject.message(message)
                    self.createModel(position)


config = Config()
mapsData = MapsData()
mod = spotMarks()


@inject.hook(PlayerAvatar, '_PlayerAvatar__startGUI')
@inject.log
def hook_start_battle(func, *args):
    func(*args)
    mod.startBattle()


@inject.hook(PlayerAvatar, '_PlayerAvatar__destroyGUI')
@inject.log
def hook_before_delete(func, *args):
    mod.stopBattle()
    func(*args)


@inject.hook(game, 'onGeometryMapped')
@inject.log
def hookOnGeometryMapped(func, *args):
    func(*args)
    mod.getMap(args[1])
