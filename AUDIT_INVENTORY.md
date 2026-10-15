# Полный реестр проверок

Сформирован из результатов **CPython 2.7.18 на dev-win11** и закреплённых деревьев EU/RU.
База аудита: `edaabc4735eddf3d00f0a772fddaae7afbded0d3`. Контекст и ограничения: [AUDIT_ALL_MODS.md](AUDIT_ALL_MODS.md).

Файлы учитываются с повторами разных архивов/версий: это покрытие артефактов, не число уникальных модов.
`!` в пути означает вложенный архив. `compile OK` не означает успешный импорт или работу в игре.

## Покрытие всех 43 папок

| Папка | Внешних файлов | Python-артефактов | Архивов с вложенными | PYC внутри/снаружи |
|---|---:|---:|---:|---:|
| `.deprecated/globalmap_extended` | 6 | 2 | 1 | 1 |
| `.deprecated/mod_account_manager` | 24 | 2 | 2 | 2 |
| `.deprecated/mod_armoring_extended` | 6 | 4 | 1 | 2 |
| `.deprecated/mod_artyCrosshair` | 9 | 3 | 2 | 1 |
| `.deprecated/mod_autoAimOptimize` | 9 | 3 | 4 | 5 |
| `.deprecated/mod_autoaim_extended` | 119 | 3 | 1 | 1 |
| `.deprecated/mod_battleChatSwitcher` | 11 | 3 | 4 | 5 |
| `.deprecated/mod_bookmarks` | 9 | 3 | 4 | 5 |
| `.deprecated/mod_chatInfo` | 9 | 3 | 5 | 16 |
| `.deprecated/mod_crewExtended` | 16 | 1 | 0 | 0 |
| `.deprecated/mod_crew_extended` | 5 | 2 | 1 | 1 |
| `.deprecated/mod_dir_indicator_extended` | 1 | 0 | 5 | 16 |
| `.deprecated/mod_dispersionCircle` | 9 | 3 | 4 | 5 |
| `.deprecated/mod_hangar_extended` | 9 | 2 | 4 | 4 |
| `.deprecated/mod_insigniaMonitor` | 21 | 4 | 4 | 5 |
| `.deprecated/mod_modPackInformer` | 9 | 3 | 2 | 1 |
| `.deprecated/mod_personalMissionColored` | 5 | 1 | 2 | 1 |
| `.deprecated/mod_pro_potapov_fixArty` | 11 | 4 | 2 | 1 |
| `.deprecated/mod_repair_extended` | 10 | 4 | 4 | 5 |
| `.deprecated/mod_replay_flag_fix` | 3 | 1 | 1 | 1 |
| `.deprecated/mod_restartRandomQueue` | 4 | 1 | 0 | 0 |
| `.deprecated/mod_rod_mod` | 7 | 1 | 1 | 1 |
| `.deprecated/mod_sightInfo` | 1 | 1 | 0 | 0 |
| `.deprecated/mod_sniperByScroll` | 3 | 1 | 2 | 1 |
| `.deprecated/mod_spotDetails` | 1 | 0 | 2 | 1 |
| `.deprecated/mod_spotMarks` | 9 | 3 | 4 | 5 |
| `.deprecated/mod_spotted_extended` | 1 | 0 | 5 | 6 |
| `.deprecated/mod_steelHunterAutoUpgrades2020` | 22 | 3 | 4 | 5 |
| `.deprecated/mod_tooltipsCountItemsLimitExtend` | 13 | 1 | 10 | 32 |
| `.deprecated/mod_vehicle_exp_extended` | 8 | 4 | 1 | 2 |
| `.deprecated/mod_winter_camo` | 2 | 1 | 1 | 1 |
| `.deprecated/quests_extended` | 6 | 1 | 0 | 0 |
| `.deprecated/stream_announcer` | 1 | 1 | 0 | 0 |
| `mod_artySplash` | 62 | 1 | 0 | 0 |
| `mod_autoServerSight` | 38 | 1 | 0 | 0 |
| `mod_creditCalc` | 80 | 2 | 16 | 0 |
| `mod_discordHangar` | 4 | 1 | 0 | 0 |
| `mod_marksOnGunExtended` | 69 | 1 | 11 | 7 |
| `mod_mods_gui` | 94 | 2 | 12 | 60 |
| `mod_muteSoundHotKey` | 38 | 1 | 0 | 0 |
| `mod_repair_extended` | 38 | 1 | 0 | 0 |
| `mod_server_turret_extended` | 38 | 1 | 0 | 0 |
| `mod_spotted_extended_light` | 38 | 1 | 0 | 0 |

## Каждый внешний Python-артефакт

82 файла `.py` + один декомпил без расширения. Скрытые каталоги и build/release-файлы включены.

