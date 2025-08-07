from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from decimal import Decimal
from datetime import date, timedelta

from .models import Category, Expenses

class ExpenseModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Food',
            description='Food and dining expenses'
        )

    def test_expense_creation(self):
        expense = Expenses.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal('25.50'),
            description='Lunch at restaurant',
            date=date.today()
        )
        self.assertEqual(expense.amount, Decimal('25.50'))
        self.assertEqual(expense.user, self.user)
        self.assertEqual(expense.category, self.category)
        self.assertEqual(str(expense), f"{self.user.username} - {self.category.name} - $25.50")

class ExpenseAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        self.category = Category.objects.create(
            name='Food',
            # description='Food expenses'
        )
        self.category2 = Category.objects.create(
            name='Transport',
            # description='Transportation expenses'
        )
        
        # Create some test expenses
        Expenses.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal('15.00'),
            description='Coffee',
            date=date.today()
        )
        Expenses.objects.create(
            user=self.user,
            category=self.category2,
            amount=Decimal('25.50'),
            description='Bus fare',
            date=date.today() - timedelta(days=1)
        )
        
        # Expense for other user
        Expenses.objects.create(
            user=self.other_user,
            category=self.category,
            amount=Decimal('100.00'),
            description='Other user expense',
            date=date.today()
        )
        
        # Get JWT token for authentication
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

    def authenticate(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

    def test_user_registration(self):
        url = reverse('expenses:register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'password_confirm': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_user_login(self):
        url = reverse('expenses:login')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_create_expense_authenticated(self):
        self.authenticate()
        url = reverse('expenses:expense-list-create')
        data = {
            'category': self.category.id,
            'amount': '30.00',
            'description': 'Dinner',
            'date': date.today().isoformat()
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Expenses.objects.filter(user=self.user).count(), 3)

    def test_create_expense_unauthenticated(self):
        url = reverse('expenses:expense-list-create')
        data = {
            'category': self.category.id,
            'amount': '30.00',
            'description': 'Dinner',
            'date': date.today().isoformat()
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_user_expenses_only(self):
        self.authenticate()
        url = reverse('expenses:expense-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should only return expenses for authenticated user (2 expenses)
        self.assertEqual(len(response.data['results']), 2)
        for expense in response.data['results']:
            self.assertEqual(expense['user'], self.user.username)

    def test_expense_summary(self):
        self.authenticate()
        url = reverse('expenses:expense-summary')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data
        self.assertEqual(data['total_spent'], '40.50')  # 15.00 + 25.50
        self.assertEqual(data['expense_count'], 2)
        self.assertIn('Food', data['categories'])
        self.assertIn('Transport', data['categories'])
        self.assertEqual(data['categories']['Food']['total'], '15.00')
        self.assertEqual(data['categories']['Transport']['total'], '25.50')

    def test_expense_validation_negative_amount(self):
        self.authenticate()
        url = reverse('expenses:expense-list-create')
        data = {
            'category': self.category.id,
            'amount': '-10.00',
            'description': 'Invalid expense',
            'date': date.today().isoformat()
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_expense_filtering_by_category(self):
        self.authenticate()
        url = reverse('expenses:expense-list-create')
        response = self.client.get(url, {'category': 'Food'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['category_name'], 'Food')

class CategoryAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

    def authenticate(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

    def test_list_categories(self):
        self.authenticate()
        Category.objects.create(name='Food', description='Food expenses')
        Category.objects.create(name='Travel', description='Travel expenses')
        
        url = reverse('expenses:category-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_create_category(self):
        self.authenticate()
        url = reverse('expenses:category-list')
        data = {
            'name': 'Entertainment',
            'description': 'Entertainment and leisure'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Category.objects.filter(name='Entertainment').exists())