from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, Customer, Service_Professional, Service_Request, Service
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bomber.sqlite'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_ECHO'] = True
db.init_app(app)

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin"


@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('customer_dashboard'))
    return redirect(url_for('admin_login'))

# Route for user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    form_id = request.form.get('form_id')
    print("Form ID:", form_id)
    
    if form_id == 'user' and request.method == 'POST':
        username = request.form['name']
        phone = request.form['phone']
        pincode = request.form['pincode']
        email = request.form['email']
        password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
        
        print("Registering new user:", username, phone, pincode, email)
        
        new_user = Customer(username=username, phone=phone, pincode=pincode, email=email, password=password)
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('User registered successfully! Please login.')
            print("User registered and committed to database.")
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            print("Error during registration:", e)
            flash('Registration failed. Please try again.')
    
    elif form_id == 'service_professional' and request.method == 'POST':
        username = request.form['name']
        email = request.form['email']
        work = request.form.getlist('options')
        password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
        
        print("Registering new service professional:", username, email)
        new_user = Service_Professional(username=username, email=email, password=password,work=work)
        
        try:
          db.session.add(new_user)
          db.session.commit()
          flash('Service Professional registered successfully! Please login.')
          print("Service professional registered and committed to database.")
          return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            print("Error during service professional registration:", e)
            flash('Registration failed. Please try again.')
    
    return render_template('user_register.html')

# Route for admin login
@app.route('/admin_login', methods=["GET", "POST"])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('name')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['user_type'] = 'admin'
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password. Please try again')
            return render_template('admin_login.html')
    
    return render_template('admin_login.html')


# Route for user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    form_id = request.form.get('form_id')
    
    if form_id == 'user' and request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = Customer.query.filter_by(email=email).first()
        
        if user is None:
            flash('Login failed. Check entered details.')
            return render_template('user_login.html')
        
        if user.status:
            flash('Youe have been blocked.')
            return redirect(url_for('admin_login'))
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.username
            session['user_type'] = 'customer'
            flash('Login successful!')
            return redirect(url_for('customer_dashboard'))
        else:
            flash('Login failed. Check entered details.')
            return redirect(url_for('admin_login'))
    
    elif form_id == 'service_professional' and request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = Service_Professional.query.filter_by(email=email).first()
        
        if user is None:
            flash('Login failed. Check entered details.')
            return render_template('user_login.html')
        
        if user.status:
            flash('Youe have been blocked.')
            return redirect(url_for('admin_login'))
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.username
            session['user_type'] = 'service_professional'
            flash('Login successful!')
            return redirect(url_for('service_professional_dashboard'))
        else:
            flash('Login failed. Check entered details.')
            return redirect(url_for('admin_login'))
    
    return render_template('user_login.html')

#user dashboard
@app.route('/userdashboard')
def customer_dashboard():
    if 'user_id' not in session:
        flash("You need to be logged in")
        return redirect(url_for('login'))
    
    user_type = session.get('user_type')  
    if user_type == 'customer':
        service= Service.query.all()
        service_request = Service_Request.query.all()
        return render_template('user_dashboard.html', service_request=service_request,service=service)
    return redirect(url_for('login'))    
   

#service professional dashboard
@app.route('/ServiceProfessionalDashboard')
def service_professional_dashboard():
        if 'user_id' not in session:
           flash("You need to be logged in")
           return redirect(url_for('login'))
        user_type = session.get('user_type')  
        if user_type == 'service_professional':
            user_id = session['user_id']
            professional = Service_Professional.query.filter_by(username=user_id, accept=True).first()
            if professional:
                service_request = Service_Request.query.all()
                request_accepted=Service_Request.query.filter_by(handled_by=user_id,status='accepted').all()
                return render_template('service_professional_dashboard.html', service_request=service_request, professional=professional,request_accepted=request_accepted)
        return redirect(url_for('login')) 


#route for service completed
@app.route('/service_professional/done/<int:id>', methods=['POST'])
def work_done(id):
    if 'user_id' not in session:
        flash("You need to be logged in")
        return redirect(url_for('login'))
    
    user = Service_Request.query.get_or_404(id)
    user.completed = True
    db.session.commit()
    flash('user been blocked.')
    return redirect(url_for('service_professional_dashboard'))


#route for approval  
@app.route('/service_professional/approve/<int:id>', methods=['POST'])
def accept_service_request(id):
    if 'user_id' not in session:
        flash("You need to be logged in to accept service requests.")
        return redirect(url_for('login'))

    service_request = Service_Request.query.get_or_404(id)
    professional_id = session['user_id']
    professional = Service_Professional.query.get(professional_id)

    try:
        service_request.status = 'accepted'
        service_request.handled_by = professional.username
        db.session.commit()
        flash("Service request accepted successfully!")
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred while accepting the service request: {str(e)}")

    return redirect(url_for('service_professional_dashboard'))
 
 
