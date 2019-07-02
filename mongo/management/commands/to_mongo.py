from django.core.management.base import BaseCommand, CommandError

from mongo.utils import entities_to_mongo


class Command(BaseCommand):
    # Show this when the user types help
    help = "Dumps all data into a mongo-db"

    # A command must define handle()
    def handle(self, *args, **options):
        entities_to_mongo()
        return 'done'
