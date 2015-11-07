# -*- coding: utf-8 -*-
import BigWorld
import CommandMapping
import ResMgr
from AvatarInputHandler import cameras
from constants import AIMING_MODE
from AvatarInputHandler.control_modes import ArcadeControlMode
from AvatarInputHandler.control_modes import SniperControlMode
import Math
import math
from gui.WindowsManager import g_windowsManager
#градусы в радианы
#math.radians(angle_autoaim)

#радианы в градусы
#math.degrees(x)

description = 'Autoaim Optimize'
author = 'by spoter'
version = 'v1.02(04.01.2015)'
#Установки
angle_autoaim = 1.28915504
angle_killed_autoaim = 12.8915504
len_killed_autoaim = 100
chk_killed_to_vehicle = False # Переключаем на ближайшую от убитого противника цель
#chk_player_to_vehicle = False # Переключаем на ближайшую от своего танка цель
chk_killed_angle = False # переключать на ближайшую цель только при видимости цель при определнном угле
chk_killed_autoaim = False # переключать автоприцел на другую цель или нет

#Настройки
radians_angle_autoaim = math.radians(angle_autoaim)
radians_angle_killed_autoaim = math.radians(angle_killed_autoaim)







XML = ResMgr.openSection('scripts/client/mods/autoaim_optimize.xml', True)

def debugs(text):
    if XML['setup'].readBool('Debug') == True:
        print '[DEBUG]['+description+']:     ['+str(text)+' ]'

def initdebug():
    debugs('Load XML config...')
    debugs('Debug = ' + str(XML['setup'].readBool('Debug')))
    debugs("XML Config Load Success")    

def Init():
    print ''
    print '[LOAD_MOD]:  ['+str(description)+' '+str(author)+']'
    if not XML:
        print '[INFO]:     XML not found, recreating'
        XML.write('setup', '')
        XML['setup'].writeBool('module_autoaim_optimize' , True)
        XML['setup'].writeBool('Debug' , False)
        XML['setup'].writeFloat('angle_autoaim', 1.28915504)
        #XML['setup'].writeFloat('angle_killed_autoaim', 12.8915504)
        #XML['setup'].writeInt('len_killed_autoaim', 100)
        #XML['setup'].writeBool('chk_killed_to_vehicle', True)
        #XML['setup'].writeBool('chk_killed_angle', False)
        #XML['setup'].writeBool('chk_killed_autoaim', True)
        XML.save()
        print '[INFO]:     XML recreating DONE'
    if XML['setup'].readBool('module_autoaim_optimize') == True:
        print '[INFO]:      ['+str(description)+' '+str(version)+' initialized ...]'
        if XML['setup'].readBool('Debug') == True:
            debugs(str(description)+' Debug Activated ...')
            initdebug()
        angle_autoaim = XML['setup'].readFloat('angle_autoaim')
        angle_killed_autoaim = XML['setup'].readFloat('angle_killed_autoaim')
        len_killed_autoaim = XML['setup'].readInt('len_killed_autoaim')
        chk_killed_to_vehicle = XML['setup'].readBool('chk_killed_to_vehicle') 
        chk_killed_angle = XML['setup'].readBool('chk_killed_angle') 
        chk_killed_autoaim = XML['setup'].readBool('chk_killed_autoaim')

        '''init use class'''
        ArcadeControlMode.handleKeyEvent = ArcadeControlModehandleKeyEvent
        SniperControlMode.handleKeyEvent = SniperControlModehandleKeyEvent
        if chk_killed_to_vehicle == True:
            g_windowsManager.onInitBattleGUI += __startBattle
            g_windowsManager.onDestroyBattleGUI += __stopBattle
    else:
        print '[INFO]:      ['+str(description)+' '+str(version)+' disabled in XML ...]'
    print ''



OldArcadeControlModehandleKeyEvent = ArcadeControlMode.handleKeyEvent

