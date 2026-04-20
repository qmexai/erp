from django.core.management.base import BaseCommand, CommandError
from api.models import User
import firebase_admin
from firebase_admin import auth

class Command(BaseCommand):
    help = 'Syncs a Django user with a Firebase user by updating the firebase_uid.'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='The email of the user to sync.')

    def handle(self, *args, **options):
        email = options['email']
        self.stdout.write(f"Attempting to sync user with email: {email}")

        try:
            # Find the user in Django's database
            user = User.objects.get(email=email)
            self.stdout.write(self.style.SUCCESS(f"Found Django user: {user.username}"))
        except User.DoesNotExist:
            raise CommandError(f"User with email {email} does not exist in the Django database.")

        try:
            # Find the user in Firebase
            firebase_user = auth.get_user_by_email(email)
            firebase_uid = firebase_user.uid
            self.stdout.write(self.style.SUCCESS(f"Found Firebase user with UID: {firebase_uid}"))
        except Exception as e:
            raise CommandError(f"Could not find user in Firebase with email {email}. Error: {e}")

        # Update the firebase_uid in the Django user model
        if user.firebase_uid == firebase_uid:
            self.stdout.write(self.style.WARNING(f"User {email} is already in sync."))
        else:
            user.firebase_uid = firebase_uid
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Successfully synced Django user {user.username} with Firebase UID {firebase_uid}."))
