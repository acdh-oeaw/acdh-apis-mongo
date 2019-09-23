# acdh-apis-mongo

a django app for serializing data from APIS-projects to mongo-db

`pip install pymongo`

add `mongo` to `INSTALLED_APPS`

provide a mongod-db settings dict in your (secret) settings file, e.g.

```
MONGO = {
    "URL": "mongodb://localhost:27017/"
}
```

run `python manage.py to_mongo` to dump your data to mongo
