import random
import string
import uuid
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

def generate_invoice_number():
    """Generates a unique invoice number."""
    return f'INV-{uuid.uuid4().hex[:8].upper()}'

class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    def _create_user(self, email, password=None, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    uid = models.CharField(max_length=255, unique=True, editable=True, blank=True, null=True)
    ROLE_CHOICES = (
        ('CEO', 'Chief Executive Officer'),
        ('HR', 'Human Resources'),
        ('Dept Head', 'Department Head'),
        ('Employee', 'Employee'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Employee')
    last_activity = models.DateTimeField(null=True, blank=True)

    # Use email as the username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [] # Email & Password are required by default.

    objects = UserManager()

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        # UIDs are assigned by Firebase Auth or created manually via Django Admin
        super().save(*args, **kwargs)

    @staticmethod
    def generate_uid(role):
        """
        Generates role-specific IDs like QM-DH-001 or QM-EMP-001.
        """
        prefix_map = {
            'CEO': 'QM-CEO',
            'HR': 'QM-HR',
            'Dept Head': 'QM-DH',
            'Employee': 'QM-EMP'
        }
        prefix = prefix_map.get(role, 'QM-USR')
        
        # Look for the last user created with this specific prefix
        last_user = User.objects.filter(username__startswith=prefix).order_by('id').last()
        
        if not last_user:
            return f"{prefix}-001"
        
        try:
            # Extract the number part from the last username (e.g., '001')
            last_id_part = last_user.username.split('-')[-1]
            new_number = int(last_id_part) + 1
            return f"{prefix}-{new_number:03d}"
        except (ValueError, IndexError):
            # Fallback random string if format is broken
            random_suffix = ''.join(random.choices(string.digits, k=3))
            return f"{prefix}-{random_suffix}"

    @staticmethod
    def generate_random_password():
        """
        Generates a secure 10-character temporary password.
        """
        characters = string.ascii_letters + string.digits + "@#%"
        return ''.join(random.choices(characters, k=10))

# Modeles Phase - 3
class Project(models.Model):
    STATUS_CHOICES = (
        ('Not Started', 'Not Started'),
        ('Active', 'Active'),
        ('Completed', 'Completed'),
        ('On Hold', 'On Hold'),
        ('Deployed', 'Deployed'),
    )
    name = models.CharField(max_length=200)
    client = models.CharField(max_length=200)
    company = models.CharField(max_length=200, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Not Started')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    assigned_to = models.ManyToManyField(User, related_name='projects')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.client}) - {self.status}"

    # ... existing methods ...

class Meeting(models.Model):
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_meetings')
    title = models.CharField(max_length=255)
    agenda = models.TextField(blank=True)
    participants = models.ManyToManyField(User, related_name='meetings')
    start_time = models.DateTimeField()
    google_meet_link = models.URLField(max_length=500, blank=True)
    is_approved = models.BooleanField(default=False)

class LeaveRequest(models.Model):
    LEAVE_STATUS = (('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected'))
    employee = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=LEAVE_STATUS, default='Pending')

class FinancialRecord(models.Model):
    TYPE_CHOICES = (('Revenue', 'Revenue/Income'), ('Spend', 'Expense/Spending'))
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2) # Supports up to 9.9 billion
    category = models.CharField(max_length=100) # e.g., 'Hosting', 'Client Payment', 'Salary'
    description = models.TextField(blank=True, null=True)
    date = models.DateField(auto_now_add=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, related_name='financial_records')


class Invoice(models.Model):
    STATUS_CHOICES = (
        ('Draft', 'Draft'),
        ('Unpaid', 'Unpaid'),
        ('Paid', 'Paid'),
        ('Overdue', 'Overdue'),
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='invoices')
    invoice_number = models.CharField(max_length=50, unique=True, default=generate_invoice_number, editable=False)
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Unpaid')
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    sub_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Invoice {self.invoice_number} for {self.project.name}"

    def update_total_amount(self):
        sub_total = self.line_items.aggregate(total=models.Sum('total'))['total'] or 0
        self.sub_total = sub_total
        self.total_amount = self.sub_total - self.discount
        self.save()

class LineItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='line_items')
    description = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        self.total = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        self.invoice.update_total_amount()

    def __str__(self):
        return f"{self.description} for {self.invoice.invoice_number}"


class ActivityLog(models.Model):
    actor = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=255) # e.g., "Created Employee", "Approved Leave"
    details = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.actor.username} - {self.action} at {self.timestamp}"


class Lead(models.Model):
    STATUS_CHOICES = (
        ('Not Started', 'Not Started'),
        ('Open', 'Open'),
        ('Not Interested', 'Not Interested'),
        ('Closed', 'Closed (Won)'),
    )
    client_name = models.CharField(max_length=255, blank=True, null=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    field = models.CharField(max_length=255, blank=True, null=True) # e.g., dental clinic, construction
    phone_number = models.CharField(max_length=50, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Not Started')
    services_needed = models.JSONField(default=list) # e.g., ["Web Dev", "AI Solutions"]
    notes = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # AUTOMATION: If Lead is Closed, automatically create a Project
        is_new_close = False
        if self.pk:
            old_status = Lead.objects.get(pk=self.pk).status
            if old_status != 'Closed (Won)' and self.status == 'Closed (Won)':
                is_new_close = True
        
        super().save(*args, **kwargs)
        
        if is_new_close:
            Project.objects.create(
                name=f"{self.client_name} - Project",
                client=self.client_name,
                description=f"Services: {', '.join(self.services_needed)}"
            )


# Task model for task assignment and self-tasks
class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='tasks_assigned')
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, related_name='tasks')
    due_date = models.DateField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.assigned_to.username}"