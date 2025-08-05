from celery import shared_task
from .models import Customer, Loan
import pandas as pd
from django.conf import settings
import os
from django.db import transaction
from django.core.exceptions import ValidationError


@shared_task
def ingest_data():
    try:
        print("Inside")
        customer_path = os.path.join(settings.BASE_DIR, "data", "customer_data.xlsx")
        loan_path = os.path.join(settings.BASE_DIR, "data", "loan_data.xlsx")
    
        customer_df = pd.read_excel(customer_path)
        loan_df = pd.read_excel(loan_path)
    
        with transaction.atomic():
            for _, row in customer_df.iterrows():
                Customer.objects.update_or_create(
                    customer_id=row["Customer ID"],
                    defaults={
                        "first_name": row["First Name"],
                        "last_name": row["Last Name"],
                        "age": row["Age"],
                        "phone_number": row["Phone Number"],
                        "monthly_income": row["Monthly Salary"],
                        "approved_limit": row["Approved Limit"]
                    }
                )
        
            for _, row in loan_df.iterrows():
                customer = Customer.objects.get(customer_id=row["Customer ID"])
                Loan.objects.update_or_create(
                    loan_id=row["Loan ID"],
                    defaults={
                        "customer": customer,
                        "loan_amount": row["Loan Amount"],
                        "tenure": row["Tenure"],
                        "interest_rate": row["Interest Rate"],
                        "monthly_installment": row["Monthly payment"],
                        "emis_paid_on_time": row["EMIs paid on Time"],
                        "start_date": row["Date of Approval"],
                        "end_date": row["End Date"]
                    }
                )
        print("Data Ingested Successfully.")
    except Exception as e:
        raise ValidationError(f"Data Ingestion failed: {str(e)}")
    