# -*- coding: utf-8 -*-
from Avatar import PlayerAvatar
import BigWorld
from BattleFeedbackCommon import BATTLE_EVENT_TYPE
from constants import VEHICLE_HIT_FLAGS
from gui.battle_control.controllers import feedback_events

enabled = False
try:
    from gui.mods import mod_pro_potapov
    enabled = True
except StandardError: pass

class Stunned(object):
    def __init__(self):
        self.stunnedList = []
        self.stunned = {}
        self.timer = None

    def clear(self):
        del self.stunnedList
        self.stunnedList = []
        self.stunned.clear()

    def timerStop(self):
        if self.timer is not None:
            BigWorld.cancelCallback(self.timer)
            self.timer = None

    def stunChecker(self):
        if self.stunned:
            cache = mod_pro_potapov.g_potapov._Potapov__cache['player']['stun']
            data = []
            for vehicleID in self.stunned:
                vehicle = BigWorld.entity(vehicleID)
                if vehicle is not None and vehicle.stunInfo:
                    cache['seconds'] += 0.1
                    if self.stunned[vehicleID]['HT_AT']:
                        cache['seconds_HT_AT'] += 0.1
                else:
                    data.append(vehicleID)
            for vehicleID in data:
                self.stunned.pop(vehicleID)
        if self.stunned:
            self.timer = BigWorld.callback(0.1, self.stunChecker)
        else:
            self.timerStop()

    def shots(self, avatar, results):
        if not mod_pro_potapov.g_potapov._Potapov__config['enable'] or not mod_pro_potapov.g_potapov._Potapov__cache['battle']['inited']:
            return
        cache = mod_pro_potapov.g_potapov._Potapov__cache['player']['stun']
        MULTI = 0
        for r in results:
            vehicleID = r & 4294967295L
            flags = r >> 32 & 4294967295L
            if avatar.playerVehicleID == vehicleID:
                continue
            if flags & VEHICLE_HIT_FLAGS.STUN_STARTED:
                MULTI += 1
                cache['stunned'] += 1
                HT_AT = avatar.guiSessionProvider.getArenaDP().getVehicleInfo(vehicleID).vehicleType.classTag in ['heavyTank', 'AT-SPG']
                self.stunned[vehicleID] = {'HT_AT': HT_AT}
                self.stunChecker()
                if HT_AT:
                    cache['stunned_HT_AT'] += 1
                if vehicleID not in self.stunnedList:
                    self.stunnedList.append(vehicleID)
                    cache['stunned_damaged_count'] += 1
            if flags & VEHICLE_HIT_FLAGS.VEHICLE_KILLED:
                if vehicleID in self.stunned:
                    cache['stunned_tracked_kill'] += 1
        if MULTI > 1:
            cache['stunned_counter_double'] += 1
        if MULTI > 2:
            cache['stunned_counter_triple'] += 1


    def event(self, avatar, events):
        if not mod_pro_potapov.g_potapov._Potapov__config['enable'] or not mod_pro_potapov.g_potapov._Potapov__cache['battle']['inited']:
            return
        cache = mod_pro_potapov.g_potapov._Potapov__cache['player']['stun']
        for data in events:
            feedbackEvent = feedback_events.PlayerFeedbackEvent.fromDict(data)
            eventID = feedbackEvent.getBattleEventType()
            extra = feedbackEvent.getExtra()
            if eventID == BATTLE_EVENT_TYPE.STUN_ASSIST:
                if extra:
                    cache['stunned_damage'] += extra.getDamage()
                    vehicleID = feedbackEvent.getTargetID()
                    if vehicleID in self.stunnedList:
                        cache['stunned_team_damaged_count'] += 1


def updateFlashDataArty():
    self = mod_pro_potapov.g_potapov
    self.__cache = self._Potapov__cache
    self.__config = self._Potapov__config
    self.__showHint = self._Potapov__showHint
    self.__prevFlashData = self._Potapov__prevFlashData
    self.potapovFlash = mod_pro_potapov.g_appLoader.getDefBattleApp().containerManager.getContainer(mod_pro_potapov.ViewTypes.VIEW).getView().components['PotapovUI']
    if not self.__config['enable'] or not self.__cache['battle']['inited']:
        return
    quest = self.__config['texts'][str(self.__cache['currentID'])]
    main_list, adv_list = self.generateFalshData(quest)
    main = self.__config['pattern']['mainQuest'].replace('{main}', self.__config['pattern']['seperators']['main'].join(main_list))
    adv = self.__config['pattern']['advQuest'].replace('{adv}', self.__config['pattern']['seperators']['adv'].join(adv_list))
    main = main.replace('{{done}}', self.__config['pattern']['state']['done'])
    main = main.replace('{{notDone}}', self.__config['pattern']['state']['notDone'])
    main = main.replace('{{unknown}}', self.__config['pattern']['state']['unknown'])
    adv = adv.replace('{{done}}', self.__config['pattern']['state']['done'])
    adv = adv.replace('{{notDone}}', self.__config['pattern']['state']['notDone'])
    adv = adv.replace('{{unknown}}', self.__config['pattern']['state']['unknown'])
    result = self.__config['pattern']['nameQuest'].replace('{name}', quest['name']) if self.__config['displayName'] else ''
    if self.guiShowMaximal:
        result += main
        result += adv
    else:
        result += main
    hint = '<font size="13" face="$FieldFont" color="#EEEEEE">Мышью можно двигать панель.</font><br>' if self.__showHint else ''
    message = self.__config['pattern']['global'].replace('{data}', result)
    tempData = hint + message
    if tempData != self.__prevFlashData:
        self.__prevFlashData = tempData
        self.potapovFlash.as_setTextS(message, hint, self.__showHint)
    if self.__config['debug']:
        with open('POTAPOV.log', 'a') as fh:
            fh.write(str(self.__cache['currentID']) + '\n')
            fh.write(message + '\n\n')

def clear():
    self = mod_pro_potapov.g_potapov
    self.__cache = self._Potapov__cache
    self.__cache['player']['stun'] = {
        'stunned': 0,
        'stunned_HT_AT': 0,
        'seconds' : 0,
        'seconds_HT_AT': 0,
        'stunned_damage': 0,
        'stunned_damaged_count': 0,
        'stunned_team_damaged_count': 0,
        'stunned_tracked_kill': 0,
        'stunned_counter_double': 0,
        'stunned_counter_triple': 0,
    }
    stunned.clear()

