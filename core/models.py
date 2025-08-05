from django.db import models

class Customer (models.Model):
    customer_id = models.IntegerField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.BigIntegerField()
    age = models.PositiveIntegerField()
    monthly_income = models.IntegerField()
    approved_limit = models.IntegerField()
    current_debt = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
class Loan (models.Model):
    loan_id = models.IntegerField(primary_key=True)
    customer = models.ForeignKey("Customer", on_delete=models.CASCADE, db_column='customer_id')
    loan_amount = models.IntegerField()
    tenure = models.IntegerField()
    interest_rate = models.DecimalField(max_digits=5,decimal_places=2)
    monthly_installment = models.FloatField()
    emis_paid_on_time = models.IntegerField(default=0)
    start_date = models.DateField()
    end_date = models.DateField()
    
    def __str__(self):
        return f"Loan {self.loan_id} for {self.customer_id}"