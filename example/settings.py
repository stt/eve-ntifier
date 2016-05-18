URL_PREFIX = 'api'

RESOURCE_METHODS = ['GET', 'POST', 'DELETE']
ITEM_METHODS = ['GET', 'PATCH', 'DELETE', 'PUT']
ITEM_URL = 'regex("[a-f0-9]+")'

DOMAIN = {
  'images': {
    'schema': {
      '_id': {
        'type': 'integer'
      },
      'name': {
        'type': 'string'
      },
    }
  }
}

