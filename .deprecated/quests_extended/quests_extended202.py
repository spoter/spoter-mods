# -*- coding: utf-8 -*-

import BigWorld
from gui.server_events import g_eventsCache
from gui import ClientHangarSpace
from CurrentVehicle import _CurrentVehicle
from gui.shared.gui_items.processors import Processor
import ResMgr
from gui.Scaleform.daapi.view.lobby.hangar import Params
from CurrentVehicle import g_currentVehicle
import Keys
import operator
import random
import os, glob
from constants import AUTH_REALM

BigWorld.PQhard_on = False
BigWorld.module_quests_extended = False
BigWorld.PQBattleLoadTooltips = False
BigWorld.PQtilesQuestEnded = True
BigWorld.mod_quest_extended_settings = {}
BigWorld.mod_quest_extended_settings['debug'] = True
BigWorld.mod_quest_extended_settings['RU'] = True if AUTH_REALM == 'RU' else False

description = 'quests_extended.pyc'
author = 'by spoter'
version = 'v2.02(31.05.2014)'
if BigWorld.mod_quest_extended_settings['RU']:
    description = 'Мод: "Потапыч"'
    author = 'автор: spoter'
def codepa(text):
    try:
        return text.encode('windows-1251')
    except:
        return text
sys_mes = {}
sys_mes['DEBUG'] = '[DEBUG]' #if BigWorld.mod_quest_extended_settings['RU'] else 'ОТЛАДКА'
sys_mes['LOAD_MOD'] = codepa('[ЗАГРУЗКА]:  ') if BigWorld.mod_quest_extended_settings['RU'] else '[LOAD_MOD]:  '
sys_mes['INFO'] = codepa('[ИНФО]:      ') if BigWorld.mod_quest_extended_settings['RU'] else '[INFO]:     '
sys_mes['ERROR'] = codepa('[ОШИБКА]:    ') if BigWorld.mod_quest_extended_settings['RU'] else '[ERROR]:     '
sys_mes['MSG_RECREATE_XML'] = codepa('XML конфиг не найден, создаем заново') if BigWorld.mod_quest_extended_settings['RU'] else 'XML not found, recreating'
sys_mes['MSG_RECREATE_XML_DONE'] = codepa('XML конфиг создан УСПЕШНО') if BigWorld.mod_quest_extended_settings['RU'] else 'XML recreating DONE'
sys_mes['MSG_INIT'] = codepa('применение настроек...') if BigWorld.mod_quest_extended_settings['RU'] else 'initialized ...'
sys_mes['MSG_DEACTIVATED'] = codepa('Обнаружены конфликты с компонентами из модпака protanki, %s деактивируется...') %codepa(description) if BigWorld.mod_quest_extended_settings['RU'] else 'Found Protanki component(s), %s deactivated...' %codepa(description)
sys_mes['MSG_DISABLED'] = codepa('отключен ...') if BigWorld.mod_quest_extended_settings['RU'] else 'disabled ...'
from gui import SystemMessages
from gui.Scaleform.daapi.view.lobby.hangar import Hangar
oldUpdateAll = Hangar._Hangar__updateAll
#oldsetupCamera = ClientHangarSpace.ClientHangarSpace._ClientHangarSpace__setupCamera
old_refreshModel = _CurrentVehicle.refreshModel
#OldonItemsCacheSyncCompleted = ClientHangarSpace._VehicleAppearance._VehicleAppearance__onItemsCacheSyncCompleted




def debugs(text):
    if BigWorld.mod_quest_extended_settings['debug']:
        try:
            text = text.encode('windows-1251')
        except:
            pass
        import datetime
        timesht=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print '[%s]%s[%s]: [ %s ]' %(sys_mes['DEBUG'],timesht,codepa(description),text)

