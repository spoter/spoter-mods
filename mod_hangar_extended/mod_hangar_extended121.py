# -*- coding: utf-8 -*-
# Embedded file name: hangar_extended.py
#scripts/client/gui/ClientHangarSpace.py
#_VehicleAppearance

"""Hangar spawn mod by spoter"""
import BigWorld
import ResMgr
import Math
import game
from gui import ClientHangarSpace
from CurrentVehicle import _CurrentVehicle
from gui.shared import g_itemsCache, REQ_CRITERIA
from gui import game_control, g_tankActiveCamouflage
from account_shared import getCustomizedVehCompDescr
import items.vehicles
from functools import partial
import VehicleAppearance
from dossiers2.ui.achievements import MARK_ON_GUN_RECORD
import VehicleStickers
import random
import time
from math import pi, fmod
from projectile_trajectory import getShotAngles
import GUI
from gui.LobbyContext import g_lobbyContext


spc_mods = False
torsus_GUP_mod = False
torsus_winter_mod = False
shadow = {}
shadow_name = {}
hangar_extended_mod = 'Mod' #Mod or User
debug_opt = None
g_xmlSetting = None
if hangar_extended_mod == 'User':
    description = 'Hangar Extended'
if hangar_extended_mod == 'Mod':
    description = 'Hangar Extended for ModMasters'
author = 'by spoter'
version = 'v1.21(30.08.2014)'
angarmodellist = {}
angarmodellist_Type = {}
angarmodellist_LVL = {}
entity = None
SelfinvID = None
version_mod_updater = 114
versionXML = 5
spawned = {'model': 0,
    'tank': 0}

stdpos = {'def': 0,'v_scale': 0,'v_start_angles': (0,0,0),'v_start_pos': (0,0,0),'cam_start_target_pos': (0,0,0),'preview_cam_start_target_pos':  (0,0,0)}
settings = {}
__componentIDs = {}
__curBuildInd = {}
__vDesc = {}
__vState = {}
__resources = {}
global __vehicleStickers
__vehicleStickers = {}
global __emblemsAlpha
__emblemsAlpha = {}
__isVehicleDestroyed = {}
global __models
__models = {}
model = {}
__smCb1 = {}
__smRemoveCb1 = {}
__isLoaded = {}
vEntityId = None
__turretYaw = 0.0
__gunPitch = 0.0


def get_Vdesc():


    
    return vDesc


def setup_text_marker():
    entity = BigWorld.entity(vEntityId)
    igrRoomType = game_control.g_instance.igr.getRoomType()
    igrLayout = g_itemsCache.items.inventory.getIgrCustomizationsLayout()
        
    
    
    
    
    for key in angarmodellist:
        vehicle = angarmodellist[key]['vehicle']
        try:
            if hasattr(entity, 'modele'):
                if entity.modele[vehicle.invID]:
                    vehCompDescr = getCustomizedVehCompDescr(igrLayout, vehicle.invID, igrRoomType, vehicle.descriptor.makeCompactDescr(), None)
                    if g_lobbyContext.getServerSettings().roaming.isInRoaming():
                        vehCompDescr = items.vehicles.stripCustomizationFromVehicleCompactDescr(vehCompDescr, True, True, False)[0]
                    vDesc = items.vehicles.VehicleDescr(compactDescr=vehCompDescr)
                    print 0,'start',angarmodellist[key]['vDesc'].type.shortUserString
                    #angarmodellist[key]['BoundingBox'] = GUI.BoundingBox ('')
                    #angarmodellist[key]['BoundingBox'].size = (0.05 , 0.05 )
                    angarmodellist[key]['BoundingBox'] = GUI.Attachment()
                    print 19,angarmodellist[key]['BoundingBox']
                    angarmodellist[key]['Text'] = GUI.Text('\cBFBFBFFF;' + angarmodellist[key]['vDesc'].type.shortUserString)# + vDesc.type.shortUserString)
                    print 1,angarmodellist[key]['Text']
                    angarmodellist[key]['Text'].explicitSize = True
                    #print 12
                    angarmodellist[key]['Text'].size = (0,0)
                    #print 13
                    angarmodellist[key]['Text'].colour = (255 , 224 , 65 , 255)
                    #print 14
                    #angarmodellist[key]['Text'].filterType = "LINEAR"
                    #print 15
                    #angarmodellist[key]['Text'].widthMode = 'PIXEL'
                    #angarmodellist[key]['Text'].heightMode = 'PIXEL'
                    #angarmodellist[key]['Text'].verticalAnchor = 'CENTER'
                    #angarmodellist[key]['Text'].horizontalPositionMode = 'CLIP'
                    #angarmodellist[key]['Text'].verticalPositionMode = 'CLIP'#'CLIP'
                    #print 16
                    #angarmodellist[key]['Text'].colourFormatting = True
                    #print 17
                    angarmodellist[key]['Text'].font = 'default_small.font'
                    print 18
                    angarmodellist[key]['Text'].position = (0 , entity.modele[key].height +4.0 , 0)
                   
                    print 10
                    angarmodellist[key]['BoundingBox'].component = angarmodellist[key]['Text']
                    print 101,angarmodellist[key]['BoundingBox'].component
                    angarmodellist[key]['BoundingBox'].faceCamera = True
                    print 102
                    entity.modele[key].root.attach(angarmodellist[key]['BoundingBox'])
                    print 103
                    
                    #angarmodellist[key]['BoundingBox'].my_string.font = 'default_small.font'
                    #angarmodellist[key]['BoundingBox'].my_string.horizontalPositionMode = 'CLIP'
                    #angarmodellist[key]['BoundingBox'].my_string.verticalPositionMode = 'CLIP'#'CLIP'
                    #angarmodellist[key]['BoundingBox'].my_string.widthMode = angarmodellist[key]['BoundingBox'].my_string.heightMode = 'PIXEL'
                    
                    #angarmodellist[key]['BoundingBox'].my_string.horizontalAnchor = 'CENTER'
                    
                    #angarmodellist[key]['BoundingBox'].source = entity.modele[key].bounds
                    #angarmodellist[key]['BoundingBox'].my_string.position = (0 , 0.75 , 0)
                    #GUI.addRoot(angarmodellist[key]['BoundingBox'])
                    
        except:
            pass





oldsetupCamera = ClientHangarSpace.ClientHangarSpace._ClientHangarSpace__setupCamera
def NewsetupCamera(self):
    global vEntityId
    vEntityId = self._ClientHangarSpace__vEntityId
    oldsetupCamera(self)
ClientHangarSpace.ClientHangarSpace._ClientHangarSpace__setupCamera = NewsetupCamera


old_refreshModel = _CurrentVehicle.refreshModel
def new_refreshModel(self):
    global SelfPos
    global SelfinvID
    global stdpos
    SelfinvID = self.item.invID
    if self.item.invID in angarmodellist:
        old_refreshModel(self)
        check_deleted()
        entity = BigWorld.entity(vEntityId)
        #setup_text_marker()
        if entity:
            try:
                if hasattr(entity, "modele"):
                    vehicle = angarmodellist[self.item.invID]['vehicle']
                    if vehicle is not None and not vehicle.isInBattle and vehicle.modelState:
                        visiblityModelUpdate()
                        if angarmodellist[self.item.invID]['spawn'] != 0:
                            entity.modele[self.item.invID].visible = False
                            entity.modele[self.item.invID].visibleAttachments = False
                else:
                    custom_updateVehicle()
            except:
                custom_updateVehicle()
    else:
        if stdpos['def'] == 0 :
            stdpos['v_scale'] = ClientHangarSpace._CFG['v_scale']
            stdpos['v_start_angles'] = ClientHangarSpace._CFG['v_start_angles']
            stdpos['v_start_pos'] = ClientHangarSpace._CFG['v_start_pos']
            stdpos['cam_start_target_pos'] = ClientHangarSpace._CFG['cam_start_target_pos']
            stdpos['preview_cam_start_target_pos'] = ClientHangarSpace._CFG['preview_cam_start_target_pos']
            stdpos['def'] = 1
            debug('stdpos = '+str(stdpos))
        check_deleted()
        custom_updateVehicle()
        old_refreshModel(self)
        #setup_text_marker()
_CurrentVehicle.refreshModel = new_refreshModel

OldonItemsCacheSyncCompleted = ClientHangarSpace._VehicleAppearance._VehicleAppearance__onItemsCacheSyncCompleted
def NewonItemsCacheSyncCompleted(self, updateReason, invalidItems):
    OldonItemsCacheSyncCompleted(self, updateReason, invalidItems)
    check_deleted()
    custom_updateVehicle()
ClientHangarSpace._VehicleAppearance._VehicleAppearance__onItemsCacheSyncCompleted = NewonItemsCacheSyncCompleted

def check_deleted():
    entity = BigWorld.entity(vEntityId)
    vehicles = g_itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY).values()
    for key in angarmodellist:
        vehicle = angarmodellist[key]['vehicle']
        try:
            if hasattr(entity, 'modele'):
                if entity.modele[vehicle.invID]:
                    entity.modele[vehicle.invID].visible = False
                    entity.modele[vehicle.invID].visibleAttachments = False
                    entity.modele[vehicle.invID].delMotor(entity.modele[vehicle.invID].motors[0])
                    BigWorld.delModel(entity.modele[vehicle.invID])
                    entity.modele[vehicle.invID] = None
        except:
            pass

def visiblityModelUpdate(invID = None):
    entity = BigWorld.entity(vEntityId)
    if invID == None:
        for key in angarmodellist:
            if angarmodellist[key]['spawn'] != 0:
                try:
                    if hasattr(entity.modele[key], "visible"):
                        if entity.modele[key].visible == False:
                            refreshModelInAngar(angarmodellist[key]['vehicle'])
                except:
                    pass
    else:
        for key in angarmodellist:
            if invID != key:
                vehicle = angarmodellist[key]['vehicle']
                if angarmodellist[key]['spawn'] != 0:
                    if vehicle is not None and not vehicle.isInBattle and vehicle.modelState:
                        try:
                            if hasattr(entity.modele[key], "visible"):
                                if entity.modele[key].visible == False:
                                    refreshModelInAngar(angarmodellist[key]['vehicle'])
                        except:
                            pass


def delete_all_models():
    entity = BigWorld.entity(vEntityId)
    vehicles = g_itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY).values()
    for key in angarmodellist:
        vehicle = angarmodellist[key]['vehicle']
        try:
            if hasattr(entity, 'modele'):
                if entity.modele[vehicle.invID]:
                    entity.modele[vehicle.invID].visible = False
                    entity.modele[vehicle.invID].visibleAttachments = False
                    entity.modele[vehicle.invID].delMotor(entity.modele[vehicle.invID].motors[0])
                    BigWorld.delModel(entity.modele[vehicle.invID])
                    entity.modele[vehicle.invID] = None
        except:
            pass
    for vehicle in vehicles:
        try:
            if hasattr(entity, 'modele'):
                if entity.modele[vehicle.invID]:
                    entity.modele[vehicle.invID].visible = False
                    entity.modele[vehicle.invID].visibleAttachments = False
                    entity.modele[vehicle.invID].delMotor(entity.modele[vehicle.invID].motors[0])
                    BigWorld.delModel(entity.modele[vehicle.invID])
                    del entity.modele[vehicle.invID]
        except:
            pass


def custom_updateVehicle():
    debug(str(1)+ ' start')
    entity = BigWorld.entity(vEntityId)
    delete_all_models()
    entity.modele = {}
    vehinlistup()
    possort()
    viehicleSpawn()
    


def vehinlistup():
    global angarmodellist
    global angarmodellist_Type
    global angarmodellist_LVL
    curr = 0
    angarmodellist = {}
    angarmodellist_Type = {}
    angarmodellist_LVL = {}
    vehicles = g_itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY).values()
    for vehicle in vehicles:
        if vehicle.invID in angarmodellist:
            pass
        else:
            angarmodellist_Type[vehicle.invID]= vehicle.type
            angarmodellist_LVL[vehicle.invID]= vehicle.level
            
            angarmodellist[vehicle.invID]={
            'pos':{'x': 10,'z': 0,'y': 0},
            'scale': 1,
            'angles': {'yaw': 0,'pitch': 0,'rotate': 0},
            'spawn': 0,
            'vehicle': vehicle}
            curr = curr +1

