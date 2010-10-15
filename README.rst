About
-----

Mustaine is a Python implemention of the `Hessian 1.0.2 specification
<http://hessian.caucho.com/doc/hessian-1.0-spec.xtp>`_, a binary web services
protocol. The library currently provides a standard HTTP-based client as well
as a general-purpose serialization library. Server support is planned.

Usage
-----

Using `mustaine.client`
+++++++++++++++++++++++

Testing against `Caucho <http://hessian.caucho.com/>`_'s reference service::

  from mustaine.client import HessianProxy
  service = HessianProxy("http://hessian.caucho.com/test/test")
  print service.replyDate_1()

Using `mustaine.server`
+++++++++++++++++++++++

An object can be served via WSGI by wrapping it with the provided
mustaine.server.WsgiApp.  An object's methods are only exposed
if decorated with mustaine.server.exposed decorator.  For example::

  from mustaine.server import exposed

  class Calculator(object):
      @exposed
      def add(self, a, b):
          return a + b

      @exposed
      def subtract(self, a, b):
          return a - b

The following code will serve a Calculator object on port 8080 using the
Python reference WSGI server::

  from wsgiref import simple_server
  from mustaine.server import WsgiApp
  s = simple_server.make_server('', 8080, WsgiApp(Calculator()))
  s.serve_forever()

This object can now be accessed over the network as already described::

  >>> from mustaine.client import HessianProxy
  >>> h = HessianProxy('http://localhost:8080/')
  >>> h.add(2, 3)
  5

Source
------

Up-to-date sources and documentation can always be found at the `mustaine
GitHub site <http://github.com/bgilmore/mustaine>`_.
