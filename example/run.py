import logging
import sys
import os

from eve import Eve
import utils
import eve_ntifier


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Eve(data=utils.DummyDataLayer)

eve_ntifier.register_events(app)

logger.info("registered paths: %s", app.url_map)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 9000))
    host = '127.0.0.1'
    app.run(host=host, port=port, debug=True)