def possort():
    count=0
    lst =0
    if settings['setup']['class_specific'] == True:
        count_lt = settings['setup']['count_angar_pos_lt']
        count_mt = settings['setup']['count_angar_pos_mt']
        count_tt = settings['setup']['count_angar_pos_ht']
        count_at = settings['setup']['count_angar_pos_at']
        count_arty = settings['setup']['count_angar_pos_arty']
        count = count_lt + count_mt + count_tt + count_at + count_arty + settings['setup']['count_angar_pos']
        if settings['setup']['level_sorted'] == True:
            if count > 0:
                for i in xrange(1,count+1):
                    if angar_position_sorted[i]['type'] == 'lightTank':
                       for word in sorted(angarmodellist_LVL, key=angarmodellist_LVL.get, reverse=True):
                            if angarmodellist[word]['spawn'] == 0 and angarmodellist_Type[word]=='lightTank':
                                angarmodellist[word]['spawn'] = angar_position_sorted[i]['pos']
                                angarmodellist[word]['turret'] = angar_position_sorted[i]['turret']
                                break
                    elif angar_position_sorted[i]['type'] == 'mediumTank':
                        for word in sorted(angarmodellist_LVL, key=angarmodellist_LVL.get, reverse=True):
                            if angarmodellist[word]['spawn'] == 0 and angarmodellist_Type[word]=='mediumTank':
                                angarmodellist[word]['spawn'] = angar_position_sorted[i]['pos']
                                angarmodellist[word]['turret'] = angar_position_sorted[i]['turret']
                                break
                    elif angar_position_sorted[i]['type'] == 'heavyTank':
                        for word in sorted(angarmodellist_LVL, key=angarmodellist_LVL.get, reverse=True):
                            if angarmodellist[word]['spawn'] == 0 and angarmodellist_Type[word]=='heavyTank':
                                angarmodellist[word]['spawn'] = angar_position_sorted[i]['pos']
                                angarmodellist[word]['turret'] = angar_position_sorted[i]['turret']
                                break
                    elif angar_position_sorted[i]['type'] == 'AT-SPG':
                        for word in sorted(angarmodellist_LVL, key=angarmodellist_LVL.get, reverse=True):
                            if angarmodellist[word]['spawn'] == 0 and angarmodellist_Type[word]=='AT-SPG':
                                angarmodellist[word]['spawn'] = angar_position_sorted[i]['pos']
                                angarmodellist[word]['turret'] = angar_position_sorted[i]['turret']
                                break
                    elif angar_position_sorted[i]['type'] == 'SPG':
                        for word in sorted(angarmodellist_LVL, key=angarmodellist_LVL.get, reverse=True):
                            if angarmodellist[word]['spawn'] == 0 and angarmodellist_Type[word]=='SPG':
                                angarmodellist[word]['spawn'] = angar_position_sorted[i]['pos']
                                angarmodellist[word]['turret'] = angar_position_sorted[i]['turret']
                                break
                    else:
                        if angar_position_sorted[i]['type'] == 'Free':
                            for word in sorted(angarmodellist_LVL, key=angarmodellist_LVL.get, reverse=True):
                                if angarmodellist[word]['spawn'] == 0:
                                    angarmodellist[word]['spawn'] = angar_position_sorted[i]['pos']
                                    angarmodellist[word]['turret'] = angar_position_sorted[i]['turret']
                                    break
        else:
            if count > 0:
                for i in xrange(1,count+1):
                    for key in angarmodellist:
                        if angarmodellist[key]['spawn'] == 0 and angarmodellist_Type[key]=='Free':
                            angarmodellist[key]['spawn'] = angar_position_sorted[i]['pos']
                            angarmodellist[key]['turret'] = angar_position_sorted[i]['turret']
                            break
    else:
        if settings['setup']['level_sorted'] == True:
            if settings['setup']['count_angar_pos'] > 0:
                count = 1
                for word in sorted(angarmodellist_LVL, key=angarmodellist_LVL.get, reverse=True):
                    if count <= settings['setup']['count_angar_pos'] and angar_position_sorted[count] is not None:
                        angarmodellist[word]['spawn']= angar_position_sorted[count]['pos']
                        angarmodellist[word]['turret'] = angar_position_sorted[count]['turret']
                        count = count +1
        else:
            count = 0
            if settings['setup']['count_angar_pos'] > 0:
                count = 1
                vehicles = g_itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY).values()
                for vehicle in vehicles:
                    if vehicle.invID in angarmodellist:
                        if count != 0 and count <= settings['setup']['count_angar_pos']:
                            angarmodellist[vehicle.invID]['spawn']= angar_position_sorted[count]['pos']
                            angarmodellist[vehicle.invID]['turret'] = angar_position_sorted[count]['turret']
                            count = count +1
    
    lst =0
    for key in angarmodellist:
        lst += 1
        debug(str(lst)+' Add to SpawnList '+str(angarmodellist[key]['vehicle'].name)+' in position='+str(angarmodellist[key]['spawn']))


def viehicleSpawn():
    vehicles = g_itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY).values()
    for vehicle in vehicles:
        if vehicle.invID in angarmodellist:
            if posint(vehicle.invID):
                if angarmodellist[vehicle.invID]['spawn'] != 0:
                    __curBuildInd[vehicle.invID] = 0
                    __smCb1[vehicle.invID] = None
                    __smRemoveCb1[vehicle.invID] = None
                    model[vehicle.invID] = None
                    refreshModelInAngar(vehicle)



def posint(invID):
    if hangar_extended_mod == 'User':
        if angarmodellist[invID]['spawn'] !=0:
            angarpos = angarmodellist[invID]['spawn']
            angarmodellist[invID]['pos']['x'] = settings[angarpos]['x']
            angarmodellist[invID]['pos']['y'] = settings[angarpos]['y']
            angarmodellist[invID]['pos']['z'] = settings[angarpos]['z']
            angarmodellist[invID]['scale'] = settings[angarpos]['v_scale']
            angarmodellist[invID]['angles']['yaw'] = settings[angarpos]['anglesYaw']
            angarmodellist[invID]['angles']['pitch'] = settings[angarpos]['anglesPitch']
            angarmodellist[invID]['angles']['rotate'] = settings[angarpos]['anglesRotate']
            return True
    else:
        if angarmodellist[invID]['spawn'] !=0:
            angarpos = angarmodellist[invID]['spawn']
            angarmodellist[invID]['pos']['x'] = g_xmlSetting[angarpos].readFloat('x')
            angarmodellist[invID]['pos']['y'] = g_xmlSetting[angarpos].readFloat('y')
            angarmodellist[invID]['pos']['z'] = g_xmlSetting[angarpos].readFloat('z')
            angarmodellist[invID]['scale'] = g_xmlSetting[angarpos].readFloat('v_scale')
            angarmodellist[invID]['angles']['yaw'] = g_xmlSetting[angarpos].readFloat('anglesYaw')
            angarmodellist[invID]['angles']['pitch'] = g_xmlSetting[angarpos].readFloat('anglesPitch')
            angarmodellist[invID]['angles']['rotate'] = g_xmlSetting[angarpos].readFloat('anglesRotate')
            return True




def refreshModelInAngar(vehicle):
    debug(str(2)+ ' init '+str(angarmodellist[vehicle.invID]['vehicle'].name)+' in '+str(angarmodellist[vehicle.invID]['spawn']))
    if vehicle is not None and not vehicle.isInBattle and vehicle.modelState:
        if vehicle.intCD not in g_tankActiveCamouflage:
            availableKinds = []
            currKind = 0
            for id, startTime, days in vehicle.descriptor.camouflages:
                if id is not None:
                    availableKinds.append(currKind)
                currKind += 1
            if len(availableKinds) > 0:
                g_tankActiveCamouflage[vehicle.intCD] = random.choice(availableKinds)
        updateVehicle(vehicle)



def updateVehicle(vehicle):
    debug(str(3)+ ' create info '+str(angarmodellist[vehicle.invID]['vehicle'].name)+' in '+str(angarmodellist[vehicle.invID]['spawn']))
    igrRoomType = game_control.g_instance.igr.getRoomType()
    igrLayout = g_itemsCache.items.inventory.getIgrCustomizationsLayout()
    vehCompDescr = getCustomizedVehCompDescr(igrLayout, vehicle.invID, igrRoomType, vehicle.descriptor.makeCompactDescr(), None)
    if g_lobbyContext.getServerSettings().roaming.isInRoaming():
        vehCompDescr = items.vehicles.stripCustomizationFromVehicleCompactDescr(vehCompDescr, True, True, False)[0]
    vDesc = items.vehicles.VehicleDescr(compactDescr=vehCompDescr)
    vState = vehicle.modelState
    recreateVehicle(vDesc, vState, vehicle)

def recreateVehicle(vDesc, vState, vehicle):
    debug(str(4)+ ' init build '+str(angarmodellist[vehicle.invID]['vehicle'].name)+' in '+str(angarmodellist[vehicle.invID]['spawn']))
    angarmodellist[vehicle.invID]['vDesc'] = vDesc
    __startBuild(vDesc, vState, vehicle)
    hitTester = vDesc.hull['hitTester']
    hitTester.loadBspModel()
    __boundingRadius = (hitTester.bbox[2] + 1) * ClientHangarSpace._CFG['v_scale']
    angarmodellist[vehicle.invID]['hitTester'] = hitTester
    #hitTester.releaseBspModel()
    #dz = 0
    #if __cam.targetMaxDist > __cam.pivotMaxDist:
    #    dz = (__cam.pivotMaxDist - _CFG['cam_start_dist']) / _CFG['cam_sens']
    #updateCameraByMouseMove(0, 0, dz)
    return

def __startBuild(vDesc, vState, vehicle):
    debug(str(5)+ ' build '+str(angarmodellist[vehicle.invID]['vehicle'].name)+' in '+str(angarmodellist[vehicle.invID]['spawn']))
    global __componentIDs
    __componentIDs[vehicle.invID] = {}
    __curBuildInd[vehicle.invID] = __curBuildInd[vehicle.invID] + 1
    __vDesc[vehicle.invID] = vDesc
    __vState[vehicle.invID] = vState
    __resources[vehicle.invID] = {}
    __vehicleStickers[vehicle.invID] = None
    __componentIDs[vehicle.invID] = {'chassis': vDesc.chassis['models'][vState],
     'hull': vDesc.hull['models'][vState],
     'turret': vDesc.turret['models'][vState],
     'gun': vDesc.gun['models'][vState],
     'camouflageExclusionMask': vDesc.type.camouflageExclusionMask}
    customization = items.vehicles.g_cache.customization(vDesc.type.customizationNationID)
    if customization is not None and vDesc.camouflages is not None:
        activeCamo = g_tankActiveCamouflage['historical'].get(vDesc.type.compactDescr)
        if activeCamo is None:
            activeCamo = g_tankActiveCamouflage.get(vDesc.type.compactDescr, 0)
        camouflageID = vDesc.camouflages[activeCamo][0]
        camouflageDesc = customization['camouflages'].get(camouflageID)
        if camouflageDesc is not None:
            __componentIDs[vehicle.invID]['camouflageTexture'] = camouflageDesc['texture']
    if vState == 'undamaged':
        __emblemsAlpha[vehicle.invID] = ClientHangarSpace._CFG['emblems_alpha_undamaged']
        __isVehicleDestroyed[vehicle.invID] = False
    else:
        __emblemsAlpha[vehicle.invID] = ClientHangarSpace._CFG['emblems_alpha_damaged']
        __isVehicleDestroyed[vehicle.invID] = True
    resources = __componentIDs[vehicle.invID].values()
    splineDesc = vDesc.chassis['splineDesc']
    if splineDesc is not None:
        resources.extend(splineDesc.values())
    BigWorld.loadResourceListBG(tuple(resources), partial(__onResourcesLoaded, __curBuildInd[vehicle.invID], vehicle.invID))
    return
    

def __onResourcesLoaded(buildInd, invID, resourceRefs):
    debug(str(6)+ ' resource load '+str(angarmodellist[invID]['vehicle'].name)+' in '+str(angarmodellist[invID]['spawn']))
    if buildInd != __curBuildInd[invID]:
        return
    failedIDs = resourceRefs.failedIDs
    resources = __resources[invID]
    succesLoaded = True
    for resID, resource in resourceRefs.items():
        if resID not in failedIDs:
            resources[resID] = resource
        else:
            LOG_ERROR('Could not load %s' % resID)
            succesLoaded = False

    if succesLoaded:
        __setupModel(buildInd,invID)

def __setupModel(buildIdx,invID):
    debug(str(7)+ ' modeling '+str(angarmodellist[invID]['vehicle'].name)+' in '+str(angarmodellist[invID]['spawn']))
    model[invID] = __assembleModel(invID)
    scale = angarmodellist[invID]['scale']
    angles = (angarmodellist[invID]['angles']['yaw'],angarmodellist[invID]['angles']['pitch'],angarmodellist[invID]['angles']['rotate'])
    pos = (angarmodellist[invID]['pos']['x'],angarmodellist[invID]['pos']['z'],angarmodellist[invID]['pos']['y'])
    model[invID].addMotor(BigWorld.Servo(_createMatrix(scale, angles, pos)))
    BigWorld.addModel(model[invID])
    BigWorld.callback(0.0, partial(__doFinalSetup, buildIdx, model[invID], True, invID))

