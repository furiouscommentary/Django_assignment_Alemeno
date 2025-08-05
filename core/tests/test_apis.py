from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from core.models import Customer, Loan
from django.utils import timezone
from datetime import timedelta

class CreditApprovalSystemAPITestCase(APITestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            customer_id=1,
            first_name="Test",
            last_name="User",
            phone_number="1234567890",
            age=30,
            monthly_income=50000,
            approved_limit=1800000,
            current_debt=0
        )

    def test_register_customer(self):
        url = reverse("register_customer")
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "age": 25,
            "monthly_income": 60000,
            "phone_number": "9876543210"
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("customer_id", response.data)

    def test_check_eligibility(self):
        url = reverse("check_eligibility")
        data = {
            "customer_id": self.customer.customer_id,
            "loan_amount": 100000,
            "interest_rate": 12.0,
            "tenure": 12
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("approval", response.data)

    def test_create_loan(self):
        url = reverse("create_loan")
        data = {
            "customer_id": self.customer.customer_id,
            "loan_amount": 100000,
            "interest_rate": 12.0,
            "tenure": 12
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["loan_approved"])

    def test_view_loan(self):
        loan = Loan.objects.create(
            loan_id=1,
            customer=self.customer,
            loan_amount=100000,
            interest_rate=12.0,
            monthly_installment=8888.0,
            tenure=12,
            emis_paid_on_time=0,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=30 * 12)
        )
        url = reverse("view_loan", args=[loan.loan_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["loan_id"], loan.loan_id)

    def test_view_loans_by_customer(self):
        Loan.objects.create(
            loan_id=1,
            customer=self.customer,
            loan_amount=100000,
            interest_rate=12.0,
            monthly_installment=8888.0,
            tenure=12,
            emis_paid_on_time=3,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=30 * 12)
        )
        url = reverse("view_loans_by_customer", args=[self.customer.customer_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(response.data[0]["repayments_left"], 9)
