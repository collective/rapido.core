import pyaml
from zope.interface import implements

from .interfaces import IImporter, IExporter


class Importer:
    implements(IImporter)

    def __init__(self, context):
        self.context = context

    def import_database(self, data):
        db = self.context
        if 'settings.yaml' in data:
            db.annotation['acl'] = pyaml.load(data['settings.yaml'])

        if 'forms' in data:
            for formid in data['forms']:
                form = db.get_form(formid)
                if not form:
                    # TODO: be able to create form/fields/etc
                    # based on the definition
                    pass


class Exporter:
    implements(IExporter)

    def __init__(self, context):
        self.context = context

    def export_database(self):
        data = {}
        dbsettings = {
            'acl': self.context.annotation['acl'],
        }
        data['settings.yaml'] = pyaml.dump(dbsettings)

        forms = {}
        for form in self.context.forms:
            settings = {
                "id": form.id,
                "title": form.title,
                "fields": form.annotation['fields'],
                "assigned_rules": form.annotation['assigned_rules'],
            }
            forms["%s.yaml" % form.id] = pyaml.dump(settings)
            forms["%s.html" % form.id] = form.layout
            forms["%s.py" % form.id] = form.code

        data['forms'] = forms

        return data
