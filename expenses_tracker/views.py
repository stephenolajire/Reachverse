from django.shortcuts import render
from rest_framework import generics, status, permissions
from .serializers import *
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from . models import *
from django.db.models import Sum, Count, Min, Max
from datetime import datetime

# Create your views here.

class RegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegistrationSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            
            return Response({
                "message": "User registration successful",
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"error": "Registration failed"}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        # Validate input
        if not email or not password:
            return Response({
                'error': 'Both email and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Try to find user by email (if using email as username)
        try:
            user = User.objects.get(email=email)
            username = user.username
        except User.DoesNotExist:
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Authenticate user
        user = authenticate(username=username, password=password)
        
        if user is not None:
            if user.is_active:
                # Create or token
                refresh =  RefreshToken.for_user(user)
                return Response({
                    'message': 'Login successful',
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Account is disabled'
                }, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
        

class UserProfileView(generics.RetrieveUpdateAPIView):
    """User profile endpoint"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user

class ExpenseListCreateView(generics.ListCreateAPIView):
    #List user expenses and create new expenses
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ExpenseCreateSerializer
        return ExpenseSerializer
    
    def get_queryset(self):
        queryset = Expenses.objects.filter(user=self.request.user).select_related('category')
        
        # Optional filtering
        category = self.request.query_params.get('category')
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if category:
            queryset = queryset.filter(category__name__icontains=category)
        if date_from:
            try:
                date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
                queryset = queryset.filter(date__gte=date_from)
            except ValueError:
                pass
        if date_to:
            try:
                date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
                queryset = queryset.filter(date__lte=date_to)
            except ValueError:
                pass
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ExpenseDetailView(generics.RetrieveUpdateDestroyAPIView):
    # Retrieve, update, or delete a specific expense
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Expenses.objects.filter(user=self.request.user).select_related('category')

class ExpenseSummaryView(APIView):
    # Get expense summary for the current user
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        expenses = Expenses.objects.filter(user=user)
        
        # Optional date filtering
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        if date_from:
            try:
                date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
                expenses = expenses.filter(date__gte=date_from)
            except ValueError:
                pass
        if date_to:
            try:
                date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
                expenses = expenses.filter(date__lte=date_to)
            except ValueError:
                pass
        
        # Calculate total spent
        total_spent = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        # Calculate spending by category
        category_summary = expenses.values('category__name').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-total')
        
        categories = {
            item['category__name']: {
                'total': item['total'],
                'count': item['count']
            }
            for item in category_summary
        }
        
        # Get date range
        date_range_data = expenses.aggregate(
            earliest=Min('date'),
            latest=Max('date')
        )
        
        date_range = {}
        if date_range_data['earliest'] and date_range_data['latest']:
            date_range = {
                'earliest': date_range_data['earliest'].isoformat(),
                'latest': date_range_data['latest'].isoformat()
            }
        
        summary_data = {
            'total_spent': total_spent,
            'categories': categories,
            'expense_count': expenses.count(),
            'date_range': date_range
        }
        
        serializer = ExpenseSummarySerializer(summary_data)
        return Response(serializer.data)

class CategoryListView(generics.ListCreateAPIView):
    # List and create categories
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
        