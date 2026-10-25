from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Project, Meeting, LeaveRequest, FinancialRecord, Lead, ActivityLog, Task, Invoice, LineItem
from .forms import UserChangeForm, UserCreationForm

# --- 1. CUSTOM USER ADMIN ---
# We use the decorator for the custom user to add the Qmexai fields
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    form = UserChangeForm
    add_form = UserCreationForm

    # This adds your specific fields to the "Edit User" page
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Qmexai ERP Data', {'fields': ('role', 'department', 'uid')}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': (
            'email', 'first_name', 'last_name', 'password1', 'password2',
        )}),
        ('Qmexai ERP Data', {'fields': ('role', 'department', 'uid')}),
    )
    # This makes them visible in the main table list
    list_display = ['name', 'email', 'role', 'is_staff', 'is_active']
    list_filter = ['role', 'is_active']
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

    @admin.display(description='Name', ordering='first_name')
    def name(self, obj):
        return obj.name

# --- 2. OTHER ERP MODELS ---
# We use 'admin.site.register' for these to quickly show them in the sidebar
# without needing to write a separate class for each.
admin.site.register(Project)
admin.site.register(Meeting)
admin.site.register(LeaveRequest)
admin.site.register(FinancialRecord)
admin.site.register(Lead)
admin.site.register(ActivityLog)
admin.site.register(Task)
admin.site.register(Invoice)
admin.site.register(LineItem)