# -*- coding: utf-8 -*-
import ast
import os
import sys
import unittest


class Stub(object):
    def __init__(self, **values):
        self.__dict__.update(values)


class Event(object):
    def __init__(self, key=42, down=True):
        self.key = key
        self.down = down

    def isKeyDown(self):
        return self.down

    def isAltDown(self):
        return True

    def isShiftDown(self):
        return False

    def isCtrlDown(self):
        return True


class Server(object):
    def __init__(self, address, handler):
        self.address = address
        self.handler = handler
        self.served = False

    def serve_forever(self):
        self.served = True


class Thread(object):
    def __init__(self, target):
        self.target = target
        self.daemon = False
        self.starts = 0

    def start(self):
        self.starts += 1
        # No real thread or network activity.


def load_hooks():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        '..', 'source', 'mod_mods_gui.py')
    with open(path, 'rb') as source:
        tree = ast.parse(source.read(), filename=path)
    # The removed P0 block also carried a shooting hook; the surviving
    # module-level hook functions are exactly these two.
    names = ('p__WebBrowser_handleKeyEvent', 'p__startServer')
    functions = [node for node in tree.body
                 if isinstance(node, ast.FunctionDef) and node.name in names]
    if sorted(node.name for node in functions) != sorted(names):
        raise AssertionError('Expected exactly the two hook functions')
    # AST only: never import the mod or execute its patches/taskkill code.
    for node in functions:
        node.decorator_list = []
    code = compile(ast.fix_missing_locations(ast.Module(body=functions)),
                   path, 'exec')
    namespace = {}
    exec(code, namespace)
    return namespace


class HooksTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if sys.version_info[:3] != (2, 7, 18):
            raise AssertionError('These tests require exactly Python 2.7.18; '
                                 'got %s' % (sys.version_info[:3],))
        cls.hooks = load_hooks()

    def setUp(self):
        self.ns = self.hooks
        self.calls = []

    def check_key(self, listening, event, result, captured):
        handler = Stub(p__listeningKeys=listening, p__lastKeyPressed=None)
        self.ns['p__SettingsHTTPRequestHandler'] = handler
        self.ns['p__Keys'] = Stub(KEY_LCONTROL=1, KEY_RCONTROL=2,
                                 KEY_LALT=3, KEY_RALT=4,
                                 KEY_LSHIFT=5, KEY_RSHIFT=6)

        def original(owner, e):
            self.calls.append((owner, e))
            return result

        self.ns['p__oldWebBrowser_handleKeyEvent'] = original
        owner = object()
        self.calls[:] = []
        self.assertIs(self.ns['p__WebBrowser_handleKeyEvent'](owner, event),
                      result)
        self.assertEqual(self.calls, [(owner, event)])
        self.assertEqual(handler.p__lastKeyPressed, captured)
        self.assertEqual(handler.p__listeningKeys,
                         False if captured is not None else listening)

    def test_key_return_and_normal_forwarding(self):
        for result in (True, False):
            self.check_key(False, Event(), result, None)
            self.check_key(True, Event(down=False), result, None)
            for key in range(1, 7):
                self.check_key(True, Event(key=key), result, None)

    def test_listening_captures_key_and_preserves_return(self):
        for result in (True, False):
            self.check_key(True, Event(), result,
                           (42, True, True, False, True))

    def test_server_binds_loopback_and_starts_only_once(self):
        servers = []
        threads = []

        def make_server(address, handler):
            server = Server(address, handler)
            servers.append(server)
            return server

        def make_thread(target):
            thread = Thread(target)
            threads.append(thread)
            return thread

        handler = object()
        self.ns.update({'p__server': None,
                        'p__SettingsHTTPRequestHandler': handler,
                        'ThreadingHTTPServer': make_server,
                        'threading': Stub(Thread=make_thread)})
        start = self.ns['p__startServer']
        start()
        self.assertEqual(len(servers), 1)
        self.assertEqual(len(threads), 1)
        server = servers[0]
        thread = threads[0]
        self.assertEqual(server.address, ('127.0.0.1', 31338))
        self.assertIs(server.handler, handler)
        self.assertIs(self.ns['p__server'], server)
        self.assertEqual(thread.target, server.serve_forever)
        self.assertIs(thread.daemon, True)
        self.assertEqual(thread.starts, 1)
        self.assertFalse(server.served)
        start()
        self.assertEqual(len(servers), 1)
        self.assertEqual(len(threads), 1)
        self.assertEqual(thread.starts, 1)
        self.assertIs(self.ns['p__server'], server)


if __name__ == '__main__':
    unittest.main()
