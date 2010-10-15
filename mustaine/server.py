#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mustaine import parser, encoder, protocol


STATUS = '200 OK'
HEADERS = [('Content-Type', 'application/x-hessian; charset=utf-8'), ]


def exposed(func):
    """Mark a function as exposed i.e. visible via Hessian."""
    func._hessian_exposed = True
    return func


def encode_reply(reply):
    """Encode a Python object as a Hessain reply."""
    return encoder.encode_reply(protocol.Reply(reply))[1]


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
            if callable(func) and hasattr(func, '_hessian_exposed') and func._hessian_exposed:
                self.functions[i] = func

    def __call__(self, environ, start_response):
        """Standard wsgi function."""
        try:
            post_data = environ['wsgi.input'].read(int(environ.get('CONTENT_LENGTH', '0')))
            response = self.hessian_call(post_data)
        except Exception, e:
            fault = protocol.Fault('ServiceException', e.message, '')
            response = encode_reply(fault)
        start_response(STATUS, HEADERS)
        return [response]

    def hessian_call(self, post_data):
        """Receive Hessian POST data and call the appropriate function."""
        try:
            call = parser.Parser().parse_string(post_data)
            func = self.functions[call.method]
            result = func(*call.args)
        except parser.ParseError, e:
            result = protocol.Fault('ProtocolException', e.message, '')
        except KeyError:
            result = protocol.Fault('NoSuchMethodException', 'The requested method "{0}" does not exist.'.format(call.method), '')
        except Exception, e:
            result = protocol.Fault('ServiceException', e.message, '')
        return encode_reply(result)
