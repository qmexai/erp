from rest_framework import generics, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .authentication import FirebaseAuthentication
from .models import User, ActivityLog, Lead, Project, FinancialRecord, LeaveRequest, Meeting, Task, Invoice, LineItem
from .serializers import LeadSerializer, ProjectSerializer, FinancialRecordSerializer, LeaveRequestSerializer, MeetingSerializer, TaskSerializer, InvoiceSerializer, LineItemSerializer, ActivityLogSerializer, UserSerializer
from firebase_admin import auth as firebase_auth
from django.db.models import Sum
from django.http import HttpResponse
import logging
from django.utils import timezone
from datetime import timedelta
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
import io

logger = logging.getLogger(__name__)

# --- 0. CUSTOM PERMISSIONS ---
class IsCEOOrHR(permissions.BasePermission):
    """
    Custom permission to only allow CEO or HR to access a view.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['CEO', 'HR']

class IsManagerOrHigher(permissions.BasePermission):
    """
    Custom permission for Managers, HR, and CEO.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['CEO', 'HR', 'Manager']

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer # You'll need to create this serializer
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = User.objects.all()
        search_query = self.request.query_params.get('search', None)
        if search_query is not None:
            queryset = queryset.filter(name__icontains=search_query)
        return queryset

# --- 5. LEAD MANAGEMENT ---
class LeadViewSet(viewsets.ModelViewSet):

    serializer_class = LeadSerializer
    queryset = Lead.objects.all().order_by('-updated_at')
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsCEOOrHR]

    def list(self, request, *args, **kwargs):
        logger.info(f"LeadViewSet.list called by user: {request.user}")
        try:
            response = super().list(request, *args, **kwargs)
            logger.info(f"LeadViewSet.list response: {response.status_code}")
            return response
        except Exception as e:
            logger.error(f"LeadViewSet.list exception: {e}", exc_info=True)
            raise

    def get_queryset(self):
        return Lead.objects.all().order_by('-updated_at')

    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            lead = Lead.objects.create(
                client_name=data.get('client_name'),
                company_name=data.get('company_name'),
                field=data.get('field'),
                phone_number=data.get('phone_number'),
                address=data.get('address'),
                status=data.get('status', 'Not Started'),
                services_needed=data.get('services_needed', []),
                notes=data.get('notes', ''),
            )
            ActivityLog.objects.create(
                actor=request.user,
                action="Created Lead",
                details=f"Lead: {lead.client_name} by {request.user.email}"
            )
            return Response({'id': lead.id, 'message': 'Lead created.'}, status=201)
        except Exception as e:
            logger.error(f"Lead creation error: {str(e)}")
            return Response({'error': str(e)}, status=500)

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        lead = self.get_object()
        status = request.data.get('status')
        followup = request.data.get('followup')
        if status:
            lead.status = status
        if followup:
            lead.notes += f"\nFollow-up: {followup}"
        if status == 'Closed (Won)':
            lead.services_needed = request.data.get('services_needed', [])
        lead.save()
        ActivityLog.objects.create(
            actor=request.user,
            action="Updated Lead Status",
            details=f"Lead: {lead.client_name} status changed to {lead.status} by {request.user.email}"
        )
        return Response({'message': 'Lead updated.'})

    @action(detail=True, methods=['post'])
    def convert_to_project(self, request, pk=None):
        lead = self.get_object()
        
        # Create a new project from the lead
        project = Project.objects.create(
            name=f"Project for {lead.client_name}",
            client=lead.client_name,
            description=f"Project initiated from lead. Services: {', '.join(lead.services_needed)}. Notes: {lead.notes}",
            status='Not Started'
        )
        
        # Update lead status
        lead.status = 'Closed'
        lead.save()
        
        # Log the activity
        ActivityLog.objects.create(
            actor=request.user,
            action="Converted Lead to Project",
            details=f"Lead '{lead.client_name}' converted to project '{project.name}' by {request.user.email}"
        )
        
        return Response(ProjectSerializer(project).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def download(self, request):
        leads = self.get_queryset()
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="leads.csv"'
        writer = csv.writer(response)
        writer.writerow(['Client Name', 'Company', 'Field', 'Phone', 'Address', 'Status', 'Services', 'Notes'])
        for l in leads:
            writer.writerow([l.client_name, l.company_name, l.field, l.phone_number, l.address, l.status, ','.join(l.services_needed), l.notes])
        return response

# --- 6. PROJECT MANAGEMENT ---
class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    queryset = Project.objects.all().order_by('-created_at')
    authentication_classes = [FirebaseAuthentication]
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'update', 'partial_update']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsManagerOrHigher]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Optionally restricts the returned projects to only those assigned
        to the currently authenticated user, unless the user is a CEO or HR.
        """
        user = self.request.user
        if user.role in ['CEO', 'HR']:
            return Project.objects.all().order_by('-created_at')
        return user.projects.all().order_by('-created_at')

    def perform_create(self, serializer):
        project = serializer.save()
        ActivityLog.objects.create(
            actor=self.request.user,
            action="Created Project",
            details=f"Project '{project.name}' created by {self.request.user.email}"
        )

    def perform_update(self, serializer):
        project = serializer.save()
        ActivityLog.objects.create(
            actor=self.request.user,
            action="Updated Project",
            details=f"Project '{project.name}' updated by {self.request.user.email}"
        )

    @action(detail=True, methods=['post'], url_path='assign-users')
    def assign_users(self, request, pk=None):
        project = self.get_object()
        user_ids = request.data.get('user_ids', [])
        
        if not isinstance(user_ids, list):
            return Response({'error': 'user_ids must be a list.'}, status=status.HTTP_400_BAD_REQUEST)

        users = User.objects.filter(id__in=user_ids)
        project.assigned_to.set(users)
        
        user_emails = list(users.values_list('email', flat=True))
        ActivityLog.objects.create(
            actor=request.user,
            action="Assigned Users to Project",
            details=f"Users {user_emails} assigned to project '{project.name}' by {request.user.email}"
        )
        
        return Response({'message': f'Users assigned successfully to {project.name}.'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def download(self, request):
        projects = self.get_queryset()
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="projects.csv"'
        writer = csv.writer(response)
        writer.writerow(['Name', 'Client', 'Status', 'Description', 'Team'])
        for p in projects:
            writer.writerow([p.name, p.client, p.status, p.description, ','.join([u.email for u in p.assigned_to.all()])])
        return response

class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all().order_by('-issue_date')
    serializer_class = InvoiceSerializer
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsManagerOrHigher]

    @action(detail=True, methods=['get'], url_path='download-pdf')
    def download_pdf(self, request, pk=None):
        invoice = self.get_object()

        # Create a file-like buffer to receive PDF data.
        buffer = io.BytesIO()

        # Create the PDF object, using the buffer as its "file."
        p = canvas.Canvas(buffer, pagesize=letter)

        # Document Info
        p.setTitle(f"Invoice {invoice.invoice_number}")

        # Header
        p.setFont("Helvetica-Bold", 16)
        p.drawString(inch, 10.5 * inch, "Qmexai ERP - INVOICE")

        # Invoice Details
        p.setFont("Helvetica", 12)
        p.drawString(inch, 10 * inch, f"Invoice #: {invoice.invoice_number}")
        p.drawString(inch, 9.8 * inch, f"Issue Date: {invoice.issue_date.strftime('%B %d, %Y')}")
        p.drawString(inch, 9.6 * inch, f"Due Date: {invoice.due_date.strftime('%B %d, %Y')}")
        p.drawString(inch, 9.4 * inch, f"Project: {invoice.project.name}")
        p.drawString(inch, 9.2 * inch, f"Client: {invoice.project.client}")

        # Line Items Table Header
        p.setFont("Helvetica-Bold", 12)
        y_position = 8.5 * inch
        p.drawString(inch, y_position, "Description")
        p.drawString(4 * inch, y_position, "Quantity")
        p.drawString(5 * inch, y_position, "Unit Price")
        p.drawString(6 * inch, y_position, "Total")
        p.line(inch, y_position - 0.1 * inch, 7.5 * inch, y_position - 0.1 * inch)

        # Line Items
        p.setFont("Helvetica", 11)
        y_position -= 0.3 * inch
        line_items = invoice.line_items.all()
        for item in line_items:
            p.drawString(inch, y_position, item.description)
            p.drawString(4.2 * inch, y_position, str(item.quantity))
            p.drawString(5.2 * inch, y_position, f"${item.unit_price:,.2f}")
            p.drawString(6.2 * inch, y_position, f"${item.total:,.2f}")
            y_position -= 0.3 * inch
        
        p.line(inch, y_position + 0.1 * inch, 7.5 * inch, y_position + 0.1 * inch)

        # Totals
        y_position -= 0.3 * inch
        p.setFont("Helvetica-Bold", 12)
        p.drawString(5 * inch, y_position, "Subtotal:")
        p.drawString(6.2 * inch, y_position, f"${invoice.sub_total:,.2f}")
        y_position -= 0.3 * inch
        p.drawString(5 * inch, y_position, "Discount:")
        p.drawString(6.2 * inch, y_position, f"- ${invoice.discount:,.2f}")
        y_position -= 0.3 * inch
        p.setFont("Helvetica-Bold", 14)
        p.drawString(5 * inch, y_position, "Total:")
        p.drawString(6.2 * inch, y_position, f"${invoice.total_amount:,.2f}")

        # Footer
        p.setFont("Helvetica-Oblique", 9)
        p.drawString(inch, 1 * inch, "Thank you for your business!")
        p.drawString(inch, 0.8 * inch, "Qmexai - Your Partner in Innovation")

        # Close the PDF object cleanly.
        p.showPage()
        p.save()

        # FileResponse sets the Content-Disposition header so that browsers
        # present the option to save the file.
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.invoice_number}.pdf"'
        return response

class LineItemViewSet(viewsets.ModelViewSet):
    queryset = LineItem.objects.all()
    serializer_class = LineItemSerializer
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsCEOOrHR]

class ActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ActivityLog.objects.all().order_by('-timestamp')
    serializer_class = ActivityLogSerializer
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsCEOOrHR]

# --- 7. FINANCE MANAGEMENT ---
class FinanceViewSet(viewsets.ModelViewSet):
    serializer_class = FinancialRecordSerializer
    queryset = FinancialRecord.objects.all().order_by('-date')
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsCEOOrHR]

    def perform_create(self, serializer):
        serializer.save(added_by=self.request.user)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        ActivityLog.objects.create(
            actor=request.user,
            action="Added Finance Record",
            details=f"Finance record added by {request.user.email}"
        )
        return response

    def get_queryset(self):
        return FinancialRecord.objects.all().order_by('-date')

    @action(detail=False, methods=['get'])
    def download(self, request):
        records = self.get_queryset()
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="finance.csv"'
        writer = csv.writer(response)
        writer.writerow(['Type', 'Amount', 'Category', 'Description', 'Date', 'Added By'])
        for r in records:
            writer.writerow([r.type, r.amount, r.category, r.description, r.date, r.added_by.email if r.added_by else ''])
        return response

# --- 8. LEAVE MANAGEMENT ---
class LeaveViewSet(viewsets.ModelViewSet):
    serializer_class = LeaveRequestSerializer
    queryset = LeaveRequest.objects.all().order_by('-start_date')
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(employee=self.request.user)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        ActivityLog.objects.create(
            actor=request.user,
            action="Applied Leave",
            details=f"Leave applied by {request.user.email}"
        )
        return response

    def get_queryset(self):
        user = self.request.user
        if user.role == 'CEO':
            return LeaveRequest.objects.all()
        elif user.role == 'HR':
            return LeaveRequest.objects.filter(employee__role__in=['Employee', 'Dept Head'])
        elif user.role == 'Dept Head':
            return LeaveRequest.objects.filter(employee__department=user.department)
        return LeaveRequest.objects.filter(employee=user)

    @action(detail=True, methods=['patch'])
    def approve(self, request, pk=None):
        leave = self.get_object()
        if request.user.role in ['CEO', 'HR', 'Dept Head']:
            leave.status = 'Approved'
            leave.save()
            ActivityLog.objects.create(
                actor=request.user,
                action="Approved Leave",
                details=f"Leave for {leave.employee.email} approved by {request.user.email}"
            )
            return Response({'message': 'Leave approved.'})
        return Response({'error': 'Unauthorized'}, status=403)

    @action(detail=True, methods=['patch'])
    def reject(self, request, pk=None):
        leave = self.get_object()
        if request.user.role in ['CEO', 'HR', 'Dept Head']:
            leave.status = 'Rejected'
            leave.save()
            ActivityLog.objects.create(
                actor=request.user,
                action="Rejected Leave",
                details=f"Leave for {leave.employee.email} rejected by {request.user.email}"
            )
            return Response({'message': 'Leave rejected.'})
        return Response({'error': 'Unauthorized'}, status=403)

# --- 9. MEETING MANAGEMENT ---
class MeetingViewSet(viewsets.ModelViewSet):
    serializer_class = MeetingSerializer
    queryset = Meeting.objects.all().order_by('-start_time')
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(host=self.request.user)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        ActivityLog.objects.create(
            actor=request.user,
            action="Scheduled Meeting",
            details=f"Meeting scheduled by {request.user.email}"
        )
        return response

    def get_queryset(self):
        user = self.request.user
        # Use .distinct() to avoid duplicate meetings if a user is both a host and a participant.
        return (Meeting.objects.filter(participants=user) | Meeting.objects.filter(host=user)).distinct()

# --- 10. TASK MANAGEMENT ---
class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Filters tasks based on the 'view' query parameter.
        - 'assigned_to_me': Tasks assigned to the current user.
        - 'assigned_by_me': Tasks assigned by the current user.
        Defaults to 'assigned_to_me'.
        """
        user = self.request.user
        view = self.request.query_params.get('view', 'assigned_to_me')

        if view == 'assigned_by_me':
            return Task.objects.filter(assigned_by=user).order_by('-created_at')
        
        # Default to tasks assigned to the user
        return Task.objects.filter(assigned_to=user).order_by('-created_at')

    def perform_create(self, serializer):
        """
        Sets the 'assigned_by' field to the current user upon creation.
        """
        task = serializer.save(assigned_by=self.request.user)
        ActivityLog.objects.create(
            actor=self.request.user,
            action="Created Task",
            details=f"Task '{task.title}' assigned to {task.assigned_to.email} by {self.request.user.email}"
        )

    @action(detail=True, methods=['patch'])
    def toggle_complete(self, request, pk=None):
        task = self.get_object()
        
        # Allow either the assignee or the assigner to mark as complete
        if request.user != task.assigned_to and request.user != task.assigned_by:
            return Response({'error': 'You are not authorized to modify this task.'}, status=status.HTTP_403_FORBIDDEN)
            
        task.completed = not task.completed
        task.save()
        
        status_str = "completed" if task.completed else "marked as not completed"
        ActivityLog.objects.create(
            actor=request.user,
            action="Updated Task Status",
            details=f"Task '{task.title}' {status_str} by {request.user.email}"
        )
        
        return Response(self.get_serializer(task).data)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import User, ActivityLog, Lead, Project, FinancialRecord, LeaveRequest, Meeting, Task, Invoice, LineItem
