from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from .models import Item
from .forms import RegisterForm, LoginForm, ItemForm, SearchForm,ContactForm
from datetime import datetime
import re
import json
from functools import wraps
from django.core.exceptions import PermissionDenied

def superuser_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "Access Denied: Superuser privileges required.")
            return redirect('gallery')  # Replace 'gallery' with your desired redirect URL
    return _wrapped_view





User = get_user_model()
def index(request):
    return render(request, 'index.html')


from django.shortcuts import render, redirect
from django.contrib import messages
import requests

# def dashboard(request):
#     # Check if the token is in the session
#     token = request.session.get('auth_token')

#     if not token:
#         # If there's no token, user is not authenticated, so redirect to login
#         messages.error(request, 'Please login to access the dashboard.')
#         return redirect('login')  # Adjust 'login' to your actual login URL name

#     try:
#         # Send a GET request to the Flask backend with the token in the Authorization header
#         headers = {'Authorization': f'Bearer {token}'}
#         response = requests.get('http://localhost:5000/dashboard', headers=headers)

#         # Check the response from Flask
#         if response.status_code == 200:
#             # If the response is successful, pass the data to the template
#             data = response.json()
#             return render(request, 'dashboard.html', {'data': data})

#         else:
#             # Handle errors if the backend fails
#             messages.error(request, 'Failed to fetch dashboard data. Please try again.')
#             return redirect('login')  # Redirect to login if failed

#     except Exception as e:
#         # Handle any connection errors
#         messages.error(request, f"Error connecting to Flask API: {e}")
#         return redirect('login')  # Redirect to login if there's a connection issue


@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

@login_required
def search_view(request):
    search = request.GET.get('search', '')
    category = request.GET.get('category', '')
    date = request.GET.get('date', '')
    location = request.GET.get('location', '')
    status = request.GET.get('status', '')
    sort_by = request.GET.get('sort_by', '')

    # Start with all items
    items = Item.objects.all()

    # Build Q filters with AND logic for precision
    filters = Q()

    # Apply filters only if fields are provided
    if search:
        filters &= (Q(name__icontains=search) | Q(description__icontains=search))
    if category:
        filters &= Q(category__iexact=category)
    if date:
        filters &= Q(date=date)
    if location:
        filters &= Q(location__icontains=location)
    if status:
        filters &= Q(status__iexact=status)

    # Apply the combined filters
    if any([search, category, date, location, status]):
        items = items.filter(filters)

    # Apply sorting if provided
    if sort_by:
        items = items.order_by(sort_by)

    return render(request, 'search.html', {
        'items': items,
        'search': search,
        'category': category,
        'date': date,
        'location': location,
        'status': status,
        'sort_by': sort_by,
    })

import re
import requests
from django.contrib import messages
from django.shortcuts import render, redirect
from datetime import datetime

import re
import requests
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
User = get_user_model()

import re
import requests
from datetime import datetime
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model

User = get_user_model()