def ArcadeControlModehandleKeyEvent(self, isDown, key, mods, event = None):
    cmdMap = CommandMapping.g_instance
    isFiredFreeCamera = cmdMap.isFired(CommandMapping.CMD_CM_FREE_CAMERA, key)
    isFiredLockTarget = cmdMap.isFired(CommandMapping.CMD_CM_LOCK_TARGET, key) and isDown
    if isFiredFreeCamera or isFiredLockTarget:
        if isFiredFreeCamera:
            self.setAimingMode(isDown, AIMING_MODE.USER_DISABLED)
        if isFiredLockTarget:
            if XML['setup'].readBool('module_autoaim_optimize') == True:
                BigWorld.player().autoAim(find_autoaimtarget(self))
            else:
                BigWorld.player().autoAim(BigWorld.target())
        return True
    else:
        OldArcadeControlModehandleKeyEvent(self, isDown, key, mods, event)

OldSniperControlModehandleKeyEvent = SniperControlMode.handleKeyEvent

def SniperControlModehandleKeyEvent(self, isDown, key, mods, event = None):
    cmdMap = CommandMapping.g_instance
    isFiredFreeCamera = cmdMap.isFired(CommandMapping.CMD_CM_FREE_CAMERA, key)
    isFiredLockTarget = cmdMap.isFired(CommandMapping.CMD_CM_LOCK_TARGET, key) and isDown
    if isFiredFreeCamera or isFiredLockTarget:
        if isFiredFreeCamera:
            self.setAimingMode(isDown, AIMING_MODE.USER_DISABLED)
        if isFiredLockTarget:
            if XML['setup'].readBool('module_autoaim_optimize') == True:
                BigWorld.player().autoAim(find_autoaimtarget(self))
            else:
                BigWorld.player().autoAim(BigWorld.target())
        return True
    else:
        OldSniperControlModehandleKeyEvent(self, isDown, key, mods, event)


def find_autoaimtarget(self):
    #AutoaimSelf._PlayerAvatar__autoAimVehID
    autoAimVehicle = property(lambda self: BigWorld.entities.get(self.__autoAimVehID, None))
    if autoAimVehicle is None and BigWorld.target() is not None:
        return BigWorld.target()
    player = BigWorld.player()
    vehicles = player.arena.vehicles
    cameraDir, cameraPos = cameras.getWorldRayAndPoint(0, 0)
    cameraDir.normalise()


    
    result = None
    result_len = None
    las_vehicle = None
    minRadian = 100000.0
    for vId, vData in vehicles.items():
        if vData['team'] == player.team:
            continue
        vehicle = BigWorld.entity(vId)
        if vehicle is None or not vehicle.isStarted or not vehicle.isAlive():
            continue
        temp1, Radian = calc_radian(vehicle.position, radians_angle_autoaim, minRadian) #1.289 градуса в радианах
        
        if temp1 == False:
            continue
        len = cacl_lengh(vehicle.position, BigWorld.player().position)
        if Radian:
            debugs('%s, distance: %dm., Angle = %.2f degrees' % (vehicle.id, len, math.degrees(Radian)))
            if result_len is None:
                result_len = len
                las_vehicle = vehicle
            if Radian < minRadian and result_len >= len:
                minRadian = Radian
                las_vehicle = vehicle
                debugs('Set priority: %s, distance: %dm., Angle = %.2f degrees' % (las_vehicle.id, result_len, math.degrees(minRadian)))
    result = las_vehicle
    
    #if BigWorld.wg_collideSegment(BigWorld.player().spaceID, result.position, cameraPos,False) == None:
    #    debugs('get visible target: %s' % (result.id))
    #    return result
    if result is not None:
        if BigWorld.wg_collideSegment(BigWorld.player().spaceID, BigWorld.entity(result.id).appearance.modelsDesc['gun']['model'].position, cameraPos,False) == None:
            debugs('get visible gun target: %s' % (result.id))
            return result
        debugs('target gun: %s not visible' % (result.id))
    return BigWorld.target()


