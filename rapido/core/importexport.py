import os
import codecs
from pyaml import yaml
from zope.interface import implements

from .interfaces import IImporter, IExporter


class Importer:
    implements(IImporter)

    def __init__(self, context):
        self.context = context

    def import_app(self, data):
        db = self.context
        if 'settings.yaml' in data:
            db.annotation['acl'] = yaml.load(data['settings.yaml']).get('acl', None)

        if 'forms' in data:
            for (form_id, form_data) in data['forms'].items():
                db.context.create_form(
                    yaml.load(form_data[form_id+'.yaml']),
                    form_data[form_id+'.py'],
                    form_data[form_id+'.html'],
                )

    def import_from_fs(self, import_path):
        data = {}
        for name in os.listdir(import_path):
            path = os.path.join(import_path, name)
            if os.path.isdir(path):
                dirpath = path
                dirname = name
                data[dirname] = {}
                for name in os.listdir(dirpath):
                    path = os.path.join(dirpath, name)
                    if os.path.isdir(path):
                        subdirpath = path
                        subdirname = name
                        data[dirname][subdirname] = {}
                        for name in os.listdir(subdirpath):
                            path = os.path.join(subdirpath, name)
                            data[dirname][subdirname][name] = "".join(codecs.open(path, 'r', 'utf-8').readlines())
                    else:
                        data[dirname][name] = "".join(codecs.open(path, 'r', 'utf-8').readlines())
            else:
                data[name] = "".join(codecs.open(path, 'r', 'utf-8').readlines())
        self.import_app(data)

class Exporter:
    implements(IExporter)

    def __init__(self, context):
        self.context = context

    def export_app(self):
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

    def export_to_fs(self, export_to):
        if not os.path.isdir(export_to):
            os.makedirs(export_to)
        data = self.export_app()
        file_list = []
        for name in data.keys():
            path = os.path.join(export_to, name)
            if '.' in name:
                file_list.append([path, data[name]])
            else:
                if not os.path.isdir(path):
                    os.makedirs(path)
                dirpath = path
                dirname = name
                for name in data[dirname].keys():
                    path = os.path.join(dirpath, name)
                    if '.' in name:
                        file_list.append([path, data[dirname][name]])
                    else:
                        if not os.path.isdir(path):
                            os.makedirs(path)
                        subdirpath = path
                        subdirname = name
                        for name in data[dirname][subdirname].keys():
                            path = os.path.join(subdirpath, name)
                            file_list.append([path, data[dirname][subdirname][name]])
        
        for (path, content) in file_list:
            fileobj = codecs.open(path, "w", "utf-8")
            fileobj.write(content)
            fileobj.close()