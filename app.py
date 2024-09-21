from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import firebase_admin
from firebase_admin import credentials, firestore, auth
import os
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import re
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash



# Load environment variables from .env file
load_dotenv()

# Initialize Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['FIREBASE_CREDENTIALS'] = os.getenv('FIREBASE_CREDENTIALS')
app.config['UPLOAD_FOLDER'] = 'static/images/user_photos/'
app.config['CANDI_UPLOAD_FOLDER'] = 'static/images/candidate_photos/'
UPLOAD_FOLDER = 'static/images/candidate_photos/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Initialize Firebase
cred = credentials.Certificate(app.config['FIREBASE_CREDENTIALS'])
firebase_admin.initialize_app(cred)
db = firestore.client()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return redirect(url_for('header'))  # Redirect to the header page

@app.route('/header')
def header():
    return render_template('header.html')  # Make sure you have 'header.html'

# admin pages

# Admin credentials (use environment variables or another secure method in production)
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
ADMIN_PASSWORD_HASH = generate_password_hash(os.getenv('ADMIN_PASSWORD'))



@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        try:
            # Send password reset email
            auth.send_password_reset_email(email)
            return jsonify({"message": "Password reset email sent"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    
    return render_template('forgot_password.html')


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return "Invalid username or password", 401
    
    return render_template('admin_login.html')
@app.route('/admin/dashboard')
def admin_dashboard():
    # Fetch candidates from Firestore
    candidates_ref = db.collection('candidates')
    candidates = candidates_ref.stream()

    candidates_list = []
    for candidate in candidates:
        candidate_dict = candidate.to_dict()
        candidates_list.append(candidate_dict)

    return render_template('admin_dashboard.html', candidates=candidates_list)

@app.route('/admin/add_candidate', methods=['POST'])
def add_candidate():
    name = request.form.get('candidate_name')
    description = request.form.get('candidate_description')
    
    # Handle file upload
    if 'candidate_image' in request.files:
        image = request.files['candidate_image']
        if image:
            image_filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['CANDI_UPLOAD_FOLDER'], image_filename)
            image.save(image_path)
            image_url = f'candidate_photos/{image_filename}'
        else:
            image_url = ''
    else:
        image_url = ''

    try:
        # Add the candidate to Firestore
        candidate_ref = db.collection('candidates').document(name)
        candidate_ref.set({
            'name': name,
            'description': description,
            'image': image_url,
            'votes': '0'  # Initialize votes to 0
        })
        
        return redirect(url_for('admin_dashboard'))
    except Exception as e:
        return f"An error occurred: {str(e)}", 500

# @app.route('/forgot_password', methods=['GET', 'POST'])
# def forgot_password():
#     if request.method == 'POST':
#         email = request.form['email']
#         try:
#             # Send password reset email
#             auth.send_password_reset_email(email)
#             return jsonify({"message": "Password reset email sent"}), 200
#         except Exception as e:
#             return jsonify({"error": str(e)}), 400
    
#     return render_template('forgot_password.html')

# @app.route('/admin/add_candidate', methods=['POST'])
# def add_candidate():
#     name = request.form.get('candidate_name')
#     description = request.form.get('candidate_description')
    
#     # Handle file upload
#     if 'candidate_image' in request.files:
#         image = request.files['candidate_image']
#         if image:
#             image_filename = secure_filename(image.filename)
#             image_path = os.path.join(app.config['CANDI_UPLOAD_FOLDER'], image_filename)
#             image.save(image_path)
#             image_url = f'candidate_photos/{image_filename}'
#         else:
#             image_url = ''
#     else:
#         image_url = ''

#     try:
#         # Add the candidate to Firestore
#         candidate_ref = db.collection('candidates').document(name)
#         candidate_ref.set({
#             'name': name,
#             'description': description,
#             'image': image_url,
#             'votes': '0'  # Initialize votes to 0
#         })
        
#         return redirect(url_for('admin_dashboard'))
#     except Exception as e:
#         return f"An error occurred: {str(e)}", 500

    
#     return render_template('admin_dashboard.html', candidates=candidates_list)

# @app.route('/admin/dashboard')
# def admin_dashboard():
#     if 'admin_logged_in' not in session:
#         return redirect(url_for('admin_login'))
    
#     # Fetch candidates from Firestore
#     candidates_ref = db.collection('candidates')
#     candidates = candidates_ref.stream()
#     candidates_list = [candidate.to_dict() for candidate in candidates]
    
#     return render_template('admin_dashboard.html', candidates=candidates_list)

# @app.route('/admin/add_candidate', methods=['POST'])
# def add_candidate():
#     if 'admin_logged_in' not in session:
#         return redirect(url_for('admin_login'))

#     candidate_name = request.form.get('candidate_name')
#     candidate_description = request.form.get('candidate_description', '')
#     candidate_image = request.form.get('candidate_image', '')

#     if candidate_name:
#         candidates_ref = db.collection('candidates').document(candidate_name)
#         candidates_ref.set({
#             'name': candidate_name,
#             'description': candidate_description,
#             'image': candidate_image,
#             'votes': 0
#         })
    
#     return redirect(url_for('admin_dashboard'))

# @app.route('/add_candidate', methods=['POST'])
# def add_candidate():
#     try:
#         # Get form data
#         name = request.form.get('candidate_name')
#         description = request.form.get('candidate_description')

#         # Handle file upload
#         if 'candidate_image' in request.files:
#             file = request.files['candidate_image']
#             if file:
#                 filename = secure_filename(file.filename)
#                 file_path = os.path.join('static/candidate_photos', filename)
#                 file.save(file_path)
#             else:
#                 filename = ''  # Default if no file is uploaded
#         else:
#             filename = ''

#         # Add candidate to Firestore
#         candidate_ref = db.collection('candidates').document(name)
#         candidate_ref.set({
#             'name': name,
#             'description': description,
#             'image': filename,  # Save filename
#             'votes': '0'  # Initialize votes
#         })

#         return redirect(url_for('admin_dashboard'))

#     except Exception as e:
#         return f"An error occurred: {str(e)}", 500


# @app.route('/admin/dashboard')
# def admin_dashboard():
#     if 'admin_logged_in' not in session:
#         return redirect(url_for('admin_login'))
    
#     # Fetch candidates from Firestore
#     candidates_ref = db.collection('candidates')
#     candidates = candidates_ref.stream()
#     candidates_list = [candidate.to_dict() for candidate in candidates]
    
#     return render_template('admin_dashboard.html', candidates=candidates_list)

# @app.route('/admin/add_candidate', methods=['POST'])
# def add_candidate():
#     if 'admin_logged_in' not in session:
#         return redirect(url_for('admin_login'))

#     candidate_name = request.form.get('candidate_name')

#     if candidate_name:
#         candidates_ref = db.collection('candidates').document(candidate_name)
#         candidates_ref.set({'name': candidate_name, 'votes': 0})
    
#     return redirect(url_for('admin_dashboard'))

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

# admin pages end

# @app.route('/registration', methods=['GET', 'POST'])
# def registration():
#     if request.method == 'POST':
#         name = request.form.get('name')
#         dob = request.form.get('dob')
#         parent_name = request.form.get('parent_name')
#         email = request.form.get('email')
#         mobile = request.form.get('mobile')
#         password = request.form.get('password')
#         confirm_password = request.form.get('confirm_password')
#         aadhar = request.form.get('aadhar')
        
#         if password != confirm_password:
#             return "Passwords do not match", 400

#         try:
#             # Create a new user document in Firestore
#             user_ref = db.collection('users').document(email)
#             user_ref.set({
#                 'name': name,
#                 'dob': dob,
#                 'parent_name': parent_name,
#                 'email': email,
#                 'mobile': mobile,
#                 'password': password,
#                 'aadhar_number': aadhar,
#                 'photo_url': ''  # Initialize with an empty photo URL
#             })
            
#             return redirect(url_for('login'))
#         except Exception as e:
#             return f"An error occurred: {str(e)}", 500

#     return render_template('registration.html')

@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        name = request.form.get('name')
        dob = request.form.get('dob')
        parent_name = request.form.get('parent_name')
        email = request.form.get('email')
        mobile = request.form.get('mobile')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        aadhar = request.form.get('aadhar')

        # Password policy
        if len(password) < 8:
            return "Password must be at least 8 characters long.", 400
        if not re.search(r"[A-Z]", password):
            return "Password must contain at least one uppercase letter.", 400
        if not re.search(r"[a-z]", password):
            return "Password must contain at least one lowercase letter.", 400
        if not re.search(r"[0-9]", password):
            return "Password must contain at least one digit.", 400
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return "Password must contain at least one special character.", 400

        if password != confirm_password:
            return "Passwords do not match", 400

        try:
            # Hash the password
            hashed_password = generate_password_hash(password, method='sha256')
            
            # Create a new user document in Firestore
            user_ref = db.collection('users').document(email)
            user_ref.set({
                'name': name,
                'dob': dob,
                'parent_name': parent_name,
                'email': email,
                'mobile': mobile,
                'password': hashed_password,
                'aadhar_number': aadhar,
                'photo_url': ''  # Initialize with an empty photo URL
            })
            
            return redirect(url_for('login'))
        except Exception as e:
            return f"An error occurred: {str(e)}", 500

    return render_template('registration.html')

@app.route('/about')
def about():
    return render_template('about.html')

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         email = request.form.get('email')
#         password = request.form.get('password')

#         try:
#             user_ref = db.collection('users').document(email)
#             user_data = user_ref.get()

#             if user_data.exists:
#                 user = user_data.to_dict()
                
#                 # Check password (this should ideally be hashed and checked securely)
#                 if user.get('password') == password:
#                     session['user_email'] = email
#                     return redirect(url_for('personal_info'))
#                 else:
#                     return "Invalid email or password", 401
#             else:
#                 return "User not found", 404

#         except Exception as e:
#             return f"An error occurred: {str(e)}", 500

#     return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            user_ref = db.collection('users').document(email)
            user_data = user_ref.get()

            if user_data.exists:
                user = user_data.to_dict()
                
                # Check hashed password
                hashed_password = user.get('password')
                if check_password_hash(hashed_password, password):
                    session['user_email'] = email
                    return redirect(url_for('personal_info'))
                else:
                    return "Invalid email or password", 401
            else:
                return "User not found", 404

        except Exception as e:
            return f"An error occurred: {str(e)}", 500

    return render_template('login.html')
@app.route('/personal_info', methods=['GET', 'POST'])
def personal_info():
    if 'user_email' in session:
        user_email = session['user_email']
        
        try:
            user_ref = db.collection('users').document(user_email)
            
            if request.method == 'POST':
                # Handle file upload
                if 'photo' in request.files:
                    photo = request.files['photo']
                    if photo:
                        photo_filename = secure_filename(photo.filename)
                        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))
                        user_ref.update({'photo_url': f'images/user_photos/{photo_filename}'})

                # Handle form data
                name = request.form.get('name')
                dob = request.form.get('dob')
                parent_name = request.form.get('parent_name')
                mobile = request.form.get('mobile')
                aadhar = request.form.get('aadhar')
                address = request.form.get('address')

                # Update user document
                user_ref.update({
                    'name': name,
                    'dob': dob,
                    'parent_name': parent_name,
                    'mobile': mobile,
                    'aadhar_number': aadhar,
                    'address': address
                })

                return redirect(url_for('personal_info'))
                
            user_data = user_ref.get()
            if user_data.exists:
                user_details = user_data.to_dict()
                return render_template('personal_info.html', 
                                       name=user_details.get('name'), 
                                       dob=user_details.get('dob'),
                                       parent_name=user_details.get('parent_name'),
                                       email=user_details.get('email'),
                                       mobile=user_details.get('mobile'),
                                       address=user_details.get('address'),
                                       aadhar=user_details.get('aadhar_number'),
                                       photo=user_details.get('photo_url'))
            else:
                return "User data not found in Firestore", 404
        
        except Exception as e:
            return f"An error occurred: {str(e)}", 500
    else:
        return redirect(url_for('login'))


