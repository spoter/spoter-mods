# coding=utf-8
import sys
import traceback
import os
import argparse

parser = argparse.ArgumentParser(description='Create mod archives.')
parser.add_argument('lesta_version', help='Client version for Lesta')
parser.add_argument('wg_version', help='Client version for WG')

args = parser.parse_args()

CLIENT_VERSION_WG = args.wg_version    # Международная версия клиента
CLIENT_VERSION_RU = args.lesta_version # Леста версия клиента

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