def __assembleModel(invID):
    debug(str(8)+ ' modeling stage 2 '+str(angarmodellist[invID]['vehicle'].name)+' in '+str(angarmodellist[invID]['spawn']))
    resources = __resources[invID]
    compIDs = __componentIDs[invID]
    chassis = resources[compIDs['chassis']]
    hull = resources[compIDs['hull']]
    turret = resources[compIDs['turret']]
    gun = resources[compIDs['gun']]
    __models[invID] = (chassis,
     hull,
     turret,
     gun)
    vehicle = angarmodellist[invID]['vehicle']
    vehicle.turretMatrix = Math.WGAdaptiveMatrixProvider()
    vehicle.gunMatrix = Math.WGAdaptiveMatrixProvider()
    chassis.node('V').attach(hull)
    turretJointName = __vDesc[invID].hull['turretHardPoints'][0]
    hull.node(turretJointName, vehicle.turretMatrix).attach(turret)
    turret.node('HP_gunJoint', vehicle.gunMatrix).attach(gun)
    __setupEmblems(__vDesc[invID], invID)
    __vehicleStickers[invID].show = False
    if not __isVehicleDestroyed[invID]:
        fashion = BigWorld.WGVehicleFashion(False, angarmodellist[invID]['scale'])
        VehicleAppearance.setupTracksFashion(fashion, __vDesc[invID], __isVehicleDestroyed[invID])
        chassis.wg_fashion = fashion
        fashion.initialUpdateTracks(1.0, 10.0)
        VehicleAppearance.setupSplineTracks(fashion, __vDesc[invID], chassis, __resources[invID])
    for model in __models[invID]:
        model.visible = False
        model.visibleAttachments = False

    return chassis

def _createMatrix(scale, angles, pos):
    mat = Math.Matrix()
    mat.setScale((scale, scale, scale))
    mat2 = Math.Matrix()
    mat2.setTranslate(pos)
    mat3 = Math.Matrix()
    mat3.setRotateYPR(angles)
    mat.preMultiply(mat3)
    mat.postMultiply(mat2)
    return mat

def __setupEmblems(vDesc,invID):
    debug(str(9)+ ' modeling setupEmblems '+str(angarmodellist[invID]['vehicle'].name)+' in '+str(angarmodellist[invID]['spawn']))
    if __vehicleStickers[invID] is not None:
        __vehicleStickers[invID].detach()
    insigniaRank = 0
    vehicleDossier = g_itemsCache.items.getVehicleDossier(vDesc.type.compactDescr)
    insigniaRank = vehicleDossier.getRandomStats().getAchievement(MARK_ON_GUN_RECORD).getValue()
    #print 0,invID, insigniaRank
    __vehicleStickers[invID] = VehicleStickers.VehicleStickers(vDesc, insigniaRank)
    #print 1,invID, __vehicleStickers[invID]
    __vehicleStickers[invID].alpha = __emblemsAlpha[invID]
    #print 2,invID, __vehicleStickers[invID].alpha
    chassis = __models[invID][0]
    hull = __models[invID][1]
    turret = __models[invID][2]
    gun = __models[invID][3]
    #print 3,invID,chassis,hull,turret,gun
    turretJointName = vDesc.hull['turretHardPoints'][0]
    #print 4,invID,turretJointName
    modelsWithParents = ((hull, chassis.node('V')), (turret, hull.node(turretJointName)), (gun, turret.node('HP_gunJoint')))
    #print 5,invID,modelsWithParents
    __vehicleStickers[invID].attach(modelsWithParents, __isVehicleDestroyed[invID], False)
    #print 6,invID,__vehicleStickers[invID]
    BigWorld.player().stats.get('clanDBID', __onClanDBIDRetrieved)
    #print 7,invID,mYclanID
    __vehicleStickers[invID].setClanID(mYclanID)
    #print 8,invID,__vehicleStickers[invID]
    return

def __onClanDBIDRetrieved(_, clanID):
    global mYclanID
    mYclanID = clanID
    #print 'clanid', clanID


def __doFinalSetup(buildIdx, model, delModel,invID):
    debug(str(10)+ ' modeling Final Stage '+str(angarmodellist[invID]['vehicle'].name)+' in '+str(angarmodellist[invID]['spawn']))
    if delModel:
        BigWorld.delModel(model)
    if model.attached:
        BigWorld.callback(0.0, partial(__doFinalSetup, buildIdx, model, False, invID))
        return
    elif buildIdx != __curBuildInd[invID]:
        return
    else:
        entity = BigWorld.entity(vEntityId)
        if entity:
            for m in __models[invID]:
                m.visible = True
                m.visibleAttachments = True
            if __vehicleStickers[invID]:
                __vehicleStickers[invID].show = True
            entity.modele[invID] = model
            entity.modele[invID].delMotor(entity.modele[invID].motors[0])
            scale = angarmodellist[invID]['scale']
            angles = (angarmodellist[invID]['angles']['yaw'],angarmodellist[invID]['angles']['pitch'],angarmodellist[invID]['angles']['rotate'])
            pos = (angarmodellist[invID]['pos']['x'],angarmodellist[invID]['pos']['z'],angarmodellist[invID]['pos']['y'])
            #debug('10 scale = ' + str(scale) +' angles = ' + str(angles) +' pos = ' + str(pos))
            entity.modele[invID].addMotor(BigWorld.Servo(_createMatrix(scale, angles, pos)))
            __isLoaded[invID] = True
            updateCamouflage(invID)
            ####
            turret_rotate(vehicle = angarmodellist[invID]['vehicle'], endPos = None)
            ####
            BigWorld.addModel(entity.modele[invID])
    
            if SelfinvID == invID:
                entity.modele[invID].visible = False
                entity.modele[invID].visibleAttachments = False
        if __vDesc[invID] is not None and 'observer' in __vDesc[invID].type.tags:
            model[invID].visible = False
            model[invID].visibleAttachments = False
        return

def __isOutOfLimits(angle, limits):
    if limits is None:
        return
    elif abs(limits[1] - angle) < 1e-05 or abs(limits[0] - angle) < 1e-05:
        return
    else:
        dpi = 2 * pi
        minDiff = fmod(limits[0] - angle + dpi, dpi)
        maxDiff = fmod(limits[1] - angle + dpi, dpi)
        if minDiff > maxDiff:
            return
        elif minDiff < dpi - maxDiff:
            return limits[0]
        return limits[1]
    return





def updateCamouflage(invID, camouflageID = None):
    debug(str(11)+ ' modeling updateCamouflage '+str(angarmodellist[invID]['vehicle'].name)+' in '+str(angarmodellist[invID]['spawn']))
    texture = ''
    colors = [0,0,0,0]
    gloss = 0
    weights = Math.Vector4(1, 0, 0, 0)
    camouflagePresent = True
    vDesc = __vDesc[invID]
    if vDesc is None:
        return
    else:
        if camouflageID is None and vDesc.camouflages is not None:
            activeCamo = g_tankActiveCamouflage['historical'].get(vDesc.type.compactDescr)
            if activeCamo is None:
                activeCamo = g_tankActiveCamouflage.get(vDesc.type.compactDescr, 0)
            camouflageID = vDesc.camouflages[activeCamo][0]
        if camouflageID is None:
            for camouflageData in vDesc.camouflages:
                if camouflageData[0] is not None:
                    camouflageID = camouflageData[0]
                    break

        customization = items.vehicles.g_cache.customization(vDesc.type.customizationNationID)
        defaultTiling = None
        if camouflageID is not None and customization is not None:
            camouflage = customization['camouflages'].get(camouflageID)
            if camouflage is not None:
                camouflagePresent = True
                texture = camouflage['texture']
                colors = camouflage['colors']
                weights = Math.Vector4(*[ (c >> 24) / 255.0 for c in colors ])
                defaultTiling = camouflage['tiling'].get(vDesc.type.compactDescr)
        if __isVehicleDestroyed[invID]:
            weights *= 0.1
        if vDesc.camouflages is not None:
            _, camStartTime, camNumDays = vDesc.camouflages[g_tankActiveCamouflage.get(vDesc.type.compactDescr, 0)]
            if camNumDays > 0:
                timeAmount = (time.time() - camStartTime) / (camNumDays * 86400)
                if timeAmount > 1.0:
                    weights *= 1.0
                elif timeAmount > 0:
                    weights *= (1.0 - timeAmount) * (1.0 - 1.0) + 1.0
        for model in __models[invID]:
            exclusionMap = vDesc.type.camouflageExclusionMask
            tiling = defaultTiling
            if tiling is None:
                tiling = vDesc.type.camouflageTiling
            if model == __models[invID][0]:
                compDesc = vDesc.chassis
            elif model == __models[invID][1]:
                compDesc = vDesc.hull
            elif model == __models[invID][2]:
                compDesc = vDesc.turret
            elif model == __models[invID][3]:
                compDesc = vDesc.gun
            else:
                compDesc = None
            if compDesc is not None:
                coeff = compDesc.get('camouflageTiling')
                if coeff is not None:
                    if tiling is not None:
                        tiling = (tiling[0] * coeff[0],
                         tiling[1] * coeff[1],
                         tiling[2] * coeff[2],
                         tiling[3] * coeff[3])
                    else:
                        tiling = coeff
                if compDesc.get('camouflageExclusionMask'):
                    exclusionMap = compDesc['camouflageExclusionMask']
            useCamouflage = camouflagePresent and exclusionMap and texture
            fashion = None
            if hasattr(model, 'wg_fashion'):
                fashion = model.wg_fashion
            elif hasattr(model, 'wg_gunRecoil'):
                fashion = model.wg_gunRecoil
            elif useCamouflage:
                fashion = model.wg_baseFashion = BigWorld.WGBaseFashion()
            elif hasattr(model, 'wg_baseFashion'):
                delattr(model, 'wg_baseFashion')
            if fashion is not None:
                if useCamouflage:
                    if BigWorld.wg_getProductVersion() == '0, 9, 4, 0':
                        fashion.setCamouflage(texture, exclusionMap, tiling, colors[0], colors[1], colors[2], colors[3], gloss, weights)
                    if BigWorld.wg_getProductVersion() == '0, 9, 5, 0':
                        fashion.setCamouflage(texture, exclusionMap, tiling, colors[0], colors[1], colors[2], colors[3], weights)
                else:
                    fashion.removeCamouflage()

        return

OLDremoveHangarShadowMap = ClientHangarSpace._VehicleAppearance._VehicleAppearance__removeHangarShadowMap
OLDsetupHangarShadowMap = ClientHangarSpace._VehicleAppearance._VehicleAppearance__setupHangarShadowMap

def NEWremoveHangarShadowMap(self):
    if angar_position_sorted:
        return
    else:
        OLDremoveHangarShadowMap(self)

def NEWsetupHangarShadowMap(self):
    if angar_position_sorted:
        return
    else:
        OLDsetupHangarShadowMap(self)

ClientHangarSpace._VehicleAppearance._VehicleAppearance__removeHangarShadowMap = NEWremoveHangarShadowMap
ClientHangarSpace._VehicleAppearance._VehicleAppearance__setupHangarShadowMap = NEWsetupHangarShadowMap





def turret_rotate(vehicle, endPos = None):
    ##########################
    invID = vehicle.invID
    if torsus_winter_mod == True:
        endPos = Math.Vector3(70,0,55)
    else:
        endPos = Math.Vector3(stdpos['v_start_pos'])
    pos = (angarmodellist[invID]['pos']['x'],angarmodellist[invID]['pos']['z'],angarmodellist[invID]['pos']['y'])
    scale = angarmodellist[invID]['scale']
    angles = (angarmodellist[invID]['angles']['yaw'],angarmodellist[invID]['angles']['pitch'],angarmodellist[invID]['angles']['rotate'])
    startPos = _createMatrix(scale, angles, pos)
    __turretYaw, __gunPitch = getShotAngles(vehicle.descriptor, startPos, (0, 0), endPos, False)
    turretYawLimits = __vDesc[invID].gun['turretYawLimits']
    closestLimit = __isOutOfLimits(__turretYaw, turretYawLimits)
    if closestLimit is not None:
        __turretYaw = closestLimit
    m = Math.Matrix()
    if angarmodellist[invID]['turret'] == True:
        m.setRotateYPR(Math.Vector3(__turretYaw, 0, 0))
    else:
        m.setRotateYPR(Math.Vector3(0, 0, 0))
    try:
        vehicle.turretMatrix.setStaticTransform(m)
    except:
        pass
    m1 = Math.Matrix()
    if angarmodellist[invID]['turret'] == True:
        m1.setRotateYPR(Math.Vector3(0, __gunPitch-0.2, 0))
    else:
        m1.setRotateYPR(Math.Vector3(0, 0, 0))
    try:
        vehicle.gunMatrix.setStaticTransform(m1)
    except:
        pass
    #####################


print ''


oldFinalSetup = ClientHangarSpace._VehicleAppearance._VehicleAppearance__doFinalSetup