def register_view(request):
    form_data = {}

    if request.method == 'POST':
        # Capture form data
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('cpassword')
        mobile = request.POST.get('phone')
        address = request.POST.get('address')
        gender = request.POST.get('gender')
        dob_str = request.POST.get('dob')
        role = request.POST.get('role') or 'user'  # Default role if not specified

        dob = datetime.strptime(dob_str, '%Y-%m-%d').date() if dob_str else None

        form_data = {
            'name': name,
            'email': email,
            'phone': mobile,
            'address': address,
            'gender': gender,
            'dob': dob_str,
            'role': role,
        }

        has_error = False

        # Validation
        if not name:
            messages.error(request, 'Name is required.')
            has_error = True
        if not email:
            messages.error(request, 'Email is required.')
            has_error = True
        if not password or not confirm_password:
            messages.error(request, 'Password and confirm password are required.')
            has_error = True
        elif password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            has_error = True
        if not mobile:
            messages.error(request, 'Mobile number is required.')
            has_error = True
        elif not re.fullmatch(r'\d{10,15}', mobile):
            messages.error(request, 'Enter a valid mobile number (10 to 15 digits).')
            has_error = True

        # Password strength
        if password:
            password_errors = []
            if len(password) < 8:
                password_errors.append("Password must be at least 8 characters long.")
            if not re.search(r"[A-Z]", password):
                password_errors.append("Must include at least one uppercase letter.")
            if not re.search(r"[a-z]", password):
                password_errors.append("Must include at least one lowercase letter.")
            if not re.search(r"\d", password):
                password_errors.append("Must include at least one number.")
            if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
                password_errors.append("Must include at least one special character.")
            for err in password_errors:
                messages.error(request, err)
            has_error = has_error or bool(password_errors)

        if not has_error:
            try:
                # Send data to Flask API
                data = {
                    'name': name,
                    'email': email,
                    'password': password,
                    'confirm_password': confirm_password,
                    'mobile': mobile,
                    'role': role
                }

                headers = {'Content-Type': 'application/json'}
                response = requests.post('http://localhost:5000/api/register', json=data, headers=headers)

                print(f"Flask Response Status: {response.status_code}")
                print(f"Flask Response Body: {response.text}")

                if response.status_code == 201:
                    # Save to Django
                    user = User.objects.create(
                        name=name,
                        email=email,
                        password=password,  # Replace with hash in production
                        phone=mobile,
                        address=address,
                        gender=gender,
                        dob=dob
                    )
                    messages.success(request, 'Registration successful via Flask and saved in Django!')
                    return redirect('login')
                else:
                    resp_json = response.json()
                    error_msg = resp_json.get('error') or 'Registration failed. Try again.'
                    messages.error(request, f'Flask API Error: {error_msg}')
            except requests.exceptions.RequestException as e:
                messages.error(request, f"Error connecting to Flask API: {e}")

    return render(request, 'register.html', {'form_data': form_data})



import requests
from django.shortcuts import render, redirect
from django.contrib import messages




from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as django_login
from django.contrib.auth import get_user_model
import requests

User = get_user_model()

def login_view(request):
    form_data = {}
    
    if request.method == 'POST':
        # Capture the form data (username and password)
        username = request.POST.get('username')  # Capture email as the username
        password = request.POST.get('password')
        role = request.POST.get('role')
        
        form_data = {
            'username': username,
        }

        has_error = False

        # Form validation
        if not username:
            messages.error(request, 'Email is required.')
            has_error = True
        if not password:
            messages.error(request, 'Password is required.')
            has_error = True
        if not role:
            messages.error(request, 'Role is required.')
            has_error = True

        if not has_error:
            try:
                # Send login request to Flask API
                data = {
                    'email': username,
                    'password': password,
                    'role': role,
                }

                headers = {'Content-Type': 'application/json'}
                response = requests.post('http://localhost:5000/api/login', json=data, headers=headers)

                print(response.json())  # Debug: Check the exact response from Flask

                if response.status_code == 200:
                    # Extract the access token from the response
                    resp_json = response.json()
                    token = resp_json.get('access_token')

                    # Save token in session
                    request.session['auth_token'] = token
                    
                    # IMPORTANT: Also authenticate the user in Django
                    # Find user in Django's database or create if not exists
                    user = User.objects.filter(email=username).first()
                    if user:
                        # Log the user into Django's authentication system
                        django_login(request, user)
                    else:
                        # If user doesn't exist in Django DB but exists in Flask,
                        # you might want to create them or handle this case
                        messages.warning(request, 'User exists in Flask but not in Django database.')
                        # Optional: Create user in Django DB here

                    # Set success message
                    messages.success(request, f'Welcome {username}!')

                    # Get 'next' parameter and redirect the user
                    next_url = request.GET.get('next', 'dashboard')
                    return redirect(next_url)

                else:
                    # Handle error if login fails
                    resp_json = response.json()
                    error_msg = resp_json.get('message') or 'Login failed. Check your credentials.'
                    messages.error(request, f'Flask API Error: {error_msg}')

            except Exception as e:
                # Handle errors when connecting to Flask API
                messages.error(request, f"Error connecting to Flask API: {e}")

    return render(request, 'login.html', {'form_data': form_data})
