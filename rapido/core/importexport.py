from pyaml import yaml
from zope.interface import implements

from .interfaces import IImporter, IExporter


class Importer:
    implements(IImporter)

    def __init__(self, context):
        self.context = context

    def import_database(self, data):
        db = self.context
        if 'settings.yaml' in data:
            db.annotation['acl'] = yaml.load(data['settings.yaml'])['acl']

        if 'forms' in data:
            for (form_id, form_data) in data['forms'].items():
                db.context.create_form(
                    yaml.load(form_data[form_id+'.yaml']),
                    form_data[form_id+'.py'],
                    form_data[form_id+'.html'],
                )


class Exporter:
    implements(IExporter)

    def __init__(self, context):
        self.context = context

    def export_database(self):
        data = {}
        dbsettings = {
            'acl': self.context.annotation['acl'],
        }
        data['settings.yaml'] = yaml.dump(dbsettings)

        forms = {}
        for form in self.context.forms:
            form_data = {}
            settings = {
                "id": form.id,
                "title": form.title,
                "fields": form.annotation['fields'],
                "assigned_rules": form.annotation['assigned_rules'],
            }
            form_data["%s.yaml" % form.id] = yaml.dump(settings)
            form_data["%s.html" % form.id] = form.layout
            form_data["%s.py" % form.id] = form.code
            forms[form.id] = form_data

        data['forms'] = forms

        return data
