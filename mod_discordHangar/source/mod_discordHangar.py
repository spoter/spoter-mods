# -*- coding: utf-8 -*-
from gui import GUI_SETTINGS
from urllib import quote_plus
# noinspection PyUnresolvedReferences
from gui.ModsListApi import g_modsListApi
from gui.mods.mod_mods_gui import browser


def openIt():
    browser.open(GUI_SETTINGS.registrationProxyURL + '&lpurl=' + quote_plus('https://discordapp.com/channels/394862285497040906/394862285497040910'))


if g_modsListApi:
    g_modsListApi.addModification('mod_discordHangar', 'Discord', 'Discord', './gui/maps/icons/artefact/notFound.png', True, False, True, openIt)

print '[LOAD_MOD]:  [sniperByScroll 1.00 (14-08-2019), by spoter]'
