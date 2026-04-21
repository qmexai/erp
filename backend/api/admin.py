from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Project, Meeting, LeaveRequest, FinancialRecord, Lead, ActivityLog

# --- 1. CUSTOM USER ADMIN ---
# We use the decorator for the custom user to add the Qmexai fields
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    # uid is editable now so you can paste Firebase UIDs manually
    readonly_fields = ()

    # This adds your specific fields to the "Edit User" page
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Qmexai ERP Data', {'fields': ('role', 'uid')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Qmexai ERP Data', {'fields': ('role',)}),
    )
    # This makes them visible in the main table list
    list_display = ['email', 'role', 'is_staff', 'is_active']
    list_filter = ['role', 'is_active']
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

# --- 2. OTHER ERP MODELS ---
# We use 'admin.site.register' for these to quickly show them in the sidebar
# without needing to write a separate class for each.
admin.site.register(Project)
admin.site.register(Meeting)
admin.site.register(LeaveRequest)
admin.site.register(FinancialRecord)
admin.site.register(Lead)
admin.site.register(ActivityLog)