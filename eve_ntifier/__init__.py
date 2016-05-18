from flask import current_app as app
import logging
import string
import sys
try:
    # py3
    import urllib.request as urlrequest
except ImportError:
    # py2
    import urllib as urlrequest

logger = logging.getLogger(__name__)


class Formatter(string.Formatter):
    def __init__(self, default='{{{0}}}'):
        self.default=default

    def get_value(self, key, args, kwds):
        try:
            if isinstance(key, str):
                return kwds.get(key, self.default.format(key))
            else:
                # there was a bug in PEP3101?
                return super(Formatter, self).get_value(key, args, kwds)
        except KeyError as e:
            logger.warn(str(e))


# defaults you are welcome to override
_resname = '_eventhooks'
_events = ['inserted','replaced','updated','deleted_item']
_formatter = Formatter()


def init_events(d):
    d[_resname] = {
      'schema': {
        'resource': {'type':'string'},
        'url': {'type':'string'}
      }
    }


def request(url):
    logger.debug('requesting %s', url)
    res = urlrequest.urlopen(url)
    logger.debug('response: %s', res.read())


def register_handler(event):

    def handle(resource, data, **args):
        lookup = {'resource': resource}
        rec = app.data.find_one(_resname, {}, lookup=lookup)
        if not rec: return

        for d in data:
            d['_resource'] = resource
            d['_event'] = event
            url = _formatter.format(rec['url'], **d)
            request(url)

    return handle


def register_events(app):
    for ev in _events:
        getattr(app, 'on_'+ev).__iadd__(register_handler(ev))