#route for decline Service_Professional.query.get(id)
@app.route('/service_professional/reject/<int:id>', methods=['POST'])
def reject_service_request(id):
    if 'user_id' not in session:
        flash("You need to be logged in to reject service requests.")
        return redirect(url_for('login'))

    service_request = Service_Request.query.get_or_404(id)
    
    try:
        service_request.status = 'rejected'
        db.session.commit()
        flash("Service request rejected successfully!")
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred while rejecting the service request: {str(e)}")

    return redirect(url_for('service_professional_dashboard'))


@app.route('/user/dashboard/create_service_request/<string:service>', methods=['GET', 'POST'])
def create_service_request(service):
    if 'user_id' not in session:
        flash("You need to be logged in")
        return redirect(url_for('login'))
        
    user = Customer.query.get(session['user_id'])  
    if not user:
        flash("User  not found. Please log in again.")
        return redirect(url_for('register'))
    
    if request.method == 'POST':
        pincode = request.form['pincode']
        date_str = request.form['date']
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        username = user.username
           
        service = Service.query.filter_by(service=service).first()    
        try:
            new_request = Service_Request(pincode=pincode, date=date, username=username,service_service=service.service)
            db.session.add(new_request)
            db.session.commit() 
            flash("Service request created successfully!") 
            return redirect(url_for('customer_dashboard'))
        except Exception as e:
            db.session.rollback() 
            flash("An error occurred while creating the service request: {}".format(str(e)))
            return redirect(url_for('customer_dashboa'))
    return render_template('create_service_request.html', username=user.username, service=service)

#route for customer service request delete  
@app.route('/user/services/delete/<int:id>', methods=['POST'])
def customer_service_delete(id):
    if 'user_id' not in session:
        flash("You need to be logged in")
        return redirect(url_for('login'))
    
    service = Service_Request.query.get_or_404(id)
    
    db.session.delete(service)
    db.session.commit()
    flash('Service deleted successfully.')
    return redirect(url_for('customer_dashboard'))   

#route for customer service edit
@app.route('/user/services/edit/<int:id>', methods=['GET','POST'])
def customer_service_edit(id):
    if 'user_id' not in session:
        flash("You need to be logged in")
        return redirect(url_for('login'))
    
    service_request = Service_Request.query.get_or_404(id)
    
    if request.method == 'POST':
        print(request.form)  
        try:
            service_request.pincode = request.form['pincode']
            date_str = request.form['date']
            service_request.date = datetime.strptime(date_str, '%Y-%m-%d').date()
            db.session.commit()
            flash('Service updated successfully')
            return redirect(url_for('customer_dashboard'))
        except KeyError as e:
            flash(f'Missing field: {str(e)}')  
            return redirect(url_for('customer_service_edit', id=id))  
    return render_template('edit_service_request.html',service_request=service_request) 


@app.route('/admin/dashboard')
def admin_dashboard():
  if 'user_type' not in session:
        flash("You need to be logged in")
        return redirect(url_for('admin_login')) 
     
  if session.get('user_type') == 'admin':
    service_professional = Service_Professional.query.filter_by(accept=False).all()
    service = Service.query.all()
    user = Customer.query.all()
    service_professional_check = Service_Professional.query.filter_by(accept=True).all()
    return render_template('admin_dashboard.html',service_professional=service_professional,service=service,user=user,service_professional_check=service_professional_check)
  return redirect(url_for('login'))  

#route for block
@app.route('/admin/dashboard/cblock/<string:username>', methods=['POST'])
def admin_c_block(username):
    if 'user_type' not in session:
        flash("You need to be logged in")
        return redirect(url_for('admin_login'))
    
    if session.get('user_type') == 'admin':
      user = Customer.query.get_or_404(username)
      user.status = True
      db.session.commit()
      flash('user been blocked.')
      return redirect(url_for('admin_dashboard'))
 
@app.route('/admin/dashboard/spblock/<string:username>', methods=['POST'])
def admin_sp_block(username):
    if 'user_type' not in session:
        flash("You need to be logged in")
        return redirect(url_for('admin_login'))
    
    if session.get('user_type') == 'admin':
      user = Service_Professional.query.get_or_404(username)
      user.status = True
      db.session.commit()
      flash('user been blocked.')
      return redirect(url_for('admin_dashboard'))  

#route for  unblock
@app.route('/admin/dashboard/cunblock/<string:username>', methods=['POST'])
def admin_c_unblock(username):
    if 'user_type' not in session:
        flash("You need to be logged in")
        return redirect(url_for('admin_login'))
    
    if session.get('user_type') == 'admin':
     user = Customer.query.get_or_404(username)
     user.status = False
     db.session.commit()
     flash('user been un-blocked.')
     return redirect(url_for('admin_dashboard'))
  
@app.route('/admin/dashboard/spunblock/<string:username>', methods=['POST'])
def admin_sp_unblock(username):
    if 'user_type' not in session:
        flash("You need to be logged in")
        return redirect(url_for('admin_login'))
    
    if session.get('user_type') == 'admin':
     user = Service_Professional.query.get_or_404(username)
     user.status = False
     db.session.commit()
     flash('user been un-blocked.')
     return redirect(url_for('admin_dashboard'))  

