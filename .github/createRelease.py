# coding=utf-8
import subprocess
import sys
import traceback
import os
import imp
CLIENT_VERSION_RU = '1.32.0.0' # Леста версия клиента
CLIENT_VERSION_WG = '1.27.1.0'# Международная версия клиента

if len(sys.argv) > 1:
    CLIENT_VERSION_RU = sys.argv[2] # Леста версия клиента
    CLIENT_VERSION_WG = sys.argv[3] # Международная версия клиента

mods_list = [
    'mod_artySplash',
    'mod_autoServerSight',
    'mod_creditCalc',
    'mod_crewExtended',
    'mod_discordHangar',
    'mod_marksOnGunExtended',
    'mod_mods_gui',
    'mod_muteSoundHotKey',
    'mod_repair_extended',
    'mod_restartRandomQueue',
    'mod_server_turret_extended',
    'mod_spotted_extended_light',
    'mod_tooltipsCountItemsLimitExtend',
]
print('---------------------')
print('Start building')
print('      RU: {}'.format(CLIENT_VERSION_RU))
print('      WG: {}'.format(CLIENT_VERSION_WG))
script_path = os.path.realpath('builder.py')
for MOD_NAME in mods_list:
    try:
        os.system("python builder.py {} {} {}".format(MOD_NAME, CLIENT_VERSION_RU, CLIENT_VERSION_WG))
    except Exception as e:
        print('ERROR: {}'.format(e))
        traceback.print_exc()
        break


print('---------------------')
print('DONE')
