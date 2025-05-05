from flask import Flask, render_template, redirect, request, url_for, flash,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from datetime import datetime
import os
from flask import jsonify, request
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash
import datetime
from flask_jwt_extended import JWTManager
from datetime import datetime



basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['SECRET_KEY'] = 'Your secret key'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
app = Flask(__name__, static_url_path='/static', static_folder='static')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['SECRET_KEY'] = 'Your secret key'
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'  # 🔐 REQUIRED for JWT


db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)  # ✅ Initialize JWT manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(100), nullable=False)
    mobile = db.Column(db.String(15), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='user')

    def set_password(self, password):
     self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
     return bcrypt.check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(10), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(10), nullable=False)



class Claim(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    product = db.Column(db.String(100))
    description = db.Column(db.Text)
    location = db.Column(db.String(200))
    date = db.Column(db.String(50))  # or db.Date, if you're handling date parsing
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
 
from flask_mail import Mail, Message

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'dikshasharma162005@gmail.com'
app.config['MAIL_PASSWORD'] = 'posh avha ylru mtgr'  # Use an app password, not your actual Gmail password
app.config['MAIL_DEFAULT_SENDER'] = 'dikshasharma162005@gmail.com'

mail = Mail(app)


with app.app_context():
    db.create_all()

    # Always remove existing admin user (if any)
    existing_admin = User.query.filter_by(email="diksha@gmail.com", role="admin").first()
    if existing_admin:
        db.session.delete(existing_admin)
        db.session.commit()

    # Create and commit a fresh admin user
    admin_user = User(name="diksha", email="diksha@gmail.com",
                      mobile="9478622626", role="admin")
    admin_user.set_password("Diksha@123")
    db.session.add(admin_user)
    db.session.commit()
    print("✅ Admin user recreated.")

        
        
       

from functools import wraps

def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.role != 'admin':
            flash("Access denied!", "danger")
            return redirect(url_for('dashboard'))
        return func(*args, **kwargs)
    return wrapper



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')

        # Modify the user query to also check for the role
        user = User.query.filter_by(email=email, role=role).first()

        if user and user.check_password(password):
            login_user(user)

            # Flash messages based on the role of the user
            if user.role == 'admin':
                flash('Welcome, Diksha!', 'success')  # Admin message
            else:
                flash('Login successful!', 'success')  # Regular user message

            # Redirect to the dashboard
            return redirect(url_for('dashboard'))  # Replace 'dashboard' with the correct endpoint

        else:
            # If credentials are incorrect
            flash('Invalid credentials!', 'danger')

    # Render the login page for GET request
    return render_template('login.html')

# @app.route('/api/login', methods=['GET', 'POST'])
# def api_login():
#  if request.method == 'POST':
#         data = request.get_json()
#         # Get email and password from the form data
#         email = data.get('email')
#         password =data.get('password')
#     # Check if email and password are provided
#         if not email or not password:
#             return jsonify({"message": "Email and password are required.", "status": "error"}), 400

# # Find the user in the database
#         user = User.query.filter_by(email=email).first()

#         if not user or not user.check_password(password):
#              return jsonify({"message": "Invalid email or password.", "status": "error"}), 401

# # Log the user in
#         login_user(user)

# # Return success response with user email
#         return jsonify({"message": f"Welcome back, {user.email}!", "status": "success",
#                          'redirect_url': url_for('dashboard')}), 200
#  # Redirect to the dashboard after login

#  return render_template('login.html')  # Render login page if it's a GET request

import jwt
from datetime import datetime, timedelta

# Add a secret key for JWT token generation
SECRET_KEY = 'your-secret-key'

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"message": "Email and password are required.", "status": "error"}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({"message": "Invalid email or password.", "status": "error"}), 401

    login_user(user)

    # Create JWT token
    token = jwt.encode({
        'sub': user.id,
        'exp': datetime.utcnow() + timedelta(hours=1)  # Token expiry time
    }, SECRET_KEY, algorithm='HS256')

    return jsonify({
        "message": f"Welcome back, {user.email}!",
        "status": "success",
        "access_token": token  # Send the token
    }), 200





