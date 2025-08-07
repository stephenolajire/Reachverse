from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from django.core.validators import MinValueValidator

# Used default django user model

# category model
class Category(models.Model) :
    # category name
    name = models.CharField(max_length=200, unique=True)
    # time created 
    created_at = models.DateTimeField(auto_now_add=True)
    # time updated
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

class Expenses (models.Model):
    # user that created the expenses
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses')
    # the category the expenses belong to
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='expenses_category')
    # amount spent
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    # expenses description
    description = models.TextField()
    # date of expense
    date = models.DateField()
    # date created or submitted
    created_at = models.DateTimeField(auto_now_add=True)
    # date updated or edited
    updated_at =  models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', 'category']

    def __str__(self):
        return f"{self.user} {self.category} {self.amount}"
    