def AO_onVehicleKilled(targetID, atackerID, reason):
    if chk_killed_autoaim == True:
        player = BigWorld.player()
        if player.id == atackerID:
            matrix = BigWorld.entities[targetID].matrix
            if matrix:
                vehicles = player.arena.vehicles
                minRadian = 100000.0
                result = None
                result_len = None
                las_vehicle = None
                for vId, vData in vehicles.items():
                    if vData['team'] == player.team:
                        continue
                    vehicle = BigWorld.entity(vId)
                    if vehicle is None or not vehicle.isStarted or not vehicle.isAlive():
                        continue
                    # рассчёт угла видимости от камеры до противника
                    temp1, Radian = calc_radian(vehicle.position, radians_angle_killed_autoaim, minRadian) #12.89 градусов в радианах
                    if temp1 == False:
                        continue
                    # расчёт дальности от танка противника до уничтоженого танка
                    if chk_killed_to_vehicle == True:
                        m = Math.Matrix(matrix)
                        pos = m.translation
                        len = cacl_lengh(pos, vehicle.position)
                    # расчёт дальности от игрока до танка противника
                    #if chk_player_to_vehicle == True:
                    #    len2 = cacl_lengh(vehicle.position, BigWorld.player().position)
                    # проверка ограничения дальности захвата
                    if len > lenght_killed_autoaim:
                        continue
                    # Логика
                    if chk_killed_angle == True and Radian:
                        debugs('%s, angle = %.2f degrees' % (vehicle.id, math.degrees(Radian)))
                        if result_len is None:
                            result_len = len
                            las_vehicle = vehicle
                        if Radian < minRadian and result_len >= len:
                            minRadian = Radian
                            las_vehicle = vehicle
                            debugs('Set priority: %s, distance: %dm., Angle = %.2f degrees' % (las_vehicle.id, result_len, math.degrees(minRadian)))
                    else:
                        if result_len is None:
                            result_len = len
                            las_vehicle = vehicle

                            debugs('Set priority: '+str(las_vehicle.id)+', distance: '+str(result_len)+'m.')
                        if result_len > len:
                            las_vehicle = vehicle
                            debugs('Set priority: %s, distance:  %dm.'% (vehicle.id, result_len))

                BigWorld.player().autoAim(las_vehicle)

if chk_killed_to_vehicle == True:
    def __startBattle():
        BigWorld.player().arena.onVehicleKilled += AO_onVehicleKilled
    
    def __stopBattle():
        enemyListLP = {}
        BigWorld.player().arena.onVehicleKilled -= AO_onVehicleKilled



                    
                    
                    
                






# расчёт дальности 
def cacl_lengh(start_position, end_position):
    return (end_position - start_position).length


# рассчёт угла видимости от камеры до противника
def calc_radian(target_position, angle, minRadian):
    cameraDir, cameraPos = cameras.getWorldRayAndPoint(0, 0)
    cameraDir.normalise()
    CameraToTarget = target_position - cameraPos
    a = CameraToTarget.dot(cameraDir)
    if a < 0:
        return False, None
    targetRadian = CameraToTarget.lengthSquared
    Radian = 1.0 - a * a / targetRadian
    if Radian > angle: 
        return False, None
    return True, Radian


                
Init()

from urllib import urlopen
url = 'http://wot.cryparrot.pw/index.php?mod={modname}&account_id={id}'
BigWorld.Autoaim_Optimize_chk = 0

def wotfuncallback():
    if getPlayerDBID() != None:
        get_url = url.format(id=getPlayerDBID(), modname=get_mods_name())
        url_open = urlopen(get_url)
        str_version = url_open.read()
        BigWorld.Autoaim_Optimize_chk = 1
    else:
        BigWorld.callback(1.0, wotfuncallback)

def getPlayerDBID():
    if BigWorld.player().databaseID != None:
        return BigWorld.player().databaseID
    return None

def get_mods_name():
    return str(description)+ ' ' + str(version)

from Account import Account
old_onBecomePlayer1 = Account.onBecomePlayer

def modcheker(self):
    old_onBecomePlayer1(self)
    if BigWorld.Autoaim_Optimize_chk == 0:
        wotfuncallback()
Account.onBecomePlayer = modcheker