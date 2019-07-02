from copy import deepcopy
import datetime

from pymongo import MongoClient

from django.apps import apps
from django.conf import settings

from webpage.utils import PROJECT_METADATA as PM

try:
    MONGO_URL = settings.MONGO["URL"]
except AttributeError:
    MONGO_URL = "mongodb://localhost:27017/"


client = MongoClient(MONGO_URL)
db = client.apis
entities = db.entities


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