# views.py
import requests
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Item
from django.contrib.auth.decorators import login_required

# @login_required
# def report_item(request, status):
#     if request.method == 'POST':
#         # Extract form data
#         name = request.POST.get('name')
#         description = request.POST.get('description')
#         category = request.POST.get('category')
#         date = request.POST.get('date_string')
#         location = request.POST.get('location')
#         image = request.FILES.get('image')

#         # Save to Django DB
#         item = Item.objects.create(
#             user=request.user,
#             name=name,
#             description=description,
#             category=category,
#             date=date,
#             location=location,
#             image=image,
#             status=status
#         )

#         # Prepare data for Flask API
#         data = {
#             'item_name': name,  # match Flask expectation
#             'description': description,
#             'category': category,
#             'date': date,
#             'location': location,
#         }
     


#         files = {}
#         if image:
#             files['image'] = (image.name, image.read(), image.content_type)

#         # ✅ Add debug prints here
#         print("📤 Sending to Flask:", data)
#         print("📎 Sending file:", image.name if image else "No image")

#         flask_url = f'http://localhost:5000/report-{status}'  # Flask API URL
#         response = requests.post(flask_url, data=data, files=files)

#         if response.status_code == 201:
#             return redirect('/dashboard/')  # Redirect to dashboard after successful submission
#         else:
#             return HttpResponse(f"Flask error: {response.text}", status=500)

#     return render(request, 'dashboard.html')


import requests
from django.shortcuts import render, redirect
from django.http import HttpResponse

from .models import Item  # your Django Item model
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import requests
from django.http import HttpResponse
from .models import Item  # Import your model

@login_required
def report_item(request, status):
    if request.method == 'POST':
        data = {
            'item_name': request.POST.get('name'),
            'description': request.POST.get('description'),
            'category': request.POST.get('category'),
            'date': request.POST.get('date_string'),
            'location': request.POST.get('location'),
            'user_id': request.user.id,  # Use the logged-in user's ID
        }
        
        image = request.FILES.get('image')
        files = {'image': image} if image else {}

        flask_url = f'http://localhost:5000/report-{status}'
        
        try:
            response = requests.post(flask_url, data=data, files=files)

            print(f"Flask response code: {response.status_code}")
            print(f"Flask response content: {response.text}")

            if response.status_code == 201:
                flask_response = response.json()
                flask_id = flask_response.get('id')  # Ensure Flask returns ID
                print(f"Received Flask ID: {flask_id}")

                # Create Django item with same ID as Flask
                item = Item(
                    flask_id=flask_id,
                    name=data['item_name'],
                    description=data['description'],
                    category=data['category'],
                    date=data['date'],
                    location=data['location'],
                    image=image,
                    status=status
                )
                item.save()
                print("Saved item in Django:", item)

                messages.success(request, f"Item successfully reported as {status}.")
                return redirect('/dashboard/')

            else:
                messages.error(request, f"Error from Flask API: {response.text}")
                return HttpResponse(f"Flask error: {response.text}", status=500)

        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return HttpResponse(f"Error: {str(e)}", status=500)

    return render(request, 'dashboard.html')



@login_required
def gallery(request):
    items = Item.objects.all()

    for item in items:
        item.can_edit = request.user.is_superuser or item.user == request.user

    return render(request, 'gallery.html', {'items': items})



from django.contrib import messages


import requests
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from .models import Item  # Your Django Item model

# import requests
# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib import messages
# from .models import Item
# def edit_item(request, item_id):
#     item = get_object_or_404(Item, id=item_id)

#     if request.method == 'POST':
#         # Update Django database
#         item.name = request.POST['item_name']
#         item.description = request.POST['description']
#         item.category = request.POST['category']
#         item.date = request.POST['date']
#         item.location = request.POST['location']
#         item.status = request.POST['status']

#         if 'image' in request.FILES and request.FILES['image']:
#             item.image = request.FILES['image']

