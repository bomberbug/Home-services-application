# Home Services Application

## Overview

The Home Services Application is a multi-user web platform that connects customers with service professionals for various home services.  
It supports three roles: Admin, Customer, and Service Professional, each with dedicated dashboards and functionalities.

---

## Features

### Admin
- Manage services (create, edit, delete)  
- Approve or reject service professionals  
- Block/unblock users and professionals  
- Search users and services  

### Customer
- Register and login  
- Browse and search services  
- Create service requests  
- Edit or delete requests  
- Track request status  

### Service Professional
- View service requests by domain  
- Accept or reject requests  
- Manage accepted tasks  
- Mark tasks as completed  

### General
- Role-based dashboards  
- Dynamic UI using Jinja2  
- Centralized logout system  
- Clean UI with CSS styling  

---

## Tech Stack

- Backend: Flask (Python)  
- Frontend: HTML, CSS  
- Templating: Jinja2  
- Database: SQLite (Flask-SQLAlchemy)  
- Authentication: Werkzeug  
- Utilities: Datetime  

---

## Project Structure


├── app.py                  
├── models.py               
├── README.md               
├── .gitignore              
│
├── instance/
│   └── database.db         
│
├── static/
│    ├── style.css
│    ├── style_log.css               
│
├── templates/
│   ├── admin_dashboard.html
│   ├── admin_login.html
│   ├── admin_register.html
│   ├── create_service.html
│   ├── create_service_request.html
│   ├── edit_service.html
│   ├── edit_service_request.html
│   ├── service_professional_dashboard.html
│   ├── user_dashboard.html
│   ├── user_login.html
│   └── user_register.html


---

## admin info
- username- admin
- password- admin

## Future Improvements

- Payment integration    
- Rating and review system  