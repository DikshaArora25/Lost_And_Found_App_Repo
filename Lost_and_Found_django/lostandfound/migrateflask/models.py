from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.db import models


class AppUserManager(BaseUserManager):
    def create_user(self, email, name, phone, address, gender, dob=None, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field is mandatory')
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            name=name,
            phone=phone,
            address=address,
            gender=gender,
            dob=dob,
            **extra_fields
        )
        
        user.set_password(password)
        
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, phone, address, gender, dob=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if not password:
            raise ValueError("Superusers must have a password.")
        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, name, phone, address, gender, dob, password, **extra_fields)


class AppUser(AbstractUser):
    role = models.CharField(max_length=50, default='user')
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    phone = models.CharField(
        max_length=10,  # Enforcing max length of 10
       
    )
    address = models.TextField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    dob = models.DateField(null=True, blank=True) 

    username = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'phone', 'address', 'gender', 'dob']

    objects = AppUserManager()
    
    def __str__(self):
        return self.email


from django.db import models
from django.conf import settings
class Item(models.Model):
    CATEGORY_CHOICES = [
        ('electronics', 'Electronics'),
        ('clothing', 'Clothing'),
        ('accessories', 'Accessories'),
        ('jewelry', 'Jewelry'),
        ('documents', 'Documents'),
        ('pets', 'Pets'),
        ('toys', 'Toys'),
        ('tools', 'Tools'),
        ('sports', 'Sports Equipment'),
        ('others', 'Others'),
    ]

    STATUS_CHOICES = [
        ('lost', 'Lost'),
        ('found', 'Found'),
        ('returned', 'Returned'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)


    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    date = models.DateField()
    location = models.CharField(max_length=255)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    image = models.ImageField(upload_to='items/', null=True, blank=True)
    flask_id = models.IntegerField(null=True, blank=True)
    

    def __str__(self):
        return self.name
from django.db import models
from django.conf import settings

class Claim(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,null=True, blank=True)


    item = models.ForeignKey(Item, on_delete=models.CASCADE, null=True, blank=True)


    submitted_at = models.DateTimeField(auto_now_add=True)  # OLD



from django.db import models

class ContactforClaim(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    product = models.CharField(max_length=100)
    description = models.TextField()
    date = models.DateField()
    location = models.CharField(max_length=200)
    image = models.ImageField(upload_to='claims/', null=True, blank=True)
    class Meta:
        verbose_name = 'ContactforClaim'
        verbose_name_plural = 'ContactforClaims'

    def __str__(self):
        return f"{self.name} - {self.product}"