#         item.save()

#         # ✅ Use Flask ID (not Django ID)
#         flask_id = item.flask_id
#         if flask_id:  # Ensure it's not None
#             flask_url = f'http://localhost:5000/api/edit/{flask_id}'
#             data = {
#                 'item_name': item.name,
#                 'description': item.description,
#                 'category': item.category,
#                 'date': item.date,
#                 'location': item.location,
#                 'status': item.status,
#             }

#             files = {}
#             if 'image' in request.FILES and request.FILES['image']:
#                 files['image'] = request.FILES['image']

#             try:
#                 response = requests.post(flask_url, data=data, files=files)
#                 if response.status_code not in (200, 204):
#                     messages.warning(request, f'Flask update failed: {response.text}')
#             except Exception as e:
#                 messages.warning(request, f'Error communicating with Flask: {str(e)}')
#         else:
#             messages.warning(request, 'No linked Flask item to update.')

#         messages.success(request, 'Item updated successfully!')
#         return redirect('gallery')

#     return render(request, 'edit_item.html', {'item': item})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
import requests
from .models import Item

def edit_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    
    if request.method == 'POST':
        # Update Django database
        item.name = request.POST['item_name']
        item.description = request.POST['description']
        item.category = request.POST['category']
        item.date = request.POST['date']
        item.location = request.POST['location']
        item.status = request.POST['status']
        
        # Handle image upload for Django
        if 'image' in request.FILES and request.FILES['image']:
            item.image = request.FILES['image']
        
        item.save()
        
        # Update Flask database using API
        flask_id = item.flask_id
        if flask_id:  # Ensure it's not None
            flask_url = f'http://localhost:5000/api/edit/{flask_id}'
            
            # Prepare data for Flask API
            data = {
                'item_name': item.name,
                'description': item.description,
                'category': item.category,
                'date': str(item.date),  # Convert date to string if it's a date object
                'location': item.location,
                'status': item.status,
            }
            
            # Properly handle file upload for Flask
            files = {}
            if 'image' in request.FILES and request.FILES['image']:
                # Save the file temporarily and open it in binary mode for Flask
                import tempfile
                import os
                
                # Create a temporary file
                temp_handle, temp_path = tempfile.mkstemp()
                try:
                    with os.fdopen(temp_handle, 'wb') as temp_file:
                        for chunk in request.FILES['image'].chunks():
                            temp_file.write(chunk)
                    
                    # Open the temp file in binary mode for Flask
                    with open(temp_path, 'rb') as img_file:
                        files = {
                            'image': (
                                request.FILES['image'].name,
                                img_file,
                                request.FILES['image'].content_type
                            )
                        }
                        
                        # Send request with file
                        response = requests.post(flask_url, data=data, files=files)
                finally:
                    # Clean up the temporary file
                    os.remove(temp_path)
            else:
                # No image, just send regular POST
                response = requests.post(flask_url, data=data)
            
            try:
                # The response variable is already set in the files handling section
                # for the image upload case, so we only need to check it here
                
                if not 'response' in locals():
                    # This means no file was uploaded, so make the request now
                    response = requests.post(flask_url, data=data)
                
                if response.status_code not in (200, 204):
                    messages.warning(request, f'Flask update failed: {response.text}')
                else:
                    messages.success(request, 'Item updated successfully in both Django and Flask!')
            except Exception as e:
                messages.warning(request, f'Error communicating with Flask: {str(e)}')
                # Item was still updated in Django
                messages.success(request, 'Item updated in Django but failed to update in Flask.')
        else:
            messages.warning(request, 'No linked Flask item to update.')
            messages.success(request, 'Item updated in Django only.')
        
        return redirect('gallery')
    
    return render(request, 'edit_item.html', {'item': item})

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
import requests
from .models import Item