# @app.route('/personal_info', methods=['GET', 'POST'])
# def personal_info():
#     if 'user_email' in session:
#         user_email = session['user_email']
        
#         try:
#             user_ref = db.collection('users').document(user_email)
#             user_data = user_ref.get()

#             if user_data.exists:
#                 user_details = user_data.to_dict()
                
#                 if request.method == 'POST':
#                     # Handle file upload and address update
#                     if 'photo' in request.files:
#                         photo = request.files['photo']
#                         if photo:
#                             photo_filename = secure_filename(photo.filename)
#                             photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))
#                             # Update Firestore with the new photo URL
#                             user_ref.update({'photo_url': f'images/user_photos/{photo_filename}'})
                    
#                     address = request.form.get('address')
#                     if address:
#                         user_ref.update({'address': address})

#                 return render_template('personal_info.html', 
#                                        name=user_details.get('name'), 
#                                        dob=user_details.get('dob'),
#                                        parent_name=user_details.get('parent_name'),
#                                        email=user_details.get('email'),
#                                        mobile=user_details.get('mobile'),
#                                        address=user_details.get('address'),
#                                        aadhar=user_details.get('aadhar_number'),
#                                        photo=user_details.get('photo_url'))
#             else:
#                 return "User data not found in Firestore", 404
        