| Путь | Python 2.7.18 compile-only |
|---|---|
| `.deprecated/globalmap_extended/globalmap_extended106.py` | OK |
| `.deprecated/globalmap_extended/mod_globalmap_extended107.py` | OK |
| `.deprecated/mod_account_manager/py_src/mod_account_manager.py` | OK |
| `.deprecated/mod_account_manager/py_src/mod_account_manager_login_button.py` | OK |
| `.deprecated/mod_armoring_extended/mod_armoring_extended203.py` | OK |
| `.deprecated/mod_armoring_extended/mod_armoring_extended204.py` | OK |
| `.deprecated/mod_armoring_extended/mod_armoring_extended205.py` | OK |
| `.deprecated/mod_armoring_extended/mod_armoring_extended206.py` | OK |
| `.deprecated/mod_artyCrosshair/.release.py` | OK |
| `.deprecated/mod_artyCrosshair/_build.py` | OK |
| `.deprecated/mod_artyCrosshair/source/mod_artyCrosshair.py` | OK |
| `.deprecated/mod_autoAimOptimize/.release.py` | OK |
| `.deprecated/mod_autoAimOptimize/_build.py` | OK |
| `.deprecated/mod_autoAimOptimize/source/mod_autoAimOptimize.py` | OK |
| `.deprecated/mod_autoaim_extended/mod_autoaim_extended308.py` | OK |
| `.deprecated/mod_autoaim_extended/mod_autoaim_extended309.py` | OK |
| `.deprecated/mod_autoaim_extended/mod_autoaim_extended310.py` | OK |
| `.deprecated/mod_battleChatSwitcher/.release.py` | OK |
| `.deprecated/mod_battleChatSwitcher/_build.py` | OK |
| `.deprecated/mod_battleChatSwitcher/source/mod_battleChatSwitcher.py` | OK |
| `.deprecated/mod_bookmarks/.release.py` | OK |
| `.deprecated/mod_bookmarks/_build.py` | OK |
| `.deprecated/mod_bookmarks/source/mod_bookmarks.py` | OK |
| `.deprecated/mod_chatInfo/.release.py` | OK |
| `.deprecated/mod_chatInfo/_build.py` | OK |
| `.deprecated/mod_chatInfo/source/mod_chatInfo.py` | OK |
| `.deprecated/mod_crewExtended/source/mod_crewExtended.py` | OK |
| `.deprecated/mod_crew_extended/mod_crew_extended403.py` | OK |
| `.deprecated/mod_crew_extended/mod_crew_extended404.py` | OK |
| `.deprecated/mod_dispersionCircle/.release.py` | OK |
| `.deprecated/mod_dispersionCircle/_build.py` | OK |
| `.deprecated/mod_dispersionCircle/source/mod_dispersionCircle.py` | OK |
| `.deprecated/mod_hangar_extended/mod_activate_hangar.py` | OK |
| `.deprecated/mod_hangar_extended/mod_hangar_extended121.py` | OK |
| `.deprecated/mod_insigniaMonitor/.release.py` | OK |
| `.deprecated/mod_insigniaMonitor/_build.py` | OK |
| `.deprecated/mod_insigniaMonitor/source/mod_insigniaMonitor.py` | OK |
| `.deprecated/mod_insigniaMonitor/source/temp.py` | OK |
| `.deprecated/mod_modPackInformer/.release.py` | OK |
| `.deprecated/mod_modPackInformer/_build.py` | OK |
| `.deprecated/mod_modPackInformer/source/mod_modPackInformer.py` | OK |
| `.deprecated/mod_personalMissionColored/source/mod_personalMissionColored.py` | OK |
| `.deprecated/mod_pro_potapov_fixArty/.release.py` | OK |
| `.deprecated/mod_pro_potapov_fixArty/_build.py` | OK |
| `.deprecated/mod_pro_potapov_fixArty/source/mod_pro_potapov` | ERROR: invalid syntax, строка 18 |
| `.deprecated/mod_pro_potapov_fixArty/source/mod_pro_potapov_fixArty.py` | OK |
| `.deprecated/mod_repair_extended/.release.py` | OK |
| `.deprecated/mod_repair_extended/_build_auto.py` | OK |
| `.deprecated/mod_repair_extended/source/.deprecated/mod_repair_extended_autoequip.py` | OK |
| `.deprecated/mod_repair_extended/source/auto/mod_repair_extended.py` | OK |
| `.deprecated/mod_replay_flag_fix/mod_replay_flag_fix102.py` | OK |
| `.deprecated/mod_restartRandomQueue/source/mod_restartRandomQueue.py` | OK |
| `.deprecated/mod_rod_mod/mod_rod_mod.py` | OK |
| `.deprecated/mod_sightInfo/mod_sightInfo.py` | OK |
| `.deprecated/mod_sniperByScroll/source/mod_sniperByScroll.py` | OK |
| `.deprecated/mod_spotMarks/.release.py` | OK |
| `.deprecated/mod_spotMarks/_build.py` | OK |
| `.deprecated/mod_spotMarks/source/mod_spotMarks.py` | OK |
| `.deprecated/mod_steelHunterAutoUpgrades2020/.release.py` | OK |
| `.deprecated/mod_steelHunterAutoUpgrades2020/_build.py` | OK |
| `.deprecated/mod_steelHunterAutoUpgrades2020/source/mod_steelHunterAutoUpgrades2020.py` | OK |
| `.deprecated/mod_tooltipsCountItemsLimitExtend/source/mod_tooltipsCountItemsLimitExtend.py` | OK |
| `.deprecated/mod_vehicle_exp_extended/mod_hangar_tooltips101.py` | OK |
| `.deprecated/mod_vehicle_exp_extended/mod_vehicle_exp_extended210.py` | OK |
| `.deprecated/mod_vehicle_exp_extended/mod_vehicle_exp_extended211.py` | OK |
| `.deprecated/mod_vehicle_exp_extended/mod_vehicle_exp_extended212.py` | OK |
| `.deprecated/mod_winter_camo/mod_winter_camo.py` | OK |
| `.deprecated/quests_extended/quests_extended202.py` | OK |
| `.deprecated/stream_announcer/stream_announcer114.py` | OK |
| `.github/builder.py` | OK |
| `.github/createRelease.py` | OK |
| `mod_artySplash/source/mod_artySplash.py` | OK |
| `mod_autoServerSight/source/mod_autoServerSight.py` | OK |
| `mod_creditCalc/source/hangarFlash/mod_hangarflash.py` | OK |
| `mod_creditCalc/source/mod_creditCalc.py` | OK |
| `mod_discordHangar/source/mod_discordHangar.py` | OK |
| `mod_marksOnGunExtended/source/mod_marksOnGunExtended.py` | OK |
| `mod_mods_gui/source/mod_mods_gui.py` | OK |
| `mod_mods_gui/tests/test_hooks.py` | OK |
| `mod_muteSoundHotKey/source/mod_muteSoundHotKey.py` | OK |
| `mod_repair_extended/source/mod_repair_extended.py` | OK |
| `mod_server_turret_extended/source/mod_server_turret_extended.py` | OK |
| `mod_spotted_extended_light/source/mod_spotted_extended_light.py` | OK |

