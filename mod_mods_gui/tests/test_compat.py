# -*- coding: utf-8 -*-
"""Tests for ``gui/mods/gambiter/compat.py`` - the cross-realm view registry shim.

compat.py ships inside the GUIFlash package (not in this mod), so the source is
located by path:

* ``$MODS_GUI_COMPAT`` - explicit path to compat.py, or
* a copy next to this test file, or
* the GUIFlash 0.6.6 checkout used by the team.

When the file is not found the case is skipped - the stand simply has no
GUIFlash sources, and that is not a failure of this mod.

Two branches of ``getEntitiesFactories()`` are covered:
* Lesta (WoT 1.45): module level ``gui.Scaleform.framework.g_entitiesFactories``;
* WG (WoT 2.4.1): ``helpers.dependency.instance(IGuiLoader).entitiesFactory``.

compat.py imports the client modules lazily (inside ``getEntitiesFactories``),
so the stub modules have to stay installed while the functions are called -
hence the ``patched_modules`` context manager below.
"""
import contextlib
import os
import sys
import types
import unittest

MODS_GUI_COMPAT = os.environ.get('MODS_GUI_COMPAT', '')
CANDIDATES = [path for path in (
    MODS_GUI_COMPAT,
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'compat.py'),
    '/tmp/guiflash-ch4mpi/res/scripts/client/gui/mods/gambiter/compat.py',
) if path]


def find_compat():
    for path in CANDIDATES:
        if os.path.isfile(path):
            return path
    return None


COMPAT_PATH = find_compat()


class Recorder(object):
    """Stands in for the client view settings registry."""

    def __init__(self, alias_return='alias'):
        self.calls = []
        self.alias_return = alias_return

    def addSettings(self, settings):
        self.calls.append(('addSettings', settings))
        return self.alias_return

    def removeSettings(self, alias):
        self.calls.append(('removeSettings', alias))


def make_module(name, **attrs):
    module = types.ModuleType(name)
    for key, value in attrs.items():
        setattr(module, key, value)
    return module


@contextlib.contextmanager
def patched_modules(stubs):
    """Install stub modules, run the block, then restore sys.modules."""
    saved = dict(sys.modules)
    try:
        for name, module in stubs.items():
            sys.modules[name] = module
        yield
    finally:
        sys.modules.clear()
        sys.modules.update(saved)


def load_compat():
    """Execute compat.py in a fresh namespace (call it inside patched_modules)."""
    with open(COMPAT_PATH, 'rb') as handle:
        code = compile(handle.read(), COMPAT_PATH, 'exec')
    namespace = {}
    exec(code, namespace)
    return namespace


def framework_stubs(**framework_attrs):
    """Stub package chain gui.Scaleform.framework (+ optional registry)."""
    return {
        'gui': make_module('gui'),
        'gui.Scaleform': make_module('gui.Scaleform'),
        'gui.Scaleform.framework': make_module('gui.Scaleform.framework',
                                               **framework_attrs),
    }


def loader_stubs(registry, igui_loader, seen):
    """Stub helpers.dependency + skeletons.gui.impl for the WG branch."""
    def instance(cls):
        seen.append(cls)
        return make_module('loader', entitiesFactory=registry)

    stubs = framework_stubs()  # framework without g_entitiesFactories
    stubs.update({
        'helpers': make_module('helpers',
                               dependency=make_module('dependency',
                                                      instance=instance)),
        'skeletons': make_module('skeletons'),
        'skeletons.gui': make_module('skeletons.gui'),
        'skeletons.gui.impl': make_module('skeletons.gui.impl',
                                          IGuiLoader=igui_loader),
    })
    return stubs


@unittest.skipUnless(COMPAT_PATH is not None,
                     'compat.py not found; set MODS_GUI_COMPAT to its path')
class CompatTest(unittest.TestCase):

    def test_lesta_branch_uses_module_level_registry(self):
        registry = Recorder()
        stubs = framework_stubs(g_entitiesFactories=registry)
        with patched_modules(stubs):
            namespace = load_compat()
            self.assertIs(namespace['_moduleFactories'], registry)
            self.assertIs(namespace['getEntitiesFactories'](), registry)

            settings = object()
            self.assertEqual(namespace['addSettings'](settings), 'alias')
            namespace['removeSettings']('GUIFlash')
        self.assertEqual(registry.calls,
                         [('addSettings', settings),
                          ('removeSettings', 'GUIFlash')])

    def test_eu_branch_uses_gui_loader_service(self):
        registry = Recorder()
        seen = []

        class IGuiLoader(object):
            pass

        stubs = loader_stubs(registry, IGuiLoader, seen)
        with patched_modules(stubs):
            namespace = load_compat()
            self.assertIsNone(namespace['_moduleFactories'])
            self.assertIs(namespace['getEntitiesFactories'](), registry)
            self.assertEqual(seen, [IGuiLoader])

            settings = object()
            self.assertEqual(namespace['addSettings'](settings), 'alias')
            namespace['removeSettings']('ModSettingsAPIWindow_mods_gui')
        self.assertEqual(registry.calls,
                         [('addSettings', settings),
                          ('removeSettings', 'ModSettingsAPIWindow_mods_gui')])

    def test_exports_and_callables(self):
        registry = Recorder()
        stubs = loader_stubs(registry, object, [])
        with patched_modules(stubs):
            namespace = load_compat()
            for name in ('getEntitiesFactories', 'addSettings', 'removeSettings'):
                self.assertIn(name, namespace['__all__'])
                self.assertTrue(callable(namespace[name]))
            # addSettings/removeSettings return whatever the registry returns.
            self.assertEqual(namespace['addSettings'](object()), 'alias')
            self.assertIsNone(namespace['removeSettings']('alias'))


if __name__ == '__main__':
    unittest.main()
