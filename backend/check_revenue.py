import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp_core.settings')
django.setup()
from api.models import FinancialRecord
from django.db.models import Sum

print("Records:", list(FinancialRecord.objects.all().values('id', 'type', 'amount')))
rev = FinancialRecord.objects.filter(type__iexact='revenue').aggregate(Sum('amount'))
print("Sum is:", rev)
