"""
  flask.ext.funktional
  ~~~~~~~~~~~~~~~~~~~~

  flask extension which hopes to make functional testing easier.


  :copyright: (c) 2013 by gregorynicholas.
  :license: MIT, see LICENSE for more details.
"""
from __future__ import unicode_literals
from flask import Flask, templating, testing
from flask import url_for as _url_for
from flask.testsuite import FlaskTestCase
from io import BytesIO
from json import loads
from werkzeug import cached_property

__version__ = "0.0.1"

__all__ = [
  "TestCase", "random_string",
  # signal events defined in this module
  "signals_available", "pre_setup_signal", "post_teardown_signal",
  # file upload helpers
  "UploadTestCase", "UploadRequest", "UploadFlaskClient",
  "httpfile", "temphttpfile",
]


try:
  import blinker
  from blinker import Namespace
  from flask import template_rendered
  signals_available = True
except ImportError:
  signals_available = False


# setup module namespace for signals.
if signals_available:
  _signals = Namespace()
  pre_setup_signal = _signals.signal("pre-setup-hook")
  post_teardown_signal = _signals.signal("post-teardown-hook")


class ContextVariableDoesNotExist(Exception):
    pass


class JsonResponseMixin:
  """
  mixin to help with testing json data in responses.
  """
  @cached_property
  def json(self):
    return loads(self.data)


class HttpAssertionsMixin(object):

  def assertStatus(self, response, status_code):
    """
    Helper method to check matching response status.

      :param response: Flask response
      :param status_code: response status code (e.g. 200)
    """
    self.assertIsNotNone(response, 'response is None')
    self.assertIsInstance(response.status_code, int,
      'response status_code is not an int.')
    self.assertEqual(response.status_code, status_code,
      'response status code {} is not {}'.format(
        response.status_code, status_code))
  assert_status = assertStatus

  def assert200(self, response):
    """
    Checks if response status code is 200

      :param response: Flask response
    """
    self.assertStatus(response, 200)
  assert_200 = assert200

  def assert302(self, response):
    """
    Checks if response status code is 302 (redirect)

      :param response: Flask response
    """
    self.assertStatus(response, 302)
  assert_302 = assert302

  def assert400(self, response):
    """
    Checks if response status code is 400

      :param response: Flask response
    """
    self.assertStatus(response, 400)
  assert_400 = assert400

  def assert401(self, response):
    """
    Checks if response status code is 401

      :param response: Flask response
    """
    self.assertStatus(response, 401)
  assert_401 = assert401

  def assert403(self, response):
    """
    Checks if response status code is 403

      :param response: Flask response
    """
    self.assertStatus(response, 403)
  assert_403 = assert403

  def assert404(self, response):
    """
    Checks if response status code is 404

      :param response: Flask response
    """
    self.assertStatus(response, 404)
  assert_404 = assert404

  def assert405(self, response):
    """
    Checks if response status code is 405

      :param response: Flask response
    """
    self.assertStatus(response, 405)
  assert_405 = assert405


def _patched_render(template, context, app):
  """
  used to monkey patch the `flask.render_template` method when the
  `render_templates` property is set to False in the TestCase
  """
  if signals_available:
    template_rendered.send(
      app, template=template, context=context)
  return ""


