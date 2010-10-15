#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
# Use local mustaine
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest

from mustaine.server import exposed, WsgiApp


class Calculator(object):
    """Test Hessian server object."""

    @exposed
    def add(self, a, b):
        return a + b

    @exposed
    def bad(self, a, b):
        return 1 / 0

    def hid(self, a, b):
        return a + b


class TestServer(unittest.TestCase):

    def setUp(self):
        self.wsgi_app = WsgiApp(Calculator())

    def test_reply(self):
        call = 'c\x01\x00m\x00\x03addI\x00\x00\x00\x05I\x00\x00\x00\x03z'  # call=add(5, 3)
        result = self.wsgi_app.hessian_call(call)
        self.assertEqual('r\x01\x00I\x00\x00\x00\x08z', result)   # reply=8

    def test_exposed(self):
        call = 'c\x01\x00m\x00\x03hidI\x00\x00\x00\x05I\x00\x00\x00\x03z'  # call=hid(5, 3)
        result = self.wsgi_app.hessian_call(call)
        fault = 'r\x01\x00f' \
                'S\x00\x04codeS\x00\x15NoSuchMethodException' \
                'S\x00\x07messageS\x00*The requested method "hid" does not exist.' \
                'S\x00\x06detailS\x00\x00zz'
        self.assertEqual(fault, result)   # reply=Fault

    def test_no_method(self):
        call = 'c\x01\x00m\x00\x03fooI\x00\x00\x00\x05I\x00\x00\x00\x03z'  # call=foo(5, 3)
        result = self.wsgi_app.hessian_call(call)
        fault = 'r\x01\x00f' \
                'S\x00\x04codeS\x00\x15NoSuchMethodException' \
                'S\x00\x07messageS\x00*The requested method "foo" does not exist.' \
                'S\x00\x06detailS\x00\x00zz'
        self.assertEqual(fault, result)   # reply=Fault
        
    def test_parse_error(self):
        call = ''  # call=<malformed>
        result = self.wsgi_app.hessian_call(call)
        fault = 'r\x01\x00f' \
                'S\x00\x04codeS\x00\x11ProtocolException' \
                'S\x00\x07messageS\x00$Encountered unexpected end of stream' \
                'S\x00\x06detailS\x00\x00zz'
        self.assertEqual(fault, result)   # reply=Fault
        
    def test_service_exception(self):
        call = 'c\x01\x00m\x00\x03badI\x00\x00\x00\x05I\x00\x00\x00\x03z'  # call=bad(5, 3)
        result = self.wsgi_app.hessian_call(call)
        fault = 'r\x01\x00fS\x00\x04code' \
                'S\x00\x10ServiceExceptionS\x00\x07message' \
                'S\x00"integer division or modulo by zero' \
                'S\x00\x06detailS\x00\x00zz'
        self.assertEqual(fault, result)   # reply=Fault


if __name__ == '__main__':
    unittest.main()
