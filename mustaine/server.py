#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mustaine import parser, encoder, protocol
from wsgiref import simple_server


def exposed(func):
    """Mark a function as exposed i.e. visible via Hessian."""
    func._hessian_exposed = True
    return func


class WsgiApp(object):
    """The Hessian server wsgi application."""

    def __init__(self, obj):
        """ Create a wsgi application which passes Hessian
        calls to a server object.

        obj:
            The object to be exposed via Hessian
        """
        self.functions = {}
        for i in dir(obj):
            func = getattr(obj, i)
            if not callable(func) or not hasattr(func, '_hessian_exposed') or not func._hessian_exposed:
                continue
            self.functions[i] = func

    def __call__(self, environ, start_response):
        """Standard wsgi function."""
        post_data = environ['wsgi.input'].read(int(environ.get('CONTENT_LENGTH', '0')))
        response = self.hessian_call(post_data)
        status = '200 OK'
        headers = [('Content-Type', 'application/x-hessian; charset=utf-8'), ]
        start_response(status, headers)
        return [response]

    def hessian_call(self, post_data):
        """Receive Hessian POST data and calls the appropriate function."""
        call = parser.Parser().parse_string(post_data)
        func = self.functions[call.method]
        result = func(*call.args)
        return encoder.encode_reply(protocol.Reply(result))[1]


class Calculator(object):

    @exposed
    def add(self, a, b):
        return a + b

if __name__ == '__main__':
    s = simple_server.make_server('', 8080, WsgiApp(Calculator()))
    s.serve_forever()