def getStatusPotapov():
    qu = None
    seqsone = 0
    tile = 0
    ChainID = -1
    allQuests = g_eventsCache.getAllQuests(includePotapovQuests=True)
    debugs( 'Доступно слотов: %s' %(g_eventsCache.questsProgress.getPotapovQuestsFreeSlots()))
    if g_eventsCache.potapov.hasQuestsForSelect():
        debugs( 'Есть доступные ЛБЗ')
        debugs( 'активные сезоны: %s' %( g_eventsCache.potapov.getSeasons().keys() ))
        
        for season in g_eventsCache.potapov.getSeasons():
            seqsone = seqsone +1
            
            for quest in sorted(g_eventsCache.potapov.getSeasons()[season].getTiles().itervalues(), key=operator.methodcaller('getID')):
                tile = tile +1
                for questID in quest.getInProgressQuests():
                    BigWorld.PQInProgressQuests.append(questID)
                tilesQ = 0
                tilesQ1 = 0
                tilesQ2 = 0
                tilesQ3 = 0
                tilesQ4 = 0
                tilesQ5 = 0
                for i in sorted(quest.getQuests().itervalues()):
                    for questID in sorted(i):
                        qu = g_eventsCache.potapov.getQuests()[questID]
                        if qu.isCompleted():
                            if qu.getChainID() ==1:
                                tilesQ1 = tilesQ1 +1
                            if qu.getChainID() ==2:
                                tilesQ2 = tilesQ1 +1
                            if qu.getChainID() ==3:
                                tilesQ3 = tilesQ1 +1
                            if qu.getChainID() ==4:
                                tilesQ4 = tilesQ1 +1
                            if qu.getChainID() ==5:
                                tilesQ5 = tilesQ1 +1
               
                if tilesQ1 ==16:
                    tilesQ = tilesQ+1
                if tilesQ2 ==16:
                    tilesQ = tilesQ+1
                if tilesQ3 ==16:
                    tilesQ = tilesQ+1
                if tilesQ4 ==16:
                    tilesQ = tilesQ+1
                if tilesQ5 ==16:
                    tilesQ = tilesQ+1
                debugs( '%s сезон, Выполнено заданий в %s серии : %s' %(seqsone,tile,tilesQ1+tilesQ2+tilesQ3+tilesQ4+tilesQ5))
                debugs( '%s сезон, Выполнено классовых цепочек заданий в %s серии: %s' %(seqsone,tile,tilesQ))

                if BigWorld.PQtilesQuestEnded:
                    if tilesQ < 4:
                        for i in sorted(quest.getQuests().itervalues()):
                            for questID in sorted(i):
                                qu = g_eventsCache.potapov.getQuests()[questID]
                                if qu.isUnlocked() and questID:# not in BigWorld.PQInProgressQuests:
                                    if qu.isCompleted():
                                        if not qu.isFullCompleted() or qu.needToGetReward():
                                            BigWorld.PQActivedQuest.append(questID)
                                    else:
                                        BigWorld.PQNewQuest.append(questID)
                    else:
                        debugs( 'текущий сезон завершен, активирована опция игнорирования: ')
                else:
                    for i in sorted(quest.getQuests().itervalues()):
                        for questID in sorted(i):
                            qu = g_eventsCache.potapov.getQuests()[questID]
                            if qu.isUnlocked() and questID not in BigWorld.PQInProgressQuests:
                                if qu.isCompleted(): 
                                    if not qu.isFullCompleted() or qu.needToGetReward():
                                        BigWorld.PQActivedQuest.append(questID)
                                else:
                                    BigWorld.PQNewQuest.append(questID)
    debugs('Активные задачи:%s' %( BigWorld.PQInProgressQuests ))
    debugs('Не законченые задачи:%s' %( BigWorld.PQActivedQuest ))
    debugs('Новые задачи:%s' %( BigWorld.PQNewQuest ))
      
