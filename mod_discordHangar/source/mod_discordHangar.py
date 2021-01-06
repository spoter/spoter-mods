# -*- coding: utf-8 -*-
# noinspection PyUnresolvedReferences
from gui.ModsListApi import g_modsListApi
from gui.mods.mod_mods_gui import browser


def openIt():
    browser.open('https://discordapp.com/channels/394862285497040906/394862285497040910')


if g_modsListApi:
    g_modsListApi.addModification('mod_discordHangar', 'Discord', 'Discord', './gui/maps/icons/artefact/notFound.png', True, False, True, openIt)

print '[LOAD_MOD]:  [discordHangar 1.02 (06-01-2021), by spoter]'