from firebase_admin import auth as firebase_auth
from django.db.models import Sum
import logging

logger = logging.getLogger(__name__)


# --- 1. CUSTOM AUTHENTICATION CLASS ---
# This class has been moved to its own file: api/authentication.py


# --- 2. LOGIN VIEW ---
class FirebaseLoginView(APIView):
    """
    Public endpoint for initial login exchange.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        token = request.data.get('token')
        if not token:
            return Response({"error": "No token provided"}, status=400)

        try:
            decoded_token = firebase_auth.verify_id_token(token)
            email = decoded_token.get('email')
            if not email:
                return Response({"error": "Email not found in Firebase token"}, status=400)

            # Get or create the user by email
            user, created = User.objects.get_or_create(email=email)

            if created:
                logger.info(f"New user created via login: {email}")
                # You might want to set a default role or other fields for new users here
                # user.role = 'Employee'
                # user.save()

            if not user.is_active:
                return Response({"error": "Account is inactive"}, status=403)

            # Return user data upon successful login
            return Response(UserSerializer(user).data)

        except firebase_auth.InvalidIdTokenError as e:
            logger.error(f"Invalid Firebase token: {e}")
            return Response({"error": "Invalid Firebase token"}, status=401)
        except Exception as e:
            logger.error(f"An unexpected error occurred during login: {e}")
            return Response({"error": "Authentication failed"}, status=401)

# --- 3. CREATE EMPLOYEE VIEW ---
class CreateEmployeeView(APIView):
    """
    Endpoint for CEO/HR to create new employees.
    """
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsCEOOrHR]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        role = request.data.get('role')
        name = request.data.get('name')

        if not all([email, password, role, name]):
            return Response({'error': 'Missing required fields'}, status=400)

        try:
            # 1. Create user in Firebase
            firebase_user = firebase_auth.create_user(
                email=email,
                password=password,
                display_name=name
            )

            # 2. Create user in Django
            # The password is not stored in plain text in Django, set_password handles hashing
            user = User.objects.create_user(
                email=email,
                role=role,
                first_name=name
            )
            user.set_password(password)
            user.save()
            
            ActivityLog.objects.create(
                actor=request.user,
                action="Created Employee",
                details=f"Employee {user.email} ({user.role}) created by {request.user.email}"
            )

            return Response({
                'message': 'Employee created successfully',
                'email': user.email,
                'password': password  # Return the generated password
            }, status=201)

        except Exception as e:
            logger.error(f"Error creating employee: {e}", exc_info=True)
            return Response({'error': str(e)}, status=500)


# --- 4. DASHBOARD STATS VIEW ---
class DashboardStatsView(APIView):
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        # Initialize stats dictionary
        stats = {}

        # Role-based stats
        if user.role in ['CEO', 'HR']:
            stats['total_employees'] = User.objects.count()
            stats['total_projects'] = Project.objects.count()
            stats['total_leads'] = Lead.objects.count()
            
            # Count users active in the last 5 minutes
            five_minutes_ago = timezone.now() - timedelta(minutes=5)
            stats['active_now'] = User.objects.filter(last_activity__gte=five_minutes_ago).count()

            # Financial Stats
            total_revenue = FinancialRecord.objects.filter(type__iexact='revenue').aggregate(Sum('amount'))['amount__sum'] or 0
            total_expenses = FinancialRecord.objects.filter(type__in=['spend', 'Spend', 'expense', 'Expense']).aggregate(Sum('amount'))['amount__sum'] or 0
            stats['total_revenue'] = total_revenue
            stats['total_expenses'] = total_expenses
            stats['net_profit'] = total_revenue - total_expenses
            
            # Invoice Stats
            paid_invoices = Invoice.objects.filter(status='Paid').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
            pending_invoices = Invoice.objects.filter(status='Pending').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
            overdue_invoices = Invoice.objects.filter(status='Overdue').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
            
            stats['paid_invoices_total'] = paid_invoices
            stats['pending_invoices_total'] = pending_invoices
            stats['overdue_invoices_total'] = overdue_invoices
            stats['current_balance'] = total_revenue - total_expenses # Simplified, can be more complex

        elif user.role == 'Manager':
            stats['assigned_projects'] = user.projects.count()
            stats['tasks_assigned_by_you'] = Task.objects.filter(assigned_by=user).count()
            stats['your_completed_tasks'] = Task.objects.filter(assigned_to=user, completed=True).count()

        else: # Employee
            stats['assigned_projects'] = user.projects.count()
            stats['active_tasks'] = Task.objects.filter(assigned_to=user, completed=False).count()
            stats['completed_tasks'] = Task.objects.filter(assigned_to=user, completed=True).count()

        # Common stats for all
        stats['leave_requests'] = LeaveRequest.objects.filter(employee=user).count()
        stats['upcoming_meetings'] = Meeting.objects.filter(participants=user).count()

        return Response(stats)

from django.http import HttpResponse

def health_check(request):
    return HttpResponse("OK", status=200)
