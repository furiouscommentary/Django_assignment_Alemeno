from django.urls import path
from .views import register_customer, view_loan, view_loans_by_customer, check_eligibility, create_loan 

urlpatterns = [
    path("check-eligibility", check_eligibility, name="check_eligibility"),
    path("register", register_customer, name="register_customer"),
    path("create-loan", create_loan, name="create_loan"),
    path("view-loan/<int:loan_id>", view_loan, name="view_loan"),
    path("view-loans/<int:customer_id>", view_loans_by_customer, name="view_loans_by_customer"),
]