#         except Exception as e:
#             return f"An error occurred: {str(e)}", 500
#     else:
#         return redirect(url_for('login'))


@app.route('/election')
def election():
# Fetch and display election schedules
    return render_template('election.html')
@app.route('/rules')
def rules():
# Fetch and display rules
    return render_template('rules.html')


@app.route('/vote', methods=['GET', 'POST'])
def vote():
    if request.method == 'GET':
        # Fetch candidates from Firestore
        candidates_ref = db.collection('candidates')
        candidates = candidates_ref.stream()

        # Convert Firestore documents to a list of dictionaries
        candidates_list = []
        for candidate in candidates:
            candidate_dict = candidate.to_dict()
            candidates_list.append(candidate_dict)

        # Render the vote page with candidates
        return render_template('vote.html', candidates=candidates_list)

    elif request.method == 'POST':
        # Get the selected candidate from the form
        selected_candidate = request.form['candidate']

        # Reference to the candidates collection's document for the selected candidate
        candidate_ref = db.collection('candidates').document(selected_candidate)

        # Fetch the candidate data
        candidate_data = candidate_ref.get()

        if candidate_data.exists:
            # If candidate exists, update the vote count
            current_votes = int(candidate_data.to_dict().get('votes', '0'))
            new_votes = current_votes + 1

            # Update the vote count for the candidate
            candidate_ref.update({'votes': str(new_votes)})

            return render_template('thankyou.html')  # Render thank you page after voting
        else:
            return "Candidate not found", 404

