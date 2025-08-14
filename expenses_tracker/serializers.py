import re
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password
from . models import *


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password', 'first_name', 'last_name']

    def validate_email(self, value):
        # Validate email format
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_regex, value):
            raise serializers.ValidationError('Please enter a valid email address')
        
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with that email already exists")
        
        return value

    def validate_first_name(self, value):
        # Validate first name length
        if len(value) < 3:
            raise serializers.ValidationError("First name must be more than 2 letters")
        return value

    def validate_last_name(self, value):
        # Validate last name length
        if len(value) < 3:
            raise serializers.ValidationError("Last name must be more than 2 letters")
        return value

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        
        # Check if passwords match
        if password != confirm_password:
            raise serializers.ValidationError("Passwords do not match.")
        
        # Other Password validation
        if len(password) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        
        if not re.search(r'[A-Z]', password):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        
        if not re.search(r'[a-z]', password):
            raise serializers.ValidationError("Password must contain at least one lowercase letter.")
        
        if not re.search(r'\d', password):
            raise serializers.ValidationError("Password must contain at least one digit.")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise serializers.ValidationError("Password must contain at least one special character.")
        
        return attrs

    def create(self, validated_data):
        # Remove confirm_password from validated_data
        validated_data.pop('confirm_password', None)
        
        # Hash the password before saving
        validated_data['password'] = make_password(validated_data['password'])
        
        return User.objects.create(**validated_data)
    

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'date_joined')
        read_only_fields = ('id', 'date_joined')

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'description', 'created_at')
        read_only_fields = ('id', 'created_at')

class ExpenseSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Expenses
        fields = (
            'id', 'user', 'category', 'category_name', 'amount', 
            'description', 'date', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero")
        return value

class ExpenseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expenses
        fields = ('category', 'amount', 'description', 'date')
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero")
        return value

class ExpenseSummarySerializer(serializers.Serializer):
    total_spent = serializers.DecimalField(max_digits=12, decimal_places=2)
    categories = serializers.DictField()
    expense_count = serializers.IntegerField()
    date_range = serializers.DictField()

        

