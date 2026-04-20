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
        # Prevent Firebase from initializing multiple times
        if not firebase_admin._apps:
            # 1. Look for the JSON data in Render Environment Variables (Production)
            firebase_json = os.environ.get('FIREBASE_JSON_DATA')

            if firebase_json:
                try:
                    # Parse the string text into a dictionary
                    cred_dict = json.loads(firebase_json)
                    cred = credentials.Certificate(cred_dict)
                    firebase_admin.initialize_app(cred)
                    print("✅ Qmexai ERP: Firebase Initialized via Environment Variable")
                    return # Exit early if successful
                except Exception as e:
                    print(f"❌ Firebase Env Var Initialization Failed: {e}")

            # 2. Fallback: Look for the local file (Development)
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
                # This prevents the "Exit Code 1" crash during Docker builds
                print("⚠️ Firebase credentials not found. Skipping initialization.")