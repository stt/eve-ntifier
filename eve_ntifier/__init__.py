from flask import current_app as app
from multiprocessing.dummy import Pool
import collections
import urllib2
import logging
import string
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
            logger.warn(str(e))


# defaults you are welcome to override
_resname = '_eventhooks'
_res = {
  'schema': {
    'resource': {'type':'string'},
    'url': {'type':'string'}
  }
}
_events = ['inserted','replaced','updated','deleted_item']
_formatter = DefaultFormatter()
_async = False
_pool = Pool()
_http = DefaultHTTPHandler()


def merge(d, u):
    "merges two dicts recursively to avoid overwriting"
    for k, v in u.iteritems():
        if isinstance(v, collections.Mapping):
            r = merge(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d


def request(url):
    try:
        logger.debug('requesting %s', url)
        res = _http.request(url)
        logger.debug('response: %s', res)
    except Exception as e:
        logger.error('while requesting %s : %s', url, e)


def register_handler(event):

    def handle(resource, data, **args):
        lookup = {'resource': resource}
        
        rs = app.data.find(_resname, {}, lookup)
        if not rs: return

        for d in data:
            d['_resource'] = resource
            d['_event'] = event

            for rec in rs:
                url = _formatter.format(rec['url'], **d)
                if _async:
                    _pool.apply(request, args=(url,))
                else:
                    request(url)

    return handle


def init(app):
    app.config = merge(app.config, {'DOMAIN': {_resname: _res}})
    app.set_defaults()

    for ev in _events:
        getattr(app, 'on_'+ev).__iadd__(register_handler(ev))

