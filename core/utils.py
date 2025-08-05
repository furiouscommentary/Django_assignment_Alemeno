from django.utils import timezone
from .models import Customer
from rest_framework.response import Response

def calculate_emi(principal, rate, tenure):
    r = rate / (12 * 100)
    if(r==0):
        return 0
    emi = (principal * r * pow(1 + r, tenure)) / (pow(1 + r, tenure) - 1)
    return emi

def get_corrected_interest(credit_score, interest_rate):
    if credit_score > 50:
        return interest_rate
    elif 30 < credit_score <= 50:
        return max(interest_rate, 12)
    elif 10 < credit_score <= 30:
        return max(interest_rate, 16)
    else:
        return 0

def calculate_credit_score(customer):
    from .models import Loan
    past_loans = Loan.objects.filter(customer=customer)
    if(len(past_loans)==0):
        return 50
    on_time_ratio = 0
    if past_loans.exists():
        on_time_ratio = sum(l.emis_paid_on_time for l in past_loans) / (sum(l.tenure for l in past_loans) or 1)

    current_year_loans = past_loans.filter(start_date__year=timezone.now().year)
    total_loan_volume = sum(l.loan_amount for l in past_loans)

    score = (
        (min(on_time_ratio * 50, 50)) +
        (min(len(past_loans)* 2 , 10)) +
        (min(len(current_year_loans) * 3, 10)) +
        (min(total_loan_volume / 100000, 20))
    )

    if customer.current_debt > customer.approved_limit:
        score = 0

    return min(int(score), 100)

def eligibilityfunc(request):
    data = request.data
    try:
        customer = Customer.objects.get(customer_id = data["customer_id"])
    except Customer.DoesNotExist:
        return Response({"error": "Customer not found"}, status=404)
    
    credit_score = calculate_credit_score(customer)
    requested_interest = float(data["interest_rate"])
    corrected_interest = get_corrected_interest(credit_score, requested_interest)
    emi = calculate_emi(float(data["loan_amount"]), corrected_interest, data["tenure"])
    
    approval = (
        credit_score > 50 or
        (30 < credit_score <= 50 and corrected_interest >= 12) or
        (10 < credit_score <= 30 and corrected_interest >= 16)
    )
    
    if(customer.current_debt + emi > customer.monthly_income * 0.5):
        approval = False
        
    return Response({
        "customer_id": customer.customer_id,
        "approval": approval,
        "interest_rate": requested_interest,
        "corrected_interest_rate": corrected_interest,
        "tenure": data["tenure"],
        "monthly_installment": round(emi, 2) 
    })