@login_required
@superuser_required
def delete_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    # Get corresponding Flask item ID
    flask_id = item.flask_id

    # First, delete from Django
    item.delete()
    messages.success(request, "Item deleted successfully!")

    # Then, try to delete from Flask via DELETE API
    if flask_id:
        try:
            flask_url = f'http://localhost:5000/api/delete/{flask_id}'
            response = requests.delete(flask_url)

            if response.status_code != 200:
                messages.warning(request, f"Flask deletion failed: {response.text}")
        except Exception as e:
            messages.warning(request, f"Error connecting to Flask API: {str(e)}")
    else:
        messages.warning(request, "No linked Flask item to delete.")

    return redirect('gallery')



from django.core.mail import send_mail
from django.conf import settings
import requests
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ContactForm

@login_required
def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST, request.FILES)
        if form.is_valid():
            claim = form.save(commit=False)

            try:
                # Send claim data to Flask API
                response = requests.post(
                    'http://localhost:5000/api/contact',  # Replace with actual Flask server URL
                   data = {
    'name': claim.name,
    'email': claim.email,
    'phone': claim.phone,
    'product': claim.product,
    'description': claim.description,
    'location': claim.location,
    'date': claim.date.strftime('%Y-%m-%d')
}

                )

                res_data = response.json()
                if response.status_code == 200:
                    messages.success(request, 'Your claim has been submitted successfully!')
                else:
                    messages.error(request, f"Flask API error: {res_data.get('message')}")

            except Exception as e:
                messages.error(request, f"Failed to submit claim: {e}")

            return redirect('contact')
    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form})




@login_required
def profile(request):
    user_role = 'admin' if request.user.is_superuser else 'user'
    return render(request, 'profile.html', {'user': request.user, 'role': user_role})

import requests
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages

@login_required
def edit_profile(request):
    user = request.user

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')

        try:
            # Send data to Flask API
            response = requests.post(
                'http://localhost:5000/api/edit_profile',  # Change to your Flask server URL
                data={
                    'name': name,
                    'email': email,
                    'mobile': phone
                },
                cookies=request.COOKIES  # if using session-based auth with Flask
            )

            res_data = response.json()
            if response.status_code == 200 and res_data.get('status') == 'success':
                messages.success(request, 'Profile updated successfully!')
            else:
                messages.error(request, f"Flask API error: {res_data.get('message')}")

        except Exception as e:
            messages.error(request, f"Failed to update profile: {e}")

        return redirect('edit_profile')

    return render(request, 'edit_profile.html', {
        'user': user,
        'role': user.role  # Display only
    })



# @login_required
# @csrf_exempt
# def claim_item(request, item_id):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             email = data.get('email')
#             phone = data.get('phone')

#             if not email or not phone:
#                 return JsonResponse({'status': 'error', 'message': 'Missing email or phone.'})

#             item = Item.objects.get(id=item_id)

#             # Format the email content
#             subject = "🛠 Lost & Found Claim Received – We’re on it!"
#             message = f"""
# Hello,

# Thank you for submitting a claim for the item you believe is yours.

# We've received your contact details and have noted your interest in the item. Our team will now review your claim and verify the details. If everything checks out, we'll get in touch with you shortly to arrange the return.

# Here’s a quick summary of what happens next:
# - Our team will match the provided details with the item: "{item.name}" found at "{item.location}" on {item.date}.
# - If there’s a match, we’ll contact you via this email or phone number.
# - You may be asked to provide additional proof of ownership, if necessary.

# We appreciate your patience and honesty in helping us return lost items to their rightful owners.

# Warm regards,  
# LostNoMore Team  
# {settings.DEFAULT_FROM_EMAIL}
# """

#             send_mail(
#                 subject,
#                 message,
#                 settings.DEFAULT_FROM_EMAIL,
#                 [email],
#                 fail_silently=False,
#             )

#             return JsonResponse({'status': 'success', 'message': 'Claim submitted.'})

#         except Exception as e:
#             return JsonResponse({'status': 'error', 'message': str(e)})

#     return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

