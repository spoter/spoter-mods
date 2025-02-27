# coding=utf-8
import traceback
import os
import argparse
import json

parser = argparse.ArgumentParser(description='Create mod archives.')
parser.add_argument('lesta_version', help='Client version for Lesta')
parser.add_argument('wg_version', help='Client version for WG')
parser.add_argument('updated_mods', help='Mods lists in format "name1,name2" or ""')

args = parser.parse_args()

CLIENT_VERSION_WG = args.wg_version    # Международная версия клиента
CLIENT_VERSION_RU = args.lesta_version # Леста версия клиента
updated_mods = args.updated_mods.split(",") if args.updated_mods else []  # список модов для обновления

def test_main_folder():
    main_folder = os.path.realpath('./../mod_mods_gui')
    if os.path.isdir(main_folder):
        return os.path.realpath('./../')
    main_folder = os.path.realpath('./mod_mods_gui')
    if os.path.isdir(main_folder):
        return os.path.realpath('./')

MAIN_FOLDER = test_main_folder()

print('---------------------')
print('Start building')
print('      RU: {}'.format(CLIENT_VERSION_RU))
print('      WG: {}'.format(CLIENT_VERSION_WG))
print('      Mods: {}'.format(updated_mods))

script_path = os.path.realpath(os.path.join(MAIN_FOLDER, '.github/builder.py'))
for MOD_NAME in updated_mods:
    try:
        os.system("python {} {} {} {}".format(script_path, MOD_NAME, CLIENT_VERSION_RU, CLIENT_VERSION_WG))
    except Exception as e:
        print('ERROR: {}'.format(e))
        traceback.print_exc()
        break

print('---------------------')
print('DONE')