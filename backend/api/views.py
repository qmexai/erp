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
import csv

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
    Custom permission for Dept Head, HR, and CEO.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['CEO', 'HR', 'Dept Head']

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer # You'll need to create this serializer
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = User.objects.all()
        search_query = self.request.query_params.get('search', None)
        if search_query is not None:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query)
            )
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
            company=lead.company_name,
            phone=lead.phone_number,
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
    queryset = Project.objects.all().prefetch_related('assigned_to').order_by('-created_at')
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
            return Project.objects.all().prefetch_related('assigned_to').order_by('-created_at')
        return user.projects.all().prefetch_related('assigned_to').order_by('-created_at')

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
    queryset = Invoice.objects.all().select_related('project').prefetch_related('line_items').order_by('-issue_date')
    serializer_class = InvoiceSerializer
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsManagerOrHigher]
    
    def get_queryset(self):
        # Auto-update overdue invoices
        from django.utils import timezone
        today = timezone.now().date()
        Invoice.objects.filter(status='Unpaid', due_date__lt=today).update(status='Overdue')
        return Invoice.objects.all().select_related('project').prefetch_related('line_items').order_by('-issue_date')

    def perform_create(self, serializer):
        invoice = serializer.save()
        ActivityLog.objects.create(
            actor=self.request.user,
            action="Created Invoice",
            details=f"Invoice {invoice.invoice_number} for {invoice.project.name} created by {self.request.user.email}"
        )

    def perform_update(self, serializer):
        invoice = serializer.save()
        ActivityLog.objects.create(
            actor=self.request.user,
            action="Updated Invoice",
            details=f"Invoice {invoice.invoice_number} updated by {self.request.user.email}"
        )

    @action(detail=True, methods=['get'], url_path='download-pdf')
    def download_pdf(self, request, pk=None):
        invoice = self.get_object()

        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch

        # Create a file-like buffer to receive PDF data.
        buffer = io.BytesIO()

        # Document margins (40 points = ~0.55 in)
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=45,
            title=f"Invoice {invoice.invoice_number}"
        )

        # Styles
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'InvTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#1e1b4b")  # Dark indigo
        )

        meta_label_style = ParagraphStyle(
            'MetaLabel',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#64748b")  # Slate text
        )

        meta_val_style = ParagraphStyle(
            'MetaVal',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#0f172a")  # Deep slate
        )

        th_style = ParagraphStyle(
            'ThStyle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=9,
            leading=12,
            textColor=colors.white
        )

        td_style = ParagraphStyle(
            'TdStyle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#334155")
        )

        td_num_style = ParagraphStyle(
            'TdNumStyle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=13,
            alignment=2,  # Right-aligned
            textColor=colors.HexColor("#334155")
        )

        summary_label_style = ParagraphStyle(
            'SummaryLabel',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=9,
            leading=13,
            alignment=2,  # Right-aligned
            textColor=colors.HexColor("#475569")
        )

        summary_val_style = ParagraphStyle(
            'SummaryVal',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=13,
            alignment=2,  # Right-aligned
            textColor=colors.HexColor("#0f172a")
        )

        total_label_style = ParagraphStyle(
            'TotalLabel',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=11,
            leading=15,
            alignment=2,  # Right-aligned
            textColor=colors.HexColor("#0f172a")
        )

        total_val_style = ParagraphStyle(
            'TotalVal',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=12,
            leading=16,
            alignment=2,  # Right-aligned
            textColor=colors.HexColor("#6366f1")  # Modern indigo
        )

        story = []

        # 1. Header Row
        header_left = Paragraph(
            "<b>QMEXAI ERP</b><br/><font color='#64748b' size='8.5'>Operations & Billing Portal</font>", 
            title_style
        )
        header_right = Paragraph(
            "<font color='#6366f1'><b>INVOICE</b></font>", 
            ParagraphStyle('InvHeadRight', parent=title_style, alignment=2, fontSize=24, leading=28)
        )
        
        header_table = Table([[header_left, header_right]], colWidths=[266, 266])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('PADDING', (0, 0), (-1, -1), 0),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 25))

        # 2. Billing & Metadata Box
        issue_date_str = invoice.issue_date.strftime('%B %d, %Y') if invoice.issue_date else 'N/A'
        due_date_str = invoice.due_date.strftime('%B %d, %Y') if invoice.due_date else 'N/A'
        
        bill_to_text = f"<b>BILL TO:</b><br/>" \
                       f"<font size='10.5'><b>{invoice.project.client}</b></font><br/>"
        if invoice.project.company:
            bill_to_text += f"{invoice.project.company}<br/>"
        if invoice.project.phone:
            bill_to_text += f"Phone: {invoice.project.phone}<br/>"
        
        bill_to_para = Paragraph(bill_to_text, meta_val_style)

        details_text = f"<b>INVOICE DETAILS:</b><br/>" \
                       f"<b>Project:</b> {invoice.project.name}<br/>" \
                       f"<b>Invoice #:</b> {invoice.invoice_number}<br/>" \
                       f"<b>Issue Date:</b> {issue_date_str}<br/>" \
                       f"<b>Due Date:</b> {due_date_str}<br/>" \
                       f"<b>Status:</b> <font color='#6366f1'><b>{invoice.status}</b></font>"
        details_para = Paragraph(details_text, meta_val_style)

        info_table = Table([[bill_to_para, details_para]], colWidths=[266, 266])
        info_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('PADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 25))

        # 3. Line Items Table
        table_data = [[
            Paragraph("Description", th_style),
            Paragraph("Qty", th_style),
            Paragraph("Unit Price", th_style),
            Paragraph("Total", th_style)
        ]]

        for item in invoice.line_items.all():
            table_data.append([
                Paragraph(item.description, td_style),
                Paragraph(str(item.quantity), td_num_style),
                Paragraph(f"INR {item.unit_price:,.2f}", td_num_style),
                Paragraph(f"INR {item.total:,.2f}", td_num_style),
            ])

        items_table = Table(table_data, colWidths=[282, 40, 105, 105])
        items_table_style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e293b")),  # Slate-800 Header
            ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ]

        # Alternating row colors
        for i in range(1, len(table_data)):
            if i % 2 == 0:
                items_table_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor("#f8fafc")))

        items_table.setStyle(TableStyle(items_table_style))
        story.append(items_table)
        story.append(Spacer(1, 20))

        # 4. Summary & Totals
        summary_data = [
            [Paragraph("Subtotal:", summary_label_style), Paragraph(f"INR {invoice.sub_total:,.2f}", summary_val_style)],
            [Paragraph("Discount:", summary_label_style), Paragraph(f"- INR {invoice.discount:,.2f}", summary_val_style)],
            [Paragraph("Total Amount:", total_label_style), Paragraph(f"INR {invoice.total_amount:,.2f}", total_val_style)],
        ]
        summary_table = Table(summary_data, colWidths=[382, 150])
        summary_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('LINEABOVE', (0, 2), (1, 2), 1, colors.HexColor("#1e293b")),
        ]))

        story.append(KeepTogether([summary_table]))

        # Page templates / Draw PAID watermark
        def make_page_renderer(inv):
            def renderer(canvas, doc_obj):
                canvas.saveState()
                # Top blue line
                canvas.setFillColor(colors.HexColor("#6366f1"))
                canvas.rect(0, 786, 612, 6, fill=True, stroke=False)
                
                # Draw watermark if Paid
                if inv.status == 'Paid':
                    canvas.setFont("Helvetica-Bold", 80)
                    canvas.setFillColor(colors.HexColor("#22c55e"))
                    canvas.saveState()
                    canvas.setFillAlpha(0.12)
                    canvas.translate(306, 396)  # center of letter
                    canvas.rotate(35)
                    canvas.drawCentredString(0, 0, "PAID")
                    canvas.restoreState()

                # Footer
                canvas.setFont("Helvetica-Oblique", 8)
                canvas.setFillColor(colors.HexColor("#64748b"))
                canvas.drawString(40, 22, "Thank you for your business! Qmexai ERP - Innovation Portal")
                canvas.drawRightString(572, 22, f"Page {canvas._pageNumber}")
                
                canvas.restoreState()
            return renderer

        # Build Document
        doc.build(story, onFirstPage=make_page_renderer(invoice), onLaterPages=make_page_renderer(invoice))

        # Close the PDF object cleanly.
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
    queryset = ActivityLog.objects.all().select_related('actor').order_by('-timestamp')
    serializer_class = ActivityLogSerializer
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsCEOOrHR]