@login_required
@csrf_exempt
def claim_item(request, item_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            phone = data.get('phone')

            if not email or not phone:
                return JsonResponse({'status': 'error', 'message': 'Missing email or phone.'})

            item = Item.objects.get(id=item_id)

            subject = "🛠 Lost & Found Claim Received – We’re on it!"
            message = f"""
Hello,

Thank you for submitting a claim for the item you believe is yours.

Item: "{item.name}"  
Location: "{item.location}"  
Date: {item.date}

We'll contact you soon.

– LostNoMore Team
"""

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )

            return JsonResponse({'status': 'success', 'message': 'Claim submitted.'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    else:
        # GET request - show a claim template (or even redirect to gallery if you want)
        item = get_object_or_404(Item, id=item_id)
        return render(request, 'gallery.html', {'item': item})



@login_required
def logout_view(request):
    logout(request)  # Log out the user
    return redirect('index')  # Redirect to homepage or another page






from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.dateparse import parse_date
import json
import re
from datetime import datetime, timedelta
from django.db.models import Q
from .models import Item


# Format function for item details with claim link
def format_items(items, title="Items found"):
    if not items:
        return f"<strong>{title}:</strong> No items found matching your query.<br>"

    formatted_items = f"<strong>{title}:</strong><br><br>"
    for item in items:
        formatted_items += (
            f"🔹 <strong>{item.name}</strong><br>"
            f"📍 <strong>Location:</strong> {item.location}<br>"
            f"📅 <strong>Date:</strong> {item.date}<br>"
            f"📝 <strong>Description:</strong> {item.description}<br>"
            f"🗂 <strong>Category:</strong> {item.category.capitalize()}<br>"
            f"🔄 <strong>Status:</strong> {item.status.capitalize()}<br>"
            f"🔗 <a href='/claim/{item.id}' target='_blank'>Claim this item</a><br>"
            f"{'-'*40}<br><br>"
        )
    return formatted_items


@csrf_exempt
@require_POST
def chatbot_query(request):
    data = json.loads(request.body)
    user_message = data.get('message', '').lower().strip()

    if not user_message:
        return JsonResponse({'response': "Please describe the item you're looking for."})

    today = datetime.today().date()

    # Time-based filters
    if "yesterday" in user_message:
        query_date = today - timedelta(days=1)
        items = Item.objects.filter(date=query_date)
        return JsonResponse({'response': format_items(items, f"Items reported on {query_date}")})

    if "last 7 days" in user_message or "past 7 days" in user_message:
        week_ago = today - timedelta(days=7)
        items = Item.objects.filter(date__gte=week_ago)
        return JsonResponse({'response': format_items(items, "Items from the past 7 days")})

    match = re.search(r'on (\d{1,2})', user_message)
    if match:
        day = int(match.group(1))
        items = Item.objects.filter(date__day=day)
        return JsonResponse({'response': format_items(items, f"Items from day {day}")})

    # Category detection
    category_map = {
        "pet": ["dog", "cat", "puppy", "kitten", "parrot", "pets"],
        "electronics": ["laptop", "phone", "tablet", "charger"],
        "documents": ["id", "card", "aadhaar", "pan", "license"],
        "accessories": ["hair", "clip", "ring", "watch"],
        "clothing": ["jacket", "sweater", "saree", "shirt", "cap"],
    }

    matched_category = None
    for category, keywords in category_map.items():
        if any(word in user_message for word in keywords):
            matched_category = category
            break

    # Location detection
    location_keywords = ["pythagoras", "turing", "alpha", "pi", "block", "zone"]
    matched_location = None
    for loc in location_keywords:
        if loc in user_message:
            matched_location = loc
            break

    # Build query
    query = Q()
    if matched_category:
        query &= Q(category__iexact=matched_category)
    if matched_location:
        query &= Q(location__icontains=matched_location)

    if not matched_category and not matched_location:
        keywords = re.findall(r'\b\w+\b', user_message)
        for word in keywords:
            query |= Q(name_icontains=word) | Q(descriptionicontains=word) | Q(location_icontains=word)

    items = Item.objects.filter(query).distinct()[:5]
    return JsonResponse({'response': format_items(items, "Here are some matching items")})