## Python внутри архивов

| Путь | Compile-only |
|---|---|
| `.deprecated/mod_tooltipsCountItemsLimitExtend/zip/mod_tooltipsCountItemsLimitExtend.zip!mods/configs/spoter/i18n/mod_tooltipsCountItemsLimitExtend.py` | ok |
| `.deprecated/mod_tooltipsCountItemsLimitExtend/zip/mod_tooltipsCountItemsLimitExtend_RU.zip!mods/configs/spoter/i18n/mod_tooltipsCountItemsLimitExtend.py` | ok |

Оба исходника tooltip дополнительно скопированы в configs/i18n; основной mod-архив содержит правильный `.pyc`. Это лишние файлы упаковки, не доказательство отсутствия основной точки входа.

## Все 72 внешних архивных контейнера

С учётом 50 вложенных проверено 122 ZIP/WOTMOD/MTMOD/SWC/PKG. У всех выполнено чтение entries с проверкой CRC; лимиты безопасности сканера не сработали. Дублирующихся имён записей нет.

| Путь | Размер | Entries | CRC/status |
|---|---:|---:|---|
| `.deprecated/globalmap_extended/zip/mod_globalmap_extended.zip` | 10843 | 8 | ok |
| `.deprecated/mod_account_manager/as3_src/lib/wg.swc` | 1801206 | 2 | ok |
| `.deprecated/mod_account_manager/release/account_manager.zip` | 55021 | 26 | ok |
| `.deprecated/mod_armoring_extended/zip/armoring_extended.zip` | 139553 | 26 | ok |
| `.deprecated/mod_artyCrosshair/zip/mod_artyCrosshair.zip` | 3555 | 9 | ok |
| `.deprecated/mod_autoAimOptimize/zip/mods_autoAimOptimize.zip` | 127128 | 17 | ok |
| `.deprecated/mod_autoaim_extended/zip/autoaim_extended.zip` | 616450 | 150 | ok |
| `.deprecated/mod_battleChatSwitcher/zip/mod_battleChatSwitcher.zip` | 126114 | 17 | ok |
| `.deprecated/mod_bookmarks/zip/mods_bookmarks.zip` | 128596 | 17 | ok |
| `.deprecated/mod_chatInfo/zip/mod_chatInfo.zip` | 330317 | 29 | ok |
| `.deprecated/mod_crew_extended/zip/crew_extended.zip` | 19212 | 12 | ok |
| `.deprecated/mod_dir_indicator_extended/zip/mods_testDir.zip` | 395229 | 31 | ok |
| `.deprecated/mod_dispersionCircle/zip/mods_dispersionCircle.zip` | 145770 | 23 | ok |
| `.deprecated/mod_hangar_extended/zip/hangar_extended.zip` | 96669618 | 12 | ok |
| `.deprecated/mod_hangar_extended/zip/hangar_extended_for_moders.zip` | 88484 | 9 | ok |
| `.deprecated/mod_hangar_extended/zip/res_mods/hangar_packages/hangar_premium_v2_1.pkg` | 61252906 | 207 | ok |
| `.deprecated/mod_hangar_extended/zip/res_mods/hangar_packages/hangar_v2_1.pkg` | 36097738 | 146 | ok |
| `.deprecated/mod_insigniaMonitor/zip/mod_insigniaMonitor.zip` | 231898 | 17 | ok |
| `.deprecated/mod_modPackInformer/zip/mods_modPackInformer.zip` | 6425 | 11 | ok |
| `.deprecated/mod_personalMissionColored/zip/mods_personalMissionColored.zip` | 1603 | 4 | ok |
| `.deprecated/mod_pro_potapov_fixArty/zip/mod_pro_potapov_fixArty.zip` | 11180 | 3 | ok |
| `.deprecated/mod_repair_extended/zip/mods_repair_extended_cheat.zip` | 130662 | 17 | ok |
| `.deprecated/mod_replay_flag_fix/zip/replay_flag_fix.zip` | 38796 | 11 | ok |
| `.deprecated/mod_rod_mod/zip/rod_mod.zip` | 74723 | 12 | ok |
| `.deprecated/mod_sniperByScroll/zip/mods_sniperByScroll.zip` | 2861 | 4 | ok |
| `.deprecated/mod_spotDetails/zip/mod_spotDetails.zip` | 15343 | 4 | ok |
| `.deprecated/mod_spotMarks/zip/mods_spotMarks.zip` | 141771 | 17 | ok |
| `.deprecated/mod_spotted_extended/zip/mods_spotted_extended.zip` | 276102 | 18 | ok |
| `.deprecated/mod_steelHunterAutoUpgrades2020/zip/mod_steelHunterAutoUpgrades2020.zip` | 147052 | 23 | ok |
| `.deprecated/mod_tooltipsCountItemsLimitExtend/zip/mod_tooltipsCountItemsLimitExtend.zip` | 274312 | 28 | ok |
| `.deprecated/mod_tooltipsCountItemsLimitExtend/zip/mod_tooltipsCountItemsLimitExtend_RU.zip` | 274312 | 28 | ok |
| `.deprecated/mod_vehicle_exp_extended/zip/vehicle_exp_extended.zip` | 18025 | 14 | ok |
| `.deprecated/mod_winter_camo/zip/mod_winter_camo.zip` | 1445 | 7 | ok |
| `mod_creditCalc/source/hangarFlash/creditCalc/swc/base_app-1.0-SNAPSHOT.swc` | 92519 | 2 | ok |
| `mod_creditCalc/source/hangarFlash/creditCalc/swc/battle.swc` | 10091 | 2 | ok |
| `mod_creditCalc/source/hangarFlash/creditCalc/swc/common-1.0-SNAPSHOT.swc` | 302472 | 2 | ok |
| `mod_creditCalc/source/hangarFlash/creditCalc/swc/common_i18n_library-1.0-SNAPSHOT.swc` | 832480 | 2 | ok |
| `mod_creditCalc/source/hangarFlash/creditCalc/swc/gui_base-1.0-SNAPSHOT.swc` | 746498 | 2 | ok |
| `mod_creditCalc/source/hangarFlash/creditCalc/swc/gui_battle-1.0-SNAPSHOT.swc` | 702930 | 2 | ok |
| `mod_creditCalc/source/hangarFlash/creditCalc/swc/gui_lobby-1.0-SNAPSHOT.swc` | 3298042 | 2 | ok |
| `mod_creditCalc/source/hangarFlash/creditCalc/swc/lobby.swc` | 28644 | 2 | ok |
| `mod_creditCalc/source/hangarFlash/hangarMarks_AS3/swc/base_app-1.0-SNAPSHOT.swc` | 94514 | 2 | ok |
| `mod_creditCalc/source/hangarFlash/hangarMarks_AS3/swc/battle.swc` | 10163 | 2 | ok |
| `mod_creditCalc/source/hangarFlash/hangarMarks_AS3/swc/common-1.0-SNAPSHOT.swc` | 302988 | 2 | ok |
| `mod_creditCalc/source/hangarFlash/hangarMarks_AS3/swc/common_i18n_library-1.0-SNAPSHOT.swc` | 991701 | 2 | ok |
| `mod_creditCalc/source/hangarFlash/hangarMarks_AS3/swc/gui_base-1.0-SNAPSHOT.swc` | 783980 | 2 | ok |
| `mod_creditCalc/source/hangarFlash/hangarMarks_AS3/swc/gui_battle-1.0-SNAPSHOT.swc` | 815647 | 2 | ok |
| `mod_creditCalc/source/hangarFlash/hangarMarks_AS3/swc/gui_lobby-1.0-SNAPSHOT.swc` | 3137939 | 2 | ok |
| `mod_creditCalc/source/hangarFlash/hangarMarks_AS3/swc/lobby.swc` | 28383 | 2 | ok |
| `mod_marksOnGunExtended/addons/mods/oldskool/oldskool.marksInHangar_1.1.7.wotmod` | 107815 | 19 | ok |
| `mod_marksOnGunExtended/addons/mods/oldskool/oldskool.marksInTechTree_1.0.9.wotmod` | 37124 | 10 | ok |
| `mod_marksOnGunExtended/addons/mods/oldskool/oldskool.modsCore_1.2.2.wotmod` | 284800 | 29 | ok |
| `mod_marksOnGunExtended/source/flashSource/as3/libs/base_app-1.0-SNAPSHOT.swc` | 92313 | 2 | ok |
| `mod_marksOnGunExtended/source/flashSource/as3/libs/battle.swc` | 9783 | 2 | ok |
| `mod_marksOnGunExtended/source/flashSource/as3/libs/common-1.0-SNAPSHOT.swc` | 293675 | 2 | ok |
| `mod_marksOnGunExtended/source/flashSource/as3/libs/common_i18n_library-1.0-SNAPSHOT.swc` | 728214 | 2 | ok |
| `mod_marksOnGunExtended/source/flashSource/as3/libs/gui_base-1.0-SNAPSHOT.swc` | 721931 | 2 | ok |
| `mod_marksOnGunExtended/source/flashSource/as3/libs/gui_battle-1.0-SNAPSHOT.swc` | 649874 | 2 | ok |
| `mod_marksOnGunExtended/source/flashSource/as3/libs/gui_lobby-1.0-SNAPSHOT.swc` | 3120764 | 2 | ok |
| `mod_marksOnGunExtended/source/flashSource/as3/libs/lobby.swc` | 28558 | 2 | ok |
| `mod_mods_gui/release/gambiter.guiflash_0.6.4.mtmod` | 58274 | 15 | ok |
| `mod_mods_gui/release/gambiter.guiflash_0.6.4.wotmod` | 58274 | 15 | ok |
| `mod_mods_gui/release/me.poliroid.modslistapi_1.6.01.mtmod` | 79776 | 56 | ok |
| `mod_mods_gui/release/me.poliroid.modslistapi_1.7.7.wotmod` | 165899 | 67 | ok |
| `mod_mods_gui/release/mod_mods_gui_3.09.mtmod` | 115200 | 13 | ok |
| `mod_mods_gui/release/mod_mods_gui_3.09.wotmod` | 115200 | 13 | ok |
| `mod_mods_gui/release/net.openwg.gameface_1.1.5.wotmod` | 42020 | 18 | ok |
| `mod_mods_gui/source/additional/gambiter.guiflash_0.6.4.mtmod` | 58274 | 15 | ok |
| `mod_mods_gui/source/additional/gambiter.guiflash_0.6.4.wotmod` | 58274 | 15 | ok |
| `mod_mods_gui/source/additional/me.poliroid.modslistapi_1.6.01.mtmod` | 79776 | 56 | ok |
| `mod_mods_gui/source/additional/me.poliroid.modslistapi_1.7.7.wotmod` | 165899 | 67 | ok |
| `mod_mods_gui/source/additional/net.openwg.gameface_1.1.5.wotmod` | 42020 | 18 | ok |

