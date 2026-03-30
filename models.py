from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Customer(db.Model):
    __tablename__ = 'customer'
    username = db.Column(db.String(50), nullable=False, unique=True,primary_key=True)
    phone = db.Column(db.Integer, nullable=False, unique=True)
    pincode = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    status = db.Column(db.Boolean, default=False)
    service_request = db.relationship('Service_Request', backref='customer', lazy=True)

class Service_Professional(db.Model):
    __tablename__ = 'service_professional'
    username = db.Column(db.String(50), nullable=False, unique=True,primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    accept = db.Column(db.Boolean, default=False)
    work = db.Column(db.JSON, default=list)
    status = db.Column(db.Boolean, default=False)
    

class Service(db.Model):
    __tablename__ = 'service'
    service = db.Column(db.String(60), nullable=False, unique=True,primary_key=True)
    charges = db.Column(db.Integer, nullable=False)
    
    def __repr__(self):
        return self.service


class Service_Request(db.Model):
    __tablename__ = 'service_request'
    id = db.Column(db.Integer, primary_key=True)
    service_service = db.Column(db.String(50), db.ForeignKey('service.service'), nullable=False)
    pincode = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False)
    username = db.Column(db.String(50), db.ForeignKey('customer.username'), nullable=True)
    service = db.relationship('Service', backref='service_request', lazy=True)
    completed= db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='pending')   
    handled_by = db.Column(db.String(50), db.ForeignKey('service_professional.username'), nullable=True)

    def __repr__(self):
        return f"<Service_Request {self.id}: {self.status}>"             