@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        mobile = request.form.get('mobile')
        role = request.form.get('role')

        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash('Email already exists!', 'danger')
            return redirect(url_for('register'))

        new_user = User(name=name, email=email, mobile=mobile, role=role)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()

    # Validate required fields
    required_fields = ['name', 'email', 'password', 'confirm_password', 'mobile', 'role']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    name = data['name']
    email = data['email']
    password = data['password']
    confirm_password = data['confirm_password']
    mobile = data['mobile']
    role = data['role']

    # Check if passwords match
    if password != confirm_password:
        return jsonify({'error': 'Passwords do not match'}), 400

    # Check if email already exists
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 400

    # Create new user instance without password
    new_user = User(name=name, email=email, mobile=mobile, role=role)
    new_user.set_password(password)  # Set and hash the password

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201


# import uuid
# from werkzeug.utils import secure_filename

# import os
# from werkzeug.utils import secure_filename

# def save_image(image):
#     # Secure the filename to prevent directory traversal attacks
#     filename = secure_filename(image.filename)
    
#     # Construct the path where the image will be saved
#     filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
#     # Save the image to the file system
#     image.save(filepath)
    
#     return filename


# @app.route('/report-<status>', methods=['POST'])
# def report_item(status):
#     try:
#         if status not in ['lost', 'found']:
#             return jsonify({'success': False, 'error': 'Invalid status'}), 400

        

#         image_file = request.files.get('image')
#         image_path = save_image(image_file) if image_file else None
#         print("📦 File saved at:", image_path)
#         item = Item(
#         name=request.form['item_name'],
#         description=request.form['description'],
#         category=request.form['category'],
#         date=request.form['date'],
#         location=request.form['location'],
#         image=image_path,  # This must be a string path (e.g., 'static/uploads/img.jpg')
#         status=status
#     )

        
#         db.session.add(item)
#         db.session.commit()
#         db.session.remove()
       
#         return jsonify({'success': True, 'message': f'Item reported as {status}'}), 201
       

#     except Exception as e:
#         print("Error in Flask:", str(e))
#         return jsonify({'success': False, 'error': str(e)}), 400
def save_image(image):
    filename = image.filename
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image.save(filepath)
    return filename

from flask_login import current_user



@app.route('/report-lost', methods=['POST'])
@app.route('/report-found', methods=['POST'])

def report_item():
    try:
        status = 'lost' if request.path == '/report-lost' else 'found'

        image_file = request.files.get('image')
        image_path = save_image(image_file) if image_file else None

        item = Item(
            name=request.form['item_name'],
            description=request.form['description'],
            category=request.form['category'],
            date=request.form['date'],
            location=request.form['location'],
            image=image_path,
            status=status,
            
        )

        db.session.add(item)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Item successfully reported as {status}.',
            'redirect_url': url_for('gallery'),
            'id': item.id
        }), 201

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/gallery')
@login_required
def gallery():
    items = Item.query.all()
    return render_template('gallery.html', items=items)


@app.route('/edit/<int:item_id>', methods=['GET', 'POST'])
@login_required

def edit_item(item_id):
    item = Item.query.get_or_404(item_id)
    if request.method == 'POST':
        item.name = request.form['item_name']
        item.description = request.form['description']
        item.category = request.form['category']
        item.date = request.form['date']
        item.location = request.form['location']
        if 'image' in request.files and request.files['image'].filename != '':
            item.image = save_image(request.files['image'])
        item.status = request.form['status']
        db.session.commit()
        return redirect(url_for('gallery'))
    return render_template('edit_item.html', item=item)

@app.route('/delete/<int:item_id>', methods=['POST'])
@login_required
@admin_required

def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('gallery'))

@app.route('/api/edit/<int:item_id>', methods=['POST'])
def api_edit_item(item_id):
    item = Item.query.get_or_404(item_id)

    # Update item fields
    item.name = request.form.get('item_name')
    item.description = request.form.get('description')
    item.category = request.form.get('category')
    item.date = request.form.get('date')
    item.location = request.form.get('location')
    item.status = request.form.get('status')

    # If new image is uploaded
    if 'image' in request.files and request.files['image'].filename != '':
        item.image = save_image(request.files['image'])

    try:
        db.session.commit()
        return jsonify({'success': True, 'message': 'Item updated in Flask DB'}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    

from flask import jsonify, request
from flask_jwt_extended import jwt_required


from flask import jsonify


@app.route('/api/delete/<int:item_id>', methods=['DELETE'])
@login_required
@admin_required
def api_delete_item(item_id):
    item = Item.query.get_or_404(item_id)

    try:
        db.session.delete(item)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Item deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500







@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'info')
    return redirect(url_for('login'))