## Границы проверки байткода

199 вхождений PYC имеют magic Python2.7. **Magic не доказывает именно patch 2.7.18 у чужого старого бинарника.** 182 code objects разобраны, 17 не разобраны линейным opcode-анализом; это не доказательство повреждения. Даже успешный разбор может видеть только обфусцированную оболочку, а не поведение payload. Ни один байткод не исполнялся.

Не разобраны:

- `.deprecated/mod_armoring_extended/zip/armoring_extended.zip!res_mods/0.9.14/scripts/client/gui/mods/mod_mods_gui.pyc` — `IndexError`.
- `.deprecated/mod_chatInfo/zip/mod_chatInfo.zip!mods/1.21.1.0/mod_mods_gui_3.04.wotmod!res/scripts/client/gui/mods/mod_mods_gui.pyc` — `IndexError`.
- `.deprecated/mod_hangar_extended/zip/hangar_extended.zip!res_mods/0.9.10/scripts/client/gui/mods/mod_hangar_extended.pyc` — `IndexError`.
- `.deprecated/mod_hangar_extended/zip/hangar_extended_for_moders.zip!res_mods/0.9.10/scripts/client/gui/mods/mod_hangar_extended121_for_moders.pyc` — `IndexError`.
- `.deprecated/mod_insigniaMonitor/zip/mod_insigniaMonitor.zip!mods/1.6.1.0/mod_mods_gui_2.23.wotmod!res/scripts/client/gui/mods/mod_mods_gui.pyc` — `IndexError`.
- `.deprecated/mod_repair_extended/zip/mods_repair_extended_cheat.zip!mods/1.4.1.1/mod_mods_gui_2.19.wotmod!res/scripts/client/gui/mods/mod_mods_gui.pyc` — `IndexError`.
- `.deprecated/mod_replay_flag_fix/zip/replay_flag_fix.zip!res_mods/0.9.10/scripts/client/gui/mods/mod_replay_flag_fix.pyc` — `IndexError`.
- `.deprecated/mod_rod_mod/zip/rod_mod.zip!res_mods/0.9.10/scripts/client/gui/mods/mod_rod_mod.pyc` — `IndexError`.
- `.deprecated/mod_spotDetails/zip/mod_spotDetails.zip!mods/1.22.0.0/spoter/spoter.spotDetails_1.01.wotmod!res/scripts/client/gui/mods/mod_spotDetails.pyc` — `IndexError`.
- `.deprecated/mod_spotMarks/zip/mods_spotMarks.zip!mods/1.6.1.0/mod_mods_gui_2.23.wotmod!res/scripts/client/gui/mods/mod_mods_gui.pyc` — `IndexError`.
- `.deprecated/mod_spotted_extended/zip/mods_spotted_extended.zip!mods/1.3.0.1/spoter/spoter.spotEngine_1.04.wotmod!res/scripts/client/gui/mods/mod_spotEngine.pyc` — `IndexError`.
- `mod_marksOnGunExtended/addons/mods/oldskool/oldskool.marksInHangar_1.1.7.wotmod!res/scripts/client/gui/mods/mod_marksInHangar.pyc` — `IndexError`.
- `mod_marksOnGunExtended/addons/mods/oldskool/oldskool.marksInTechTree_1.0.9.wotmod!res/scripts/client/gui/mods/mod_marksInTechTree.pyc` — `IndexError`.
- `mod_marksOnGunExtended/addons/mods/oldskool/oldskool.modsCore_1.2.2.wotmod!res/scripts/client/gui/mods/mod_oldskoolCore.pyc` — `IndexError`.
- `mod_marksOnGunExtended/addons/mods/oldskool/oldskool.modsCore_1.2.2.wotmod!res/scripts/client/gui/oldskool/playersPanelAPI.pyc` — `IndexError`.
- `mod_marksOnGunExtended/addons/mods/oldskool/oldskool.modsCore_1.2.2.wotmod!res/scripts/client/gui/oldskool/utils.pyc` — `IndexError`.
- `mod_marksOnGunExtended/addons/mods/oldskool/oldskool.modsCore_1.2.2.wotmod!res/scripts/client/gui/oldskool/__init__.pyc` — `IndexError`.

