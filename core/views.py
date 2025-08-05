from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Customer, Loan
from .serializers import CustomerSerializer, LoanSerializer
from .utils import calculate_credit_score, calculate_emi, get_corrected_interest, eligibilityfunc
from django.utils import timezone
from datetime import timedelta

@api_view(["POST"])
def register_customer(request):
    data = request.data.copy()
    count = Customer.objects.count()
    data["customer_id"] = count+1
    salary = int(data["monthly_income"])
    data["approved_limit"] = round(36 * salary, -5)
    serializer = CustomerSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "customer_id": serializer.data["customer_id"],
            "name": f"{serializer.data['first_name']} {serializer.data['last_name']}",
            "age": serializer.data["age"],
            "monthly_income": serializer.data["monthly_income"],
            "approved_limit": serializer.data["approved_limit"],
            "phone_number": serializer.data["phone_number"]
        }, status=201)
    return Response(serializer.errors, status=400)


@api_view(["POST"])
def check_eligibility(request):
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
    

@api_view(["POST"])
def create_loan(request):
    eligibility_resp = eligibilityfunc(request).data
    if not eligibility_resp["approval"]:
        return Response({
            "loan_id": None,
            "customer_id": request.data["customer_id"],
            "loan_approved": False,
            "message": "The customer is not eligible for this loan.",
            "monthly_installment": float(0)
        }, status=200)
    
    customer = Customer.objects.get(customer_id = request.data["customer_id"])
    emi = eligibility_resp["monthly_installment"]
    count = Loan.objects.count()
    
    loan = Loan.objects.create(
        loan_id=count+1,
        customer=customer,
        loan_amount=request.data["loan_amount"],
        tenure=eligibility_resp["tenure"],
        interest_rate=eligibility_resp["corrected_interest_rate"],
        monthly_installment=emi,
        start_date=timezone.now().date(),
        end_date=timezone.now().date() + timedelta(days=30 * int(request.data["tenure"]))
    )
    
    customer.current_debt += emi
    customer.save()
    
    return Response({
        "loan_id": loan.loan_id,
        "customer_id": customer.customer_id,
        "loan_approved": True,
        "message": None,
        "monthly_installment": loan.monthly_installment    
    }, status=201)
    
@api_view(["GET"])
def view_loan(request, loan_id):
    try:
        loan = Loan.objects.select_related("customer").get(loan_id=loan_id)
    except Loan.DoesNotExist:
        return Response({"error": "Loan not found."}, status=404)
    return Response({
        "loan_id": loan.loan_id,
        "customer": {
            "customer_id": loan.customer.customer_id,
            "first_name": loan.customer.first_name,
            "last_name": loan.customer.last_name,
            "phone_number": loan.customer.phone_number,
            "age": loan.customer.age,
        },
        "loan_amount": loan.loan_amount,
        "interest_rate": loan.interest_rate,
        "monthly_installment": loan.monthly_installment,
        "tenure": loan.tenure,
    }, status=200)
    
@api_view(["GET"])
def view_loans_by_customer(request, customer_id):
    loans = Loan.objects.filter(customer_id=customer_id)
    
    loans_arr=[]
    
    for loan in loans:
        loans_arr.append({
            "loan_id": loan.loan_id,
            "loan_amount": loan.loan_amount,
            "interest_rate": loan.interest_rate,
            "monthly_installment": loan.monthly_installment,
            "repayments_left": loan.tenure - loan.emis_paid_on_time,
        })
    
    return Response(loans_arr, status=200)
    
    
    