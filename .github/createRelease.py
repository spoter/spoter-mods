# coding=utf-8
import sys
import traceback
import os
import argparse

# Настройка парсера аргументов
parser = argparse.ArgumentParser(description='Create mod archives.')
parser.add_argument('lesta_version', help='Client version for Lesta')
parser.add_argument('wg_version', help='Client version for WG')
parser.add_argument('updated_mods', nargs='+',
                    help='List of mods to update')  # Используем nargs='+' для обработки списка модов

# Парсим аргументы
args = parser.parse_args()

# Получаем версии клиентов и список модов
CLIENT_VERSION_WG = args.wg_version  # Международная версия клиента
CLIENT_VERSION_RU = args.lesta_version  # Леста версия клиента
updated_mods = args.updated_mods  # Список модов для обновления

# Отладочный вывод полученных аргументов
print('DEBUG: Получены аргументы: python .github/createRelease.py %s %s %s' % (
args.lesta_version, args.wg_version, " ".join(args.updated_mods)))
print('DEBUG: Список модов для обновления: %s' % updated_mods)


# Функция для поиска основной папки с модами
def test_main_folder():
    # Проверяем наличие папки mod_mods_gui в родительской директории
    main_folder = os.path.realpath('./../mod_mods_gui')
    if os.path.isdir(main_folder):
        return os.path.realpath('./../')

    # Проверяем наличие папки mod_mods_gui в текущей директории
    main_folder = os.path.realpath('./mod_mods_gui')
    if os.path.isdir(main_folder):
        return os.path.realpath('./')

    # Если папка не найдена, возвращаем None
    return None


# Получаем основную папку с модами
MAIN_FOLDER = test_main_folder()

# Проверяем, что основная папка найдена
if MAIN_FOLDER is None:
    print('ERROR: Основная папка с модами не найдена.')
    sys.exit(1)

# Отладочный вывод основной папки
print('DEBUG: Основная папка с модами: %s' % MAIN_FOLDER)

# Отладочный вывод информации о версиях и модах
print('---------------------')
print('Начало сборки:')
print('      RU: {}'.format(CLIENT_VERSION_RU))
print('      WG: {}'.format(CLIENT_VERSION_WG))
print('      Моды: {}'.format(updated_mods))
print('---------------------')

# Путь к скрипту сборки
script_path = os.path.realpath(os.path.join(MAIN_FOLDER, '.github/builder.py'))

# Обрабатываем каждый мод
for MOD_NAME in updated_mods:
    print("Обработка мода: {}".format(MOD_NAME))  # Исправлено форматирование строки
    try:
        # Запускаем скрипт сборки для каждого мода
        command = "python {} {} {} {}".format(script_path, MOD_NAME, CLIENT_VERSION_RU, CLIENT_VERSION_WG)
        print('DEBUG: Выполняем команду: {}'.format(command))
        os.system(command)
    except Exception as e:
        # Обрабатываем ошибки и выводим их в консоль
        print('ERROR: Ошибка при обработке мода {}: {}'.format(MOD_NAME, e))
        traceback.print_exc()
        sys.exit(1)

# Завершение скрипта
print('---------------------')
print('Сборка завершена.')
print('DONE')