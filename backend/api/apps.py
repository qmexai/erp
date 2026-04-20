# import os
# import json
# import firebase_admin
# from firebase_admin import credentials
# from django.apps import AppConfig
# from django.conf import settings

# class ApiConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'api'

#     def ready(self):
#         if not firebase_admin._apps:
#             firebase_json = os.environ.get('FIREBASE_JSON_DATA')

#             if firebase_json:
#                 try:
#                     cred_dict = json.loads(firebase_json)
#                     cred = credentials.Certificate(cred_dict)
#                     firebase_admin.initialize_app(cred)
#                     print("✅ Qmexai ERP: Firebase Initialized via Environment Variable")
#                     return 
#                 except Exception as e:
#                     print(f"❌ Firebase Env Var Initialization Failed: {e}")

#             service_account_path = os.path.join(
#                 settings.BASE_DIR, 
#                 'qmexaierp-firebase-adminsdk-fbsvc-03c293320b.json'
#             )
            
#             if os.path.exists(service_account_path):
#                 try:
#                     cred = credentials.Certificate(service_account_path)
#                     firebase_admin.initialize_app(cred)
#                     print("🚀 Qmexai ERP: Firebase Initialized via Local File")
#                 except Exception as e:
#                     print(f"❌ Firebase File Initialization Failed: {e}")
#             else:
#                 print("⚠️ Firebase credentials not found. Skipping initialization.")

#                 from django.contrib.auth import get_user_model
#                  User = get_user_model()
#                     email = "muhsinkalodi9311@gmail.com"
#                     if not User.objects.filter(email=email).exists():
#                         User.objects.create_superuser(
#                             email=email,
#                             password="Kalodi123!", 
#                             username="muhsin"
#                         )
#                         print(f"✅ Superuser created for {email}")


import os
import json
import firebase_admin
from firebase_admin import credentials
from django.apps import AppConfig
from django.conf import settings

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        # 1. --- FIREBASE INITIALIZATION ---
        if not firebase_admin._apps:
            firebase_json = os.environ.get('FIREBASE_JSON_DATA')

            if firebase_json:
                try:
                    cred_dict = json.loads(firebase_json)
                    cred = credentials.Certificate(cred_dict)
                    firebase_admin.initialize_app(cred)
                    print("✅ Qmexai ERP: Firebase Initialized via Environment Variable")
                except Exception as e:
                    print(f"❌ Firebase Env Var Initialization Failed: {e}")
            else:
                service_account_path = os.path.join(
                    settings.BASE_DIR, 
                    'qmexaierp-firebase-adminsdk-fbsvc-03c293320b.json'
                )
                
                if os.path.exists(service_account_path):
                    try:
                        cred = credentials.Certificate(service_account_path)
                        firebase_admin.initialize_app(cred)
                        print("🚀 Qmexai ERP: Firebase Initialized via Local File")
                    except Exception as e:
                        print(f"❌ Firebase File Initialization Failed: {e}")
                else:
                    print("⚠️ Firebase credentials not found. Skipping initialization.")

        # 2. --- TEMPORARY SUPERUSER CREATION ---
        # We wrap this in a try/except because during 'collectstatic' in Docker build,
        # the database might not be ready yet.
       # 2. --- TEMPORARY SUPERUSER CREATION ---
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            email = "muhsinkalodi9311@gmail.com"
            
            # This ensures we only run this if the 'User' table actually exists in Postgres
            u, created = User.objects.get_or_create(email=email, defaults={'username': 'muhsin'})
            u.set_password("Kalodi123") 
            u.is_superuser = True
            u.is_staff = True
            u.save()
            print(f"✅ Superuser setup success for {email}")
        except Exception as e:
            # This will catch if the table 'api_user' doesn't exist yet
            print(f"ℹ️ Database not ready yet for Superuser check. It will work after migration: {e}")