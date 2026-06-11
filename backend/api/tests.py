from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate
from api.models import User, ActivityLog, Task
from api.serializers import UserSerializer, ActivityLogSerializer, FinancialRecordSerializer
from api.views import FirebaseLoginView, UserViewSet
from unittest.mock import patch

class UserTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="employee@qmexai.com",
            role="Employee",
            first_name="John",
            last_name="Doe",
            department="Engineering"
        )
        self.task = Task.objects.create(
            title="Design System",
            assigned_to=self.user,
            assigned_by=self.user
        )
        self.log = ActivityLog.objects.create(
            actor=self.user,
            action="LoggedIn",
            details="User logged in securely."
        )

    def test_string_representations(self):
        # Verify str representations use email
        self.assertEqual(str(self.user), "employee@qmexai.com")
        self.assertEqual(str(self.log), f"employee@qmexai.com - LoggedIn at {self.log.timestamp}")
        self.assertEqual(str(self.task), "Design System - employee@qmexai.com")

    def test_user_serializer(self):
        serializer = UserSerializer(self.user)
        data = serializer.data
        self.assertEqual(data["name"], "John Doe")
        self.assertEqual(data["department"], "Engineering")

    def test_log_serializer(self):
        serializer = ActivityLogSerializer(self.log)
        self.assertEqual(serializer.data["actor_name"], "John Doe")

    def test_user_search_filtering(self):
        # Setup request for UserViewSet
        factory = APIRequestFactory()
        request = factory.get('/api/users/', {'search': 'John'})
        force_authenticate(request, user=self.user)
        
        view = UserViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["email"], "employee@qmexai.com")

    @patch('firebase_admin.auth.verify_id_token')
    def test_login_validation(self, mock_verify):
        mock_verify.return_value = {"email": "employee@qmexai.com", "uid": "mock-uid-123"}
        
        # 1. Existing user should be allowed to login and have their uid synced
        factory = APIRequestFactory()
        request = factory.post('/api/login/', {"token": "valid-firebase-token"})
        view = FirebaseLoginView.as_view()
        
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.uid, "mock-uid-123")

        # 2. Unregistered email should be rejected (security fix)
        mock_verify.return_value = {"email": "stranger@external.com", "uid": "stranger-uid"}
        request = factory.post('/api/login/', {"token": "stranger-token"})
        response = view(request)
        self.assertEqual(response.status_code, 401)
        self.assertFalse(User.objects.filter(email="stranger@external.com").exists())