class TestCase(FlaskTestCase, HttpAssertionsMixin):
  """
  base testcase class. provides a number of helpers for functional & end-to-end
  testing of flask applications.

  while the class aims to be as unintrusive as possible, it also provides two
  different styles for "hooking" into setup + teardown events, through signals
  and through callable attributes defined on the subclasses.

  the only requirement of sublcasses is to define an attribute for `flaskapp` -
  which can be a property, or callable method. again, aim is for unintrusive.
  """

  def flaskapp(self):
    """
    return your flask app here, configure anyway you need.
    """
    raise NotImplementedError

  # setup + teardown..
  # ---------------------------------------------------------------------------

  def __call__(self, result=None):
    """
    intitializes the class setup. doing setup here means subclasses don't have
    to call `super.setup()`.
    """
    self.rendered_templates = []
    self.render_templates = True
    if signals_available:
      pre_setup_signal.send(self)
    try:
      self._pre_setup()
      FlaskTestCase.__call__(self, result)
    finally:
      self._post_teardown()
    if signals_available:
      post_teardown_signal.send(self)

  def _pre_setup(self):
    """
    sets-up the testcase class.
    """
    if hasattr(self, "setup_pre_hook"):
      self.setup_pre_hook()

    self.app = self._ctx = None
    if isinstance(self.flaskapp, Flask):
      self.app = self.flaskapp
    elif callable(self.flaskapp):
      self.app = self.flaskapp()
    else:
      self.app = self.flaskapp

    self._orig_response_class = self.app.response_class
    self.app.response_class = self._make_response_cls(
      self.app.response_class)

    if hasattr(self, "test_client_class"):
      self.app.test_client_class = self.test_client_class
    self.client = self.app.test_client()
    # self._ctx = self.app.test_request_context()
    # self._ctx.push()

    # if the subclass sets the render_templates value to False,
    # then monkey patch..
    if not self.render_templates:
      self._monkey_patch_render_template()

    if signals_available:
      template_rendered.connect(self._on_template_render)

    if hasattr(self, "setup_post_hook"):
      self.setup_post_hook()

  def _post_teardown(self):
    """
    tears-down the testcase class.
    """
    if hasattr(self, "teardown_pre_hook"):
      self.teardown_pre_hook()

    if self._ctx is not None:
      # self._ctx.pop()
      pass
    if self.app is not None:
      self.app.response_class = self._orig_response_class

    if signals_available:
      template_rendered.disconnect(self._on_template_render)

    if hasattr(self, "_true_render"):
      templating._render = self._true_render

    if hasattr(self, "teardown_post_hook"):
      self.teardown_post_hook()

  # helpers..
  # ---------------------------------------------------------------------------

  def _make_response_cls(self, response_class):
    """
    this monkey's the response class for the flask application to mixin
    additional convenience.
    """
    class TestResponse(response_class, JsonResponseMixin):
      pass
    return TestResponse

  # http assertions + helpers..
  # ---------------------------------------------------------------------------

  def url_for(self, handler, **kw):
    """
    hopes to avoid test code from ever having to statically define url's
    to internal flask routes.

      :param handler: string path to the route handler. ex: app.module.route1
    """
    with self.app.test_request_context():
      url = _url_for(handler, **kw)
      server_name = self.app.config.get("SERVER_NAME")
      if server_name is None:
        return url
      else:
        pre, name, path = url.partition(server_name)
        if len(path) is 0:
          return None, pre
        return pre + name, path

  def get(self, handler, url_args={}, *args, **kw):
    return self.open(
      handler, url_args, method='GET', *args, **kw)

  def open(self, handler, handler_args, *args, **kw):
    base_url, url = self.url_for(handler, **handler_args)
    follow_redirects = kw.pop("follow_redirects", True)
    return self.client.open(
      url, follow_redirects=follow_redirects, base_url=base_url, *args, **kw)

  # template patching + assertions + helpers..
  # ---------------------------------------------------------------------------

  def _on_template_render(self, app, template, context):
    """
    binds to the signal sent in flask.templating
    """
    self.rendered_templates.append((template, context))

  def _monkey_patch_render_template(self):
    self._true_render = templating._render
    templating._render = _patched_render

  def assertTemplateRendered(self, name):
    """
    checks if a given template is rendered in the request. only works if your
    version of flask has signals support (0.6+) and blinker is installed.

      :param name: string name of the template.
    """
    if not signals_available:
      raise RuntimeError("Signals not supported")
    for template, context in self.rendered_templates:
      if template.name == name:
        return True
    raise AssertionError("template %s not rendered".format(name))
  assert_template_Rendered = assertTemplateRendered

  def get_template_context(self, name):
    """
    returns a variable from the context passed to the
    template. only works if your version of flask
    has signals support (0.6+) and blinker is installed.

    raises a contextvariabledoesnotexist exception if does
    not exist in context.

      :param name: name of variable
    """
    if not signals_available:
      raise RuntimeError("Signals not supported")
    for template, context in self.rendered_templates:
      if name in context:
        return context[name]
    raise ContextVariableDoesNotExist

  def assertTemplateContext(self, name, value):
    """
    checks if given name exists in the template context
    and equals the given value.

      :param name: name of context variable
      :param value: value to check against
    """
    try:
      self.assertEqual(self.get_template_context(name), value)
    except ContextVariableDoesNotExist:
      self.fail("Context variable does not exist: %s" % name)
  assert_template_context = assertTemplateContext


# file upload testing..
# ---------------------------------------------------------------------------

from random import choice
from string import letters, digits
from StringIO import StringIO
from flask import Request


class UploadFlaskClient(testing.FlaskClient):
  """
  `flask.testing.FlaskClient` subclass which provides an uplooad method to
  post data to an application.
  """

  def upload(self, handler, *uploads, **kw):
    """
      :param handler:
      :param uploads: tuple of (formname, filepath)
      :param headers:
    """
    headers = {"enctype": "multipart/form-data"}
    headers.update(kw.pop("headers", {}))
    data = {}

    for upload in uploads:
      bytes, name, _ = httpfile(filename=upload(1))
      data[upload(0)] = (bytes, name)

    return self.open(
      handler, handler_args=kw, data=data, headers=headers)


class UploadRequest(Request):
  """
  overrides the `_get_file_stream` method return an instance of `FileUploadIO`
  """
  def _get_file_stream(*args, **kwargs):
    return FileUploadIO()


class FileUploadIO(StringIO):
  type_options = {}

  def close(self):
    """
    overriden to do nothing.
    """


class UploadTestCase(TestCase):
  """
  `TestCase` subclass which
  """
  test_client_class = UploadFlaskClient

  def setup_pre_hook(self):
    self._app.request_class = self.app.request_class
    self.app.request_class = UploadRequest

  def teardown_post_hook(self):
    self.app.request_class = self._app_request_class


def httpfile(path):
  """
  open a file as a StringIO object to use with a flask test client.

    :param path: string path to a file

    :returns: tuple for bytes, filename, size
  """
  with open(path, "r") as f:
    data = f.read()
    size = len(data)
  return (StringIO(data), path, size)


def temphttpfile(filename=None, data=None, size=None):
  """
  create an on-the-fly StringIO object to use with a flask test client.

    :param data: string of the filename
    :param filename: optional string of the filename
    :param size: if data is None, generates data of the specified size

    :returns: tuple for bytes, filename, size
  """
  if data is None and size:
    data = random_string(size)
  return (BytesIO(data), filename, len(data))


def random_string(size):
  return "".join([choice(letters + digits) for _ in range(size)])