# --- 7. FINANCE MANAGEMENT ---
class FinanceViewSet(viewsets.ModelViewSet):
    serializer_class = FinancialRecordSerializer
    queryset = FinancialRecord.objects.all().select_related('added_by', 'project').order_by('-date')
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
        return FinancialRecord.objects.all().select_related('added_by', 'project').order_by('-date')

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
    queryset = LeaveRequest.objects.all().select_related('employee').order_by('-start_date')
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
            return LeaveRequest.objects.all().select_related('employee')
        elif user.role == 'HR':
            return LeaveRequest.objects.filter(employee__role__in=['Employee', 'Dept Head']).select_related('employee')
        elif user.role == 'Dept Head':
            return LeaveRequest.objects.filter(employee__department=user.department).select_related('employee')
        return LeaveRequest.objects.filter(employee=user).select_related('employee')

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
    queryset = Meeting.objects.all().select_related('host').prefetch_related('participants').order_by('-start_time')
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
        return (Meeting.objects.filter(participants=user) | Meeting.objects.filter(host=user)).distinct().select_related('host').prefetch_related('participants')

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
            return Task.objects.filter(assigned_by=user).select_related('assigned_to', 'assigned_by', 'project').order_by('-created_at')
        
        # Default to tasks assigned to the user
        return Task.objects.filter(assigned_to=user).select_related('assigned_to', 'assigned_by', 'project').order_by('-created_at')

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
            decoded_token = firebase_auth.verify_id_token(token, clock_skew_seconds=10)
            email = decoded_token.get('email')
            uid = decoded_token.get('uid')
            if not email:
                return Response({"error": "Email not found in Firebase token"}, status=400)

            # Strictly require the user profile to be pre-created by HR/CEO
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                logger.warning(f"Login attempt failed: Email {email} does not exist in the ERP system.")
                return Response({"error": "This account is not authorized/registered in the ERP system. Please contact HR."}, status=401)

            if uid and not user.uid:
                user.uid = uid
                user.save()

            if not user.is_active:
                return Response({"error": "Account is inactive"}, status=403)

            # Log the login activity
            ActivityLog.objects.create(
                actor=user,
                action="Logged In",
                details=f"Secure User Login: {user.email}"
            )

            # Return user data upon successful login
            return Response(UserSerializer(user).data)

        except firebase_auth.InvalidIdTokenError as e:
            logger.error(f"Invalid Firebase token: {e}")
            return Response({"error": "Invalid Firebase token"}, status=401)
        except Exception as e:
            logger.error(f"An unexpected error occurred during login: {e}")
            return Response({"error": f"Authentication failed: {str(e)}"}, status=401)

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
        department = request.data.get('department', '')

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
                first_name=name,
                department=department
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
            pending_invoices = Invoice.objects.filter(status='Unpaid').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
            overdue_invoices = Invoice.objects.filter(status='Overdue').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
            
            stats['paid_invoices_total'] = paid_invoices
            stats['pending_invoices_total'] = pending_invoices
            stats['overdue_invoices_total'] = overdue_invoices
            stats['current_balance'] = total_revenue - total_expenses # Simplified, can be more complex

        elif user.role == 'Dept Head':
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