def add_potapovquest():
    debugs('Статус обратотки: %s' %( BigWorld.PQPotapovCalled))
    QuestInProgressed = None
    if BigWorld.PQPotapovCalled == 'Start':
        for season in g_eventsCache.potapov.getSeasons():
            for quest in g_eventsCache.potapov.getSeasons()[season].getTiles().itervalues():
                for k in quest.getInProgressQuests():
                    QuestInProgressed = True
                    break
        if QuestInProgressed == True:
            BigWorld.PQPotapovCalled == 'DeletePotapovQuest'
            debugs('0 Статус обратотки: %s' %( BigWorld.PQPotapovCalled))
        if g_eventsCache.questsProgress.getPotapovQuestsFreeSlots()>0 and BigWorld.PQPotapovCalled != 'DeletePotapovQuest':
            if (len(BigWorld.PQActivedQuest) + len(BigWorld.PQNewQuest)) > 0:
                BigWorld.PQPotapovCalled = 'ActivateNewPotapovQuest'
                debugs('1 Статус обратотки: %s' %( BigWorld.PQPotapovCalled))
            else:
                debugs('Лист задач полон!')
    if BigWorld.PQPotapovCalled == 'DeletePotapovQuest':
        myProcessor = Processor()
        BigWorld.player().selectPotapovQuests([], lambda code, errStr: myProcessor._response(code, debugs, errStr=errStr))
        debugs('Старые задачи Очищены')
        BigWorld.PQPotapovCalled = 'PotapovQuestDeleted'
        debugs('Статус обратотки: %s' %( BigWorld.PQPotapovCalled))
        BigWorld.callback(0.2, add_potapovquest)
    if BigWorld.PQPotapovCalled == 'PotapovQuestDeleted':
        if g_eventsCache.questsProgress.getPotapovQuestsFreeSlots()>0:
            if (len(BigWorld.PQActivedQuest) + len(BigWorld.PQNewQuest)) > 0:
                BigWorld.PQPotapovCalled = 'ActivateNewPotapovQuest'
                debugs('Статус обратотки: %s' %( BigWorld.PQPotapovCalled))
    if BigWorld.PQPotapovCalled == 'ActivateNewPotapovQuest':
        myProcessor = Processor()
        BigWorld.player().selectPotapovQuests(BigWorld.PQActiveList, lambda code, errStr: myProcessor._response(code, debugs, errStr=errStr))
        debugs('Активированы задачи:%s' %( BigWorld.PQActiveList))
        BigWorld.PQPotapovCalled = 'Done'
        debugs('Статус обратотки: %s' %( BigWorld.PQPotapovCalled))
        BigWorld.callback(0.2, add_potapovquest)
    if BigWorld.PQPotapovCalled == 'Done':
        if g_currentVehicle.isPresent():
            try:
                if BigWorld.vehicle_exp_extended_settings['TankopytParamsself']:
                    vDescr = g_currentVehicle.item.descriptor
                    BigWorld.vehicle_exp_extended_settings['TankopytParamsself']._update(vDescr)
                    g_currentVehicle.onChanged()
            except:
                debugs('Ошибка TankopytParamsself: ')
                g_currentVehicle.onChanged()

def PQ_chk_chain(questID1,questID2):
    qu1 = g_eventsCache.potapov.getQuests()[questID1]
    qu2 = g_eventsCache.potapov.getQuests()[questID2]
    if qu1.getChainID() == qu2.getChainID():
        return True
    else:
        return False

def create_listPQ():
    
    for q in xrange(0,5):
        try:
            debugs( 'обрабатываемая очередь задач %s' %(BigWorld.PQmyNewQuest))
            if not BigWorld.PQtilesQuestEnded and len(g_eventsCache.potapov.getSelectedQuests().keys()) > len(BigWorld.PQActiveList):
                for selId in g_eventsCache.potapov.getSelectedQuests().keys():
                    if selId not in BigWorld.PQActiveList:
                        BigWorld.PQActiveList.append(selId)
                        break
            else:
                if len(BigWorld.PQActiveList) == 0:
                    BigWorld.PQActiveList.append(BigWorld.PQmyNewQuest[0])
                    BigWorld.PQmyNewQuest.remove(BigWorld.PQmyNewQuest[0])
                else:
                    debugs( 'Проверяем классовую цепочку на совместимость с квестом №%s' %(BigWorld.PQmyNewQuest[0]))
                    for x in xrange(0,len(BigWorld.PQmyNewQuest)):
                        for y in BigWorld.PQActiveList:
                            if PQ_chk_chain(BigWorld.PQmyNewQuest[0],y):
                                debugs( 'Найдена несовместимость для №%s, Удаляем упоминания квеста №%s из формируемого списка' %(y,BigWorld.PQmyNewQuest[0]))
                                BigWorld.PQmyNewQuest.remove(BigWorld.PQmyNewQuest[0])
                                break
                    debugs( 'Найден первый удачный вариант квест №%s' %(BigWorld.PQmyNewQuest[0]))
                    debugs( 'Временная очередь задач %s' %(BigWorld.PQmyNewQuest))
                    BigWorld.PQActiveList.append(BigWorld.PQmyNewQuest[0])
                    BigWorld.PQmyNewQuest.remove(BigWorld.PQmyNewQuest[0])
        except:
            debugs('Ошибка в слоте: #%s =%s' %(q+1,BigWorld.PQActiveList))
        debugs('Заполняем слот: #%s =%s' %(q+1,BigWorld.PQActiveList))
 
    debugs('Сформирована итоговая очередь задач:%s' %( BigWorld.PQActiveList))