## Некорректный strict JSON: все 7 вхождений

4 вхождения crew/vehicle_exp имеют комментарии и проходят соответствующие извлечённые `json_comments` + json.loads на Python2.7.18; их не считать повреждёнными. Bookmarks (2) содержит лишние запятые, spotted (1) — пропущенную запятую.

- `.deprecated/mod_bookmarks/source/configs/bookmarks.json`.
- `.deprecated/mod_bookmarks/zip/mods_bookmarks.zip!mods/configs/spoter/bookmarks/bookmarks.json`.
- `.deprecated/mod_crew_extended/zip/crew_extended.zip!res_mods/configs/spoter_mods/crew_extended/crew_extended.json`.
- `.deprecated/mod_crew_extended/zip/res_mods/configs/spoter_mods/crew_extended/crew_extended.json`.
- `.deprecated/mod_spotted_extended/zip/mods_spotted_extended.zip!mods/configs/spoter/spotted_extended/spotted_extended.json`.
- `.deprecated/mod_vehicle_exp_extended/zip/res_mods/configs/spoter_mods/vehicle_exp_extended/vehicle_exp_extended.json`.
- `.deprecated/mod_vehicle_exp_extended/zip/vehicle_exp_extended.zip!res_mods/configs/spoter_mods/vehicle_exp_extended/vehicle_exp_extended.json`.

