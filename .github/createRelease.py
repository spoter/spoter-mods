# coding=utf-8
import sys
import traceback
import os
CLIENT_VERSION_RU = '1.32.0.0' # Леста версия клиента
CLIENT_VERSION_WG = '1.27.1.0'# Международная версия клиента

if len(sys.argv) > 1:
    CLIENT_VERSION_RU = sys.argv[2] # Леста версия клиента
    CLIENT_VERSION_WG = sys.argv[3] # Международная версия клиента

def test_main_folder():
    main_folder = os.path.realpath('./../mod_mods_gui')
    if os.path.isdir(main_folder):
        return os.path.realpath('./../')
    main_folder = os.path.realpath('./mod_mods_gui')
    if os.path.isdir(main_folder):
        return os.path.realpath('./')

MAIN_FOLDER = test_main_folder()

mods_list = [
    'mod_mods_gui',
    'mod_artySplash',
    'mod_autoServerSight',
    'mod_creditCalc',
    'mod_crewExtended',
    'mod_discordHangar',
    'mod_marksOnGunExtended',
    'mod_muteSoundHotKey',
    'mod_repair_extended',
    'mod_restartRandomQueue',
    'mod_server_turret_extended',
    'mod_spotted_extended_light',
]
print('---------------------')
print('Start building')
print('      RU: {}'.format(CLIENT_VERSION_RU))
print('      WG: {}'.format(CLIENT_VERSION_WG))

script_path = os.path.realpath(os.path.join(MAIN_FOLDER, '.github/builder.py'))
for MOD_NAME in mods_list:
    try:
        os.system("python {} {} {} {}".format(script_path, MOD_NAME, CLIENT_VERSION_RU, CLIENT_VERSION_WG))
    except Exception as e:
        print('ERROR: {}'.format(e))
        traceback.print_exc()
        break


print('---------------------')
print('DONE')