def newFinalSetup(self, buildIdx, model, delModel):
    oldFinalSetup(self, buildIdx, model, delModel)
    entity = BigWorld.entity(self._VehicleAppearance__vEntityId)
    if entity:
        corx, corz, cory = ClientHangarSpace._CFG['v_start_pos']
        chassis_ext = 0
        hull_ext = 0
        turret_ext = 0
        gun_ext = 0
        
        if spawned['model'] < g_xmlSetting['setup'].readInt('count_models'):
            debug('Model spawn count ='+str(g_xmlSetting['setup'].readInt('count_models')))
            for m in xrange(1,g_xmlSetting['setup'].readInt('count_models')+1):
                spawned['model'] = m
                modelname = 'model' + str(m)
                entity.modelname = BigWorld.Model(g_xmlSetting['model' + str(m)].readString('path_model')) # Scale or Static
                if g_xmlSetting['model' + str(m)].readString('type_coord') == 'Static':
                    coordins = (g_xmlSetting['model' + str(m)].readFloat('x'),g_xmlSetting['model' + str(m)].readFloat('z'),g_xmlSetting['model' + str(m)].readFloat('y'))
                else:
                    coordins = (g_xmlSetting['model' + str(m)].readFloat('x')+corx,g_xmlSetting['model' + str(m)].readFloat('z')+corz,g_xmlSetting['model' + str(m)].readFloat('y')+cory)
                entity.modelname.addMotor(BigWorld.Servo(ClientHangarSpace._createMatrix(g_xmlSetting['model' + str(m)].readFloat('v_scale'), (g_xmlSetting['model' + str(m)].readFloat('anglesYaw'),g_xmlSetting['model' + str(m)].readFloat('anglesRotate'),g_xmlSetting['model' + str(m)].readFloat('anglesPitch')), coordins)))
                BigWorld.addModel(entity.modelname)
                debug('Resource '+str(modelname)+' spawned')
        
        
        if spawned['tank'] < g_xmlSetting['setup'].readInt('count_tanks'):
            debug('Tank spawn count ='+str(g_xmlSetting['setup'].readInt('count_tanks')))
            for m in xrange(1,g_xmlSetting['setup'].readInt('count_tanks')+1):
                spawned['tank'] = m
                modelname = 'tank' + str(m)
                chassis = BigWorld.Model(str(g_xmlSetting['tank' + str(m)].readString('chassis')))
                hull = BigWorld.Model(str(g_xmlSetting['tank' + str(m)].readString('hull')))
                turret = BigWorld.Model(str(g_xmlSetting['tank' + str(m)].readString('turret')))
                gun = BigWorld.Model(str(g_xmlSetting['tank' + str(m)].readString('gun')))
                if g_xmlSetting['tank' + str(m)].readString('chassis_ext') is not None and g_xmlSetting['tank' + str(m)].readString('chassis_ext') != '' and g_xmlSetting['tank' + str(m)].readString('chassis_ext') != 'None':
                    debug('Extended chassis to '+str(modelname)+' added')
                    chassis_ext  = BigWorld.Model(str(g_xmlSetting['tank' + str(m)].readString('chassis_ext')))
                if g_xmlSetting['tank' + str(m)].readString('hull_ext') is not None and g_xmlSetting['tank' + str(m)].readString('hull_ext') != '' and g_xmlSetting['tank' + str(m)].readString('hull_ext') != 'None':
                    debug('Extended hull to '+str(modelname)+' added')
                    hull_ext = BigWorld.Model(str(g_xmlSetting['tank' + str(m)].readString('hull_ext')))
                if g_xmlSetting['tank' + str(m)].readString('turret_ext') is not None and g_xmlSetting['tank' + str(m)].readString('turret_ext') != '' and g_xmlSetting['tank' + str(m)].readString('turret_ext') != 'None':
                    debug('Extended turret to '+str(modelname)+' added')
                    turret_ext = BigWorld.Model(str(g_xmlSetting['tank' + str(m)].readString('turret_ext')))
                if g_xmlSetting['tank' + str(m)].readString('gun_ext') is not None and g_xmlSetting['tank' + str(m)].readString('gun_ext') != '' and g_xmlSetting['tank' + str(m)].readString('gun_ext') != 'None':
                    debug('Extended gun to '+str(modelname)+' added')
                    gun_ext = BigWorld.Model(str(g_xmlSetting['tank' + str(m)].readString('gun_ext')))
               
                chassis.node('V').attach(hull)
                hull.node('HP_turretJoint').attach(turret)
                turret.node('HP_gunJoint').attach(gun)
                
                if chassis_ext != 0:
                    chassis.node('V').attach(chassis_ext)
                if hull_ext != 0:
                    hull.node('HP_turretJoint').attach(hull_ext)
                if turret_ext != 0:
                    turret.node('HP_gunJoint').attach(turret_ext)
                if gun_ext != 0:
                    gun.node('HP_gunFire').attach(gun_ext)
                entity.modelname = chassis
                if g_xmlSetting['tank' + str(m)].readString('type_coord') == 'Static':
                    coordins = (g_xmlSetting['tank' + str(m)].readFloat('x'),g_xmlSetting['tank' + str(m)].readFloat('z'),g_xmlSetting['tank' + str(m)].readFloat('y'))
                else:
                    coordins = (g_xmlSetting['tank' + str(m)].readFloat('x')+corx,g_xmlSetting['tank' + str(m)].readFloat('z')+corz,g_xmlSetting['tank' + str(m)].readFloat('y')+cory)
                entity.modelname.addMotor(BigWorld.Servo(ClientHangarSpace._createMatrix(g_xmlSetting['tank' + str(m)].readFloat('v_scale'), (g_xmlSetting['tank' + str(m)].readFloat('anglesYaw'),g_xmlSetting['tank' + str(m)].readFloat('anglesRotate'),g_xmlSetting['tank' + str(m)].readFloat('anglesPitch')), coordins)))
                BigWorld.addModel(entity.modelname)
                debug('Resource '+str(modelname)+' spawned')
            
        #entity.angar_model1 = BigWorld.Model('objects/misc/bbox/bboxcube05.model')
        #entity.angar_model2 = BigWorld.Model('objects/Niurko_MODs/ovcharik/ovcharik.model')
        #entity.angar_model3 = BigWorld.Model('content/BuildingsRare/blr009_chapel2/normal/lod0/blr009_chapel2_Italy.model')

        #entity.angar_model1.addMotor(BigWorld.Servo(ClientHangarSpace._createMatrix(ClientHangarSpace._CFG['v_scale'], ClientHangarSpace._CFG['v_start_angles'], (corx + 2.0, corz, cory + 2.0))))
        #entity.angar_model2.addMotor(BigWorld.Servo(ClientHangarSpace._createMatrix(ClientHangarSpace._CFG['v_scale'], ClientHangarSpace._CFG['v_start_angles'], (corx - 2.0, corz, cory - 2.0))))
        #entity.angar_model3.addMotor(BigWorld.Servo(ClientHangarSpace._createMatrix(ClientHangarSpace._CFG['v_scale'], ClientHangarSpace._CFG['v_start_angles'], (corx - 2.0, corz+2.0, cory - 2.0))))
        #BigWorld.addModel(entity.angar_model1)
        #BigWorld.addModel(entity.angar_model2)
        #BigWorld.addModel(entity.angar_model3)
        
def debug(text):
    if debug_opt == True:
        print('[DEBUG]      ['+str(description)+']: '+str(text))



OldonGeometryMapped = game.onGeometryMapped

def NewonGeometryMapped(spaceID, path):
    OldonGeometryMapped(spaceID, path)
    angar_position_sorted = None
    settings = None
    init_hangar_position(spaceID, path)
    
game.onGeometryMapped = NewonGeometryMapped


def check_hangar(informating = None):
    global hangar_trap
    import os
    hangar_trap = {'hangar_premium_v2_1': {'file': './res_mods/hangar_packages/hangar_premium_v2_1.pkg','space': 'spaces/hangar_premium_v2_1', 'name': 'hangar_premium_v2_1, created by AleksLee', 'found': False}, 'hangar_v2_1': {'file': './res_mods/hangar_packages/hangar_v2_1.pkg','space': 'spaces/hangar_v2_1', 'name': 'hangar_v2_1, created by AleksLee', 'found': False}}
    path = './res_mods/hangar_packages'
    sec = ResMgr.openSection('../paths.xml', True)
    subsec = sec['Paths']
    vals = subsec.values()
    pathXml = ResMgr.openSection('../paths.xml')
    pathXmlValues = pathXml['Paths'].values()
    HangarLoaderMod = None
    for folderPath in pathXmlValues:
        if os.path.isfile(os.path.join(folderPath.asString, 'scripts', 'client', 'mods','angar_packages_loader.pyc')):
            HangarLoaderMod = True
            from sys import path as sysPath
    if os.path.exists(path):
        for key in hangar_trap:
            if os.path.isfile(str(hangar_trap[key]['file'])):
                prn = None
                if HangarLoaderMod:
                    if hangar_trap[key]['file'] in sysPath:
                        prn = 1
                else:
                    for val in vals:
                        mp = (val.asString)
                        if mp == str(hangar_trap[key]['file']):
                            prn = 1
                if prn != 1:
                    hangar_trap[key]['found'] = False
                    if informating:
                        if HangarLoaderMod:
                            print '[ERROR]:     ['+str(description)+' '+str(hangar_trap[key]['file'])+' NOT LOADED by angar_packages_loader.pyc mod ]'
                        else:
                            print '[ERROR]:     ['+str(description)+' in ./Path.xml not found section <Path>'+str(path)+'/'+str(hangar_trap[key]['file'])+'</Path> ]'
                else:
                    hangar_trap[key]['found'] = True
                    if informating:
                        print '[INFO]:      ['+str(description)+' Activated to '+str(hangar_trap[key]['name'])+' ]'
    else:
        if informating:
            print '[ERROR]:     ['+str(description)+' NOT Found Correct hangar directory /res_mods/hangar_packages/]'



