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


class HessianWrapper(object):
    """Wraps an object to enable it to accept Hessian calls."""
    def __init__(self, obj):
        """Create a HessianWrapper for the provided object.

        Note that only methods decorated with @exposed will
        be exposed by this wrapper.

        obj:
            The object to be exposed via Hessian.
        """
        self.functions = {}
        for i in dir(obj):
            func = getattr(obj, i)
            if callable(func) and hasattr(func, '_hessian_exposed') and func._hessian_exposed:
                self.functions[i] = func

    def call(self, hessian_data):
        """Receive Hessian call data, call the appropriate function and return result.

        hessian_data:
            Hessian binary call data.
        """
        try:
            call = parser.Parser().parse_string(hessian_data)
            func = self.functions[call.method]
            result = func(*call.args)
        except parser.ParseError, e:
            result = protocol.Fault('ProtocolException', str(e), '')
        except KeyError:
            result = protocol.Fault('NoSuchMethodException', 'The requested method "{0}" does not exist.'.format(call.method), '')
        except Exception, e:
            result = protocol.Fault('ServiceException', str(e), '')
        return encode_reply(result)


class WsgiApp(object):
    """The Hessian server wsgi application."""

    def __init__(self, obj):
        """Create a wsgi application which passes Hessian
        calls to a server object.

        obj:
            The object to be exposed via Hessian
        """
        self.wrapper = HessianWrapper(obj)

    def __call__(self, environ, start_response):
        """Standard wsgi function."""
        try:
            post_data = environ['wsgi.input'].read(int(environ.get('CONTENT_LENGTH', '0')))
            response = self.wrapper.call(post_data)
        except Exception, e:
            fault = protocol.Fault('ServiceException', str(e), '')
            response = encode_reply(fault)
        start_response(STATUS, HEADERS)
        return [response]