def upd_config():
    self = mod_pro_potapov.g_potapov
    self.__config = self._Potapov__config
    config = {
        "61" : {  # StuG IV - САУ 1
            "name": "САУ-1. Заявить о себе",
            "main": ["{state} Оглушить технику противника не менее 3 раз. <font color=\"#2EFE2E\"><b>{counter}</b></font>"],
            "adv" : ["{state} Выстрелом или тараном нанести урон технике противника не менее 3 раз. <font color=\"#2EFE2E\"><b>{counter}</b></font>"]
        },
        "62" : {  # StuG IV - САУ 2
            "name": "САУ-2. Тик-так",
            "main": ["{state} Оглушить технику противника суммарно на 50 и более секунд. <font color=\"#2EFE2E\"><b>{counter}</b></font>"],
            "adv" : ["{state} Уничтожить противника."]
        },
        "63" : {  # StuG IV - САУ 3
            "name": "САУ-3. Лишить преимущества",
            "main": ["{state} Оглушить тяжёлый танк или ПТ-САУ противника не менее 2 раз. <font color=\"#2EFE2E\"><b>{counter}</b></font>"],
            "adv" : ["{state} Победить."]
        },
        "64" : {  # StuG IV - САУ 4
            "name": "САУ-4. Не стой под стрелой!",
            "main": ["{state} Оглушить тяжёлый танк или ПТ-САУ противника суммарно на 30 секунд и более. <font color=\"#2EFE2E\"><b>{counter}</b></font>"],
            "adv" : ["{state} Победить."]
        },
        "65" : {  # StuG IV - САУ 5
            "name": "САУ-5. Загоризонтная поддержка",
            "main": ["{state} Помочь союзникам нанести не менее 600 урона, оглушив и/или обездвижив технику противника. <font color=\"#2EFE2E\"><b>{counter}</b></font>"],
            "adv" : ["{state} Выстрелами или тараном нанести урон технике противника не менее 3 раз. <font color=\"#2EFE2E\"><b>{counter}</b></font>"]
        },
        "66" : {  # StuG IV - САУ 6
            "name": "САУ-6. Молот Тора",
            "main": ["{state} Оглушить или обездвижить не менее 2 разных машин противника. Союзники должны нанести урон каждой из 2 оглушённых или обездвиженных вами машин противника. <font color=\"#2EFE2E\"><b>{counter}</b></font>"],
            "adv" : ["{state} Победить."]
        },
        "67" : {  # StuG IV - САУ 7
            "name": "САУ-7. Контроль популяции",
            "main": ["{state} Оглушить не менее 2 машин противника. <font color=\"#2EFE2E\"><b>{counter}</b></font>"],
            "adv" : ["{state} Победить."]
        },
        "68" : {  # StuG IV - САУ 8
            "name": "САУ-8. Удачный бой",
            "main": ["{state} Попасть в топ-7 игроков своей команды по опыту."],
            "adv" : ["{state} Победить."]
        },
        "69" : {  # StuG IV - САУ 9
            "name": "САУ-9. Бей в кость",
            "main": ["{state} Вывести из строя не менее 3 любых модулей или ранить членов экипажа техники противника. <font color=\"#2EFE2E\"><b>{counter}</b></font>"],
            "adv" : ["{state} Выжить."]
        },
        "70" : {  # StuG IV - САУ 10
            "name": "САУ-10. Весь спектр услуг",
            "main": ["{state} Сумма нанесённого вами урона, а также урона, нанесённого союзниками по оглушённым и обездвиженным вами целям должна составлять не менее 1000. <font color=\"#2EFE2E\"><b>{counter}</b></font>"],
            "adv" : ["{state} Союзники должны уничтожить как минимум 1 оглушённую или обездвиженную вами машину противника. <font color=\"#2EFE2E\"><b>{counter}</b></font>"]
        },
        "71" : {  # StuG IV - САУ 11
            "name": "САУ-11. Площадь поражения",
            "main": ["{state} Оглушить не менее 2 машин противника одним выстрелом."],
            "adv" : ["{state} Оглушить технику противника суммарно на 50 и более секунд. <font color=\"#2EFE2E\"><b>{counter}</b></font>"]
        },
        "72" : {  # StuG IV - САУ 12
            "name": "САУ-12. Дурной глаз",
            "main": ["{state} Оглушить технику противника суммарно на 50 и более секунд. <font color=\"#2EFE2E\"><b>{counter}</b></font>", "{state} Союзники должны уничтожить как минимум 1 оглушённую или обездвиженную вами машину противника."],
            "adv" : ["{state} Победить."]
        },
        "73" : {  # StuG IV - САУ 13
            "name": "САУ-13. Совместные действия (лично/взвод)",
            "main": ["{state} Лично или суммарно взводом не менее 4 раз нанести урон или не менее 6 раз оглушить технику противника. <font color=\"#2EFE2E\"><b>{counter_1} | {counter_2}</b></font>"],
            "adv" : ["{state} Победить."]
        },
        "74" : {  # StuG IV - САУ 14
            "name": "САУ-14. Часть корабля - часть команды (лично/взвод)",
            "main": ["{state} Лично или суммарно взводом оглушить технику противника в общей сложности на 70 и более секунд или помочь союзникам нанести не менее 400 урона, обездвижив технику противника. <font color=\"#2EFE2E\"><b>{counter_1} | {counter_2}</b></font>"],
            "adv" : ["{state} Победить."]
        },
        "75" : {  # StuG IV - САУ 15
            "name": "САУ-15. Боги войны",
            "main": ["{state} Попасть в топ-5 команды по опыту.", "{state} Помочь союзникам нанести не менее 1000 урона, оглушив и/или обездвижив технику противника.. <font color=\"#2EFE2E\"><b>{counter}</b></font>"],
            "adv" : ["{state} Выжить."]
        },

        "136": {  # T28 Concept - САУ 1
            "name": "САУ-1. Заявить о себе",
            "main": ["{state} Оглушить технику противника не менее 5 раз. <font color=\"#2EFE2E\"><b>{counter}</b></font>"],
            "adv" : ["{state} Выстрелом или тараном нанести урон технике противника не менее 5 раз. <font color=\"#2EFE2E\"><b>{counter}</b></font>"]
        },
        "137": {  # T28 Concept - САУ 2
            "name": "САУ-2. Тик-так",
            "main": ["{state} Оглушить технику противника суммарно на 100 и более секунд. <font color=\"#2EFE2E\"><b>{counter}</b></font>"],
            "adv" : ["{state} Уничтожить минимум 2 противника. <font color=\"#2EFE2E\"><b>{counter}</b></font>"]
        },
        "138": {  # T28 Concept - САУ 3
            "name": "САУ-3. Лишить преимущества",
            "main": ["{state} Оглушить тяжёлый танк или ПТ-САУ противника не менее 4 раз. <font color=\"#2EFE2E\"><b>{counter}</b></font>"],
            "adv" : ["{state} Победить."]
        },
        "139": {  # T28 Concept - САУ 4
            "name": "САУ-4. Не стой под стрелой!",
            "main": ["{state} Оглушить тяжёлый танк или ПТ-САУ противника суммарно на 50 секунд и более. <font color=\"#2EFE2E\"><b>{counter}</b></font>"],
            "adv" : ["{state} Победить."]
        },
        "140": {  # T28 Concept - САУ 5
            "name": "САУ-5. Загоризонтная поддержка",
            "main": ["{state} Помочь союзникам нанести не менее 1000 урона, оглушив и/или обездвижив технику противника. <font color=\"#2EFE2E\"><b>{counter}</b></font>"],
            "adv" : ["{state} Выстрелами или тараном нанести урон технике противника не менее 5 раз. <font color=\"#2EFE2E\"><b>{counter}</b></font>"]
        },
        "141": {  # T28 Concept - САУ 6
            "name": "САУ-6. Молот Тора",
            "main": ["{state} Оглушить или обездвижить не менее 3 разных машин противника, Союзники должны нанести урон каждой из 3 оглушённых или обездвиженных вами машин противника. <font color=\"#2EFE2E\"><b>{counter}</b></font>"],
            "adv" : ["{state} Победить."]
        },
        "142": {  # T28 Concept - САУ 7
            "name": "САУ-7. Контроль популяции",
            "main": ["{state} Оглушить не менее 3 машин противника. <font color=\"#2EFE2E\"><b>{counter}</b></font>"],
            "adv" : ["{state} Победить."]
        },
        "143": {  # T28 Concept - САУ 8
            "name": "САУ-8. Удачный бой",
            "main": ["{state} Попасть в топ-5 игроков своей команды по опыту."],
            "adv" : ["{state} Победить."]
        },
        "144": {  # T28 Concept - САУ 9
            "name": "САУ-9. Бей в кость",
            "main": ["{state} Вывести из строя не менее 5 любых модулей или ранить членов экипажа техники противника. <font color=\"#2EFE2E\"><b>{counter}</b></font>"],
            "adv" : ["{state} Выжить.", "{state} Победить."]
        },
        "145": {  # T28 Concept - САУ 10
            "name": "САУ-10. Весь спектр услуг",
            "main": ["{state} Сумма нанесённого вами урона, а также урона, нанесённого союзниками по оглушённым и обездвиженным вами целям, должна составлять не менее 2000. <font color=\"#2EFE2E\"><b>{counter}</b></font>"],
            "adv" : ["{state} Союзники должны уничтожить как минимум 1 оглушённую или обездвиженную вами машину противника. <font color=\"#2EFE2E\"><b>{counter}</b></font>"]
        },
        "146": {  # T28 Concept - САУ 11
            "name": "САУ-11. Площадь поражения",
            "main": ["{state} Дважды оглушить не менее 2 машин противника одним выстрелом. <font color=\"#2EFE2E\"><b>{counter}</b></font>"],
            "adv" : ["{state} Оглушить технику противника суммарно на 100 и более секунд. <font color=\"#2EFE2E\"><b>{counter}</b></font>"]
        },
        "147": {  # T28 Concept - САУ 12
            "name": "САУ-12. Дурной глаз",
            "main": ["{state} Оглушить технику противника суммарно на 100 и более секунд. <font color=\"#2EFE2E\"><b>{counter}</b></font>", "{state} Союзники должны уничтожить как минимум 1 оглушённую или обездвиженную вами машину противника. <font color=\"#2EFE2E\"><b>{counter}</b></font>"],
            "adv" : ["{state} Победить."]
        },
        "148": {  # T28 Concept - САУ 13
            "name": "САУ-13. Совместные действия (лично/взвод)",
            "main": ["{state} Лично или суммарно взводом не менее 6 раз нанести урон или не менее 8 раз оглушить технику противника. <font color=\"#2EFE2E\"><b>{counter_1} | {counter_2}</b></font>"],
            "adv" : ["{state} Победить."]
        },
        "149": {  # T28 Concept - САУ 14
            "name": "САУ-14. Часть корабля - часть команды (лично/взвод)",
            "main": ["{state} Лично или суммарно взводом оглушить технику противника в общей сложности на 100 и более секунд, или помочь союзникам нанести не менее 600 урона, обездвижив технику противника. <font color=\"#2EFE2E\"><b>{counter_1} | {counter_2}</b></font>"],
            "adv" : ["{state} Лично выжить."]
        },
        "150": {  # T28 Concept - САУ 15
            "name": "САУ-15. Боги войны",
            "main": ["{state} Попасть в топ-3 игроков своей команды по опыту.", "{state} Помочь союзникам нанести не менее 1500 урона, оглушив и/или обездвижив технику противника. <font color=\"#2EFE2E\"><b>{counter}</b></font>"],
            "adv" : ["{state} Выжить."]
        },

        "211": {  # T 55A - САУ 1
            "name": "САУ-1. Заявить о себе",
            "main": ["{state} Оглушить технику противника не менее 7 раз. <font color=\"#2EFE2E\"><b>{counter}</b></font>"],
            "adv" : ["{state} Выстрелом или тараном нанести урон технике противника не менее 6 раз. <font color=\"#2EFE2E\"><b>{counter}</b></font>"]
        },
        "212": {  # T 55A - САУ 2
            "name": "САУ-2. Тик-так",
            "main": ["{state} Оглушить технику противника суммарно на 150 и более секунд. <font color=\"#2EFE2E\"><b>{counter}</b></font>"],
            "adv" : ["{state} Уничтожить минимум 3 противника. <font color=\"#2EFE2E\"><b>{counter}</b></font>"]
        },
        "213": {  # T 55A - САУ 3
            "name": "САУ-3. Лишить преимущества",
            "main": ["{state} Оглушить тяжёлый танк или ПТ-САУ противника не менее 6 раз. <font color=\"#2EFE2E\"><b>{counter}</b></font>"],
            "adv" : ["{state} Победить.", "{state} Выжить."]
        },
        "214": {  # T 55A - САУ 4
            "name": "САУ-4. Не стой под стрелой!",
            "main": ["{state} Оглушить тяжёлый танк или ПТ-САУ противника суммарно на 80 секунд и более. <font color=\"#2EFE2E\"><b>{counter}</b></font>"],
            "adv" : ["{state} Победить.", "{state} Выжить."]
        },
        "215": {  # T 55A - САУ 5
            "name": "САУ-5. Загоризонтная поддержка",
            "main": ["{state} Помочь союзникам нанести не менее 2000 урона, оглушив и/или обездвижив технику противника. <font color=\"#2EFE2E\"><b>{counter}</b></font>"],
            "adv" : ["{state} Выстрелами или тараном нанести урон технике противника не менее 6 раз.<font color=\"#2EFE2E\"><b>{counter}</b></font>"]
        },
        "216": {  # T 55A - САУ 6
            "name": "САУ-6. Молот Тора",
            "main": ["{state} Оглушить или обездвижить не менее 5 разных машин противника. Союзники должны нанести урон каждой из 5 оглушённых или обездвиженных вами машин противника.<font color=\"#2EFE2E\"><b>{counter}</b></font>"],
            "adv" : ["{state} Победить.", "{state} Выжить."]
        },
        "217": {  # T 55A - САУ 7
            "name": "САУ-7. Контроль популяции",
            "main": ["{state} Оглушить не менее 5 машин противника. <font color=\"#2EFE2E\"><b>{counter}</b></font>"],
            "adv" : ["{state} Победить.", "{state} Выжить."]
        },
        "218": {  # T 55A - САУ 8
            "name": "САУ-8. Удачный бой",
            "main": ["{state} Попасть в топ-3 игроков своей команды по опыту."],
            "adv" : ["{state} Победить."]
        },
        "219": {  # T 55A - САУ 9
            "name": "САУ-9. Бей в кость",
            "main": ["{state} Вывести из строя не менее 8 любых модулей или ранить членов экипажа техники противника. <font color=\"#2EFE2E\"><b>{counter}</b></font>"],
            "adv" : ["{state} Выжить.", "{state} Победить.", "{state} Не засветиться за весь бой."]
        },
        "220": {  # T 55A - САУ 10
            "name": "САУ-10. Весь спектр услуг",
            "main": ["{state} Сумма нанесённого вами урона, а также урона, нанесённого союзниками по оглушённым и обездвиженным вами целям, должна составлять не менее 3000. <font color=\"#2EFE2E\"><b>{counter}</b></font>"],
            "adv" : ["{state} Союзники должны уничтожить не менее 2 оглушённых или обездвиженных вами машин противника. <font color=\"#2EFE2E\"><b>{counter}</b></font>", "{state} Победить."]
        },
        "221": {  # T 55A - САУ 11
            "name": "САУ-11. Площадь поражения",
            "main": ["{state} Оглушить не менее 3 машин противника одним выстрелом."],
            "adv" : ["{state} глушить технику противника суммарно на 150 и более секунд. <font color=\"#2EFE2E\"><b>{counter}</b></font>"]
        },
        "222": {  # T 55A - САУ 12
            "name": "САУ-12. Дурной глаз",
            "main": ["{state} Оглушить технику противника суммарно на 150 и более секунд. <font color=\"#2EFE2E\"><b>{counter}</b></font>", "{state} Союзники должны уничтожить не менее 2 оглушённых или обездвиженных вами машин противника или более. <font color=\"#2EFE2E\"><b>{counter}</b></font>"],
            "adv" : ["{state} Победить."]
        },
        "223": {  # T 55A - САУ 13
            "name": "САУ-13. Совместные действия (лично/взвод)",
            "main": ["{state} Лично или суммарно взводом не менее 8 раз нанести урон или не менее 10 раз оглушить технику противника. <font color=\"#2EFE2E\"><b>{counter_1} | {counter_2}</b></font>"],
            "adv" : ["{state} Победить."]
        },
        "224": {  # T 55A - САУ 14
            "name": "САУ-14. Часть корабля - часть команды (лично/взвод)",
            "main": ["{state} Лично или суммарно взводом оглушить технику противника в общей сложности на 180 и более секунд, или помочь союзникам нанести не менее 800 урона, обездвижив технику противника. <font color=\"#2EFE2E\"><b>{counter_1} | {counter_2}</b></font>"],
            "adv" : ["{state} Победить."]
        },
        "225": {  # T 55A - САУ 15
            "name": "САУ-15. Боги войны",
            "main": ["{state} Занять 1 место в команде по опыту.", "{state} Помочь союзникам нанести не менее 2500 урона, оглушив и/или обездвижив технику противника. <font color=\"#2EFE2E\"><b>{counter}</b></font>"],
            "adv" : ["{state} Выжить."]
        },

        "286": {  # Объект 260 - САУ 1
            "name": "САУ-1. Заявить о себе",
            "main": ["{state} Оглушить технику противника не менее 10 раз. <font color=\"#2EFE2E\"><b>{counter}</b></font>"],
            "adv" : ["{state} Выстрелом или тараном нанести урон технике противника не менее 8 раз. <font color=\"#2EFE2E\"><b>{counter}</b></font>"]
        },
        "287": {  # Объект 260 - САУ 2
            "name": "САУ-2. Тик-так",
            "main": ["{state}  Оглушить технику противника суммарно на 200 и более секунд. <font color=\"#2EFE2E\"><b>{counter}</b></font>"],
            "adv" : ["{state} Уничтожить не менее 4 машин противника. <font color=\"#2EFE2E\"><b>{counter}</b></font>"]
        },
        "288": {  # Объект 260 - САУ 3
            "name": "САУ-3. Лишить преимущества",
            "main": ["{state} Оглушить тяжёлый танк или ПТ-САУ противника не менее 8 раз. <font color=\"#2EFE2E\"><b>{counter}</b></font>"],
            "adv" : ["{state} Победить.", "{state} Выжить."]
        },
        "289": {  # Объект 260 - САУ 4
            "name": "САУ-4. Не стой под стрелой!",
            "main": ["{state} Оглушить тяжёлый танк или ПТ-САУ противника суммарно на 120 секунд и более. <font color=\"#2EFE2E\"><b>{counter}</b></font>"],
            "adv" : ["{state} Победить.", "{state} Выжить."]
        },
        "290": {  # Объект 260 - САУ 5
            "name": "САУ-5. Загоризонтная поддержка",
            "main": ["{state} Помочь союзникам нанести не менее 3000 урона, оглушив и/или обездвижив технику противника. <font color=\"#2EFE2E\"><b>{counter}</b></font>"],
            "adv" : ["{state} Выстрелами или тараном нанести урон технике противника не менее 8 раз. <font color=\"#2EFE2E\"><b>{counter}</b></font>"]
        },
        "291": {  # Объект 260 - САУ 6
            "name": "САУ-6. Молот Тора",
            "main": ["{state} Оглушить или обездвижить не менее 6 разных машин противника. Союзники должны нанести урон каждой из 6 оглушённых или обездвиженных вами машин противника.<font color=\"#2EFE2E\"><b>{counter}</b></font>"],
            "adv" : ["{state} Победить.", "{state} Выжить."]
        },
        "292": {  # Объект 260 - САУ 7
            "name": "САУ-7. Контроль популяции",
            "main": ["{state} Оглушить не менее 6 машин противника. <font color=\"#2EFE2E\"><b>{counter}</b></font>"],
            "adv" : ["{state} Победить.", "{state} Выжить."]
        },
        "293": {  # Объект 260 - САУ 8
            "name": "САУ-8. Удачный бой",
            "main": ["{state} Занять 1 место среди игроков своей команды по опыту."],
            "adv" : ["{state} Победить."]
        },
        "294": {  # Объект 260 - САУ 9
            "name": "САУ-9. Бей в кость",
            "main": ["{state} Вывести из строя не менее 10 любых модулей или ранить членов экипажа техники противника. <font color=\"#2EFE2E\"><b>{counter}</b></font>"],
            "adv" : ["{state} Выжить.", "{state} Победить.", "{state} Не засветиться за весь бой."]
        },
        "295": {  # Объект 260 - САУ 10
            "name": "САУ-10. Весь спектр услуг",
            "main": ["{state} Сумма нанесённого вами урона, а также урона, нанесённого союзниками по оглушённым и обездвиженным вами целям должна составлять не менее 4000. <font color=\"#2EFE2E\"><b>{counter}</b></font>"],
            "adv" : ["{state} Союзники должны уничтожить не менее 3 оглушённых или обездвиженных вами машин противника. <font color=\"#2EFE2E\"><b>{counter}</b></font>", "{state} Победить."]
        },
        "296": {  # Объект 260 - САУ 11
            "name": "САУ-11. Площадь поражения",
            "main": ["{state} Дважды оглушить не менее 3 машин противника одним выстрелом. <font color=\"#2EFE2E\"><b>{counter}</b></font>"],
            "adv" : ["{state} Оглушить технику противника суммарно на 200 и более секунд. <font color=\"#2EFE2E\"><b>{counter}</b></font>"]
        },
        "297": {  # Объект 260 - САУ 12
            "name": "САУ-12. Дурной глаз",
            "main": ["{state} Оглушить технику противника суммарно на 200 и более секунд. <font color=\"#2EFE2E\"><b>{counter}</b></font>", "{state} Союзники должны уничтожить не менее 3 оглушённых или обездвиженных вами машин противника. <font color=\"#2EFE2E\"><b>{counter}</b></font>"],
            "adv" : ["{state} Победить."]
        },
        "298": {  # Объект 260 - САУ 13
            "name": "САУ-13. Совместные действия (лично/взвод)",
            "main": ["{state} Лично или суммарно взводом не менее 10 раз нанести урон или не менее 12 раз оглушить технику противника. <font color=\"#2EFE2E\"><b>{counter_1} | {counter_2}</b></font>"],
            "adv" : ["{state} Победить."]
        },
        "299": {  # Объект 260 - САУ 14
            "name": "САУ-14. Часть корабля - часть команды (лично/взвод)",
            "main": ["{state} Лично или суммарно взводом оглушить технику противника в общей сложности на 250 и более секунд, или помочь союзникам нанести не менее 1000 урона, обездвижив технику противника. <font color=\"#2EFE2E\"><b>{counter_1} | {counter_2}</b></font>"],
            "adv" : ["{state} Победить."]
        },
        "300": {  # Объект 260 - САУ 15
            "name": "САУ-15. Боги войны",
            "main": ["{state} Занять 1 место в командах по опыту.", "{state} Помочь союзникам нанести не менее 3500 урона, оглушив и/или обездвижив технику противника. <font color=\"#2EFE2E\"><b>{counter}</b></font>"],
            "adv" : ["{state} Выжить."]
        },
    }

    for questID in config:
        if questID in self.__config['texts']:
            self.__config['texts'][questID] = config[questID]


