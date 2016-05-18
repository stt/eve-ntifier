from flask import current_app as app
from multiprocessing.dummy import Pool
import collections
import urllib2
import logging
import string
import json
import sys
from httphandler import DefaultHTTPHandler

logger = logging.getLogger(__name__)


class DefaultFormatter(string.Formatter):
    def __init__(self, default='{{{0}}}'):
        self.default=default

    def get_value(self, key, args, kwds):
        try:
            if isinstance(key, str):
                return kwds.get(key, self.default.format(key))
            else:
                # there was a bug in PEP3101?
                return string.Formatter.get_value(self, key, args, kwds)
        except KeyError as e:
            logger.warn("%s: %s" % (type(e), e))


# defaults you are welcome to override
_resname = '_eventhooks'
_res = {
  'schema': {
    'resource': {'type':'string'},
    'method': {'type':'string'}, # GET/POST
    'url': {'type':'string'}
  }
}
_events = ['inserted','replaced','updated','deleted_item']
_formatter = DefaultFormatter()
_async = True
_pool = Pool()
_http = DefaultHTTPHandler()
_event_cache = []


def event_request(res, data):
    url = _formatter.format(res['url'], **data)
    if res.get('method') == 'POST':
        args = {
          'data': json.dumps(data, default=str),
          'headers': {'Content-type': 'application/json'}
        }
        request(url, **args)
    else:
        request(url)


def request(url, **args):
    """Called to send a resource event request
    If you want to add headers/auth etc look into _http
    but override this function if you want something more exotic
    """
    try:
        logger.debug('requesting %s', url)
        res = _http.request(url, **args)
        logger.debug('response: %s', res)
    except Exception as e:
        logger.error('while requesting %s : %s', url, e)


def get_eventhooks():
    global _event_cache
    # fyi: can't call this in init(), datalayer is properly usable only
    # after flask run(), config object is not really valid before
    if len(_event_cache) == 0:
        _event_cache = app.data.find(_resname, {}, {})
    return _event_cache


def register_handler(event):

    def handle(resource, data, **args):
        global _event_cache
        if resource == _resname:
            _event_cache = []
        rs = filter(lambda r: r['resource']==resource, get_eventhooks())
        if not rs: return

        for d in data:
            d['_resource'] = resource
            d['_event'] = event

            for rec in rs:
                if _async:
                    _pool.apply(event_request, args=(rec, d))
                else:
                    event_request(rec, d)

    return handle


def init(app):
    app.config['DOMAIN'][_resname] = _res
    app.register_resource(_resname, _res)

    for ev in _events:
        getattr(app, 'on_'+ev).__iadd__(register_handler(ev))