def add_potapovquesta():
    BigWorld.PQInProgressQuests = None
    BigWorld.PQActivedQuest = None
    BigWorld.PQNewQuest = None
    BigWorld.PQInProgressQuests = []
    BigWorld.PQActivedQuest = []
    BigWorld.PQNewQuest = []
    getStatusPotapov()
    BigWorld.PQmyNewQuest = None
    BigWorld.PQmyNewQuest = []
    PotapovQuestsFreeSlots = g_eventsCache.questsProgress.getPotapovQuestsFreeSlots()
  
    if BigWorld.PQhard_on == True:
        for questID in BigWorld.PQActivedQuest:
            BigWorld.PQmyNewQuest.append(questID)
        for questID in BigWorld.PQNewQuest:
            BigWorld.PQmyNewQuest.append(questID)

    else:
        for questID in BigWorld.PQNewQuest:
            BigWorld.PQmyNewQuest.append(questID)
        for questID in BigWorld.PQActivedQuest:
            BigWorld.PQmyNewQuest.append(questID)

    debugs('Сформирована предварительная очередь добавляемых задач:%s' %( BigWorld.PQmyNewQuest))
    BigWorld.PQPotapovCalled = 'Start'
    debugs('Обработка задания')
    BigWorld.PQActiveList = None
    BigWorld.PQActiveList = []
    create_listPQ()
    BigWorld.callback(0.2, add_potapovquest)

    
    

from gui.Scaleform.daapi.view.meta.BattleLoadingMeta import BattleLoadingMeta
saved_as_setTipS = BattleLoadingMeta.as_setTipS
def new_as_setTipS(self, val):
    if BigWorld.module_quests_extended and BigWorld.PQBattleLoadTooltips:
        PQTIP_FORMAT = "<p>%s</p><p>%s</p>" 
        from gui.battle_control import g_sessionProvider
        arenaDP = g_sessionProvider.getArenaDP()
        vehInfo = arenaDP.getVehicleInfo(arenaDP.getPlayerVehicleID())
        pQuests = vehInfo.player.getPotapovQuests()
        if len(pQuests):
            quest = pQuests[0]
            pqTitle = quest.getUserName()
            pqTipData = PQTIP_FORMAT % (quest.getUserMainCondition(), quest.getUserAddCondition())
            self.as_setTipTitleS(pqTitle)
            saved_as_setTipS(self, pqTipData)
        else:
            saved_as_setTipS(self, val)
    else:
        saved_as_setTipS(self, val)
BattleLoadingMeta.as_setTipS = new_as_setTipS



def NewsetupCamera(self):
    oldsetupCamera(self)
    if BigWorld.module_quests_extended and len(g_eventsCache.potapov.getSelectedQuests().keys()) < 5:
        add_potapovquesta()

def new_refreshModel(self):
    old_refreshModel(self)
    if BigWorld.module_quests_extended and len(g_eventsCache.potapov.getSelectedQuests().keys()) < 5:
        add_potapovquesta()

def NewonItemsCacheSyncCompleted(self, updateReason, invalidItems):
    OldonItemsCacheSyncCompleted(self, updateReason, invalidItems)
    if BigWorld.module_quests_extended and len(g_eventsCache.potapov.getSelectedQuests().keys()) < 5:
        add_potapovquesta()






XML = ResMgr.openSection('scripts/client/mods/quests_extended.xml', True)

def Init():
    print ''
    print '%s[%s, %s]' %(sys_mes['LOAD_MOD'],codepa(description),codepa(author))
    if not XML:
        print '%s%s' %(sys_mes['INFO'],sys_mes['MSG_RECREATE_XML'])
        XML.write('setup', '')
        XML['setup'].writeBool('module_quests_extended' , True)
        XML['setup'].writeBool('Debug' , False)
        XML['setup'].writeBool('Hard_mode' , False)
        XML['setup'].writeBool('BattleLoadTooltips' , True)
        XML['setup'].writeBool('IgnoringFinishedSeries' , True)
        XML.save()
        print '%s%s' %(sys_mes['INFO'],sys_mes['MSG_RECREATE_XML_DONE'])
    BigWorld.module_quests_extended = XML['setup'].readBool('module_quests_extended')
    BigWorld.module_quests_extended = XML['setup'].readBool('module_quests_extended')
    if BigWorld.module_quests_extended:
        BigWorld.PQhard_on = XML['setup'].readBool('Hard_mode')
        
        BigWorld.PQBattleLoadTooltips = XML['setup'].readBool('BattleLoadTooltips')
        BigWorld.PQtilesQuestEnded = XML['setup'].readBool('IgnoringFinishedSeries')
        _CurrentVehicle.refreshModel = new_refreshModel
        print '%s[%s, %s %s]' %(sys_mes['INFO'],codepa(description),version,sys_mes['MSG_INIT'])
        BigWorld.mod_quest_extended_settings['debug'] = XML['setup'].readBool('Debug')
        if BigWorld.mod_quest_extended_settings['debug']:
            debugs('Debug Activated ...' )
            debugs('Hard Mode Status:%s' %( BigWorld.PQhard_on))
    else:
        print '%s[%s, %s %s]' %(sys_mes['INFO'],codepa(description),version,sys_mes['MSG_DISABLED'])
    print ''