def updater():
    self = mod_pro_potapov.g_potapov
    self.__cache = self._Potapov__cache
    self.__config = self._Potapov__config
    if not self.__config['enable']: return
    if not self.__cache['battle']['inited']:
        return BigWorld.callback(1.0, updater)
    #"САУ-1. Заявить о себе" 61, 136, 211, 286
    if self.__cache['currentID'] == 61:
        def quest_61(quest):
            main_list, adv_list = ([], [])
            data_1 = self.__cache['player']['stun']['stunned']
            data_2 = self.__cache['player']['damage']['counter_any']
            cond_1 = '{{done}}' if data_1 >= 3 else '{{notDone}}'
            cond_2 = '{{done}}' if data_2 >= 3 else '{{notDone}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)).replace('{counter}', str(data_1)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_2)).replace('{counter}', str(data_2)))
            return (main_list, adv_list)
        self.generateFalshData = quest_61
    if self.__cache['currentID'] == 136:
        def quest_136(quest):
            main_list, adv_list = ([], [])
            data_1 = self.__cache['player']['stun']['stunned']
            data_2 = self.__cache['player']['damage']['counter_any']
            cond_1 = '{{done}}' if data_1 >= 5 else '{{notDone}}'
            cond_2 = '{{done}}' if data_2 >= 5 else '{{notDone}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)).replace('{counter}', str(data_1)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_2)).replace('{counter}', str(data_2)))
            return (main_list, adv_list)
        self.generateFalshData = quest_136
    if self.__cache['currentID'] == 211:
        def quest_211(quest):
            main_list, adv_list = ([], [])
            data_1 = self.__cache['player']['stun']['stunned']
            data_2 = self.__cache['player']['damage']['counter_any']
            cond_1 = '{{done}}' if data_1 >= 7 else '{{notDone}}'
            cond_2 = '{{done}}' if data_2 >= 6 else '{{notDone}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)).replace('{counter}', str(data_1)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_2)).replace('{counter}', str(data_2)))
            return (main_list, adv_list)
        self.generateFalshData = quest_211
    if self.__cache['currentID'] == 286:
        def quest_286(quest):
            main_list, adv_list = ([], [])
            data_1 = self.__cache['player']['stun']['stunned']
            data_2 = self.__cache['player']['damage']['counter_any']
            cond_1 = '{{done}}' if data_1 >= 10 else '{{notDone}}'
            cond_2 = '{{done}}' if data_2 >= 8 else '{{notDone}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)).replace('{counter}', str(data_1)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_2)).replace('{counter}', str(data_2)))
            return (main_list, adv_list)
        self.generateFalshData = quest_286

    # "САУ-2. Тик-так" 62, 137, 212, 287
    if self.__cache['currentID'] == 62:
        def quest_62(quest):
            main_list, adv_list = ([], [])
            data_1 = self.__cache['player']['stun']['seconds']
            data_2 = self.__cache['player']['kill']['counter_any']
            cond_1 = '{{done}}' if data_1 >= 50 else '{{notDone}}'
            cond_2 = '{{done}}' if data_2 >= 1 else '{{notDone}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_2)))
            return (main_list, adv_list)
        self.generateFalshData = quest_62
    if self.__cache['currentID'] == 137:
        def quest_137(quest):
            main_list, adv_list = ([], [])
            data_1 = self.__cache['player']['stun']['seconds']
            data_2 = self.__cache['player']['kill']['counter_any']
            cond_1 = '{{done}}' if data_1 >= 100 else '{{notDone}}'
            cond_2 = '{{done}}' if data_2 >= 2 else '{{notDone}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_2)))
            return (main_list, adv_list)
        self.generateFalshData = quest_137
    if self.__cache['currentID'] == 212:
        def quest_212(quest):
            main_list, adv_list = ([], [])
            data_1 = self.__cache['player']['stun']['seconds']
            data_2 = self.__cache['player']['kill']['counter_any']
            cond_1 = '{{done}}' if data_1 >= 150 else '{{notDone}}'
            cond_2 = '{{done}}' if data_2 >= 3 else '{{notDone}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_2)))
            return (main_list, adv_list)
        self.generateFalshData = quest_212
    if self.__cache['currentID'] == 287:
        def quest_287(quest):
            main_list, adv_list = ([], [])
            data_1 = self.__cache['player']['stun']['seconds']
            data_2 = self.__cache['player']['kill']['counter_any']
            cond_1 = '{{done}}' if data_1 >= 200 else '{{notDone}}'
            cond_2 = '{{done}}' if data_2 >= 4 else '{{notDone}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_2)))
            return (main_list, adv_list)
        self.generateFalshData = quest_287

    #"САУ-3. Лишить преимущества" 63, 138, 213, 288
    if self.__cache['currentID'] == 63:
        def quest_63(quest):
            main_list, adv_list = ([], [])
            data_1 = self.__cache['player']['stun']['stunned_HT_AT']
            cond_1 = '{{done}}' if data_1 >= 2 else '{{notDone}}'
            cond_2 = '{{unknown}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)).replace('{counter}', str(data_1)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_2)))
            return (main_list, adv_list)
        self.generateFalshData = quest_63
    if self.__cache['currentID'] == 138:
        def quest_138(quest):
            main_list, adv_list = ([], [])
            data_1 = self.__cache['player']['stun']['stunned_HT_AT']
            cond_1 = '{{done}}' if data_1 >= 4 else '{{notDone}}'
            cond_2 = '{{unknown}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)).replace('{counter}', str(data_1)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_2)))
            return (main_list, adv_list)
        self.generateFalshData = quest_138
    if self.__cache['currentID'] == 213:
        def quest_213(quest):
            main_list, adv_list = ([], [])
            data_1 = self.__cache['player']['stun']['stunned_HT_AT']
            cond_1 = '{{done}}' if data_1 >= 6 else '{{notDone}}'
            cond_2 = '{{unknown}}'
            cond_3 = '{{unknown}}' if self.__cache['player']['alive'] else '{{notDone}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)).replace('{counter}', str(data_1)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_2)))
            adv_list.append(quest['adv'][1].replace('{state}', str(cond_3)))
            return (main_list, adv_list)
        self.generateFalshData = quest_213
    if self.__cache['currentID'] == 288:
        def quest_288(quest):
            main_list, adv_list = ([], [])
            data_1 = self.__cache['player']['stun']['stunned_HT_AT']
            cond_1 = '{{done}}' if data_1 >= 8 else '{{notDone}}'
            cond_2 = '{{unknown}}'
            cond_3 = '{{unknown}}' if self.__cache['player']['alive'] else '{{notDone}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)).replace('{counter}', str(data_1)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_2)))
            adv_list.append(quest['adv'][1].replace('{state}', str(cond_3)))
            return (main_list, adv_list)
        self.generateFalshData = quest_288
    # "САУ-4. Не стой под стрелой!" 64, 139, 214, 289
    if self.__cache['currentID'] == 64:
        def quest_64(quest):
            main_list, adv_list = ([], [])
            data_1 = self.__cache['player']['stun']['seconds_HT_AT']
            cond_1 = '{{done}}' if data_1 >= 30 else '{{notDone}}'
            cond_2 = '{{unknown}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)).replace('{counter}', str(data_1)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_2)))
            return (main_list, adv_list)
        self.generateFalshData = quest_64
    if self.__cache['currentID'] == 139:
        def quest_139(quest):
            main_list, adv_list = ([], [])
            data_1 = self.__cache['player']['stun']['seconds_HT_AT']
            cond_1 = '{{done}}' if data_1 >= 50 else '{{notDone}}'
            cond_2 = '{{unknown}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)).replace('{counter}', str(data_1)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_2)))
            return (main_list, adv_list)
        self.generateFalshData = quest_139
    if self.__cache['currentID'] == 214:
        def quest_214(quest):
            main_list, adv_list = ([], [])
            data_1 = self.__cache['player']['stun']['seconds_HT_AT']
            cond_1 = '{{done}}' if data_1 >= 80 else '{{notDone}}'
            cond_2 = '{{unknown}}'
            cond_3 = '{{unknown}}' if self.__cache['player']['alive'] else '{{notDone}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)).replace('{counter}', str(data_1)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_2)))
            adv_list.append(quest['adv'][1].replace('{state}', str(cond_3)))
            return (main_list, adv_list)
        self.generateFalshData = quest_214
    if self.__cache['currentID'] == 289:
        def quest_289(quest):
            main_list, adv_list = ([], [])
            data_1 = self.__cache['player']['stun']['seconds_HT_AT']
            cond_1 = '{{done}}' if data_1 >= 120 else '{{notDone}}'
            cond_2 = '{{unknown}}'
            cond_3 = '{{unknown}}' if self.__cache['player']['alive'] else '{{notDone}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)).replace('{counter}', str(data_1)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_2)))
            adv_list.append(quest['adv'][1].replace('{state}', str(cond_3)))
            return (main_list, adv_list)
        self.generateFalshData = quest_289

    # "САУ-5. Загоризонтная поддержка" 65, 140, 215, 290
    if self.__cache['currentID'] == 65:
        def quest_65(quest):
            main_list, adv_list = ([], [])
            data_1 = self.__cache['player']['stun']['stunned_damage'] + self.__cache['player']['damage']['track_by_alies']
            data_2 = self.__cache['player']['damage']['counter_any']
            cond_1 = '{{done}}' if data_1 >= 600 else '{{notDone}}'
            cond_2 = '{{done}}' if data_2 >= 3 else '{{notDone}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)).replace('{counter}', str(data_1)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_2)).replace('{counter}', str(data_2)))
            return (main_list, adv_list)
        self.generateFalshData = quest_65
    if self.__cache['currentID'] == 140:
        def quest_140(quest):
            main_list, adv_list = ([], [])
            data_1 = self.__cache['player']['stun']['stunned_damage'] + self.__cache['player']['damage']['track_by_alies']
            data_2 = self.__cache['player']['damage']['counter_any']
            cond_1 = '{{done}}' if data_1 >= 1000 else '{{notDone}}'
            cond_2 = '{{done}}' if data_2 >= 5 else '{{notDone}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)).replace('{counter}', str(data_1)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_2)).replace('{counter}', str(data_2)))
            return (main_list, adv_list)
        self.generateFalshData = quest_140
    if self.__cache['currentID'] == 215:
        def quest_215(quest):
            main_list, adv_list = ([], [])
            data_1 = self.__cache['player']['stun']['stunned_damage'] + self.__cache['player']['damage']['track_by_alies']
            data_2 = self.__cache['player']['damage']['counter_any']
            cond_1 = '{{done}}' if data_1 >= 2000 else '{{notDone}}'
            cond_2 = '{{done}}' if data_2 >= 6 else '{{notDone}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)).replace('{counter}', str(data_1)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_2)).replace('{counter}', str(data_2)))
            return (main_list, adv_list)
        self.generateFalshData = quest_215
    if self.__cache['currentID'] == 290:
        def quest_290(quest):
            main_list, adv_list = ([], [])
            data_1 = self.__cache['player']['stun']['stunned_damage'] + self.__cache['player']['damage']['track_by_alies']
            data_2 = self.__cache['player']['damage']['counter_any']
            cond_1 = '{{done}}' if data_1 >= 3000 else '{{notDone}}'
            cond_2 = '{{done}}' if data_2 >= 8 else '{{notDone}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)).replace('{counter}', str(data_1)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_2)).replace('{counter}', str(data_2)))
            return (main_list, adv_list)
        self.generateFalshData = quest_290
    # "САУ-6. Молот Тора" 66, 141, 216, 291
    if self.__cache['currentID'] == 66:
        def quest_66(quest):
            main_list, adv_list = ([], [])
            data_1 = self.__cache['player']['stun']['stunned_team_damaged_count']
            cond_1 = '{{done}}' if data_1 >= 2 else '{{notDone}}'
            cond_2 = '{{unknown}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)).replace('{counter}', str(data_1)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_2)))
            return (main_list, adv_list)
        self.generateFalshData = quest_66
    if self.__cache['currentID'] == 141:
        def quest_141(quest):
            main_list, adv_list = ([], [])
            data_1 = self.__cache['player']['stun']['stunned_team_damaged_count']
            cond_1 = '{{done}}' if data_1 >= 3 else '{{notDone}}'
            cond_2 = '{{unknown}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)).replace('{counter}', str(data_1)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_2)))
            return (main_list, adv_list)
        self.generateFalshData = quest_141
    if self.__cache['currentID'] == 216:
        def quest_216(quest):
            main_list, adv_list = ([], [])
            data_1 = self.__cache['player']['stun']['stunned_team_damaged_count']
            cond_1 = '{{done}}' if data_1 >= 5 else '{{notDone}}'
            cond_2 = '{{unknown}}'
            cond_3 = '{{unknown}}' if self.__cache['player']['alive'] else '{{notDone}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)).replace('{counter}', str(data_1)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_2)))
            adv_list.append(quest['adv'][1].replace('{state}', str(cond_3)))
            return (main_list, adv_list)
        self.generateFalshData = quest_216
    if self.__cache['currentID'] == 291:
        def quest_291(quest):
            main_list, adv_list = ([], [])
            data_1 = self.__cache['player']['stun']['stunned_team_damaged_count']
            cond_1 = '{{done}}' if data_1 >= 6 else '{{notDone}}'
            cond_2 = '{{unknown}}'
            cond_3 = '{{unknown}}' if self.__cache['player']['alive'] else '{{notDone}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)).replace('{counter}', str(data_1)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_2)))
            adv_list.append(quest['adv'][1].replace('{state}', str(cond_3)))
            return (main_list, adv_list)
        self.generateFalshData = quest_291
    # "САУ-7. Контроль популяции" 67, 142, 217, 292
    if self.__cache['currentID'] == 67:
        def quest_67(quest):
            main_list, adv_list = ([], [])
            data_1 = self.__cache['player']['stun']['stunned_damaged_count']
            cond_1 = '{{done}}' if data_1 >= 2 else '{{notDone}}'
            cond_2 = '{{unknown}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)).replace('{counter}', str(data_1)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_2)))
            return (main_list, adv_list)
        self.generateFalshData = quest_67
    if self.__cache['currentID'] == 142:
        def quest_142(quest):
            main_list, adv_list = ([], [])
            data_1 = self.__cache['player']['stun']['stunned_damaged_count']
            cond_1 = '{{done}}' if data_1 >= 3 else '{{notDone}}'
            cond_2 = '{{unknown}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)).replace('{counter}', str(data_1)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_2)))
            return (main_list, adv_list)
        self.generateFalshData = quest_142
    if self.__cache['currentID'] == 217:
        def quest_217(quest):
            main_list, adv_list = ([], [])
            data_1 = self.__cache['player']['stun']['stunned_damaged_count']
            cond_1 = '{{done}}' if data_1 >= 5 else '{{notDone}}'
            cond_2 = '{{unknown}}'
            cond_3 = '{{unknown}}' if self.__cache['player']['alive'] else '{{notDone}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)).replace('{counter}', str(data_1)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_2)))
            adv_list.append(quest['adv'][1].replace('{state}', str(cond_3)))
            return (main_list, adv_list)
        self.generateFalshData = quest_217
    if self.__cache['currentID'] == 292:
        def quest_292(quest):
            main_list, adv_list = ([], [])
            data_1 = self.__cache['player']['stun']['stunned_damaged_count']
            cond_1 = '{{done}}' if data_1 >= 6 else '{{notDone}}'
            cond_2 = '{{unknown}}'
            cond_3 = '{{unknown}}' if self.__cache['player']['alive'] else '{{notDone}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)).replace('{counter}', str(data_1)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_2)))
            adv_list.append(quest['adv'][1].replace('{state}', str(cond_3)))
            return (main_list, adv_list)
        self.generateFalshData = quest_292
    # "САУ-8. Удачный бой" 68, 143, 218, 293
    if self.__cache['currentID'] == 68:
        def quest_68(quest):
            main_list, adv_list = ([], [])
            cond_1 = '{{unknown}}'
            cond_2 = '{{unknown}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_2)))
            return (main_list, adv_list)
        self.generateFalshData = quest_68
    if self.__cache['currentID'] == 143:
        def quest_143(quest):
            main_list, adv_list = ([], [])
            cond_1 = '{{unknown}}'
            cond_2 = '{{unknown}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_2)))
            return (main_list, adv_list)
        self.generateFalshData = quest_143
    if self.__cache['currentID'] == 218:
        def quest_218(quest):
            main_list, adv_list = ([], [])
            cond_1 = '{{unknown}}'
            cond_2 = '{{unknown}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_2)))
            return (main_list, adv_list)
        self.generateFalshData = quest_218
    if self.__cache['currentID'] == 293:
        def quest_293(quest):
            main_list, adv_list = ([], [])
            cond_1 = '{{unknown}}'
            cond_2 = '{{unknown}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_2)))
            return (main_list, adv_list)
        self.generateFalshData = quest_293
    # "САУ-9. Бей в кость" 69, 144, 219, 294
    if self.__cache['currentID'] == 69:
        def quest_69(quest):
            main_list, adv_list = ([], [])
            data_1 = self.__cache['player']['damage']['counter_devices']
            cond_1 = '{{unknown}}' if data_1 >= 3 else '{{notDone}}'
            cond_2 = '{{unknown}}' if self.__cache['player']['alive'] else '{{notDone}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)).replace('{counter}', str(data_1)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_2)))
            return (main_list, adv_list)
        self.generateFalshData = quest_69
    if self.__cache['currentID'] == 144:
        def quest_144(quest):
            main_list, adv_list = ([], [])
            data_1 = self.__cache['player']['damage']['counter_devices']
            cond_1 = '{{unknown}}' if data_1 >= 5 else '{{notDone}}'
            cond_2 = '{{unknown}}' if self.__cache['player']['alive'] else '{{notDone}}'
            cond_3 = '{{unknown}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)).replace('{counter}', str(data_1)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_2)))
            adv_list.append(quest['adv'][1].replace('{state}', str(cond_3)))
            return (main_list, adv_list)
        self.generateFalshData = quest_144
    if self.__cache['currentID'] == 219:
        def quest_219(quest):
            main_list, adv_list = ([], [])
            data_1 = self.__cache['player']['damage']['counter_devices']
            cond_1 = '{{unknown}}' if data_1 >= 8 else '{{notDone}}'
            cond_2 = '{{unknown}}' if self.__cache['player']['alive'] else '{{notDone}}'
            cond_3 = '{{unknown}}'
            cond_4 = '{{notDone}}' if self.__cache['player']['observed'] else '{{unknown}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)).replace('{counter}', str(data_1)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_2)))
            adv_list.append(quest['adv'][1].replace('{state}', str(cond_3)))
            adv_list.append(quest['adv'][2].replace('{state}', str(cond_4)))
            return (main_list, adv_list)
        self.generateFalshData = quest_219
    if self.__cache['currentID'] == 294:
        def quest_294(quest):
            main_list, adv_list = ([], [])
            data_1 = self.__cache['player']['damage']['counter_devices']
            cond_1 = '{{unknown}}' if data_1 >= 10 else '{{notDone}}'
            cond_2 = '{{unknown}}' if self.__cache['player']['alive'] else '{{notDone}}'
            cond_3 = '{{unknown}}'
            cond_4 = '{{notDone}}' if self.__cache['player']['observed'] else '{{unknown}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)).replace('{counter}', str(data_1)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_2)))
            adv_list.append(quest['adv'][1].replace('{state}', str(cond_3)))
            adv_list.append(quest['adv'][2].replace('{state}', str(cond_4)))
            return (main_list, adv_list)
        self.generateFalshData = quest_294
    # "САУ-10. Весь спектр услуг" 70, 145, 220, 295
    if self.__cache['currentID'] == 70:
        def quest_70(quest):
            main_list, adv_list = ([], [])
            data_1 = self.__cache['player']['stun']['stunned_damage'] + self.__cache['player']['damage']['track_by_alies'] + self.__cache['player']['damage']['any']
            data_2 = self.__cache['player']['stun']['stunned_tracked_kill'] + self.__cache['player']['kill']['track_by_alies']
            cond_1 = '{{done}}' if data_1 >= 1000 else '{{notDone}}'
            cond_2 = '{{done}}' if data_2 >= 1 else '{{notDone}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)).replace('{counter}', str(data_1)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_2)).replace('{counter}', str(data_2)))
            return (main_list, adv_list)
        self.generateFalshData = quest_70
    if self.__cache['currentID'] == 145:
        def quest_145(quest):
            main_list, adv_list = ([], [])
            data_1 = self.__cache['player']['stun']['stunned_damage'] + self.__cache['player']['damage']['track_by_alies'] + self.__cache['player']['damage']['any']
            data_2 = self.__cache['player']['stun']['stunned_tracked_kill'] + self.__cache['player']['kill']['track_by_alies']
            cond_1 = '{{done}}' if data_1 >= 2000 else '{{notDone}}'
            cond_2 = '{{done}}' if data_2 >= 1 else '{{notDone}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)).replace('{counter}', str(data_1)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_2)).replace('{counter}', str(data_2)))
            return (main_list, adv_list)
        self.generateFalshData = quest_145
    if self.__cache['currentID'] == 220:
        def quest_220(quest):
            main_list, adv_list = ([], [])
            data_1 = self.__cache['player']['stun']['stunned_damage'] + self.__cache['player']['damage']['track_by_alies'] + self.__cache['player']['damage']['any']
            data_2 = self.__cache['player']['stun']['stunned_tracked_kill'] + self.__cache['player']['kill']['track_by_alies']
            cond_1 = '{{done}}' if data_1 >= 3000 else '{{notDone}}'
            cond_2 = '{{done}}' if data_2 >= 2 else '{{notDone}}'
            cond_3 = '{{unknown}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)).replace('{counter}', str(data_1)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_2)).replace('{counter}', str(data_2)))
            adv_list.append(quest['adv'][1].replace('{state}', str(cond_3)))
            return (main_list, adv_list)
        self.generateFalshData = quest_220
    if self.__cache['currentID'] == 295:
        def quest_295(quest):
            main_list, adv_list = ([], [])
            data_1 = self.__cache['player']['stun']['stunned_damage'] + self.__cache['player']['damage']['track_by_alies'] + self.__cache['player']['damage']['any']
            data_2 = self.__cache['player']['stun']['stunned_tracked_kill'] + self.__cache['player']['kill']['track_by_alies']
            cond_1 = '{{done}}' if data_1 >= 4000 else '{{notDone}}'
            cond_2 = '{{done}}' if data_2 >= 3 else '{{notDone}}'
            cond_3 = '{{unknown}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)).replace('{counter}', str(data_1)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_2)).replace('{counter}', str(data_2)))
            adv_list.append(quest['adv'][1].replace('{state}', str(cond_3)))
            return (main_list, adv_list)
        self.generateFalshData = quest_295
    # "САУ-11. Площадь поражения" 71, 146, 221, 296
    if self.__cache['currentID'] == 71:
        def quest_71(quest):
            main_list, adv_list = ([], [])
            data_1 = self.__cache['player']['stun']['stunned_counter_double']
            data_2 = self.__cache['player']['stun']['seconds']
            cond_1 = '{{done}}' if data_1 >= 1 else '{{notDone}}'
            cond_2 = '{{done}}' if data_1 >= 50 else '{{notDone}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)).replace('{counter}', str(data_1)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_2)).replace('{counter}', str(data_2)))
            return (main_list, adv_list)
        self.generateFalshData = quest_71
    if self.__cache['currentID'] == 146:
        def quest_146(quest):
            main_list, adv_list = ([], [])
            data_1 = self.__cache['player']['stun']['stunned_counter_double']
            data_2 = self.__cache['player']['stun']['seconds']
            cond_1 = '{{done}}' if data_1 >= 2 else '{{notDone}}'
            cond_2 = '{{done}}' if data_1 >= 100 else '{{notDone}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)).replace('{counter}', str(data_1)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_2)).replace('{counter}', str(data_2)))
            return (main_list, adv_list)
        self.generateFalshData = quest_146
    if self.__cache['currentID'] == 221:
        def quest_221(quest):
            main_list, adv_list = ([], [])
            data_1 = self.__cache['player']['stun']['stunned_counter_triple']
            data_2 = self.__cache['player']['stun']['seconds']
            cond_1 = '{{done}}' if data_1 >= 1 else '{{notDone}}'
            cond_2 = '{{done}}' if data_1 >= 150 else '{{notDone}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)).replace('{counter}', str(data_1)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_2)).replace('{counter}', str(data_2)))
            return (main_list, adv_list)
        self.generateFalshData = quest_221
    if self.__cache['currentID'] == 296:
        def quest_296(quest):
            main_list, adv_list = ([], [])
            data_1 = self.__cache['player']['stun']['stunned_counter_triple']
            data_2 = self.__cache['player']['stun']['seconds']
            cond_1 = '{{done}}' if data_1 >= 2 else '{{notDone}}'
            cond_2 = '{{done}}' if data_1 >= 200 else '{{notDone}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)).replace('{counter}', str(data_1)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_2)).replace('{counter}', str(data_2)))
            return (main_list, adv_list)
        self.generateFalshData = quest_296
    # "САУ-12. Дурной глаз" 72, 147, 222, 297
    if self.__cache['currentID'] == 72:
        def quest_72(quest):
            main_list, adv_list = ([], [])
            data_1 = self.__cache['player']['stun']['stunned']
            data_2 = self.__cache['player']['stun']['stunned_tracked_kill'] + self.__cache['player']['kill']['track_by_alies']
            cond_1 = '{{done}}' if data_1 >= 50 else '{{notDone}}'
            cond_2 = '{{done}}' if data_2 >= 1 else '{{notDone}}'
            cond_3 = '{{unknown}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)).replace('{counter}', str(data_1)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_2)).replace('{counter}', str(data_2)))
            adv_list.append(quest['adv'][1].replace('{state}', str(cond_3)))
            return (main_list, adv_list)
        self.generateFalshData = quest_72
    if self.__cache['currentID'] == 147:
        def quest_147(quest):
            main_list, adv_list = ([], [])
            data_1 = self.__cache['player']['stun']['stunned']
            data_2 = self.__cache['player']['stun']['stunned_tracked_kill'] + self.__cache['player']['kill']['track_by_alies']
            cond_1 = '{{done}}' if data_1 >= 100 else '{{notDone}}'
            cond_2 = '{{done}}' if data_2 >= 1 else '{{notDone}}'
            cond_3 = '{{unknown}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)).replace('{counter}', str(data_1)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_2)).replace('{counter}', str(data_2)))
            adv_list.append(quest['adv'][1].replace('{state}', str(cond_3)))
            return (main_list, adv_list)
        self.generateFalshData = quest_147
    if self.__cache['currentID'] == 222:
        def quest_222(quest):
            main_list, adv_list = ([], [])
            data_1 = self.__cache['player']['stun']['stunned']
            data_2 = self.__cache['player']['stun']['stunned_tracked_kill'] + self.__cache['player']['kill']['track_by_alies']
            cond_1 = '{{done}}' if data_1 >= 150 else '{{notDone}}'
            cond_2 = '{{done}}' if data_2 >= 2 else '{{notDone}}'
            cond_3 = '{{unknown}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)).replace('{counter}', str(data_1)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_2)).replace('{counter}', str(data_2)))
            adv_list.append(quest['adv'][1].replace('{state}', str(cond_3)))
            return (main_list, adv_list)
        self.generateFalshData = quest_222
    if self.__cache['currentID'] == 297:
        def quest_297(quest):
            main_list, adv_list = ([], [])
            data_1 = self.__cache['player']['stun']['stunned']
            data_2 = self.__cache['player']['stun']['stunned_tracked_kill'] + self.__cache['player']['kill']['track_by_alies']
            cond_1 = '{{done}}' if data_1 >= 200 else '{{notDone}}'
            cond_2 = '{{done}}' if data_2 >= 3 else '{{notDone}}'
            cond_3 = '{{unknown}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)).replace('{counter}', str(data_1)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_2)).replace('{counter}', str(data_2)))
            adv_list.append(quest['adv'][1].replace('{state}', str(cond_3)))
            return (main_list, adv_list)
        self.generateFalshData = quest_297
    # "САУ-13. Совместные действия (лично/взвод)" 73, 148, 223, 298
    if self.__cache['currentID'] == 73:
        def quest_73(quest):
            main_list, adv_list = ([], [])
            data_1 = self.__cache['player']['squad']['counter_any']
            data_2 = self.__cache['player']['stun']['stunned']
            cond_1 = '{{unknown}}' if data_1 >= 4 or data_2 >= 6 else '{{notDone}}'
            cond_2 = '{{unknown}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)).replace('{counter_1}', str(data_1)).replace('{counter_2}', str(data_2)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_2)))
            return (main_list, adv_list)
        self.generateFalshData = quest_73
    if self.__cache['currentID'] == 148:
        def quest_148(quest):
            main_list, adv_list = ([], [])
            data_1 = self.__cache['player']['squad']['counter_any']
            data_2 = self.__cache['player']['stun']['stunned']
            cond_1 = '{{unknown}}' if data_1 >= 6 or data_2 >= 8 else '{{notDone}}'
            cond_2 = '{{unknown}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)).replace('{counter_1}', str(data_1)).replace('{counter_2}', str(data_2)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_2)))
            return (main_list, adv_list)
        self.generateFalshData = quest_148
    if self.__cache['currentID'] == 223:
        def quest_223(quest):
            main_list, adv_list = ([], [])
            data_1 = self.__cache['player']['squad']['counter_any']
            data_2 = self.__cache['player']['stun']['stunned']
            cond_1 = '{{unknown}}' if data_1 >= 8 or data_2 >= 10 else '{{notDone}}'
            cond_2 = '{{unknown}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)).replace('{counter_1}', str(data_1)).replace('{counter_2}', str(data_2)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_2)))
            return (main_list, adv_list)
        self.generateFalshData = quest_223
    if self.__cache['currentID'] == 298:
        def quest_298(quest):
            main_list, adv_list = ([], [])
            data_1 = self.__cache['player']['squad']['counter_any']
            data_2 = self.__cache['player']['stun']['stunned']
            cond_1 = '{{unknown}}' if data_1 >= 10 or data_2 >= 12 else '{{notDone}}'
            cond_2 = '{{unknown}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)).replace('{counter_1}', str(data_1)).replace('{counter_2}', str(data_2)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_2)))
            return (main_list, adv_list)
        self.generateFalshData = quest_298
    # "САУ-14. Часть корабля - часть команды (лично/взвод)" 74, 149, 224, 299
    if self.__cache['currentID'] == 74:
        def quest_74(quest):
            main_list, adv_list = ([], [])
            data_1 = self.__cache['player']['stun']['seconds']
            data_2 = self.__cache['player']['damage']['track_by_alies']
            cond_1 = '{{done}}' if data_1 >= 70 or data_2 >= 400 else '{{notDone}}'
            cond_2 = '{{unknown}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)).replace('{counter_1}', str(data_1)).replace('{counter_2}', str(data_2)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_2)))
            return (main_list, adv_list)
        self.generateFalshData = quest_74
    if self.__cache['currentID'] == 149:
        def quest_149(quest):
            main_list, adv_list = ([], [])
            data_1 = self.__cache['player']['stun']['seconds']
            data_2 = self.__cache['player']['damage']['track_by_alies']
            cond_1 = '{{done}}' if data_1 >= 100 or data_2 >= 600 else '{{notDone}}'
            cond_2 = '{{unknown}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)).replace('{counter_1}', str(data_1)).replace('{counter_2}', str(data_2)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_2)))
            return (main_list, adv_list)
        self.generateFalshData = quest_149
    if self.__cache['currentID'] == 224:
        def quest_224(quest):
            main_list, adv_list = ([], [])
            data_1 = self.__cache['player']['stun']['seconds']
            data_2 = self.__cache['player']['damage']['track_by_alies']
            cond_1 = '{{done}}' if data_1 >= 180 or data_2 >= 800 else '{{notDone}}'
            cond_2 = '{{unknown}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)).replace('{counter_1}', str(data_1)).replace('{counter_2}', str(data_2)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_2)))
            return (main_list, adv_list)
        self.generateFalshData = quest_224
    if self.__cache['currentID'] == 299:
        def quest_299(quest):
            main_list, adv_list = ([], [])
            data_1 = self.__cache['player']['stun']['seconds']
            data_2 = self.__cache['player']['damage']['track_by_alies']
            cond_1 = '{{done}}' if data_1 >= 250 or data_2 >= 1000 else '{{notDone}}'
            cond_2 = '{{unknown}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)).replace('{counter_1}', str(data_1)).replace('{counter_2}', str(data_2)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_2)))
            return (main_list, adv_list)
        self.generateFalshData = quest_299
    # "САУ-15. Боги войны" 75, 150, 225, 300
    if self.__cache['currentID'] == 75:
        def quest_75(quest):
            main_list, adv_list = ([], [])
            data_1 = self.__cache['player']['stun']['stunned_damage'] + self.__cache['player']['damage']['track_by_alies']
            cond_1 = '{{unknown}}'
            cond_2 = '{{done}}' if data_1 >= 1000 else '{{notDone}}'
            cond_3 = '{{unknown}}' if self.__cache['player']['alive'] else '{{notDone}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)))
            main_list.append(quest['main'][1].replace('{state}', str(cond_2)).replace('{counter}', str(data_1)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_3)))
            return (main_list, adv_list)
        self.generateFalshData = quest_75
    if self.__cache['currentID'] == 150:
        def quest_150(quest):
            main_list, adv_list = ([], [])
            data_1 = self.__cache['player']['stun']['stunned_damage'] + self.__cache['player']['damage']['track_by_alies']
            cond_1 = '{{unknown}}'
            cond_2 = '{{done}}' if data_1 >= 1500 else '{{notDone}}'
            cond_3 = '{{unknown}}' if self.__cache['player']['alive'] else '{{notDone}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)))
            main_list.append(quest['main'][1].replace('{state}', str(cond_2)).replace('{counter}', str(data_1)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_3)))
            return (main_list, adv_list)
        self.generateFalshData = quest_150
    if self.__cache['currentID'] == 225:
        def quest_225(quest):
            main_list, adv_list = ([], [])
            data_1 = self.__cache['player']['stun']['stunned_damage'] + self.__cache['player']['damage']['track_by_alies']
            cond_1 = '{{unknown}}'
            cond_2 = '{{done}}' if data_1 >= 2500 else '{{notDone}}'
            cond_3 = '{{unknown}}' if self.__cache['player']['alive'] else '{{notDone}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)))
            main_list.append(quest['main'][1].replace('{state}', str(cond_2)).replace('{counter}', str(data_1)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_3)))
            return (main_list, adv_list)
        self.generateFalshData = quest_225
    if self.__cache['currentID'] == 300:
        def quest_300(quest):
            main_list, adv_list = ([], [])
            data_1 = self.__cache['player']['stun']['stunned_damage'] + self.__cache['player']['damage']['track_by_alies']
            cond_1 = '{{unknown}}'
            cond_2 = '{{done}}' if data_1 >= 3500 else '{{notDone}}'
            cond_3 = '{{unknown}}' if self.__cache['player']['alive'] else '{{notDone}}'
            main_list.append(quest['main'][0].replace('{state}', str(cond_1)))
            main_list.append(quest['main'][1].replace('{state}', str(cond_2)).replace('{counter}', str(data_1)))
            adv_list.append(quest['adv'][0].replace('{state}', str(cond_3)))
            return (main_list, adv_list)
        self.generateFalshData = quest_300

