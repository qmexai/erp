import logging
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from firebase_admin import auth as firebase_auth
from .models import User

logger = logging.getLogger(__name__)

class FirebaseAuthentication(BaseAuthentication):
    """
    Verifies the Firebase ID Token from the Authorization Header.
    If valid, it returns the corresponding Django user.
    """
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header or not auth_header.startswith('Bearer '):
            logger.warning("AUTH: No Bearer token in Authorization header.")
            return None

        token = auth_header.split('Bearer ')[1]
        try:
            decoded_token = firebase_auth.verify_id_token(token, clock_skew_seconds=10)
            email = decoded_token.get('email')
            uid = decoded_token.get('uid')
            if not email:
                raise AuthenticationFailed('No email found in Firebase token.')

            try:
                user, created = User.objects.get_or_create(email=email)
                if created:
                    user.qm_id = uid  # Store the Firebase UID during creation
                    user.save()
                    logger.info(f"AUTH: New user created for email {email} from Firebase token.")
                else:
                    # Update qm_id if it's blank but we have a valid uid from Firebase
                    if uid and not user.qm_id:
                        user.qm_id = uid
                        user.save()
                    logger.info(f"AUTH: User '{user.email}' authenticated successfully via Firebase.")
                return (user, None)
            except Exception as e:
                logger.error(f"AUTH: An unexpected error occurred during user retrieval/creation: {e}")
                raise AuthenticationFailed('Authentication failed due to an internal database error.')

        except firebase_auth.InvalidIdTokenError as e:
            logger.error(f"AUTH: Invalid Firebase ID Token: {e}")
            raise AuthenticationFailed(f'Invalid Firebase ID Token: {e}')
        except Exception as e:
            logger.error(f"AUTH: An unexpected error occurred during Firebase authentication: {e}")
            raise AuthenticationFailed(f'Firebase authentication failed: {e}')
