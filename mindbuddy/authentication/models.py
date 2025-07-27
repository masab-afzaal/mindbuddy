# authentication/models.py
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class UserManager(BaseUserManager):
    """Custom user manager for the custom User model"""
    
    def create_user(self, name, password=None, **extra_fields):
        """Create and return a regular user with a name and password"""
        if not name:
            raise ValueError('The Name field must be set')
        
        extra_fields.setdefault('is_active', True)
        user = self.model(name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, name, password=None, **extra_fields):
        """Create and return a superuser with a name and password"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(name, password, **extra_fields)

class User(AbstractUser):
    """Custom user model with just name and password"""
    # Remove email requirement and use name instead of username
    email = None  # Remove email field
    username = None  # Remove username field
    
    name = models.CharField(max_length=150, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = UserManager()  # Use custom manager
    
    USERNAME_FIELD = 'name'
    REQUIRED_FIELDS = []
    
    def __str__(self):
        return self.name