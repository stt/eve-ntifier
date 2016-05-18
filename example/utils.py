from eve.io.base import DataLayer
from eve.methods.common import serialize
from eve.utils import config, auto_fields, str_to_date
import json


class ResultWrapper(list):
    def count(self, **kwargs):
        return len(self)


class JsonDataLayer(DataLayer):

    serializers = {
        'integer': lambda value: int(value) if value is not None else None,
        'float': lambda value: float(value) if value is not None else None,
        'number': lambda val: json.loads(val) if val is not None else None,
        'datetime': str_to_date
    }

    def _write(self):
        with open(self.datafile,'w+') as fh:
            fh.write(json.dumps(self.repo, default=str))
    def init_app(self, app):
        self.datafile = app.config.get('DUMMYDATA_FILE','data.json')
        try:
            with open(self.datafile,'r+') as fh:
                self.repo = json.loads(fh.read())
        except IOError, ValueError:
            self.repo = {}

        for m,v in app.config['DOMAIN'].items():
            if m not in self.repo:
                self.repo[m] = {}

    def combine_queries(self, query_a, query_b):
        z = query_a.copy()
        z.update(query_b)
        return z

    def _find(self, resource, req, **lookup):
        spec = {}
        sort = []
        """
        if req:
          if req.where:
            spec = json.loads(req.where)
          if req.sort:
              for sort_arg in [s.strip() for s in req.sort.split(",")]:
                  sn = sort_arg[1:] if sort_arg[0] == "-" else sort_arg
                  try:
                      if sort_arg[0] == "-":
                          sort.append(getattr(model, sn).desc())
                      else:
                          sort.append(getattr(model, sn))
                  except AttributeError:
                      abort(400, description='Unknown field name: %s' % sn)

        """
        if 'lookup' in lookup and lookup['lookup']:
            spec = self.combine_queries(
                spec, lookup['lookup'])
            spec = lookup['lookup']

        client_projection = self._client_projection(req)

        datasource, spec, projection, sort = self._datasource_ex(
            resource,
            spec,
            client_projection,
            sort)

        if len(spec) == 0:
            return self.repo[resource].values()

        # id from query is str, in repo it's int
        spec = serialize(spec, resource)
        spec = set(spec.items())

        rs = []

        for id,r in self.repo[resource].items():
            ok = len(set(r.items()) & spec) == len(spec)
            if ok: rs.append(r.copy())

        return rs


    def find_one(self, resource, req, **lookup):
        rs = self._find(resource, req, lookup=lookup)
        print lookup, rs
        return None if len(rs) < 1 else rs[0]

    def find(self, resource, req, sub_resource_lookup):
        return ResultWrapper(self._find(resource, req, lookup=sub_resource_lookup))

    def insert(self, resource, doc_or_docs):
        #if isinstance(doc_or_docs, list): TODO
        # if upsert..
        ids = []
        for doc in doc_or_docs:
            keys = self.repo[resource].keys()
            id = 1 if len(keys) == 0 else int(max(keys))+1
            for f in auto_fields(resource):
                if f in doc: del doc[f]
            doc[config.ID_FIELD] = id
            self.repo[resource][id] = doc
            ids.append(id)
        self._write()
        return ids

    def update(self, resource, id_, updates, original):
        self.replace(resource, id_, updates, original)

    def replace(self, resource, id_, updates, original):
        d = {getattr(doc_or_docs, config.ID_FIELD): doc_or_docs}
        self.repo[resource].update(doc_or_docs)
        self._write()

    def remove(self, resource, lookup):
        rs = self._find(resource, None, lookup=lookup)
        for rec in rs:
            del self.repo[resource][rec[config.ID_FIELD]]
        self._write()