@app.route('/contact')
def contact():
    return render_template('contact.html')
from flask import request, jsonify
from flask_mail import Message
 # Your SQLAlchemy model for claims

@app.route('/api/contact', methods=['POST'])
def api_contact():
    try:
        data = request.form

        # Save claim to DB
        claim = Claim(
            name=data.get('name'),
            email=data.get('email'),
            phone=data.get('phone'),
            product=data.get('product'),
            description=data.get('description'),
            location=data.get('location'),
            date=data.get('date')
        )
        db.session.add(claim)
        db.session.commit()

        # Send email
        msg = Message(
            subject="✅ Claim Submission Received – LostNoMore",
            sender=app.config['MAIL_USERNAME'],
            recipients=[claim.email],
            body=f"""
Hi {claim.name},

Thank you for submitting a claim for the lost item.

Here are the details you submitted:
- Item Name: {claim.product}
- Description: {claim.description}
- Location Lost: {claim.location}
- Date: {claim.date}
- Your Phone: {claim.phone}

Our team will review the details and contact you shortly through a phone call. 
You can expect an update within the next 36 hours if the item is found.

Thanks for trusting LostNoMore.

Warm regards,  
LostNoMore Team  
{app.config['MAIL_USERNAME']}
"""
        )
        mail.send(msg)

        return jsonify({'status': 'success', 'message': 'Claim submitted and email sent!'}), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        current_user.name = request.form.get('name')
        current_user.email = request.form.get('email')
        current_user.mobile = request.form.get('mobile')
        current_user.role = request.form.get('role')
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    return render_template('edit_profile.html', user=current_user)

from flask import request, jsonify
from flask_login import login_required, current_user


 # replace with your actual model

@app.route('/api/edit_profile', methods=['POST'])
@login_required
def api_edit_profile():
    try:
        data = request.form  # or request.json if you're sending JSON
        current_user.name = data.get('name', current_user.name)
        current_user.email = data.get('email', current_user.email)
        current_user.mobile = data.get('mobile', current_user.mobile)
        current_user.role = current_user.role  # role not editable

        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Profile updated successfully!',
            'user': {
                'name': current_user.name,
                'email': current_user.email,
                'mobile': current_user.mobile,
                'role': current_user.role
            }
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Update failed: {str(e)}'
        }), 500

@app.route('/all-claims')
def all_claims():
    claims = Claim.query.all()
    return render_template('all_claims.html', claims=claims)



@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    if request.method == 'GET':
        return render_template('search.html', items=[])
    elif request.method == 'POST':
        data = request.get_json()
        search = data.get('search', '')
        category = data.get('category', '')
        date = data.get('date', '')
        location = data.get('location', '')
        sort = data.get('sort', 'date')

        # Build query
        items_query = Item.query

        if search:
            items_query = items_query.filter(Item.name.ilike(f'%{search}%') | Item.description.ilike(f'%{search}%'))
        if category:
            items_query = items_query.filter_by(category=category)
        if date:
            items_query = items_query.filter_by(date=date)
        if location:
            items_query = items_query.filter(Item.location.ilike(f'%{location}%'))

        if sort == 'date':
            items_query = items_query.order_by(Item.date)
        elif sort == 'name':
            items_query = items_query.order_by(Item.name)

        items = items_query.all()

        results = [
            {
                'name': item.name,
                'description': item.description,
                'category': item.category,
                'date': item.date,
                'location': item.location,
                'image': url_for('static', filename='uploads/' + item.image),
                'status': item.status
            }
            for item in items
        ]

        return jsonify(results)



from flask_migrate import Migrate
migrate = Migrate(app, db)


if __name__ == '__main__':
    app.run(debug=True)
