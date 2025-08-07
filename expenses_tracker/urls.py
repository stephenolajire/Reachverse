from django.urls import path
from . import views

urlpatterns = [
    # regitration
    path('auth/register/', views.RegistrationView.as_view(), name='register'),
    path('auth/login/', views.LoginView.as_view(), name='login'),

     # Expenses
    path('expenses/', views.ExpenseListCreateView.as_view(), name='expense-list-create'),
    path('expenses/<int:pk>/', views.ExpenseDetailView.as_view(), name='expense-detail'),
    path('expenses/summary/', views.ExpenseSummaryView.as_view(), name='expense-summary'),
    
    # Categories
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
]