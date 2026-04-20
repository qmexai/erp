from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CreateEmployeeView, DashboardStatsView, FirebaseLoginView,
    LeadViewSet, ProjectViewSet, FinanceViewSet, LeaveViewSet, MeetingViewSet, TaskViewSet,
    InvoiceViewSet, LineItemViewSet, ActivityLogViewSet, UserViewSet
)

# Instantiate the router
router = DefaultRouter()

router.register(r'users', UserViewSet, basename='user')
router.register(r'leads', LeadViewSet, basename='lead')
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'finance', FinanceViewSet, basename='finance')
router.register(r'leave-requests', LeaveViewSet, basename='leave')
router.register(r'meetings', MeetingViewSet, basename='meeting')
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'invoices', InvoiceViewSet, basename='invoice')
router.register(r'lineitems', LineItemViewSet, basename='lineitem')
router.register(r'activity-logs', ActivityLogViewSet, basename='activitylog')

urlpatterns = [
    path('create-employee/', CreateEmployeeView.as_view(), name='create_employee'),
    path('login/', FirebaseLoginView.as_view(), name='firebase_login'),
    path('dashboard/stats/', DashboardStatsView.as_view(),name="dashboard_stats"),
    path('', include(router.urls)),
]