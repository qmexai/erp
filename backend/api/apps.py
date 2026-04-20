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


