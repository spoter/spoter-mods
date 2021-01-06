import BigWorld, ResMgr, Event, json, os, math, codecs, traceback
from gui.shared.personality import ServicesLocator
from gui.app_loader.settings import APP_NAME_SPACE
from gui.Scaleform.framework.entities.View import View
from gui.shared import events, EVENT_BUS_SCOPE, g_eventBus
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.framework import g_entitiesFactories, ViewSettings, ViewTypes, ScopeTemplates
        
        
class flashInHangar():
    
    def __init__(self):
        g_eventBus.addListener(events.ComponentEvent.COMPONENT_REGISTERED, self.__componentRegisteringHandler, scope=EVENT_BUS_SCOPE.GLOBAL)
        g_eventBus.addListener(events.AppLifeCycleEvent.INITIALIZED, self.__onAppInitialized, scope=EVENT_BUS_SCOPE.GLOBAL)
        
        g_entitiesFactories.addSettings(ViewSettings('hangarMarks', FlashMeta, 'marksInHangar.swf', ViewTypes.WINDOW, None, ScopeTemplates.GLOBAL_SCOPE))
        
        self.onHeaderUpdate = Event.Event()
        self.onHangarLoaded = Event.Event()
        self.setPosition = Event.Event()
        self.setBackground = Event.Event()
        self.setText = Event.Event()

    def __onAppInitialized(self, event):
        if event.ns == APP_NAME_SPACE.SF_LOBBY:
            app = ServicesLocator.appLoader.getApp(event.ns)
            if app is None:
                return
            app.loadView(SFViewLoadParams('hangarMarks'))
        
    def __componentRegisteringHandler(self, event):
        if event.alias == HANGAR_ALIASES.AMMUNITION_PANEL:
            self.setPosition(100, 100) #x and y
            self.setBackground(True, '0x000000', 0.1) # change to false if dont want
            self.setText('Test Test Test') # text
        
class FlashMeta(View):
        
    def _populate(self):
        super(FlashMeta, self)._populate()
        g_marksInHangar.setText += self._setText
        g_marksInHangar.setPosition += self._setPosition
        g_marksInHangar.setBackground += self._setBackground
        
    def _dispose(self):
        super(FlashMeta, self)._dispose()
        
    def py_newPos(self, posX, posY):
        pass
        
    def _setText(self, text):
        if self._isDAAPIInited():
            self.flashObject.as_setText(text)
            
    def _setPosition(self, x, y):
        if self._isDAAPIInited():
            self.flashObject.as_setPosition(x, y)
            
    def _setBackground(self, enabled, bgcolor, alpha):
        if self._isDAAPIInited():
            self.flashObject.as_setBackground(enabled, bgcolor, alpha)
            
g_flashInHangar = flashInHangar()