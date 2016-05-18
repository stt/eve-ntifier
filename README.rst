eve-ntifier
===========

Adds a resource (_eventhooks by default) where you can insert URLs to be called when a given resource is changed. The URL can have template keywords surrounded by curlybraces that will be filled in with data from the changed record.


Usage
-----

.. code-block:: python

    from eve import Eve
    import eve_ntifier

    app = Eve()
    eve_ntifier.init(app)


Example
-------

.. code:: console

    $ echo -e "HTTP/1.1 200 OK\r\n\r\nHello" | nc -l 1234 >out.txt &
    $ PYTHONPATH=. python example/run.py &

    $ curl -F resource=images -F "url=http://localhost:1234/event/{_resource}/{_event}/{name}" localhost:9000/api/_eventhooks
    INFO:werkzeug:127.0.0.1 - - [18/May/2016 11:54:48] "POST /api/_eventhooks HTTP/1.1" 201 -
    {"_updated": "Thu, 01 Jan 1970 00:00:00 GMT", "_links": {"self": {"href": "_eventhooks/1", "title": "_eventhook"}}, "_created": "Thu, 01 Jan 1970 00:00:00 GMT", "_status": "OK", "_id": "1", "_etag": "b0e30153c7df89c34f6a11fa58b04c8a59dff456"}

    $ curl -F name=test2.jpg localhost:9000/api/images
    DEBUG:eve_ntifier:requesting http://localhost:1234/event/images/inserted/test2.jpg
    DEBUG:eve_ntifier:response: Hello
    INFO:werkzeug:127.0.0.1 - - [18/May/2016 11:58:13] "POST /api/images HTTP/1.1" 201 -
    {"_updated": "Thu, 01 Jan 1970 00:00:00 GMT", "_links": {"self": {"href": "images/1", "title": "Image"}}, "_created": "Thu, 01 Jan 1970 00:00:00 GMT", "_status": "OK", "_id": 1, "_etag": "71980304104c6837203498dd8ad984c30138c1d8"}

    $ cat out.txt
    GET /event/images/inserted/test2.jpg HTTP/1.0
    Host: localhost:1234
    User-Agent: Python-urllib/1.17


Trivia
------

* Eve events are registered for all known resources at launch
* hooks are cached in memory and matched to events as they happen
* unresolvable template variable gets value "None" and warning is logged
* http errors are logged
* cache is refreshed when hooks are changed via Eve

.. code:: console

    $ curl -F resource=_eventhooks -F method=POST -F "url=http://localhost:1234/ev/{_resource}/{_event}/{name}" localhost:9000/api/_eventhooks
    WARNING:eve_ntifier:<type 'exceptions.KeyError'>: u'name'
    DEBUG:eve_ntifier:requesting http://localhost:1234/ev/_eventhooks/inserted/None
    ERROR:eve_ntifier:while requesting http://localhost:1234/ev/_eventhooks/inserted/None : <HTTPHandlerError 111, Connection refused>
    INFO:werkzeug:127.0.0.1 - - [19/May/2016 00:12:01] "POST /api/_eventhooks HTTP/1.1" 201 -
    {"_updated": "Thu, 01 Jan 1970 00:00:00 GMT", "_links": {"self": {"href": "_eventhooks/1", "title": "_eventhook"}}, "_created": "Thu, 01 Jan 1970 00:00:00 GMT", "_status": "OK", "_id": 1, "_etag": "39adfe6fc04411791d1ffcae485d6346ade6cd22"}

    # w/ `nc -l 1234 >out.txt &` the above event produces this request
    $ cat out.txt
    POST /ev/_eventhooks/inserted/None HTTP/1.1
    Accept-Encoding: identity
    Content-Length: 378
    Host: localhost:1234
    Content-Type: application/json
    Connection: close
    User-Agent: Python-urllib/2.7

    {"_updated": "1970-01-01 00:00:00", "resource": "_eventhooks", "_resource": "_eventhooks", "url": "http://localhost:1234/ev/{_resource}/{_event}/{name}", "_event": "inserted", "method": "POST", "_links": {"self": {"href": "_eventhooks/5", "title": "_eventhook"}}, "_created": "1970-01-01 00:00:00", "_status": "OK", "_id": 5, "_etag": "8bfc014ce3dc39af3eb8688d2b845ca5977f0371"}