def init_hangar_position(spaceID, path):
    global cur_hangar_path
    cur_hangar_path = path
    global settings
    global angar_position_sorted
    angar_position_sorted = {}
    settings = {}
    import sys
    sys.stderr.write('[SPACE]      ['+str(description)+'] Check in : '+str(path)+'\n')
    if hangar_extended_mod == 'User':
        
        settings= {'version_mod': version_mod_updater, 'hangar': {}}
        if spc_mods == True:
            if torsus_winter_mod == True:
                sys.stderr.write('[INFO]:      ['+str(description)+' Loaded spawn position for Torsus Winter Mod Hangar ]\n')
                settings['setup'] ={'class_specific': False, 'level_sorted': True, 'count_angar_pos': 53, 'count_angar_pos_lt': 0,'count_angar_pos_mt': 0,'count_angar_pos_ht': 0,'count_angar_pos_at': 0, 'count_angar_pos_arty': 0}
                settings['angar_pos1'] = {'x': 35.00000, 'y': 55.00000, 'anglesYaw': 1.57079633, 'z': 0.5000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos2'] = {'x': 37.00000, 'y': 63.00000, 'anglesYaw': 1.91986218, 'z': 0.5000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos3'] = {'x': 55.00000, 'y': 70.00000, 'anglesYaw': 2.35619449, 'z': 0.5000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos4'] = {'x': 65.00000, 'y': 75.00000, 'anglesYaw': 2.967059728, 'z': 0.5000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos5'] = {'x': 60.00000, 'y': 35.00000, 'anglesYaw': 0.5235987756, 'z': 0.1000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos6'] = {'x': 75.00000, 'y': 40.00000, 'anglesYaw': 6.021385919, 'z': 0.3000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos7'] = {'x': 85.00000, 'y': 45.00000, 'anglesYaw': 5.585053606, 'z': 0.3000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos8'] = {'x': 100.00000, 'y': 50.00000, 'anglesYaw': 5.323254219, 'z': 0.5000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos9'] = {'x': 95.00000, 'y': 65.00000, 'anglesYaw': 4.625122518, 'z': 0.5000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos10'] = {'x': 80.00000, 'y': 75.00000, 'anglesYaw': 3.490658504, 'z': 0.5000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos11'] = {'x': 20.00000, 'y': 80.00000, 'anglesYaw': 2.00712864, 'z': 0.5000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos12'] = {'x': 15.00000, 'y': 70.00000, 'anglesYaw': 1.745329252, 'z': 0.5000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos13'] = {'x': 15.00000, 'y': 60.00000, 'anglesYaw': 1.570796327, 'z': 0.5000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos14'] = {'x': 15.00000, 'y': 50.00000, 'anglesYaw': 1.570796327, 'z': 0.5000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos15'] = {'x': 15.00000, 'y': 40.00000, 'anglesYaw': 1.134464014, 'z': 0.5000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos16'] = {'x': 20.00000, 'y': 30.00000, 'anglesYaw': 0.9599310886, 'z': 0.5000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos17'] = {'x': 15.00000, 'y': 20.00000, 'anglesYaw': 0.7853981634, 'z': 0.5000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos18'] = {'x': 20.00000, 'y': 10.00000, 'anglesYaw': 0.7853981634, 'z': 0.5000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos19'] = {'x': 30.00000, 'y': 5.00000, 'anglesYaw': 0.6981317008, 'z': 0.5000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos20'] = {'x': 40.00000, 'y': 10.00000, 'anglesYaw': 0.6108652382, 'z': 0.5000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos21'] = {'x': 30.00000, 'y': 90.00000, 'anglesYaw': 2.35619449, 'z': 0.5000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos22'] = {'x': 40.00000, 'y': 90.00000, 'anglesYaw': 2.35619449, 'z': 0.5000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos23'] = {'x': 30.00000, 'y': 100.00000, 'anglesYaw': 2.268928028, 'z': 0.5000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos24'] = {'x': 45.00000, 'y': 100.00000, 'anglesYaw': 2.443460953, 'z': 0.5000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos25'] = {'x': 55.00000, 'y': 105.00000, 'anglesYaw': 2.967059728, 'z': 0.5000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos26'] = {'x': 45.00000, 'y': 110.00000, 'anglesYaw': 2.792526803, 'z': 0.5000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos27'] = {'x': 65.00000, 'y': 110.00000, 'anglesYaw': 3.141592654, 'z': 0.5000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos28'] = {'x': 75.00000, 'y': 105.00000, 'anglesYaw': 3.141592654, 'z': 0.5000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos29'] = {'x': 85.00000, 'y': 115.00000, 'anglesYaw': 3.316125579, 'z': 0.5000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos30'] = {'x': 140.00000, 'y': 20.00000, 'anglesYaw': 4.886921906, 'z': 0.5000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos31'] = {'x': 50.00000, 'y': 120.00000, 'anglesYaw': 2.35619449, 'z': 0.5000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos32'] = {'x': 140.00000, 'y': 5.00000, 'anglesYaw': 4.537856055, 'z': 0.5000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos33'] = {'x': 130.00000, 'y': 25.00000, 'anglesYaw': 5.061454831, 'z': 0.5000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos34'] = {'x': 60.00000, 'y': 150.00000, 'anglesYaw': 3.316125579, 'z': 0.5000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos35'] = {'x': 15.00000, 'y': 140.00000, 'anglesYaw': 2.094395102, 'z': 0.5000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos36'] = {'x': 30.00000, 'y': 165.00000, 'anglesYaw': 2.35619449, 'z': 0.5000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos37'] = {'x': 30.00000, 'y': 130.00000, 'anglesYaw': 1.919862177, 'z': 0.5000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos38'] = {'x': 55.00000, 'y': 135.00000, 'anglesYaw': 1.570796327, 'z': 0.5000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos39'] = {'x': 40.00000, 'y': 150.00000, 'anglesYaw': 2.617993878, 'z': 0.5000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos40'] = {'x': 50.00000, 'y': 190.00000, 'anglesYaw': 2.967059728, 'z': 0.5000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}                
                settings['angar_pos41'] = {'x': 55.00000, 'y': 170.00000, 'anglesYaw': 3.141592654, 'z': 0.5000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos42'] = {'x': 110.00000, 'y': 75.00000, 'anglesYaw': 4.36332313, 'z': 0.5000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos43'] = {'x': 110.00000, 'y': 65.00000, 'anglesYaw': 4.537856055, 'z': 0.5000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos44'] = {'x': 120.00000, 'y': 80.00000, 'anglesYaw': 4.276056667, 'z': 0.5000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos45'] = {'x': 120.00000, 'y': 60.00000, 'anglesYaw': 4.71238898, 'z': 0.5000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos46'] = {'x': 130.00000, 'y': 80.00000, 'anglesYaw': 4.276056667, 'z': 0.5000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos47'] = {'x': 135.00000, 'y': 70.00000, 'anglesYaw': 4.537856055, 'z': 0.5000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos48'] = {'x': 130.00000, 'y': 60.00000, 'anglesYaw': 4.71238898, 'z': 0.5000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos49'] = {'x': 115.00000, 'y': 50.00000, 'anglesYaw': 4.886921906, 'z': 0.5000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos50'] = {'x': 120.00000, 'y': 40.00000, 'anglesYaw': 5.061454831, 'z': 0.5000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos51'] = {'x': 160.00000, 'y': 10.00000, 'anglesYaw': 4.71238898, 'z': 0.5000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos52'] = {'x': 150.00000, 'y': 15.00000, 'anglesYaw': 4.71238898, 'z': 0.5000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos53'] = {'x': 150.00000, 'y': 5.00000, 'anglesYaw': 4.71238898, 'z': 0.5000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}

            elif torsus_GUP_mod == True:
                sys.stderr.write('[INFO]:      ['+str(description)+' Loaded spawn position for Torsus Girls und Panzer Hangar ]\n')
                settings['setup'] ={'class_specific': True, 'level_sorted': True, 'count_angar_pos': 10, 'count_angar_pos_lt': 10,'count_angar_pos_mt': 10,'count_angar_pos_ht': 10,'count_angar_pos_at': 10, 'count_angar_pos_arty': 10}
                #R9
                #start x 133.915, z 8.89, y 19.33, scale 0.1
                settings['angar_pos_arty10'] = {'x': 132, 'y': 27.0, 'anglesYaw': 2.35619449, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos_arty9'] = {'x': 133, 'y': 27.1, 'anglesYaw': 2.35619449, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos_arty8'] = {'x': 134, 'y': 27.2, 'anglesYaw': 2.35619449, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos_arty7'] = {'x': 135, 'y': 27.3, 'anglesYaw': 2.35619449, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos_arty6'] = {'x': 136, 'y': 27.4, 'anglesYaw': 2.35619449, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos_arty5'] = {'x': 137, 'y': 27.5, 'anglesYaw': 2.35619449, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos_arty4'] = {'x': 138, 'y': 27.6, 'anglesYaw': 2.35619449, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos_arty3'] = {'x': 139, 'y': 27.7, 'anglesYaw': 2.35619449, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos_arty2'] = {'x': 140, 'y': 27.8, 'anglesYaw': 2.35619449, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos_arty1'] = {'x': 141, 'y': 27.9, 'anglesYaw': 2.35619449, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                
                settings['angar_pos_ht1'] = {'x': 142, 'y': 28, 'anglesYaw': 3.14159265, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos_ht2'] = {'x': 143, 'y': 28.1, 'anglesYaw': 3.14159265, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos_ht3'] = {'x': 144, 'y': 28.2, 'anglesYaw': 3.14159265, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos_ht4'] = {'x': 145, 'y': 28.3, 'anglesYaw': 3.14159265, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos_ht5'] = {'x': 146, 'y': 28.4, 'anglesYaw': 3.14159265, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos_ht6'] = {'x': 147, 'y': 28.5, 'anglesYaw': 3.14159265, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos_ht7'] = {'x': 148, 'y': 28.6, 'anglesYaw': 3.14159265, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos_ht8'] = {'x': 149, 'y': 28.7, 'anglesYaw': 3.14159265, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos_ht9'] = {'x': 150, 'y': 28.8, 'anglesYaw': 3.14159265, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos_ht10'] = {'x': 151, 'y': 28.9, 'anglesYaw': 3.14159265, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}

                settings['angar_pos_at10'] = {'x': 132, 'y': 15.0, 'anglesYaw': 0.000000, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos_at9'] = {'x': 133, 'y': 15.1, 'anglesYaw': 0.000000, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos_at8'] = {'x': 134, 'y': 15.2, 'anglesYaw': 0.000000, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos_at7'] = {'x': 135, 'y': 15.3, 'anglesYaw': 0.000000, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos_at6'] = {'x': 136, 'y': 15.4, 'anglesYaw': 0.000000, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos_at5'] = {'x': 137, 'y': 15.5, 'anglesYaw': 0.000000, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos_at4'] = {'x': 138, 'y': 15.6, 'anglesYaw': 0.000000, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos_at3'] = {'x': 139, 'y': 15.7, 'anglesYaw': 0.000000, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos_at2'] = {'x': 140, 'y': 15.8, 'anglesYaw': 0.000000, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos_at1'] = {'x': 141, 'y': 15.9, 'anglesYaw': 0.000000, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}

                settings['angar_pos_mt1'] = {'x': 142, 'y': 16.0, 'anglesYaw': 0.000000, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos_mt2'] = {'x': 143, 'y': 16.1, 'anglesYaw': 0.000000, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos_mt3'] = {'x': 144, 'y': 16.2, 'anglesYaw': 0.000000, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos_mt4'] = {'x': 145, 'y': 16.3, 'anglesYaw': 0.000000, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos_mt5'] = {'x': 146, 'y': 16.4, 'anglesYaw': 0.000000, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos_mt6'] = {'x': 147, 'y': 16.5, 'anglesYaw': 0.000000, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos_mt7'] = {'x': 148, 'y': 16.6, 'anglesYaw': 0.000000, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos_mt8'] = {'x': 149, 'y': 16.7, 'anglesYaw': 0.000000, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos_mt9'] = {'x': 150, 'y': 16.8, 'anglesYaw': 0.000000, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos_mt10'] = {'x': 151, 'y': 16.9, 'anglesYaw': 0.000000, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                
                
                
                
                settings['angar_pos_lt1'] = {'x': 137, 'y': 17, 'anglesYaw': 5.49778714, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos_lt2'] = {'x': 137, 'y': 19, 'anglesYaw': 5.49778714, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos_lt3'] = {'x': 137, 'y': 21, 'anglesYaw': 5.49778714, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos_lt4'] = {'x': 137, 'y': 23, 'anglesYaw': 5.49778714, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos_lt5'] = {'x': 137, 'y': 25, 'anglesYaw': 5.49778714, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos_lt6'] = {'x': 138, 'y': 18, 'anglesYaw': 5.49778714, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos_lt7'] = {'x': 138, 'y': 20, 'anglesYaw': 5.49778714, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos_lt8'] = {'x': 138, 'y': 22, 'anglesYaw': 5.49778714, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos_lt9'] = {'x': 138, 'y': 24, 'anglesYaw': 5.49778714, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos_lt10'] = {'x': 138, 'y': 26, 'anglesYaw': 5.49778714, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}


                settings['angar_pos1'] = {'x': 148, 'y': 18, 'anglesYaw': 5.49778714, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos2'] = {'x': 146, 'y': 19, 'anglesYaw': 5.49778714, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos3'] = {'x': 144, 'y': 20, 'anglesYaw': 5.49778714, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos4'] = {'x': 142, 'y': 21, 'anglesYaw': 5.49778714, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos5'] = {'x': 140, 'y': 22, 'anglesYaw': 5.49778714, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos6'] = {'x': 140, 'y': 23, 'anglesYaw': 3.92699082, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos7'] = {'x': 142, 'y': 24, 'anglesYaw': 3.92699082, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos8'] = {'x': 144, 'y': 25, 'anglesYaw': 3.92699082, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos9'] = {'x': 146, 'y': 26, 'anglesYaw': 3.92699082, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                settings['angar_pos10'] = {'x': 148, 'y': 27, 'anglesYaw': 3.92699082, 'z': 8.89, 'RotateTurretToSpawn': True, 'v_scale': 0.100000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}

            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            else:
                settings['setup'] ={'class_specific': False, 'level_sorted': True, 'count_angar_pos': 0, 'count_angar_pos_lt': 0,'count_angar_pos_mt': 0,'count_angar_pos_ht': 0,'count_angar_pos_at': 0,'count_angar_pos_arty': 0}
        else:
            check_hangar()
            if path == hangar_trap['hangar_premium_v2_1']['space'] and hangar_trap['hangar_premium_v2_1']['found'] == True:
                sys.stderr.write('[INFO]:      ['+str(description)+' Loaded spawn position for '+str(hangar_trap['hangar_premium_v2_1']['name'])+' ]'+'\n')
                settings['setup'] ={'class_specific': False, 'level_sorted': True, 'count_angar_pos': 31, 'count_angar_pos_lt': 0,'count_angar_pos_mt': 0,'count_angar_pos_ht': 0,'count_angar_pos_at': 0, 'count_angar_pos_arty': 0}
                #L7
                settings['angar_pos1'] = {'RotateTurretToSpawn': False, 'v_scale': 1.000000, 'anglesYaw': 4.71238898, 'anglesPitch': 0.000000, 'anglesRotate': 0.000000, 'x': 20.00000, 'y': 3.0000, 'z': 1.85000}
                #L8
                settings['angar_pos2'] = {'RotateTurretToSpawn': False, 'v_scale': 1.000000, 'anglesYaw': 4.71238898, 'anglesPitch': 0.000000, 'anglesRotate': 0.000000, 'x': 20.00000, 'y': -6.0000, 'z': 1.85000}
                #L6
                settings['angar_pos3'] = {'RotateTurretToSpawn': False, 'v_scale': 1.000000, 'anglesYaw': 4.71238898, 'anglesPitch': 0.000000, 'anglesRotate': 0.000000, 'x': 21.00000, 'y': 10.50000, 'z': 1.85000}
                #R6
                settings['angar_pos4'] = {'RotateTurretToSpawn': False, 'v_scale': 1.000000, 'anglesYaw': 1.57079633, 'anglesPitch': 0.000000, 'anglesRotate': 0.000000, 'x': -18.00000, 'y': 13.00000, 'z': 1.55000}
                #L5
                settings['angar_pos5'] = {'RotateTurretToSpawn': False, 'v_scale': 1.000000, 'anglesYaw': 4.71238898, 'anglesPitch': 0.000000, 'anglesRotate': 0.000000, 'x': 21.00000, 'y': 19.50000, 'z': 1.85000}
                #LR5
                settings['angar_pos6'] = {'RotateTurretToSpawn': False, 'v_scale': 1.000000, 'anglesYaw': 1.57079633, 'anglesPitch': 0.000000, 'anglesRotate': 0.000000, 'x': -18.00000, 'y': 20.50000, 'z': 1.55000}
                #L9
                settings['angar_pos7'] = {'RotateTurretToSpawn': False, 'v_scale': 1.000000, 'anglesYaw': 4.71238898, 'anglesPitch': 0.000000, 'anglesRotate': 0.000000, 'x': 18.5000, 'y': -16.0000, 'z': 1.85000}
                #R9
                settings['angar_pos8'] = {'RotateTurretToSpawn': False, 'v_scale': 1.000000, 'anglesYaw': 1.57079633, 'anglesPitch': 0.000000, 'anglesRotate': 0.000000, 'x': -18.00000, 'y': -14.00000, 'z': 1.55000}
                #P1
                settings['angar_pos9'] = {'RotateTurretToSpawn': True, 'v_scale': 1.000000, 'anglesYaw': 3.92699082, 'anglesPitch': 0.000000, 'anglesRotate': 0.000000, 'x': 5.00000, 'y': 15.00000, 'z': 1.55000}
                #P2
                settings['angar_pos10'] = {'RotateTurretToSpawn': True, 'v_scale': 1.000000, 'anglesYaw': 3.92699082, 'anglesPitch': 0.000000, 'anglesRotate': 0.000000, 'x': 4.00000, 'y': 25.00000, 'z': 1.55000}
                #L4
                settings['angar_pos11'] = {'RotateTurretToSpawn': False, 'v_scale': 1.000000, 'anglesYaw': 4.71238898, 'anglesPitch': 0.000000, 'anglesRotate': 0.000000, 'x': 21.00000, 'y': 27.50000, 'z': 1.85000}
                #R4
                settings['angar_pos12'] = {'RotateTurretToSpawn': False, 'v_scale': 1.000000, 'anglesYaw': 1.57079633, 'anglesPitch': 0.000000, 'anglesRotate': 0.000000, 'x': -18.00000, 'y': 30.00000, 'z': 1.55000}
                #R10
                settings['angar_pos13'] = {'RotateTurretToSpawn': False, 'v_scale': 1.000000, 'anglesYaw': 1.57079633, 'anglesPitch': 0.000000, 'anglesRotate': 0.000000, 'x': -18.00000, 'y': -22.00000, 'z': 1.55000}
                #F2
                settings['angar_pos14'] = {'RotateTurretToSpawn': True, 'v_scale': 1.000000, 'anglesYaw': -0.436332313, 'anglesPitch': 0.000000, 'anglesRotate': 0.000000, 'x': 5.00000, 'y': -17.00000, 'z': 1.55000}
                #F1
                settings['angar_pos15'] = {'RotateTurretToSpawn': True, 'v_scale': 1.000000, 'anglesYaw': 0.436332313, 'anglesPitch': 0.000000, 'anglesRotate': 0.000000, 'x': -5.00000, 'y': -17.00000, 'z': 1.55000}
                #F4
                settings['angar_pos16'] = {'RotateTurretToSpawn': True, 'v_scale': 1.000000, 'anglesYaw': -0.436332313, 'anglesPitch': 0.000000, 'anglesRotate': 0.000000, 'x': 6.00000, 'y': -30.00000, 'z': 1.55000}
                #F3
                settings['angar_pos17'] = {'RotateTurretToSpawn': True, 'v_scale': 1.000000, 'anglesYaw': 0.436332313, 'anglesPitch': 0.000000, 'anglesRotate': 0.000000, 'x': -6.00000, 'y': -30.00000, 'z': 1.55000}
                #L3
                settings['angar_pos18'] = {'RotateTurretToSpawn': False, 'v_scale': 1.000000, 'anglesYaw': 4.71238898, 'anglesPitch': 0.000000, 'anglesRotate': 0.000000, 'x': 21.00000, 'y': 37.00000, 'z': 1.55000}
                #R3
                settings['angar_pos19'] = {'RotateTurretToSpawn': False, 'v_scale': 1.000000, 'anglesYaw': 1.57079633, 'anglesPitch': 0.000000, 'anglesRotate': 0.000000, 'x': -21.00000, 'y': 37.00000, 'z': 1.55000}
                #L2
                settings['angar_pos20'] = {'RotateTurretToSpawn': False, 'v_scale': 1.000000, 'anglesYaw': 4.71238898, 'anglesPitch': 0.000000, 'anglesRotate': 0.000000, 'x': 21.00000, 'y': 45.00000, 'z': 1.55000}
                #R2
                settings['angar_pos21'] = {'RotateTurretToSpawn': False, 'v_scale': 1.000000, 'anglesYaw': 1.57079633, 'anglesPitch': 0.000000, 'anglesRotate': 0.000000, 'x': -21.00000, 'y': 47.00000, 'z': 1.55000}
                #L11
                settings['angar_pos22'] = {'RotateTurretToSpawn': False, 'v_scale': 1.000000, 'anglesYaw': 4.71238898, 'anglesPitch': 0.000000, 'anglesRotate': 0.000000, 'x': 18.5000, 'y': -31.0000, 'z': 1.85000}
                #R11
                settings['angar_pos23'] = {'RotateTurretToSpawn': False, 'v_scale': 1.000000, 'anglesYaw': 1.57079633, 'anglesPitch': 0.000000, 'anglesRotate': 0.000000, 'x': -18.00000, 'y': -31.00000, 'z': 1.55000}
                #L1
                settings['angar_pos24'] = {'RotateTurretToSpawn': False, 'v_scale': 1.000000, 'anglesYaw': 4.71238898, 'anglesPitch': 0.000000, 'anglesRotate': 0.000000, 'x': 23.00000, 'y': 53.00000, 'z': 1.55000}
                #R1
                settings['angar_pos25'] = {'RotateTurretToSpawn': False, 'v_scale': 1.000000, 'anglesYaw': 1.57079633, 'anglesPitch': 0.000000, 'anglesRotate': 0.000000, 'x': -21.00000, 'y': 53.00000, 'z': 1.55000}
                #L12
                settings['angar_pos26'] = {'RotateTurretToSpawn': False, 'v_scale': 1.000000, 'anglesYaw': 4.71238898, 'anglesPitch': 0.000000, 'anglesRotate': 0.000000, 'x': 18.5000, 'y': -40.0000, 'z': 1.85000}
                #R13
                settings['angar_pos27'] = {'RotateTurretToSpawn': False, 'v_scale': 1.000000, 'anglesYaw': 1.57079633, 'anglesPitch': 0.000000, 'anglesRotate': 0.000000, 'x': -18.00000, 'y': -45.00000, 'z': 1.55000}
                #P3
                settings['angar_pos28'] = {'RotateTurretToSpawn': True, 'v_scale': 1.000000, 'anglesYaw': 3.57792497, 'anglesPitch': 0.000000, 'anglesRotate': 0.000000, 'x': 1.00000, 'y': 35.00000, 'z': 1.55000}
                #F6
                settings['angar_pos29'] = {'RotateTurretToSpawn': True, 'v_scale': 1.000000, 'anglesYaw': 0.000000, 'anglesPitch': 0.000000, 'anglesRotate': 0.000000, 'x': 5.00000, 'y': -43.00000, 'z': 1.55000}
                #F5
                settings['angar_pos30'] = {'RotateTurretToSpawn': True, 'v_scale': 1.000000, 'anglesYaw': 0.000000, 'anglesPitch': 0.000000, 'anglesRotate': 0.000000, 'x': -5.00000, 'y': -43.00000, 'z': 1.55000}
                #P4
                settings['angar_pos31'] = {'RotateTurretToSpawn': True, 'v_scale': 1.000000, 'anglesYaw': 3.14159265, 'anglesPitch': 0.000000, 'anglesRotate': 0.000000, 'x': -5.00000, 'y': 40.00000, 'z': 1.55000}
            elif path == hangar_trap['hangar_v2_1']['space'] and hangar_trap['hangar_v2_1']['found'] == True:
                sys.stderr.write('[INFO]:      ['+str(description)+' Loaded spawn position for '+str(hangar_trap['hangar_v2_1']['name'])+' ]'+'\n')
                settings['setup'] ={'class_specific': False, 'level_sorted': True, 'count_angar_pos': 33, 'count_angar_pos_lt': 0,'count_angar_pos_mt': 0,'count_angar_pos_ht': 0,'count_angar_pos_at': 0, 'count_angar_pos_arty': 0}
                #R9
                settings['angar_pos1'] = {'x': 20.00000, 'y': -4.00000, 'anglesYaw': 4.71238898, 'z': 0.0000, 'RotateTurretToSpawn': False, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                #R7
                settings['angar_pos2'] = {'x': 18.50000, 'y': 10.00000, 'anglesYaw': 4.71238898, 'z': 0.0000, 'RotateTurretToSpawn': False, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                #L6
                settings['angar_pos3'] = {'x': -18.00000, 'y': 17.50000, 'anglesYaw': 1.57079633, 'z': 0.5000, 'RotateTurretToSpawn': False, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                #R6
                settings['angar_pos4'] = {'x': 18.50000, 'y': 17.00000, 'anglesYaw': 4.71238898, 'z': 0.0000, 'RotateTurretToSpawn': False, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                #L5
                settings['angar_pos5'] = {'x': -18.00000, 'y': 23.00000, 'anglesYaw': 1.57079633, 'z': 0.5000, 'RotateTurretToSpawn': False, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                #R5
                settings['angar_pos6'] = {'x': 18.50000, 'y': 23.00000, 'anglesYaw': 4.71238898, 'z': 0.0000, 'RotateTurretToSpawn': False, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                #P1
                settings['angar_pos7'] = {'x': 7.00000, 'y': -12.00000, 'anglesYaw': -0.785398163, 'z': 0.000000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                #L11
                settings['angar_pos8'] = {'x': -18.00000, 'y': -15.00000, 'anglesYaw': 1.57079633, 'z': 0.5000, 'RotateTurretToSpawn': False, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                #R11
                settings['angar_pos9'] = {'x': 18.50000, 'y': -17.00000, 'anglesYaw': 4.71238898, 'z': 0.0000, 'RotateTurretToSpawn': False, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                #L12
                settings['angar_pos10'] = {'x': -18.00000, 'y': -22.00000, 'anglesYaw': 1.57079633, 'z': 0.5000, 'RotateTurretToSpawn': False, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                #F1
                settings['angar_pos11'] = {'x': 6.00000, 'y': 16.00000, 'anglesYaw': -0.785398163, 'z': 0.000000, 'RotateTurretToSpawn': False, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                #L4
                settings['angar_pos12'] = {'x': -18.00000, 'y': 30.00000, 'anglesYaw': 1.57079633, 'z': 0.5000, 'RotateTurretToSpawn': False, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                #R4
                settings['angar_pos13'] = {'x': 18.00000, 'y': 30.00000, 'anglesYaw': 4.71238898, 'z': 0.0000, 'RotateTurretToSpawn': False, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                #L3
                settings['angar_pos14'] = {'x': -18.00000, 'y': 36.00000, 'anglesYaw': 1.57079633, 'z': 0.5000, 'RotateTurretToSpawn': False, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                #R3
                settings['angar_pos15'] = {'x': 18.00000, 'y': 36.00000, 'anglesYaw': 4.71238898, 'z': 0.0000, 'RotateTurretToSpawn': False, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                #L13
                settings['angar_pos16'] = {'x': -18.00000, 'y': -28.50000, 'anglesYaw': 1.57079633, 'z': 0.5000, 'RotateTurretToSpawn': False, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                #R13
                settings['angar_pos17'] = {'x': 17.50000, 'y': -28.50000, 'anglesYaw': 4.71238898, 'z': 0.0000, 'RotateTurretToSpawn': False, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                #F2
                settings['angar_pos18'] = {'x': 7.00000, 'y': 23.00000, 'anglesYaw': -0.436332313, 'z': 0.000000, 'RotateTurretToSpawn': False, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                #L2
                settings['angar_pos19'] = {'x': -18.00000, 'y': 43.00000, 'anglesYaw': 1.57079633, 'z': 0.5000, 'RotateTurretToSpawn': False, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                #R2
                settings['angar_pos20'] = {'x': 18.00000, 'y': 43.00000, 'anglesYaw': 4.71238898, 'z': 0.0000, 'RotateTurretToSpawn': False, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                #L14
                settings['angar_pos21'] = {'x': -18.00000, 'y': -35.00000, 'anglesYaw': 1.57079633, 'z': 0.5000, 'RotateTurretToSpawn': False, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                #R14
                settings['angar_pos22'] = {'x': 18.00000, 'y': -35.00000, 'anglesYaw': 4.71238898, 'z': 0.0000, 'RotateTurretToSpawn': False, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                #F4
                settings['angar_pos23'] = {'x': -5.00000, 'y': 31.00000, 'anglesYaw': 0.610865238, 'z': 0.000000, 'RotateTurretToSpawn': False, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                #F3
                settings['angar_pos24'] = {'x': 7.00000, 'y': 33.00000, 'anglesYaw': -0.610865238, 'z': 0.000000, 'RotateTurretToSpawn': False, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                #L1
                settings['angar_pos25'] = {'x': -18.00000, 'y': 49.00000, 'anglesYaw': 1.57079633, 'z': 0.5000, 'RotateTurretToSpawn': False, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                #R1
                settings['angar_pos26'] = {'x': 18.00000, 'y': 49.00000, 'anglesYaw': 4.71238898, 'z': 0.0000, 'RotateTurretToSpawn': False, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                #P2
                settings['angar_pos27'] = {'x': 7.00000, 'y': -29.00000, 'anglesYaw': -0.610865238, 'z': 0.000000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                #P3
                settings['angar_pos28'] = {'x': -5.00000, 'y': -36.00000, 'anglesYaw': 0.436332313, 'z': 0.000000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                #P4
                settings['angar_pos29'] = {'x': 6.00000, 'y': -40.00000, 'anglesYaw': -0.436332313, 'z': 0.000000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                #R15
                settings['angar_pos30'] = {'x': 18.00000, 'y': -41.50000, 'anglesYaw': 4.71238898, 'z': 0.0000, 'RotateTurretToSpawn': False, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                #L15
                settings['angar_pos31'] = {'x': -18.00000, 'y': -41.50000, 'anglesYaw': 1.57079633, 'z': 0.5000, 'RotateTurretToSpawn': False, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                #F6
                settings['angar_pos32'] = {'x': -4.00000, 'y': 43.00000, 'anglesYaw': 0.785398163, 'z': 0.000000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                #F5
                settings['angar_pos33'] = {'x': 5.00000, 'y': 43.00000, 'anglesYaw': -0.785398163, 'z': 0.000000, 'RotateTurretToSpawn': True, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                #R8
                #settings['angar_pos9'] = {'x': 23.00000, 'y': 3.00000, 'anglesYaw': 4.71238898, 'z': 0.0000, 'RotateTurretToSpawn': False, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                #R10
                #settings['angar_pos10'] = {'x': 118.50000, 'y': -10.00000, 'anglesYaw': 4.71238898, 'z': 0.0000, 'RotateTurretToSpawn': False, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                #R12
                #settings['angar_pos13'] = {'x': 18.50000, 'y': -22.00000, 'anglesYaw': 4.71238898, 'z': 0.0000, 'RotateTurretToSpawn': False, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                #L7
                #settings['angar_pos20'] = {'x': -18.00000, 'y': 10.00000, 'anglesYaw': 1.57079633, 'z': 0.5000, 'RotateTurretToSpawn': False, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                #L8
                #settings['angar_pos21'] = {'x': -18.00000, 'y': 3.00000, 'anglesYaw': 1.57079633, 'z': 0.5000, 'RotateTurretToSpawn': False, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                #L9
                #settings['angar_pos22'] = {'x': -18.00000, 'y': -4.00000, 'anglesYaw': 1.57079633, 'z': 0.5000, 'RotateTurretToSpawn': False, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
                #L10
                #settings['angar_pos23'] = {'x': -18.00000, 'y': -10.00000, 'anglesYaw': 1.57079633, 'z': 0.5000, 'RotateTurretToSpawn': False, 'v_scale': 1.000000,  'anglesPitch': 0.000000, 'anglesRotate': 0.000000}
            else:
                settings['setup'] ={'class_specific': False, 'level_sorted': True, 'count_angar_pos': 0, 'count_angar_pos_lt': 0,'count_angar_pos_mt': 0,'count_angar_pos_ht': 0,'count_angar_pos_at': 0,'count_angar_pos_arty': 0}




        
        
        count = 0
        count1=0
        count2=0
        count3=0
        count4=0
        count5=0
        count_lt = settings['setup']['count_angar_pos_lt']
        count_mt = settings['setup']['count_angar_pos_mt']
        count_tt = settings['setup']['count_angar_pos_ht']
        count_at = settings['setup']['count_angar_pos_at']
        count_arty = settings['setup']['count_angar_pos_arty']
        angar_position_sorted= {}
        if  settings['setup']['class_specific'] == True:
            count1 = count_lt
            count2 = count1 + count_mt
            count3 = count2 + count_tt
            count4 = count3 + count_at
            count5 = count4 + count_arty
            count = count5 + settings['setup']['count_angar_pos']
        else:
            count = settings['setup']['count_angar_pos']
        debug('Count of Angar Position is '+str(count))
        lt=1
        mt=1
        ht=1
        at=1
        ar=1
        co=1
        for i in xrange(1,count+1):
            angar_position_sorted[i]={}
            if settings['setup']['class_specific'] == True:
                if i <= count1:
                    angar_position_sorted[i]={'type': 'lightTank', 'pos': 'angar_pos_lt'+str(lt), 'turret': settings['angar_pos_lt' + str(lt)]['RotateTurretToSpawn']}
                    lt=lt+1
                elif i <= count2:
                    angar_position_sorted[i]={'type': 'mediumTank', 'pos': 'angar_pos_mt'+str(mt), 'turret': settings['angar_pos_mt' + str(mt)]['RotateTurretToSpawn']}
                    mt=mt+1
                elif i <= count3:
                    angar_position_sorted[i]={'type': 'heavyTank', 'pos': 'angar_pos_ht'+str(ht), 'turret': settings['angar_pos_ht' + str(ht)]['RotateTurretToSpawn']}
                    ht=ht+1
                elif i <= count4:
                    angar_position_sorted[i]={'type': 'AT-SPG', 'pos': 'angar_pos_at'+str(at), 'turret': settings['angar_pos_at' + str(at)]['RotateTurretToSpawn']}
                    at=at+1
                elif i <= count5:
                    angar_position_sorted[i]={'type': 'SPG', 'pos': 'angar_pos_arty'+str(ar), 'turret': settings['angar_pos_arty' + str(ar)]['RotateTurretToSpawn']}
                    ar=ar+1
                elif i <= count:
                    angar_position_sorted[i]={'type': 'Free', 'pos': 'angar_pos'+str(co), 'turret': settings['angar_pos' + str(co)]['RotateTurretToSpawn']}
                    co=co+1
            else:
                angar_position_sorted[i]={'type': 'Free', 'pos': 'angar_pos'+str(i), 'turret': settings['angar_pos' + str(i)]['RotateTurretToSpawn']}
    elif hangar_extended_mod =='Mod':
        g_xmlSetting = ResMgr.openSection('scripts/client/gui/mods/hangar_extended.xml', True)
        count = 0
        count1=0
        count2=0
        count3=0
        count4=0
        count5=0
        count_lt = g_xmlSetting['setup'].readInt('count_angar_pos_lt')
        count_mt = g_xmlSetting['setup'].readInt('count_angar_pos_mt')
        count_tt = g_xmlSetting['setup'].readInt('count_angar_pos_ht')
        count_at = g_xmlSetting['setup'].readInt('count_angar_pos_at')
        count_arty = g_xmlSetting['setup'].readInt('count_angar_pos_arty')
        angar_position_sorted= {}
        if g_xmlSetting['setup'].readBool('class_specific') == True:
            count1 = count_lt
            count2 = count1 + count_mt
            count3 = count2 + count_tt
            count4 = count3 + count_at
            count5 = count4 + count_arty
            count = count5 + g_xmlSetting['setup'].readInt('count_angar_pos')
        else:
            count = g_xmlSetting['setup'].readInt('count_angar_pos')
        debug('Count of Angar Position is '+str(count))
        lt=1
        mt=1
        ht=1
        at=1
        ar=1
        co=1
        for i in xrange(1,count+1):
            angar_position_sorted[i]={}
            if g_xmlSetting['setup'].readBool('class_specific') == True:
                if i <= count1:
                    angar_position_sorted[i]={'type': 'lightTank', 'pos': 'angar_pos_lt'+str(lt), 'turret': g_xmlSetting['angar_pos_lt' + str(lt)].readBool('RotateTurretToSpawn')}
                    lt=lt+1
                elif i <= count2:
                    angar_position_sorted[i]={'type': 'mediumTank', 'pos': 'angar_pos_mt'+str(mt), 'turret': g_xmlSetting['angar_pos_mt' + str(mt)].readBool('RotateTurretToSpawn')}
                    mt=mt+1
                elif i <= count3:
                    angar_position_sorted[i]={'type': 'heavyTank', 'pos': 'angar_pos_ht'+str(ht), 'turret': g_xmlSetting['angar_pos_ht' + str(ht)].readBool('RotateTurretToSpawn')}
                    ht=ht+1
                elif i <= count4:
                    angar_position_sorted[i]={'type': 'AT-SPG', 'pos': 'angar_pos_at'+str(at), 'turret': g_xmlSetting['angar_pos_at' + str(at)].readBool('RotateTurretToSpawn')}
                    at=at+1
                elif i <= count5:
                    angar_position_sorted[i]={'type': 'SPG', 'pos': 'angar_pos_arty'+str(ar), 'turret': g_xmlSetting['angar_pos_ar' + str(ar)].readBool('RotateTurretToSpawn')}
                    ar=ar+1
                elif i <= count:
                    angar_position_sorted[i]={'type': 'Free', 'pos': 'angar_pos'+str(co), 'turret': g_xmlSetting['angar_pos' + str(co)].readBool('RotateTurretToSpawn')}
                    co=co+1
            else:
                angar_position_sorted[i]={'type': 'Free', 'pos': 'angar_pos'+str(i), 'turret': g_xmlSetting['angar_pos' + str(i)].readBool('RotateTurretToSpawn')}

        settings= {'version_mod': g_xmlSetting['setup'].readString('version_mod')}
        settings['setup'] ={'class_specific': g_xmlSetting['setup'].readBool('class_specific'), 'level_sorted': g_xmlSetting['setup'].readBool('level_sorted'), 'count_angar_pos': g_xmlSetting['setup'].readInt('count_angar_pos'), 'count_angar_pos_lt': g_xmlSetting['setup'].readInt('count_angar_pos_lt'),'count_angar_pos_mt': g_xmlSetting['setup'].readInt('count_angar_pos_mt'),'count_angar_pos_ht': g_xmlSetting['setup'].readInt('count_angar_pos_ht'),'count_angar_pos_at': g_xmlSetting['setup'].readInt('count_angar_pos_at'), 'count_angar_pos_arty': g_xmlSetting['setup'].readInt('count_angar_pos_arty')}


def init():
    print '[LOAD_MOD]:  ['+str(description)+' '+str(author)+']'
    global debug_opt
    if hangar_extended_mod =='Mod':
        print '[INFO]:      ['+str(description)+' '+str(version)+' initialized ...]'
        global g_xmlSetting
        g_xmlSetting = ResMgr.openSection('scripts/client/gui/mods/hangar_extended.xml', True)
        if not g_xmlSetting:
            g_xmlSetting.write('setup', '')
            g_xmlSetting['setup'].writeInt('count_models' , 0)
            g_xmlSetting['setup'].writeInt('count_tanks' , 0)
            g_xmlSetting['setup'].writeBool('class_specific' , True)
            g_xmlSetting['setup'].writeBool('level_sorted' , True)
            g_xmlSetting['setup'].writeInt('count_angar_pos' , 24)
            g_xmlSetting['setup'].writeInt('count_angar_pos_lt' , 12)
            g_xmlSetting['setup'].writeInt('count_angar_pos_mt' , 12)
            g_xmlSetting['setup'].writeInt('count_angar_pos_ht' , 12)
            g_xmlSetting['setup'].writeInt('count_angar_pos_at' , 12)
            g_xmlSetting['setup'].writeInt('count_angar_pos_arty' , 12)
            g_xmlSetting['setup'].writeBool('debug' , False)
            g_xmlSetting['setup'].writeInt('versionXML' , versionXML)
            g_xmlSetting['setup'].writeInt('version_mod', version_mod_updater)
            g_xmlSetting.save()
        if g_xmlSetting['setup'].readBool('debug') == True:
            debug_opt = g_xmlSetting['setup'].readBool('debug')
            debug('DEBUG MODE ON')
            debug('v_start_pos = ' + str(ClientHangarSpace._CFG['v_start_pos']))
            debug('v_start_angles = ' + str(ClientHangarSpace._CFG['v_start_angles']))
            debug('v_scale = ' + str(ClientHangarSpace._CFG['v_scale']))

        if g_xmlSetting['setup'].readInt('versionXML') != versionXML:
            print '[ERROR]:     ['+str(description)+' '+str(version)+' in XML version mismatch. please delete old XML...]' 
        x,z,y = ClientHangarSpace._CFG['v_start_pos']
        scl = ClientHangarSpace._CFG['v_scale']
        anglesYaw, anglesRotate, anglesPitch = ClientHangarSpace._CFG['v_start_angles']
        for m in xrange(1,g_xmlSetting['setup'].readInt('count_models')+1):
            if not g_xmlSetting['model' + str(m)]:
                debug('Added in XML model'+str(m))
                g_xmlSetting.write('model' + str(m), '')
                g_xmlSetting['model' + str(m)].writeString('path_model', 'objects/misc/bbox/bboxcube05.model') # Scale or Static
                g_xmlSetting['model' + str(m)].writeFloat('v_scale', scl)
                g_xmlSetting['model' + str(m)].writeFloat('anglesYaw', anglesYaw)
                g_xmlSetting['model' + str(m)].writeFloat('anglesPitch', anglesPitch)
                g_xmlSetting['model' + str(m)].writeFloat('anglesRotate', anglesRotate)
                g_xmlSetting['model' + str(m)].writeString('type_coord', 'Static') # Scale or Static
                g_xmlSetting['model' + str(m)].writeFloat('x', x)
                g_xmlSetting['model' + str(m)].writeFloat('y', y+10+(10*m))
                g_xmlSetting['model' + str(m)].writeFloat('z', z)
                g_xmlSetting.save()
        for m in xrange(1,g_xmlSetting['setup'].readInt('count_tanks')+1):
            if not g_xmlSetting['tank' + str(m)]:
                debug('Added in XML tank'+str(m))
                g_xmlSetting.write('tank' + str(m), '')
                g_xmlSetting['tank' + str(m)].writeString('chassis', 'vehicles/german/G48_E-25/normal/lod0/Chassis.model')
                g_xmlSetting['tank' + str(m)].writeString('hull', 'vehicles/german/G48_E-25/normal/lod0/Hull.model')
                g_xmlSetting['tank' + str(m)].writeString('turret', 'vehicles/german/G48_E-25/normal/lod0/Turret_01.model')
                g_xmlSetting['tank' + str(m)].writeString('gun', 'vehicles/german/G48_E-25/normal/lod0/Gun_01.model')
                g_xmlSetting['tank' + str(m)].writeString('chassis_ext', 'None')
                g_xmlSetting['tank' + str(m)].writeString('hull_ext', 'content/Interface/marker_green.model')
                g_xmlSetting['tank' + str(m)].writeString('turret_ext', 'None')
                g_xmlSetting['tank' + str(m)].writeString('gun_ext', 'None')
                g_xmlSetting['tank' + str(m)].writeFloat('v_scale', scl)
                g_xmlSetting['tank' + str(m)].writeFloat('anglesYaw', anglesYaw)
                g_xmlSetting['tank' + str(m)].writeFloat('anglesPitch', anglesPitch)
                g_xmlSetting['tank' + str(m)].writeFloat('anglesRotate', anglesRotate)
                g_xmlSetting['tank' + str(m)].writeString('type_coord', 'Scale') # Scale or Static
                g_xmlSetting['tank' + str(m)].writeFloat('x', x)
                if m == 1:
                    g_xmlSetting['tank' + str(m)].writeFloat('y', y+(10*m))
                elif m == 2:
                    g_xmlSetting['tank' + str(m)].writeFloat('y', y-(10*m))
                else:
                    g_xmlSetting['tank' + str(m)].writeFloat('y', y+(10*m))
                g_xmlSetting['tank' + str(m)].writeFloat('z', z)
                g_xmlSetting.save()
        for m in xrange(1,g_xmlSetting['setup'].readInt('count_angar_pos')+1):
            if not g_xmlSetting['angar_pos' + str(m)]:
                debug('Added in XML angar positions'+str(m))
                g_xmlSetting.write('angar_pos' + str(m), '')
                g_xmlSetting['angar_pos' + str(m)].writeBool('RotateTurretToSpawn' , True)
                g_xmlSetting['angar_pos' + str(m)].writeFloat('v_scale', 1)
                g_xmlSetting['angar_pos' + str(m)].writeFloat('anglesYaw', 0)
                g_xmlSetting['angar_pos' + str(m)].writeFloat('anglesPitch', 0)
                g_xmlSetting['angar_pos' + str(m)].writeFloat('anglesRotate', 0)
                g_xmlSetting['angar_pos' + str(m)].writeFloat('x', x+10)
                if m < 7:
                    g_xmlSetting['angar_pos' + str(m)].writeFloat('x', x+10)
                    g_xmlSetting['angar_pos' + str(m)].writeFloat('y', y-(10*m))
                if m < 13:
                    g_xmlSetting['angar_pos' + str(m)].writeFloat('x', x+10)
                    g_xmlSetting['angar_pos' + str(m)].writeFloat('y', y+(10*(m-6)))
                if m < 19:
                    g_xmlSetting['angar_pos' + str(m)].writeFloat('x', x-10)
                    g_xmlSetting['angar_pos' + str(m)].writeFloat('y', y-(10*(m-12)))
                if m < 25:
                    g_xmlSetting['angar_pos' + str(m)].writeFloat('x', x-10)
                    g_xmlSetting['angar_pos' + str(m)].writeFloat('y', y+(10*(m-18)))
                else:
                    g_xmlSetting['angar_pos' + str(m)].writeFloat('x', x-10)
                    g_xmlSetting['angar_pos' + str(m)].writeFloat('y', y+(10*(m-24)))
                g_xmlSetting['angar_pos' + str(m)].writeFloat('z', z+5)
                g_xmlSetting.save()
        if g_xmlSetting['setup'].readBool('class_specific') == True:
            for m in xrange(1,g_xmlSetting['setup'].readInt('count_angar_pos_lt')+1):
                if not g_xmlSetting['angar_pos_lt' + str(m)]:
                    debug('Added in XML LightTank angar positions'+str(m))
                    g_xmlSetting.write('angar_pos_lt' + str(m), '')
                    g_xmlSetting['angar_pos_lt' + str(m)].writeBool('RotateTurretToSpawn' , True)
                    g_xmlSetting['angar_pos_lt' + str(m)].writeFloat('v_scale', 1)
                    g_xmlSetting['angar_pos_lt' + str(m)].writeFloat('anglesYaw', 0)
                    g_xmlSetting['angar_pos_lt' + str(m)].writeFloat('anglesPitch', 0)
                    g_xmlSetting['angar_pos_lt' + str(m)].writeFloat('anglesRotate', 0)
                    g_xmlSetting['angar_pos_lt' + str(m)].writeFloat('x', x+10)
                    if m < 7:
                        g_xmlSetting['angar_pos_lt' + str(m)].writeFloat('y', y+(10*m))
                    else:
                        g_xmlSetting['angar_pos_lt' + str(m)].writeFloat('y', y-(10*(m-6)))
                    g_xmlSetting['angar_pos_lt' + str(m)].writeFloat('z', z)
                    g_xmlSetting.save()
            for m in xrange(1,g_xmlSetting['setup'].readInt('count_angar_pos_mt')+1):
                if not g_xmlSetting['angar_pos_mt' + str(m)]:
                    debug('Added in XML MediumTank angar positions'+str(m))
                    g_xmlSetting.write('angar_pos_mt' + str(m), '')
                    g_xmlSetting['angar_pos_mt' + str(m)].writeBool('RotateTurretToSpawn' , True)
                    g_xmlSetting['angar_pos_mt' + str(m)].writeFloat('v_scale', 1)
                    g_xmlSetting['angar_pos_mt' + str(m)].writeFloat('anglesYaw', 0)
                    g_xmlSetting['angar_pos_mt' + str(m)].writeFloat('anglesPitch', 0)
                    g_xmlSetting['angar_pos_mt' + str(m)].writeFloat('anglesRotate', 0)
                    g_xmlSetting['angar_pos_mt' + str(m)].writeFloat('x', x+5)
                    if m < 7:
                        g_xmlSetting['angar_pos_mt' + str(m)].writeFloat('y', y+(10*m))
                    else:
                        g_xmlSetting['angar_pos_mt' + str(m)].writeFloat('y', y-(10*(m-6)))
                    g_xmlSetting['angar_pos_mt' + str(m)].writeFloat('z', z)
                    g_xmlSetting.save()
            for m in xrange(1,g_xmlSetting['setup'].readInt('count_angar_pos_at')+1):
                if not g_xmlSetting['angar_pos_at' + str(m)]:
                    debug('Added in XML AntiTank angar positions'+str(m))
                    g_xmlSetting.write('angar_pos_at' + str(m), '')
                    g_xmlSetting['angar_pos_at' + str(m)].writeBool('RotateTurretToSpawn' , True)
                    g_xmlSetting['angar_pos_at' + str(m)].writeFloat('v_scale', 1)
                    g_xmlSetting['angar_pos_at' + str(m)].writeFloat('anglesYaw', 0)
                    g_xmlSetting['angar_pos_at' + str(m)].writeFloat('anglesPitch', 0)
                    g_xmlSetting['angar_pos_at' + str(m)].writeFloat('anglesRotate', 0)
                    g_xmlSetting['angar_pos_at' + str(m)].writeFloat('x', x)
                    if m < 7:
                        g_xmlSetting['angar_pos_at' + str(m)].writeFloat('y', y+(10*m))
                    else:
                        g_xmlSetting['angar_pos_at' + str(m)].writeFloat('y', y-(10*(m-6)))
                    g_xmlSetting['angar_pos_at' + str(m)].writeFloat('z', z)
                    g_xmlSetting.save()
            for m in xrange(1,g_xmlSetting['setup'].readInt('count_angar_pos_ht')+1):
                if not g_xmlSetting['angar_pos_ht' + str(m)]:
                    debug('Added in XML HeavyTank angar positions'+str(m))
                    g_xmlSetting.write('angar_pos_ht' + str(m), '')
                    g_xmlSetting['angar_pos_ht' + str(m)].writeBool('RotateTurretToSpawn' , True)
                    g_xmlSetting['angar_pos_ht' + str(m)].writeFloat('v_scale', 1)
                    g_xmlSetting['angar_pos_ht' + str(m)].writeFloat('anglesYaw', 0)
                    g_xmlSetting['angar_pos_ht' + str(m)].writeFloat('anglesPitch', 0)
                    g_xmlSetting['angar_pos_ht' + str(m)].writeFloat('anglesRotate', 0)
                    g_xmlSetting['angar_pos_ht' + str(m)].writeFloat('x', x-5)
                    if m < 7:
                        g_xmlSetting['angar_pos_ht' + str(m)].writeFloat('y', y+(10*m))
                    else:
                        g_xmlSetting['angar_pos_ht' + str(m)].writeFloat('y', y-(10*(m-6)))
                    g_xmlSetting['angar_pos_ht' + str(m)].writeFloat('z', z)
                    g_xmlSetting.save()
            for m in xrange(1,g_xmlSetting['setup'].readInt('count_angar_pos_arty')+1):
                if not g_xmlSetting['angar_pos_arty' + str(m)]:
                    debug('Added in XML ARTY angar positions'+str(m))
                    g_xmlSetting.write('angar_pos_arty' + str(m), '')
                    g_xmlSetting['angar_pos_arty' + str(m)].writeBool('RotateTurretToSpawn' , True)
                    g_xmlSetting['angar_pos_arty' + str(m)].writeFloat('v_scale', 1)
                    g_xmlSetting['angar_pos_arty' + str(m)].writeFloat('anglesYaw', 0)
                    g_xmlSetting['angar_pos_arty' + str(m)].writeFloat('anglesPitch', 0)
                    g_xmlSetting['angar_pos_arty' + str(m)].writeFloat('anglesRotate', 0)
                    g_xmlSetting['angar_pos_arty' + str(m)].writeFloat('x', x-10)
                    if m < 7:
                        g_xmlSetting['angar_pos_arty' + str(m)].writeFloat('y', y+(10*m))
                    else:
                        g_xmlSetting['angar_pos_arty' + str(m)].writeFloat('y', y-(10*(m-6)))
                    g_xmlSetting['angar_pos_arty' + str(m)].writeFloat('z', z)
                    g_xmlSetting.save()
        ClientHangarSpace._VehicleAppearance._VehicleAppearance__doFinalSetup = newFinalSetup
    elif hangar_extended_mod == 'User':
        print '[INFO]:      ['+str(description)+' '+str(version)+' initialized ...]'
        if spc_mods == False:
            check_hangar(True)
        else:
            if torsus_GUP_mod == True:
                print '[INFO]:      ['+str(description)+' Activated to Torsus Girls und Panzer Hangar ]'
            if torsus_winter_mod == True:
                print '[INFO]:      ['+str(description)+' Activated to Torsus Winter Mod Hangar ]'
    else:
        print '[INFO]:      ['+str(description)+' '+str(version)+' disabled...]'
    print ''

init()

pass
import BigWorld
from gui.Scaleform.daapi.view.lobby.hangar import Hangar
from constants import AUTH_REALM
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
