from rest_framework import serializers
from .models import Lead, Project, FinancialRecord, LeaveRequest, Meeting, Task, User, Invoice, LineItem, ActivityLog

class UserSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'name', 'role', 'uid', 'department']

class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = '__all__'

class ProjectSerializer(serializers.ModelSerializer):
    assigned_to = UserSerializer(many=True, read_only=True)
    assigned_to_ids = serializers.PrimaryKeyRelatedField(
        many=True, write_only=True, queryset=User.objects.all(), source='assigned_to', required=False
    )

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'client', 'company', 'phone', 'description', 'status', 
            'start_date', 'end_date', 'created_at', 'updated_at',
            'assigned_to', 'assigned_to_ids'
        ]

class FinancialRecordSerializer(serializers.ModelSerializer):
    added_by_name = serializers.ReadOnlyField(source='added_by.name')

    class Meta:
        model = FinancialRecord
        fields = ['id', 'type', 'amount', 'category', 'description', 'date', 'added_by', 'added_by_name']
        read_only_fields = ('added_by',)

class LeaveRequestSerializer(serializers.ModelSerializer):
    employee_name = serializers.ReadOnlyField(source='employee.name')
    employee_email = serializers.ReadOnlyField(source='employee.email')

    class Meta:
        model = LeaveRequest
        fields = '__all__'
        read_only_fields = ('employee',)

class MeetingSerializer(serializers.ModelSerializer):
    participants_details = UserSerializer(many=True, read_only=True, source='participants')
    host_details = UserSerializer(read_only=True, source='host')

    class Meta:
        model = Meeting
        fields = ['id', 'title', 'agenda', 'start_time', 'participants', 'host', 'is_approved', 'participants_details', 'host_details', 'google_meet_link']
        read_only_fields = ('host',)

class TaskSerializer(serializers.ModelSerializer):
    assigned_by = UserSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=User.objects.all(), source='assigned_to'
    )

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'project', 'due_date', 
            'completed', 'created_at', 'updated_at',
            'assigned_by', 'assigned_to', 'assigned_to_id'
        ]
        read_only_fields = ('assigned_by',)
        extra_kwargs = {
            'project': {'required': False, 'allow_null': True}
        }


class LineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = LineItem
        fields = ['id', 'description', 'quantity', 'unit_price', 'total']

class InvoiceSerializer(serializers.ModelSerializer):
    line_items = LineItemSerializer(many=True, read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    line_items_data = serializers.ListField(write_only=True, child=serializers.DictField(), required=False)

    class Meta:
        model = Invoice
        fields = [
            'id', 'project', 'project_name', 'invoice_number', 
            'issue_date', 'due_date', 'status', 'sub_total', 
            'discount', 'total_amount', 'line_items', 'line_items_data',
            'payment_method', 'transaction_id'
        ]

    def create(self, validated_data):
        line_items_data = validated_data.pop('line_items_data', [])
        invoice = Invoice.objects.create(**validated_data)
        for item_data in line_items_data:
            item_data.pop('id', None)
            item_data.pop('total', None)
            LineItem.objects.create(invoice=invoice, **item_data)
        invoice.update_total_amount()
        return invoice

    def update(self, instance, validated_data):
        line_items_data = validated_data.pop('line_items_data', None)
        
        # Update invoice fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # If line items were provided, update them
        if line_items_data is not None:
            # Delete old line items and create new ones
            instance.line_items.all().delete()
            for item_data in line_items_data:
                item_data.pop('id', None)
                item_data.pop('total', None)
                LineItem.objects.create(invoice=instance, **item_data)
            instance.update_total_amount()
            
        return instance

class ActivityLogSerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(source='actor.name', read_only=True)

    class Meta:
        model = ActivityLog
        fields = ['id', 'actor_name', 'action', 'details', 'timestamp']