#route for creating new services
@app.route('/admin/dashboard/create_service', methods=['GET', 'POST'])
def create_service():
    if 'user_type' not in session:
        flash("You need to be logged in")
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        service_name = request.form['service']
        charges = request.form['charges']
        
        existing_service = Service.query.filter_by(service=service_name).first()
        if existing_service:
            flash('Service already exists! Please enter a different service name.')
            return redirect(url_for('admin_dashboard'))

        try:
           new_service = Service(service=service_name, charges=charges)
           db.session.add(new_service)
           db.session.commit()
           flash('Service added successfully!')
           return redirect(url_for('admin_dashboard'))
        except KeyError as e:
           db.session.rollback() 
           flash("An error occurred while creating the service request: {}".format(str(e)))
           return redirect(url_for('admin_dashboard'))
    
    professionals = Service_Professional.query.all()
    return render_template('create_service.html', professionals=professionals)

#route for service delete  
@app.route('/admin/services/delete/<string:service>', methods=['POST'])
def admin_service_delete(service):
    if 'user_type' not in session:
        flash("You need to be logged in")
        return redirect(url_for('admin_login'))
    
    if session.get('user_type') == 'admin':
     service = Service.query.get_or_404(service)
     db.session.delete(service)
     db.session.commit()
     flash('Service deleted successfully.')
     return redirect(url_for('admin_dashboard'))


#route for service edit
@app.route('/admin/services/edit/<string:service>', methods=['GET','POST'])
def admin_service_edit(service):
    if 'user_type' not in session:
        flash("You need to be logged in")
        return redirect(url_for('admin_login'))
    
    if session.get('user_type') == 'admin':
     service = Service.query.get_or_404(service)
    
     if request.method == 'POST':
        print(request.form)  
        try:
            service.name = request.form['service']
            service.charges = request.form['charges']
            db.session.commit()
            flash('Service updated successfully')
            return redirect(url_for('admin_dashboard'))
        except KeyError as e:
            flash(f'Missing field: {str(e)}')  
            return redirect(url_for('admin_service_edit', service=service))  
     return render_template('edit_service.html',service=service)   

#route for approval  
@app.route('/admin/approve/<string:username>', methods=['POST'])
def admin_approve_service_professional(username):
    if 'user_type' not in session:
        flash("You need to be logged in")
        return redirect(url_for('admin_login'))
    if session.get('user_type') == 'admin':
     professional = Service_Professional.query.get_or_404(username)
     professional.accept=True 
     db.session.commit()
     return redirect(url_for('admin_dashboard'))
  
#route for decline Service_Professional.query.get(id)
@app.route('/admin/decline/<string:username>', methods=['POST'])
def admin_decline_service_professional(username):
    if 'user_type' not in session:
        flash("You need to be logged in")
        return redirect(url_for('admin_login'))
    
    if session.get('user_type') == 'admin':
     professional = Service_Professional.query.get_or_404(username)
     db.session.delete(professional) 
     db.session.commit()  
     flash('Service professional declined successfully.')
     return redirect(url_for('admin_dashboard'))  
 
# Route for admin searching service_professional
@app.route('/admin_search_service_professional', methods=['GET'])
def admin_search_service_professional():
    
    service_query = request.args.get('service', '').strip()  
    user_name_query = request.args.get('user_name', '').strip()  
    
    query_sp = Service_Professional.query
    query_c = Customer.query

    if service_query:
        query_sp = query_sp.filter(Service_Professional.work.ilike(f'%{service_query}%'))

    if user_name_query:
        query_sp = query_sp.filter(Service_Professional.username.ilike(f'%{user_name_query}%'))
        query_c = query_c.filter(Customer.username.ilike(f'%{user_name_query}%'))
    
    service_professional_searched = query_sp.all()
    customer_searched = query_c.all()
    service_re=Service_Request.query.all()
    
    return render_template('admin_dashboard.html',
                           service_professional_searched=service_professional_searched,
                           customer_searched=customer_searched,
                           service_re=service_re)
    
#route for customer searching services    
@app.route('/customer_search_services', methods=['GET'])
def customer_search_services():
    
    cost_query = request.args.get('cost', '').strip() 
    service_query = request.args.get('service', '').strip()  
    
    query = Service.query

    if service_query:
        query = query.filter(Service.service.ilike(f'%{service_query}%'))  

    if cost_query:
        try:
            max_cost = float(cost_query) 
            query = query.filter(Service.charges <= max_cost)  
        except ValueError:
            return render_template('user_dashboard.html', service_p=[], error="Invalid cost value.")

    
    service_p = query.all()
    
    return render_template('user_dashboard.html', service_p=service_p)


    

# Route for user logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out')
    return redirect(url_for('admin_login'))

# Initialize the database
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)