## Манифесты с отсутствующими путями

- `.deprecated/mod_modPackInformer/source/VERSION`: `[{"i18n": "configs/i18n"}]`.
- `mod_server_turret_extended/source/VERSION`: `[{"config": "configs/serverTurretExtended.json"}]`.

## Все 41 вхождение импортов без пути в одном/обоих регионах

Проверены 395 вхождений выбранных игровых namespace по **полным** scripts-деревьям: EU 12843 записи, RU 15653. Поиск client/common/client_common дополнен поиском суффикса в остальных script-папках. Это проверка файлов, не всех символов/транзитивных зависимостей.
**41 — не число сломанных модов.** Региональные `try/except` marks/server-turret/queue могут корректно использовать альтернативу. Native API/динамические exports нельзя диагностировать только отсутствием файла. Содержательная оценка находится в AUDIT_ACTIVE / AUDIT_DEPRECATED.

| Исходник:строка | Импорт | EU | RU |
|---|---|---|---|
| `.deprecated/mod_armoring_extended/mod_armoring_extended203.py:23` | `gui.Scaleform.Flash` | путь не найден | путь не найден |
| `.deprecated/mod_armoring_extended/mod_armoring_extended203.py:24` | `gui.Scaleform.Battle` | путь не найден | путь не найден |
| `.deprecated/mod_armoring_extended/mod_armoring_extended204.py:18` | `gui.Scaleform.Battle` | путь не найден | путь не найден |
| `.deprecated/mod_armoring_extended/mod_armoring_extended205.py:23` | `gui.Scaleform.Battle` | путь не найден | путь не найден |
| `.deprecated/mod_armoring_extended/mod_armoring_extended206.py:23` | `gui.Scaleform.Battle` | путь не найден | путь не найден |
| `.deprecated/mod_autoaim_extended/mod_autoaim_extended308.py:21` | `tutorial.gui.Scaleform.battle` | путь не найден | путь не найден |
| `.deprecated/mod_autoaim_extended/mod_autoaim_extended308.py:23` | `gui.Scaleform.Battle` | путь не найден | путь не найден |
| `.deprecated/mod_autoaim_extended/mod_autoaim_extended309.py:21` | `tutorial.gui.Scaleform.battle` | путь не найден | путь не найден |
| `.deprecated/mod_autoaim_extended/mod_autoaim_extended309.py:23` | `gui.Scaleform.Battle` | путь не найден | путь не найден |
| `.deprecated/mod_autoaim_extended/mod_autoaim_extended310.py:20` | `tutorial.gui.Scaleform.battle` | путь не найден | путь не найден |
| `.deprecated/mod_autoaim_extended/mod_autoaim_extended310.py:22` | `gui.Scaleform.Battle` | путь не найден | путь не найден |
| `.deprecated/mod_crewExtended/source/mod_crewExtended.py:9` | `gui.Scaleform.daapi.view.lobby.barracks` | путь не найден | путь есть |
| `.deprecated/mod_crewExtended/source/mod_crewExtended.py:10` | `gui.Scaleform.daapi.view.meta.CrewMeta` | путь не найден | путь не найден |
| `.deprecated/mod_crew_extended/mod_crew_extended403.py:17` | `gui.Scaleform.daapi.view.meta.CrewMeta` | путь не найден | путь не найден |
| `.deprecated/mod_crew_extended/mod_crew_extended403.py:18` | `gui.Scaleform.daapi.view.meta.BarracksMeta` | путь не найден | путь есть |
| `.deprecated/mod_crew_extended/mod_crew_extended404.py:17` | `gui.Scaleform.daapi.view.meta.CrewMeta` | путь не найден | путь не найден |
| `.deprecated/mod_crew_extended/mod_crew_extended404.py:18` | `gui.Scaleform.daapi.view.meta.BarracksMeta` | путь не найден | путь есть |
| `.deprecated/mod_dispersionCircle/source/mod_dispersionCircle.py:13` | `AvatarInputHandler.AimingSystems.SniperAimingSystem` | путь не найден | путь не найден |
| `.deprecated/mod_hangar_extended/mod_hangar_extended121.py:18` | `VehicleAppearance` | путь не найден | путь не найден |
| `.deprecated/mod_hangar_extended/mod_hangar_extended121.py:26` | `gui.LobbyContext` | путь не найден | путь не найден |
| `.deprecated/mod_pro_potapov_fixArty/source/mod_pro_potapov_fixArty.py:7` | `bootcamp.aop.common` | путь не найден | путь есть |
| `.deprecated/mod_repair_extended/source/.deprecated/mod_repair_extended_autoequip.py:7` | `gui.Scaleform.daapi.view.lobby.hangar.AmmunitionPanel` | путь не найден | путь не найден |
| `.deprecated/mod_replay_flag_fix/mod_replay_flag_fix102.py:14` | `gui.Scaleform.daapi.view.battle.BattleRibbonsPanel` | путь не найден | путь не найден |
| `.deprecated/mod_restartRandomQueue/source/mod_restartRandomQueue.py:16` | `gui.Scaleform.daapi.view.lobby.battle_queue.battle_queue` | путь есть | путь не найден |
| `.deprecated/mod_rod_mod/mod_rod_mod.py:9` | `gui.Scaleform.Minimap` | путь не найден | путь не найден |
| `.deprecated/mod_rod_mod/mod_rod_mod.py:13` | `gui.Scaleform.Flash` | путь не найден | путь не найден |
| `.deprecated/mod_rod_mod/mod_rod_mod.py:14` | `gui.Scaleform.Battle` | путь не найден | путь не найден |
| `.deprecated/mod_sightInfo/mod_sightInfo.py:3` | `gui.Scaleform.daapi.view.battle.shared.crosshair_panel` | путь не найден | путь не найден |
| `.deprecated/mod_spotMarks/source/mod_spotMarks.py:14` | `tutorial.control.battle.functional` | путь не найден | путь не найден |
| `.deprecated/mod_steelHunterAutoUpgrades2020/source/mod_steelHunterAutoUpgrades2020.py:6` | `tutorial.control.battle.functional` | путь не найден | путь не найден |
| `.deprecated/mod_steelHunterAutoUpgrades2020/source/mod_steelHunterAutoUpgrades2020.py:8` | `gui.Scaleform.daapi.view.battle.battle_royale.battle_upgrade_panel` | путь не найден | путь не найден |
| `.deprecated/mod_steelHunterAutoUpgrades2020/source/mod_steelHunterAutoUpgrades2020.py:9` | `gui.Scaleform.daapi.view.battle.battle_royale.minimap` | путь не найден | путь не найден |
| `.deprecated/mod_steelHunterAutoUpgrades2020/source/mod_steelHunterAutoUpgrades2020.py:10` | `gui.Scaleform.daapi.view.battle.battle_royale.minimap.settings` | путь не найден | путь не найден |
| `.deprecated/mod_vehicle_exp_extended/mod_vehicle_exp_extended210.py:16` | `gui.Scaleform.daapi.view.meta.ParamsMeta` | путь не найден | путь не найден |
| `.deprecated/mod_vehicle_exp_extended/mod_vehicle_exp_extended211.py:16` | `gui.Scaleform.daapi.view.meta.ParamsMeta` | путь не найден | путь не найден |
| `.deprecated/mod_vehicle_exp_extended/mod_vehicle_exp_extended212.py:16` | `gui.Scaleform.daapi.view.meta.ParamsMeta` | путь не найден | путь не найден |
| `.deprecated/mod_winter_camo/mod_winter_camo.py:2` | `VehicleAppearance` | путь не найден | путь не найден |
| `.deprecated/quests_extended/quests_extended202.py:268` | `gui.Scaleform.daapi.view.meta.BattleLoadingMeta` | путь не найден | путь не найден |
| `mod_marksOnGunExtended/source/mod_marksOnGunExtended.py:32` | `gui.impl.lobby.hangar.presenters.crew_presenter` | путь есть | путь не найден |
| `mod_server_turret_extended/source/mod_server_turret_extended.py:30` | `AvatarInputHandler.player_notifications.siege_mode.sound_notifications` | путь есть | путь не найден |
| `mod_server_turret_extended/source/mod_server_turret_extended.py:34` | `AvatarInputHandler.siege_mode_player_notifications` | путь не найден | путь есть |

## Данные для воспроизведения

- Windows: `C:\Users\spoter.LOCAL\Desktop\dsh-workspace\work\audit-all-mods\full_audit.py` и `full-audit-v2.json`.
- Аналитическая копия: `/home/spoter/wot-mods-audit/full-audit-v2.json`, `import-paths.json`, `script-trees.json`.
- Полный JSON SHA-256: `876f521bba71d45e1dff79dd7e6faa5d7b03ab6f4215deaba37a10cb3a9e7494`.
- Python-сканер compile-only не импортирует моды; `.pkg`/`.swc` проверяются как контейнеры, не компилируются и не запускаются.
- Существующие строители и CI не запускались при полном аудите; ранее отдельно собран только GUI, его артефакты теперь отмечены как непригодные для использования до устранения обнаруженной логики стрельбы.
