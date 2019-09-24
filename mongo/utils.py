from copy import deepcopy
import datetime

from pymongo import MongoClient, GEO2D

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
errors = db.errors


def is_public():
    """ checks if list and detail views are public """
    if settings.APIS_LIST_VIEWS_ALLOWED and settings.APIS_DETAIL_VIEWS_ALLOWED:
        return True
    else:
        return False


RETURN_STRING = """instance is not public, no data dumped \n
 settings.APIS_LIST_VIEWS_ALLOWED and settings.APIS_DETAIL_VIEWS_ALLOWED need to be changed to True
"""


def current_date():
    return datetime.datetime.utcnow()


def entities_to_mongo():
    if is_public():
        print(datetime.datetime.now())
        db.entities.create_index([("loc", GEO2D)])
        projects = db.projects
        projects.find_one_and_replace({'title': PM['title']}, PM, upsert=True)
        for model in apps.get_app_config('apis_entities').get_models():
            print(model)
            for x in model.objects.all():
                try:
                    my_ent = deepcopy(x.get_serialization())
                except Exception as e:
                    my_error = {
                        "global_id": f"{PM['title']}__{x.id}__{model.__name__.lower()}",
                        "error_msg": f"{e}",
                        "project_title": PM['title'],
                        "last_modified": datetime.datetime.utcnow()
                    }
                    errors.find_one_and_replace(
                        {'url': my_error['global_id']}, my_error, upsert=True
                    )
                    continue
                if x.get_child_class() == 'Place':
                    latlng = [x.get_child_entity().lng, x.get_child_entity().lat]
                    if latlng[0]:
                        my_ent['loc'] = latlng
                my_ent['project'] = PM['title']
                my_ent['last_modified'] = datetime.datetime.utcnow()
                try:
                    my_ent['start_date'] = datetime.datetime.combine(
                        x.start_date, datetime.datetime.min.time()
                    )
                except:
                    pass
                try:
                    my_ent['end_date'] = datetime.datetime.combine(
                        x.end_date, datetime.datetime.min.time()
                    )
                except:
                    pass
                try:
                    entities.find_one_and_replace({'url': my_ent['url']}, my_ent, upsert=True)
                except Exception as e:
                    my_error = {
                        "url": my_ent['url'],
                        "error_msg": f"{e}",
                        "project_title": PM['title'],
                        "last_modified": datetime.datetime.utcnow()
                    }
                    errors.find_one_and_replace(
                        {'url': my_ent['url']}, my_error, upsert=True
                    )
        print(datetime.datetime.now())
        print('done')
    else:
        print(RETURN_STRING)


def relations_to_mongo():
    if is_public():
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
                if source_field is not None and target_field is not None:
                    rel_obj['global_id'] = f"{settings.APIS_BASE_URI}/relation/{x.id}"
                    rel_obj['id'] = x.id
                    rel_obj['relation'] = model.__name__.lower()
                    try:
                        rel_obj['start_date'] = datetime.datetime.combine(
                            x.start_date, datetime.datetime.min.time()
                        )
                    except:
                        pass
                    try:
                        rel_obj['end_date'] = datetime.datetime.combine(
                            x.end_date, datetime.datetime.min.time()
                        )
                    except:
                        pass
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
                    rel_obj['project'] = PM['title']
                    try:
                        relations.find_one_and_replace(
                            {'global_id': rel_obj['global_id']}, rel_obj, upsert=True
                        )
                    except Exception as e:
                        my_error = {
                            "url": rel_obj['global_id'],
                            "error_msg": f"{e}",
                            "project_title": PM['title'],
                            "last_modified": datetime.datetime.utcnow()
                        }
                        errors.find_one_and_replace(
                            {'url': my_ent['url']}, my_error, upsert=True
                        )
            print(datetime.datetime.now())
    else:
        print(RETURN_STRING)
