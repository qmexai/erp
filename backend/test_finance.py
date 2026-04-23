import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "erp_core.settings")
django.setup()

from api.models import FinancialRecord, User
from django.db.models import Sum

try:
    user, _ = User.objects.get_or_create(email="test@qmexai.com", defaults={"role": "CEO"})
    FinancialRecord.objects.all().delete()
    FinancialRecord.objects.create(type="Revenue", amount=2000, category="Test", added_by=user)
    
    total_rev = FinancialRecord.objects.filter(type__iexact='revenue').aggregate(Sum('amount'))['amount__sum'] or 0
    total_exp = FinancialRecord.objects.filter(type__in=['spend', 'Spend', 'expense', 'Expense']).aggregate(Sum('amount'))['amount__sum'] or 0
    
    print(f"Total Revenue: {total_rev}")
    print(f"Total Expenses: {total_exp}")
    
    records = FinancialRecord.objects.all()
    print(f"Count: {records.count()}")
    for r in records:
        print(f"- {r.amount}")
except Exception as e:
    print(e)