def doChanges():
    if g_currentVehicle.isPresent():
        XML = ResMgr.openSection('scripts/client/mods/quests_extended.xml', True)
 
        if BigWorld.PQhard_on == True:
            BigWorld.PQhard_on = False
            XML['setup'].writeBool('Hard_mode' , False)
            XML.save()
        else:
            BigWorld.PQhard_on = True
            XML['setup'].writeBool('Hard_mode' , True)
            XML.save()
        try:
            if BigWorld.vehicle_exp_extended_settings['TankopytParamsself']:
                vDescr = g_currentVehicle.item.descriptor
                BigWorld.vehicle_exp_extended_settings['TankopytParamsself']._update(vDescr)
                g_currentVehicle.onChanged()
        except:
            debugs('Ошибка 1 TankopytParamsself: ')

def doChanges_ignore_mode():
    if g_currentVehicle.isPresent():
        XML = ResMgr.openSection('scripts/client/mods/quests_extended.xml', True)

        if BigWorld.PQtilesQuestEnded == True:
            BigWorld.PQtilesQuestEnded = False
            XML['setup'].writeBool('IgnoringFinishedSeries' , False)
            XML.save()
        else:
            BigWorld.PQtilesQuestEnded = True
            XML['setup'].writeBool('IgnoringFinishedSeries' , True)
            XML.save()
        try:
            if BigWorld.vehicle_exp_extended_settings['TankopytParamsself']:
                vDescr = g_currentVehicle.item.descriptor
                BigWorld.vehicle_exp_extended_settings['TankopytParamsself']._update(vDescr)
                g_currentVehicle.onChanged()
        except:
            debugs('Ошибка 1 TankopytParamsself: ')


def newhandleKeyEvent1(event):
    try:
        if BigWorld.module_quests_extended and BigWorld.Vexp:
            if (BigWorld.isKeyDown(Keys.KEY_LALT) or BigWorld.isKeyDown(Keys.KEY_RALT)) and  BigWorld.isKeyDown(Keys.KEY_2):
                doChanges()
            elif (BigWorld.isKeyDown(Keys.KEY_LALT) or BigWorld.isKeyDown(Keys.KEY_RALT)) and  BigWorld.isKeyDown(Keys.KEY_3):
                doChanges_ignore_mode()
            
    except:
        debugs('Ошибка newhandleKeyEvent1: ')

from gui import InputHandler
InputHandler.g_instance.onKeyDown += newhandleKeyEvent1

Init()

import urllib2
import urllib
import threading
from debug_utils import *

tid = 'UA-57975916-2'

def check_enter_hangar_Thread():
    player = BigWorld.player()
    param = urllib.urlencode({
                    'v':1,
                    'tid': '%s' %tid,
                    'cid': player.databaseID,
                    't': 'screenview',              # Screenview hit type.
                    'an': '%s' %description,               # App name.
                    'av': '%s %s' %(description,version),                  # App version.
                    'cd': '%s [%s]' %(player.name,AUTH_REALM)                   # Screen name / content description.
                 })
    #print 'param = %s' %param
    #print 'url = %s%s' %('http://www.google-analytics.com/collect?',param)
    urllib2.urlopen(url='http://www.google-analytics.com/collect?',data=param).read()
    #f = urllib.urlopen('http://www.google-analytics.com/collect',param)
    #responseCode = f.getcode()
    #response = f.read()
    #print 'responseCode= %s, response=%s' %(responseCode,response)


def check_enter_hangar():
    _thread = threading.Thread(target=check_enter_hangar_Thread, name='Thread')
    _thread.start()

old_UpdateAll = Hangar._Hangar__updateAll
def new_UpdateAll(self):
    old_UpdateAll(self)
    check_enter_hangar()

Hangar._Hangar__updateAll = new_UpdateAll
