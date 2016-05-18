from eve.io.base import DataLayer
from eve.utils import config, auto_fields
import json


class ResultWrapper(list):
    def count(self, **kwargs):
        return len(self)


class DummyDataLayer(DataLayer):
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

    def _find(self, resource, req, **lookup):
        """
        spec = {}
        sort = []
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
        """
        if not 'lookup' in lookup: return None

        rs = []

        for k,v in lookup['lookup'].items():
            if k == config.ID_FIELD and k in self.repo[resource]:
                return self.repo[resource][v]
            else:
                for id,r in self.repo[resource].items():
                    if r[k] == v:
                        rs.append(r)
        return rs


    def find_one(self, resource, req, **lookup):
        return self._find(resource, req, lookup)

    def find(self, resource, req, sub_resource_lookup):
        return ResultWrapper(self._find(resource, req, lookup=sub_resource_lookup))

    def insert(self, resource, doc_or_docs):
        #if isinstance(doc_or_docs, list): TODO
        # if upsert..
        ids = []
        for doc in doc_or_docs:
            keys = self.repo[resource].keys()
            id = 1 if len(keys) == 0 else max(keys)
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
        rs = self._find(resource, None, lookup)
        for rec in rs:
            del self.repo[resource][rec[config.ID_FIELD]]