def hookOnBattleEvents(self, events):
    data = oldOnBattleEvents(self, events)
    stunned.event(self, events)
    return data

def hookShowShotResults(self, results):
    data = oldShowShotResults(self, results)
    stunned.shots(self, results)
    return data

def hookClearCache(self):
    data = oldClearCache(self)
    clear()
    return data

def hookStartBattle(self):
    data = oldStartBattle(self)
    updater()
    return data

def hookStopBattle(self):
    data = oldStopBattle(self)
    stunned.timerStop()
    return data


if enabled:
    stunned = Stunned()
    upd_config()
    mod_pro_potapov.g_potapov.updateFlashData = updateFlashDataArty

    oldClearCache = mod_pro_potapov.g_potapov.clearCache
    mod_pro_potapov.g_potapov.clearCache = hookClearCache

    clear()

    oldStartBattle = PlayerAvatar._PlayerAvatar__startGUI
    PlayerAvatar._PlayerAvatar__startGUI = hookStartBattle

    oldStopBattle = PlayerAvatar._PlayerAvatar__destroyGUI
    PlayerAvatar._PlayerAvatar__destroyGUI = hookStopBattle

    oldOnBattleEvents = PlayerAvatar.onBattleEvents
    PlayerAvatar.onBattleEvents = hookOnBattleEvents

    oldShowShotResults = PlayerAvatar.showShotResults
    PlayerAvatar.showShotResults = hookShowShotResults




