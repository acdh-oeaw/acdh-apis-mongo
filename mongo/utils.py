from copy import deepcopy
import datetime

from pymongo import MongoClient

from django.apps import apps
from django.conf import settings

from webpage.utils import PROJECT_METADATA as PM

rel_url = settings.APIS_BASE_URI
ent_url = f"{settings.APIS_BASE_URI}/apis/api2/entity/"

try:
    MONGO_URL = settings.MONGO["URL"]
except AttributeError:
    MONGO_URL = "mongodb://localhost:27017/"


client = MongoClient(MONGO_URL)
db = client.apis
entities = db.entities
relations = db.relations


def entities_to_mongo():
    print(datetime.datetime.now())
    projects = db.projects
    projects.find_one_and_replace({'title': PM['title']}, PM, upsert=True)

    for model in apps.get_app_config('apis_entities').get_models():
        print(model)
        for x in model.objects.all():
            my_ent = deepcopy(x.get_serialization())
            my_ent['project'] = PM
            entities.find_one_and_replace({'id': x.id}, my_ent, upsert=True)
    print(datetime.datetime.now())
    print('done')


def relations_to_mongo():
    print(datetime.datetime.now())
    for model in apps.get_app_config('apis_relations').get_models():
        print(model)
        for x in model.objects.all():
            rel_obj = {}
            try:
                source_field = getattr(x, x._meta.get_fields()[-2].name)
                rel_type = getattr(x, 'relation_type')
                target_field = getattr(x, x._meta.get_fields()[-1].name)
            except AttributeError:
                source_field = None
                rel_type = None
                target_field = None
            if source_field is not None:
                rel_obj['global_id'] = f"{settings.APIS_BASE_URI}/relation/{x.id}"
                rel_obj['id'] = x.id
                rel_obj['relation'] = model.__name__.lower()
                rel_obj['start_date'] = x.start_date
                rel_obj['end_date'] = x.end_date
                rel_obj['start_date_written'] = x.start_date_written
                rel_obj['end_date_written'] = x.end_date_written
                rel_obj['source'] = {
                    "id": f"{source_field.id}",
                    "url": f"{ent_url}{source_field.id}",
                    "name": source_field.name
                }
                rel_obj['target'] = {
                    "id": f"{target_field.id}",
                    "url": f"{ent_url}{target_field.id}",
                    "name": target_field.name
                }
                rel_obj['relation_type'] = {
                    "id": rel_type.id,
                    "label": rel_type.label,
                    "name": rel_type.name
                }
                rel_obj['project'] = PM
                relations.find_one_and_replace(
                    {'global_id': rel_obj['global_id']}, rel_obj, upsert=True
                )
        print(datetime.datetime.now())
