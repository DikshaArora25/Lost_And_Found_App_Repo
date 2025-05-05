from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from migrateflask.models import  Item
from django.contrib.auth import get_user_model
User = get_user_model()


class RegisterForm(UserCreationForm):
    username = forms.CharField(required=True)  # Changed from 'username' to 'name'
    email = forms.EmailField(required=True)
    mobile = forms.CharField(required=True)
    password1 = forms.CharField(widget=forms.PasswordInput, required=True)  # Changed from 'password1'
    password2 = forms.CharField(widget=forms.PasswordInput, required=True)  # Changed from 'password2'

    class Meta:
        model = User
        fields = ['username', 'email', 'mobile', 'password1', 'password2']
        def save(self, commit=True):
            user = super().save(commit=False)
            user.is_staff = True  # Grant admin access
            user.is_active=True
            if commit:
                user.save()
            return user

from django import forms

class SearchForm(forms.Form):
    search = forms.CharField(required=False, label='Search by name')
    category = forms.ChoiceField(
        required=False,
        choices=[('', 'All Categories'), 
                 ('electronics', 'Electronics'), 
                 ('clothing', 'Clothing'),
                 ('accessories', 'Accessories'), 
                 ('jewelry', 'Jewelry'), 
                 ('documents', 'Documents'),
                 ('pets', 'Pets'), 
                 ('toys', 'Toys'), 
                 ('tools', 'Tools'), 
                 ('sports', 'Sports Equipment'),
                 ('others', 'Others')]
    )
    date = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Search by date'
    )
    location = forms.CharField(required=False, label='Search by location')
    sort = forms.ChoiceField(
        required=False,
        choices=[('date', 'Date (newest first)'), ('name', 'Name (A-Z)')],
        label='Sort by'
    )

    # Optional: You can override clean method to validate more complex logic
    def clean(self):
        cleaned_data = super().clean()
        search = cleaned_data.get('search')
        category = cleaned_data.get('category')
        location = cleaned_data.get('location')

        # You can add extra validation here if needed
        # For example, if you want to ensure that at least one filter is applied
        if not any([search, category, location]):
            raise forms.ValidationError("Please provide at least one search filter.")
        
        return cleaned_data

# User Login Form
class LoginForm(AuthenticationForm):
    username = forms.CharField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

# Item Submission Form
class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'description', 'category', 'date', 'location', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-md'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border rounded-md'}),
            'category': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded-md'}),
            'date': forms.DateInput(attrs={'class': 'w-full px-3 py-2 border rounded-md', 'type': 'date'}),
            'location': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-md'}),
            'image': forms.FileInput(attrs={'class': 'w-full px-3 py-2 border rounded-md'}),
        }

    def save(self, commit=True):
        item = super().save(commit=False)
        item.status = "lost"  # Default status assignment
        if commit:
            item.save()
        return item
    

from django import forms
from .models import ContactforClaim

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactforClaim
        fields = '__all__'
