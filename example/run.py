import logging
import sys
import os

from eve import Eve
import utils
import eve_ntifier


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Eve(data=utils.JsonDataLayer)

# ID_FIELD defaults to objectid which our JsonDataLayer doesn't support
_id = app.config['ID_FIELD']
eve_ntifier._res['schema'][_id] = {'type': 'integer'}

eve_ntifier.init(app)

logger.info("registered paths: %s", app.url_map)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 9000))
    host = '127.0.0.1'
    app.run(host=host, port=port, debug=True)

