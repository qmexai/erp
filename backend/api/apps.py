import os
from django.apps import AppConfig
import firebase_admin
from firebase_admin import credentials
from django.conf import settings

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        # This prevents Firebase from trying to initialize twice
        if not firebase_admin._apps:
            # This matches the filename I saw in your folder earlier
            service_account_path = os.path.join(
                settings.BASE_DIR, 
                'qmexaierp-firebase-adminsdk-fbsvc-03c293320b.json'
            )
            
            try:
                cred = credentials.Certificate(service_account_path)
                firebase_admin.initialize_app(cred)
                print("🚀 Qmexai ERP: Firebase Admin SDK Initialized")
            except Exception as e:
                print(f"❌ Firebase Initialization Failed: {e}")