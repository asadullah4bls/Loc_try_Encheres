from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy.orm  import  relationship

db = SQLAlchemy()


class User(db.Model, UserMixin):
    __tablename__ = "users"  # Optional: specify table name
    id = db.Column(db.Integer, primary_key=True)
    session_data = db.Column(db.Text)
    expiry = db.Column(db.DateTime)
    name = db.Column(db.String(120), unique=False, nullable=False)
    firstname = db.Column(db.String(120), unique=False, nullable=False)
    city = db.Column(db.String(120), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    website = db.Column(db.String(120), unique=True, nullable=True)
    logo = db.Column(db.String(120), unique=True, nullable=True)
    bg_color = db.Column(db.String(7))  # Store colors in hex format, e.g., '#FFFFFF'
    bg_font_color = db.Column(db.String(7))
    title_color = db.Column(db.String(7))
    title_font_color = db.Column(db.String(7))
    attribut_color = db.Column(db.String(7))
    attribut_font_color = db.Column(db.String(7))
    fontFamily = db.Column(db.String(50))
    password_hash = db.Column(db.String(255), nullable=False)
    subscription_status = db.Column(db.String(50), default="free")
    consumed_reports = db.Column(db.Integer, default=0, server_default="0")
    is_active = db.Column(
        db.Boolean, default=False
    )  # Will be used after email confirmation
    reset_token = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
    ip_ad = db.Column(db.String(500), nullable=True)
    phone = db.Column(db.String(500), nullable=True)
    address = db.Column(db.String(500), nullable=True)
    post_code = db.Column(db.String(500), nullable=True)
    free_rep = db.Column(db.Boolean, default=True)
    verif_code = db.Column(db.String(500), nullable=True)
    is_subscribed = db.Column(db.Boolean, default=False)
    subscription_ends = db.Column(db.DateTime, nullable=True)
    reports_count = db.Column(db.Integer, nullable=True)
    code_timer = db.Column(db.DateTime, nullable=True)
    token_reset_pass= db.Column(db.Text, nullable=True)
    subs_type = db.Column(db.String(500), nullable=True)
    subs_start = db.Column(db.DateTime, nullable=True)
    downloaded_current = db.Column(db.Integer, nullable=True)
    downloaded_history = db.Column(db.Integer, nullable=True)
    is_superuser = db.Column(db.Boolean, default=False)
    def set_password(self, password):
        """Hash the password before saving."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check hashed password for authentication."""
        return check_password_hash(self.password_hash, password)


class ContactMessage(db.Model):  # {{ edit_1 }}
    __tablename__ = "contact_messages"  # Optional: specify table name
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)  # Name of the sender
    email = db.Column(db.String(120), nullable=False)  # Email of the sender
    subject = db.Column(db.String(255), nullable=False)  # Subject of the message
    message = db.Column(db.Text, nullable=False)  # The message content
    created_at = db.Column(db.DateTime, default=db.func.now())  # Timestamp of creation


class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    stripe_customer_id = db.Column(db.String(120), nullable=False)
    stripe_subscription_id = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(50), default="active")

    user = db.relationship("User", backref="subscription")


class  ReportsLog(db.Model):
    __tablename__ = 'Reports_Logs'  # Optional: name the table explicitly
    
    id = db.Column(db.Integer, primary_key=True)  # Add an 'id' column as primary key (optional, for unique identification)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = relationship('User', backref=db.backref('Reports_Logs', lazy=True)) 
    city = db.Column(db.String(500), nullable=True)
    property_type = db.Column(db.String(500), nullable=True)
    download_date = db.Column(db.DateTime, nullable=True)


class PaymentMethod(db.Model):
    __tablename__ = 'payment_methods'  # Optional: name the table explicitly
    
    id = db.Column(db.Integer, primary_key=True)  # Add an 'id' column as primary key (optional, for unique identification)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = relationship('User', backref=db.backref('payment_methods', lazy=True))  # Assuming you have a User model defined
    brand = db.Column(db.String(122), nullable=True)
    card_id = db.Column(db.String(122), nullable=True)
    ccv = db.Column(db.Integer, nullable=True)  # Avoid storing CVV in production!
    exp_month = db.Column(db.String(122), nullable=True)
    exp_year = db.Column(db.String(122), nullable=True)
    last4 = db.Column(db.String(4), nullable=True)  # Only store the last 4 digits of the card
    name_on_card = db.Column(db.String(122), nullable=True)
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp(), nullable=False)

    def __repr__(self):
        return f"<PaymentMethod {self.brand} ending in {self.last4}>"



class UserProfile(db.Model):
    __tablename__ = 'userprofile'  # Optional: You can define the table name if different from the default

    id = db.Column(db.Integer, primary_key=True)
    # One-to-one relationship with User
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('userprofile', uselist=False), uselist=False)
    # Stripe customer ID field
    stripe_customer_id = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f'<UserProfile {self.user.username}>'