# @app.route('/vote', methods=['GET', 'POST'])
# def vote():
#     if request.method == 'GET':
#         # Fetch candidates from Firestore
#         candidates_ref = db.collection('candidates')
#         candidates = candidates_ref.stream()

#         # Convert Firestore documents to a list of dictionaries
#         candidates_list = []
#         for candidate in candidates:
#             candidate_dict = candidate.to_dict()
#             candidates_list.append(candidate_dict)

#         # Render the vote page with candidates
#         return render_template('vote.html', candidates=candidates_list)

#     elif request.method == 'POST':
#         # Get the selected candidate from the form
#         selected_candidate = request.form['candidate']

#         # Reference to the vote-bank collection's document for the selected candidate
#         vote_ref = db.collection('vote-bank').document(selected_candidate)

#         # Fetch the vote data
#         vote_data = vote_ref.get()

#         if vote_data.exists:
#             # If candidate exists in vote-bank, update the vote count
#             current_votes = int(vote_data.to_dict().get('votes', 0))
#             new_votes = current_votes + 1

#             # Update the vote count for the candidate
#             vote_ref.update({'votes': str(new_votes)})
#         else:
#             # If the candidate doesn't exist in vote-bank, add with one vote
#             vote_ref.set({'candidate': selected_candidate, 'votes': '1'})

#         return render_template('thankyou.html')


if __name__ == '__main__':
    app.run(debug=True)
