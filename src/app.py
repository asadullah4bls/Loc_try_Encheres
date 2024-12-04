from . import Data_generator as dg
# from src import Data_generator as dg
from . import Report_generator as rg
from . import db_models
from .utility import log_execution_time
#from .Report_Customiser import upload_logo, customise_workbook
import random
import string
import os
from datetime import datetime,timedelta
from dateutil.relativedelta  import relativedelta
import secrets
import logging
from datetime import timedelta
from dotenv import load_dotenv
from pathlib import Path
from google.cloud import storage
import  stripe
import  pandas  as  pd



from flask import (
    Flask,
    jsonify,
    request,
    render_template,
    send_file,
    redirect,
    url_for,
    flash,
    session
    # abort,
)
from flask_session import Session

from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)

from flask_mail import Mail, Message

# from flask_caching import Cache
# from werkzeug.urls import url_has_allowed_host_and_scheme

from itsdangerous import URLSafeTimedSerializer
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import StringField 
# from wtforms.validators import DataRequired, Email, EqualTo

# Example form class
class MyForm(FlaskForm):
    name = StringField('Name')
# from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


# # Define your function to be scheduled
# def scheduled_function():
#     print("Scheduled function executed at", datetime.now())

# # Create a scheduler instance
# scheduler = BackgroundScheduler()
# log_execution_time = utility.log_execution_time

load_dotenv()
REPORT_DIR = os.getenv("REPORTS_DIR")
# project = os.getenv("PROJECT_ID")
# bucket_name = os.getenv("BUCKET_ID")
# storage_client = storage.Client(project)
# bucket = storage_client.bucket(bucket_name)
# LOGO_DIR = os.getenv("LOGO_DIR")
# bucket_logo = storage_client.bucket(LOGO_DIR)
SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS")
stripe.api_key = os.getenv("STRIPE_API_KEY")
# MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")

BASE_DIR = Path(__file__).parent.parent

REPORTS_DIR = f"{BASE_DIR}/{REPORT_DIR}"
the_fl_var = "static/css/payment/data_report.csv"
CS_FL_DIR = f"{BASE_DIR}/{the_fl_var}"

db = db_models.db
User = db_models.User
ContactMessage = db_models.ContactMessage
ReportsLog = db_models.ReportsLog
app = Flask(__name__, static_folder="../static", template_folder="../templates")
# Gmail SMTP server configuration
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False
app.config["MAIL_USERNAME"] = os.getenv(
    "MAIL_USERNAME"
)  # Replace with your Gmail address
app.config["MAIL_PASSWORD"] = os.getenv(
    "MAIL_PASSWORD"
)  # Replace with your Gmail app password


MAIL_DEFAULT_SENDER = os.getenv(
    "MAIL_DEFAULT_SENDER")  # Default sender email

app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_DEFAULT_SENDER")
mail = Mail(app)
from schedule import Scheduler
import  time
import  threading
# Define the function to be scheduled
def give_admin_gold():
    with app.app_context():  # Ensure Flask application context
        print("Scheduled function executed at", datetime.now())
        current_time = datetime.now()
        if  db.session.query(db_models.User.query.filter(db_models.User.subscription_ends<current_time).filter(db_models.User.is_subscribed.is_(True)).filter(db_models.User.subscription_ends.isnot(None)).exists()).scalar():
            print("subs exp users exist") 
            all_users = User.query.filter(User.subscription_ends < current_time,User.is_subscribed.is_(True),User.subscription_ends.isnot(None)).all()
            for  user in all_users:
                user.is_subscribed = False
                user.reports_count = 0
                db.session.commit()

            for  user in all_users:
                context_data = {'codevar': "subscription ended",'link': f"We hope this message finds you well. We wanted to inform you that your subscription ended.",'flag_password_reset': False,'flag_confirm_email':"121"}

                #html_message = render_template('confrim_email.html', **context_data) 
                # msg = Message(
                #     subject= "Fin de l'abonnement",
                #     sender=os.getenv("EMAIL_SENDER"),
                #     recipients=[user.email], 
                #     html=html_message
                # ) 
                msg = Message(
                    "Fin de l'abonnement",
                    sender=os.getenv(
                        "EMAIL_SENDER"
                    ),  # Use environment variable for sender email
                    recipients=[user.email],
                    body=f"Nous espérons que ce message vous parvient bien. Nous tenions à vous informer que votre abonnement est terminé.",
                )
                try:
                    mail.send(msg)
                except Exception as e:
                    logging.error(f"subs end Failed to send email to {user.email}: {e}")

        else:
            print("subs exp users not exist")

def run_continuously(interval=1):
    """ Continuously run, while executing pending jobs at each elapsed time interval. """
    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                scheduler.run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.setDaemon(True)
    continuous_thread.start()
    return cease_continuous_run


scheduler = Scheduler()


# Add a job to the scheduler
scheduler.every(2).minutes.do(give_admin_gold)

# Start the scheduler in a separate thread
run_continuously()
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv(
#     "GOOGLE_APPLICATION_CREDENTIALS"
# )

logging.basicConfig(level=logging.DEBUG)

# Get Stripe Customer 
def get_stripe_customer_id(user):
    # try:
        stripe_customer = stripe.Customer.create(
            email = user.email,
            name = user.name,
            description = 'Customer pushed from API'
        )
        return stripe_customer.id
    # except Exception as e:
    #     return None
# @log_execution_time
# def file_exists_in_bucket(file_name):
#     """Check if a file exists in the Google Cloud Storage bucket."""
#     blob = bucket.blob(file_name)
#     return blob.exists()


# @log_execution_time
# def download_file_from_bucket(file_name, report_path):
#     """Download a file from the Google Cloud Storage bucket."""
#     # bucket = storage_client.bucket(bucket_name)
#     blob = bucket.blob(file_name)
#     blob.download_to_filename(report_path)  # Save to local file


# @log_execution_time
# def upload_file_to_bucket(file_name, report_path):
#     """Upload a file to the Google Cloud Storage bucket."""
#     # bucket = storage_client.bucket(bucket_name)
#     blob = bucket.blob(file_name)
#     blob.upload_from_filename(report_path)


color_palette = [
    "#9CABB4",
    "#73a1b2",
    "#E3C1B4",
    "#44576D",
    "#768A96",
    "#610C27",
    "#73A1B2",
    "#AB644B",
    "#A48374",
    "#3C5759",
    "#F1BD78",
    "#eeeeee",
]
cities = dg.get_cities()
# def create_app():
csrf = CSRFProtect(app)  # Enable CSRF protection globally
# app.secret_key = os.getenv("SECRET_KEY", os.urandom(24))
# app.secret_key = os.getenv("SECRET_KEY", secrets.token_hex(24))
# Configure session cookie settings
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.config["SESSION_COOKIE_NAME"] = "user_rem_session"
app.config["SESSION_COOKIE_SECURE"] = False  # Set to True in production (for HTTPS)
app.config["SESSION_COOKIE_HTTPONLY"] = True  # Prevent JavaScript access
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"  # CSRF protection
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=120)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = SQLALCHEMY_TRACK_MODIFICATIONS
app.config['WTF_CSRF_ENABLED'] = True



s = URLSafeTimedSerializer(app.config["SECRET_KEY"])
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "strong"  # or 'basic', depending on your needs
# Customize the login message
login_manager.login_message = "Connexion requise !"
login_manager.login_view = "connexion"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Generate token for password reset
def generate_token(email, salt="email-confirmation-salt"):
    # s = URLSafeTimedSerializer(app.config["SECRET_KEY"])
    # return s.dumps(email, salt="password-reset-salt")
    return s.dumps(email, salt=salt)

# Generate token for password reset
def generate_token_expiration(email, salt="password-reset-salt",expiration=180):
    # s = URLSafeTimedSerializer(app.config["SECRET_KEY"])
    # return s.dumps(email, salt="password-reset-salt")
    return s.dumps(email, salt=salt)

def send_confirmation_email(user_email: str):
    """
    Generates a confirmation token for a user's email address.
    ARG : user_email
    """
    
    token = generate_token(email=user_email, salt="email-confirmation-salt")
    link = url_for("confirm_email", token=token, _external=True)
    flag_password_reset= False
    flag_confirm_email = True
    context_data = { 'link': link,'flag_password_reset':flag_password_reset,'flag_confirm_email':flag_confirm_email}
    

    html_message = render_template('confrim_email.html', **context_data)
    # plain_message = render_template('confrim_email.txt', **context_data)
    email_subject = "Confirmez votre e-mail"
    msg = Message(
        subject=email_subject,
        sender=os.getenv("EMAIL_SENDER"),
        recipients=[user_email],
        # body=plain_message,
        html=html_message
    )
    # msg = Message(
    #     "Confirm Your Email",
    #     sender=os.getenv(
    #         "EMAIL_SENDER"
    #     ),  # Use environment variable for sender email
    #     recipients=[user_email],
    #     body=f"Please click the following link to confirm your email: {link}",
    # )

    # add to the body of the email contains a link
    # that the user can click to confirm their email address
    # link = url_for("confirm_email", token=token, _external=True)
    # msg.body = f"Please click the following link to confirm your email: {link}"
    # send the email
    try:
        mail.send(msg)
    except Exception as e:
        logging.error(f"Failed to send email to {user_email}: {e}")
        flash("Failed to send confirmation email. Please try again later.", "error")

# Confirm the token and return the user's email
def confirm_token(token, salt="email-confirmation-salt", expiration=3600):
    """
    Validates the token received from the email confirmation link.
    ARG: token
    ARG: expiration=3600
    """
    # s = URLSafeTimedSerializer(app.config["SECRET_KEY"])
    try:
        # decode the token using the same URLSafeTimedSerializer
        # and checks if it is still valid (not expired)
        # email = s.loads(token, salt="password-reset-salt", max_age=expiration)
        email = s.loads(token, salt=salt, max_age=expiration)
    except Exception as e:
        # If the token is invalid or expired,
        #  it catches the exception, logs the error,
        #  and returns 'false'.

        logging.debug(f"An error occurred when confirming the token: {e}")
        return "false"
    # If the token is valid, it returns
    # the associated email address
    return email




def confirm_token_expire(token, salt="password-reset-salt", expiration=180):

    try:
        
        email = s.loads(token, salt=salt, max_age=expiration)
        print("Email after confirming:", email)
        
        
        user = User.query.filter_by(email=email).first()
        print("user reset token" ,user.token_reset_pass)
        if not user:
            raise ValueError("User not found.")

        
        if user.token_reset_pass != token:
            raise ValueError("Token does not match the one stored in the database.")
        

        
        user.token_reset_pass = None
        db.session.commit()
        print("Token matched successfully. Email:", email)
        return email

    except Exception as e:
        logging.error(f"Token validation failed: {e}")
        raise  

@app.route("/")
@log_execution_time
def index():
    return render_template("index.html")

@app.route("/code_form")
@log_execution_time
def code_form():
    form = request.args.get('form') or None
    if form is None:
        form= MyForm()
    is_res = request.args.get('is_res') or None
    userz = request.args.get('userz')  # Access zemi from the query string
    print("code form data",is_res,userz)
    if  is_res  is  None:
        pass
    else: 
        code_timer = datetime.now() + timedelta(minutes=2) 
        codevar = ''.join(random.choices(string.ascii_letters + string.digits, k=5))     #str(uuid.uuid4())
        db.session.query(db_models.User).filter(db_models.User.id == userz).update({'verif_code': codevar,"code_timer":code_timer})
        db.session.commit()  # Don't forget to commit the changes
        user = User.query.filter_by(id=userz).first() 
        context_data = {'codevar':codevar,'link': f"Code de confirmation de l'adresse IP renvoyé: ",'flag_password_reset': False,'flag_confirm_email':"121"}

        html_message = render_template('confrim_email.html', **context_data) 
        msg = Message(
            subject= "Confirmation de l'adresse IP",
            sender=os.getenv("EMAIL_SENDER"),
            recipients=[user.email], 
            html=html_message
        )
        # msg = Message(
        #     "Ip Address Confirmation",
        #     sender=os.getenv(
        #         "EMAIL_SENDER"
        #     ),  # Use environment variable for sender email
        #     recipients=[user.email],
        #     body=f"ip address confirmation code resent: {codevar}",
        # )
        try:
            mail.send(msg)
            flash("ip address confirmation code resent to your email","info")
        except Exception as e:
            logging.error(f"from ip addres Failed to send email to {user.email}: {e}")
            flash("Failed to re send ip address confirmation email. Please try again later.", "error")

    
    
    return render_template("code_fil.html",userz=userz,form=form)

@app.route("/submit_code", methods=["POST"])
def submit_code():
    if request.method == 'POST': 
        user_id = request.form.get('useri')
        code = request.form.get('name')
        if  db.session.query(db_models.User.query.filter(db_models.User.id==user_id).filter(db_models.User.verif_code==code).exists()).scalar():
            current_time = datetime.now()
            if  db.session.query(db_models.User.query.filter(db_models.User.id==user_id).filter(db_models.User.code_timer>current_time).exists()).scalar(): 
                user = User.query.filter_by(id=user_id).first()
                login_user(user)
                db.session.query(db_models.User).filter(db_models.User.id == user.id).update({'ip_ad': request.remote_addr})
                db.session.commit()  # Don't forget to commit the changes
                return redirect(url_for('index'))
            else:
                form = MyForm()
                flash("Code  expired")
                return render_template("code_fil.html",userz=user_id,form=form)
        else:
            form = MyForm()
            flash("Code  is invalid")
            return render_template("code_fil.html",userz=user_id,form=form)
    


@app.route('/paym')
@login_required
@log_execution_time
def paym_form():
    package = request.args.get('package') or None
    print("order package",package)
    form = MyForm()
    if int(package)  == 3:
        package_amount =  300
    elif int(package) == 6:
        package_amount =  510
    elif int(package) == 12:
        package_amount =  900
    else:
        pass
    # Create the PaymentIntent
    payment_intent = stripe.PaymentIntent.create(
        amount= package_amount *  100,  # Amount in the smallest currency unit (e.g., cents)
        currency= "eur",
        # Optional: You can specify payment method types like 'card'
        payment_method_types=['card'],
        description="Payment for export transaction (e.g., goods or services)",
        metadata={
            'export_description': 'Product or service provided for export'
        }
    )
    user_stripe_id = db_models.User.query.filter_by(id=current_user.id).first()
    return render_template('paym_strpjs.html',clsk=payment_intent.client_secret,adl="J348+RCQ, Murree Rd, Aria Mohalla Marir",adci="Rawalpindi",adst="Punjab",adcon="PK", cname=user_stripe_id.name,form=form,package=package)
    user_stripe_id = db_models.UserProfile.query.filter_by(user_id=current_user.id).first()
    form = MyForm()
    # Check if the user profile exists and retrieve the stripe_customer_id
    if user_stripe_id and user_stripe_id.stripe_customer_id:
        sid = user_stripe_id.stripe_customer_id
        print(" already cus")
    else:
        print("not already cus")
        cid = get_stripe_customer_id(current_user)
        user_stripe_id.stripe_customer_id = cid
        # Commit the change to the database
        db.session.commit()
        sid = cid
    return render_template('paymenthg.html',sid=sid, user_id=user_stripe_id.user_id,form=form)

@app.route("/submitt_payment", methods=["POST"])
def SubmittPayment():
    if request.method == 'POST': 
        user_id = request.form.get('user_id') 
        stripeToken = request.form.get('stripeToken') 
        stripe_customer_id = request.form.get('stripe_customer_id') 
        print("resp_tok",stripeToken)
        try:
            respn = stripe.PaymentMethod.create( type="card", card= {'token': str(stripeToken)}, ) 
            attached_source = stripe.PaymentMethod.attach( respn.id, customer=stripe_customer_id, )
            if  db.session.query(db_models.PaymentMethod.query.filter(db_models.PaymentMethod.user_id==user_id).filter(db_models.PaymentMethod.last4==attached_source.card.last4).exists()).scalar():
                print("yes same card")
            else:
                print("not same card")
                payment_method_instance = db_models.PaymentMethod(user_id=user_id,is_default=1,brand=attached_source.card.brand,card_id=attached_source.id,ccv=123,exp_month=attached_source.card.exp_month,exp_year=attached_source.card.exp_year,last4=attached_source.card.last4,name_on_card="xyz")
                db.session.add(payment_method_instance)
                db.session.commit()
            # payrfn = stripe.PaymentIntent.create( amount=3532, currency="usd", payment_method_types=["card"], payment_method_options={"card": {"capture_method": "manual"}}, payment_method =   "pm_1PG4lUP48sR47vUF6n8Qfna6", customer =  "cus_Q6HSsOg8o1glkE", confirm=True, ) 
            # payrfntw = stripe.PaymentIntent.capture(payrfn.id) 
        except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught
            body = e.json_body 
            print("erbbb",body)
        except stripe.error.StripeError as e:
            print("eroo",e)
            # Something else happened, completely unrelated to Stripe
        # respn = stripe.PaymentMethod.create( type="card", card= {'token': str(stripeToken)}, ) 
        # print("reson",respn)  
        # attached_source = stripe.PaymentMethod.attach( respn.id, customer=stripe_customer_id, ) 
        # payment_method_instance = PaymentMethod.objects.create(user_id=user_id,is_default=1,brand=attached_source.card.brand,card_id=attached_source.id,ccv=123,exp_month=attached_source.card.exp_month,exp_year=attached_source.card.exp_year,last4=attached_source.card.last4,name_on_card="xyz")
        # payment_method_instance.save()
        payrfn = stripe.PaymentIntent.create( amount=1532, currency="usd", payment_method_types=["card"], payment_method_options={"card": {"capture_method": "manual"}}, payment_method = respn.id, customer = stripe_customer_id, ) 
        payrfntw = stripe.PaymentIntent.capture(payrfn.id) 
        print("captuu",payrfntw) 
        # return HttpResponseRedirect(reverse('add_session_form2', kwargs={'session_id': session_id}))

        return redirect(url_for('pricing'))
    return redirect(url_for('paym_form'))

@app.route("/customise_report", methods=["POST"])
@log_execution_time
def customise_report():
    # Handle the form submission
    # logo = request.files.get("logo")
    # logo_link = request.form.get("logoLink")
    form = MyForm()
    bg_color = request.form.get("bg_color")
    title_color = request.form.get("title_color")
    attribut_color = request.form.get("attribut_color")
    bg_font_color = request.form.get("bg_font_color")
    title_font_color = request.form.get("title_font_color")
    attribut_font_color = request.form.get("attribut_font_color")
    font_family = request.form.get("fontFamily")

    # Assuming you have a user session or a way to identify the user
    # user_id = session.get("user_id")  # Replace with your user identification logic
    # user = User.query.get(user_id)  # Fetch the user from the database

    # if request.method == "POST":
    # Check and update user attributes only if they exist
    # if logo:
    #     current_user.logo = logo  # Or save the logo file and update the path
    if bg_color:
        current_user.bg_color = bg_color
    if title_color:
        current_user.title_color = title_color
    if attribut_color:
        current_user.attribut_color = attribut_color
    if bg_font_color:
        current_user.bg_font_color = bg_font_color
    if title_font_color:
        current_user.title_font_color = title_font_color
    if attribut_font_color:
        current_user.attribut_font_color = attribut_font_color
    if font_family:
        current_user.font_family = font_family

    # Commit the changes to the database
    db.session.commit()
    flash("Report customised successfully!")
    # else:
    #     flash("User not found!")

    # Redirect to a different page or render a template
    return render_template(
        "preparer.html", cities=cities, report_available=False, user=current_user, form = form
    )

@app.route("/preparer", methods=["GET", "POST"])
@login_required
@log_execution_time

def preparer():
    if not current_user.is_authenticated:
        flash("Please log in to generate reports.", "warning")
        return redirect(url_for("connexion"))
    
    form = MyForm()
    rep_count = False
    if  db.session.query(db_models.User.query.filter(db_models.User.id==current_user.id).filter(db_models.User.reports_count==0).exists()).scalar():
        rep_count = True
    # no_report = request.args.get('no_report') or None
    # print("no_report",no_report)
    
    if request.method == "POST":
        # if (current_user.consumed_reports > 5) and (
        #     current_user.subscription_status == "free"
        # ):
        #     # flash("Vous avez dépasser le nombre de rapport gratuits.", "warning")
        #     return jsonify(
        #         {
        #             "message": "Vous avez dépasser le nombre de rapports gratuits.",
        #             "message_class": "error",
        #             "report_available": False,
        #             "report_name": "",
        #         }
        #     )
        # else:
        selected_city = request.form["city"]
        type_bien = request.form["property_type"]

        criteria = dict(commune=selected_city, type_local=type_bien)
        print("critera dd",criteria)

        year = dg.get_annee_max()["data"][0]["Annee"] + 1
        report_name = f"{criteria['commune']}_{criteria['type_local']}_{year}"
        report_name = report_name.replace(" ", "_")

        report_path = f"reports/{report_name}.xlsx"
        report_name = f"{report_name}.xlsx"

        # if file_exists_in_bucket(report_name):
        #     logging.debug(
        #         f"File exist in bucket: {report_name} | {report_path}"
        #     )
        #     # download_file_from_bucket(
        #     #     report_name, report_path
        #     # )  # Download the file
        #     # customise_workbook(
        #     #     current_user, report_path, REPORT_DIR, bucket_logo
        #     # )
        #     current_user.consumed_reports += 1
        #     db.session.commit()

        #     return jsonify(
        #         {
        #             "message": f"Télécharger le rapport {report_name}.",
        #             "message_class": "success",
        #             "report_available": True,
        #             "report_name": report_name,
        #         }
        #     )
        # else:
        analytics = dg.get_transactions_stats(criteria)
        # analytics = analytics.replace(0, None)

        if analytics.empty:
            flash(f"{criteria['type_local']} non disponible pour {criteria['commune']}.","error")
            return redirect(url_for('preparer'))
            # flash(f"{criteria['type_local']} non disponible pour {criteria['commune']}.","error")
            # return redirect(url_for('preparer'))
            #return redirect(url_for('preparer',no_report=f"{criteria['type_local']} non disponible pour {criteria['commune']}."))
            return jsonify(
                {
                    "message": f"{criteria['type_local']} non disponible pour {criteria['commune']}.",
                    "message_class": "error",
                    "report_available": False,
                    "reports_count_flag ":"true",
                }
            )

        historique_volumes_pieces = dg.get_historique_volumes_pieces(
            criteria
        )
        historique_volumes_pieces = historique_volumes_pieces.replace(
            0, None
        )

        historique_volumes_surfaces = dg.get_historique_volumes_surfaces(
            criteria
        )
        historique_volumes_surfaces = historique_volumes_surfaces.replace(
            0, None
        )

        historique_prix_m2_pieces = dg.get_historique_prix_m2_pieces(
            criteria
        )
        # historique_prix_m2_pieces = historique_prix_m2_pieces.replace(0, None)

        scoring_voies = dg.get_scoring_voies(criteria)
        distributions_decotes = dg.get_distributions_decotes(criteria)

        surface = analytics.iloc[[-1]].surface.values[0]
        prix_m2 = analytics.iloc[[-1]].prix_m2_c.values[0]
        prix_marche = int(prix_m2 * surface)
        analytics.prix_m2_c = analytics.prix_m2_c.astype(int)


        new_df = pd.read_csv(CS_FL_DIR)
        rg.REPORT_BUILDER(
            report_name=report_name,
            df_stats=analytics[["annee", "prix_m2_c50", "Volume_c"]],
            df_volumes_pieces=historique_volumes_pieces,
            df_prix_m2_pieces=historique_prix_m2_pieces,
            df_volumes_surfaces=historique_volumes_surfaces,
            df_distributions_decotes=distributions_decotes,
            df_scoring=new_df,
            # user_logo=current_user.logo,
            # user_website=current_user.website,
            color_palette=color_palette,
            prix_marche=prix_marche,
            taux_frais=0.15,
            taux_travaux=0.1,
            bbg_color="#73a1b2",
            info_font_color="#9da19e",
            selection_color="#d99795",
            criteria=criteria,
        )


        # report = rg.REPORT_BUILDER(
        # try:
        #     rg.REPORT_BUILDER(
        #         report_name=report_name,
        #         df_stats=analytics[["annee", "prix_m2_c50", "Volume_c"]],
        #         df_volumes_pieces=historique_volumes_pieces,
        #         df_prix_m2_pieces=historique_prix_m2_pieces,
        #         df_volumes_surfaces=historique_volumes_surfaces,
        #         df_distributions_decotes=distributions_decotes,
        #         df_scoring=scoring_voies,
        #         # user_logo=current_user.logo,
        #         # user_website=current_user.website,
        #         color_palette=color_palette,
        #         prix_marche=prix_marche,
        #         taux_frais=0.15,
        #         taux_travaux=0.1,
        #         bbg_color="#73a1b2",
        #         info_font_color="#9da19e",
        #         selection_color="#d99795",
        #         criteria=criteria,
        #     )
        # except:
        #     new_df = pd.read_csv(CS_FL_DIR)
        #     rg.REPORT_BUILDER(
        #         report_name=report_name,
        #         df_stats=analytics[["annee", "prix_m2_c50", "Volume_c"]],
        #         df_volumes_pieces=historique_volumes_pieces,
        #         df_prix_m2_pieces=historique_prix_m2_pieces,
        #         df_volumes_surfaces=historique_volumes_surfaces,
        #         df_distributions_decotes=distributions_decotes,
        #         df_scoring=new_df,
        #         # user_logo=current_user.logo,
        #         # user_website=current_user.website,
        #         color_palette=color_palette,
        #         prix_marche=prix_marche,
        #         taux_frais=0.15,
        #         taux_travaux=0.1,
        #         bbg_color="#73a1b2",
        #         info_font_color="#9da19e",
        #         selection_color="#d99795",
        #         criteria=criteria,
        #     )
            # return jsonify(
            #     {
            #         "message": f"{criteria['type_local']} non disponible pour {criteria['commune']}.",
            #         "message_class": "error",
            #         "report_available": False,
            #         "reports_count_flag ":"true",
            #     }
            # )

        # report_path = os.path.join(BASE_DIR, '..', report_path)
        # report_path = os.path.join(REPORTS_DIR, report_name)
        # upload_file_to_bucket(report_name, report_path)
        # customise_workbook(
        #     current_user, report_path, REPORT_DIR, bucket_logo
        # )
        reports_count_flag = "true"
        if  current_user.reports_count  == 1:
            reports_count_flag = "false" 

        current_user.consumed_reports += 1
        current_user.reports_count = current_user.reports_count - 1
        if   current_user.downloaded_current  is  None:
            current_user.downloaded_current = 1
        else:
            current_user.downloaded_current  =  current_user.downloaded_current + 1
        if   current_user.downloaded_history  is  None:
            current_user.downloaded_history = 1
        else:
            current_user.downloaded_history  =  current_user.downloaded_history + 1 
        db.session.commit()

        report_log_instance = db_models.ReportsLog(user_id=current_user.id,city=selected_city,property_type=type_bien,download_date=datetime.now())
        db.session.add(report_log_instance)
        db.session.commit()

        flash(f"Télécharger le rapport {report_name}.","info")
        return redirect(url_for('preparer'))

        return jsonify(
            {
                "message": f"Télécharger le rapport {report_name}.",
                "message_class": "success",
                "report_available": True,
                "report_name": report_name,
                "reports_count_flag":reports_count_flag,
            }
        )

    
    # if no_report is None:
    #     pass
    # else:
    #     flash(no_report,"error")
    # print("preparer cities",cities)
    return render_template(
        "preparerc.html", cities=cities, report_available=False, user=current_user,form=form,
        rep_count=rep_count
    )
    
    # if request.method == "POST":
    #     if (current_user.consumed_reports > 5) and (
    #         current_user.subscription_status == "free"
    #     ):
    #         # flash("Vous avez dépasser le nombre de rapport gratuits.", "warning")
    #         return jsonify(
    #             {
    #                 "message": "Vous avez dépasser le nombre de rapports gratuits.",
    #                 "message_class": "error",
    #                 "report_available": False,
    #                 "report_name": "",
    #             }
    #         )
    #     else:
    #         selected_city = request.form["city"]
    #         type_bien = request.form["property_type"]

    #         criteria = dict(commune=selected_city, type_local=type_bien)

    #         year = dg.get_annee_max()["data"][0]["Annee"] + 1
    #         report_name = f"{criteria['commune']}_{criteria['type_local']}_{year}"
    #         report_name = report_name.replace(" ", "_")

    #         report_path = f"reports/{report_name}.xlsx"
    #         report_name = f"{report_name}.xlsx"

    #         # if file_exists_in_bucket(report_name):
    #         #     logging.debug(
    #         #         f"File exist in bucket: {report_name} | {report_path}"
    #         #     )
    #         #     # download_file_from_bucket(
    #         #     #     report_name, report_path
    #         #     # )  # Download the file
    #         #     # customise_workbook(
    #         #     #     current_user, report_path, REPORT_DIR, bucket_logo
    #         #     # )
    #         #     current_user.consumed_reports += 1
    #         #     db.session.commit()

    #         #     return jsonify(
    #         #         {
    #         #             "message": f"Télécharger le rapport {report_name}.",
    #         #             "message_class": "success",
    #         #             "report_available": True,
    #         #             "report_name": report_name,
    #         #         }
    #         #     )
    #         # else:
    #         analytics = dg.get_transactions_stats(criteria)
    #         # analytics = analytics.replace(0, None)

    #         if analytics.empty:
    #             return jsonify(
    #                 {
    #                     "message": f"{criteria['type_local']} non disponible pour {criteria['commune']}.",
    #                     "message_class": "error",
    #                     "report_available": False,
    #                 }
    #             )

    #         historique_volumes_pieces = dg.get_historique_volumes_pieces(
    #             criteria
    #         )
    #         historique_volumes_pieces = historique_volumes_pieces.replace(
    #             0, None
    #         )

    #         historique_volumes_surfaces = dg.get_historique_volumes_surfaces(
    #             criteria
    #         )
    #         historique_volumes_surfaces = historique_volumes_surfaces.replace(
    #             0, None
    #         )

    #         historique_prix_m2_pieces = dg.get_historique_prix_m2_pieces(
    #             criteria
    #         )
    #         # historique_prix_m2_pieces = historique_prix_m2_pieces.replace(0, None)

    #         scoring_voies = dg.get_scoring_voies(criteria)
    #         distributions_decotes = dg.get_distributions_decotes(criteria)

    #         surface = analytics.iloc[[-1]].surface.values[0]
    #         prix_m2 = analytics.iloc[[-1]].prix_m2_c.values[0]
    #         prix_marche = int(prix_m2 * surface)
    #         analytics.prix_m2_c = analytics.prix_m2_c.astype(int)

    #         # report = rg.REPORT_BUILDER(
    #         rg.REPORT_BUILDER(
    #             report_name=report_name,
    #             df_stats=analytics[["annee", "prix_m2_c50", "Volume_c"]],
    #             df_volumes_pieces=historique_volumes_pieces,
    #             df_prix_m2_pieces=historique_prix_m2_pieces,
    #             df_volumes_surfaces=historique_volumes_surfaces,
    #             df_distributions_decotes=distributions_decotes,
    #             df_scoring=scoring_voies,
    #             # user_logo=current_user.logo,
    #             # user_website=current_user.website,
    #             color_palette=color_palette,
    #             prix_marche=prix_marche,
    #             taux_frais=0.15,
    #             taux_travaux=0.1,
    #             bbg_color="#73a1b2",
    #             info_font_color="#9da19e",
    #             selection_color="#d99795",
    #             criteria=criteria,
    #         )

    #         # report_path = os.path.join(BASE_DIR, '..', report_path)
    #         # report_path = os.path.join(REPORTS_DIR, report_name)
    #         # upload_file_to_bucket(report_name, report_path)
    #         # customise_workbook(
    #         #     current_user, report_path, REPORT_DIR, bucket_logo
    #         # )

    #         current_user.consumed_reports += 1
    #         db.session.commit()

    #         return jsonify(
    #             {
    #                 "message": f"Télécharger le rapport {report_name}.",
    #                 "message_class": "success",
    #                 "report_available": True,
    #                 "report_name": report_name,
    #             }
    #         )

    
    # user_reports = ReportsLog.query.filter_by(user_id=current_user.id).all()
    # return render_template("preparer.html", reports=user_reports  )
    



    





@app.route("/download/<report_name>", methods=["GET"])
@log_execution_time
def download(report_name):
    print(f"#########: {report_name}")
    # report_path = os.path.join(BASE_DIR, 'reports', report_name)
    # report_path = os.path.join(BASE_DIR, '..', report_name)
    report_path = os.path.join(REPORTS_DIR, report_name)
    # print(f"#########: {report_path}")
    logging.debug(f"Report path: {report_path}")
    if os.path.exists(report_path):
        # add_user_logo(current_user, REPORT_DIR, report_path, bucket_logo)
        # customise_workbook(current_user, report_path, REPORT_DIR, bucket_logo)

        return send_file(report_path, as_attachment=True)
    else:
        return f"File {report_path} not found", 404

@app.route("/frais", methods=["GET", "POST"])
@login_required
@log_execution_time
def frais():

    if not current_user.is_authenticated:
        flash("Connexion requise.", "warning")
        return redirect(url_for("connexion"))
    form = MyForm()
    if request.method == "POST":

        user_type = request.form.get("user_type")
        prix_adjudication = float(request.form.get("prix_adjudication", 0))
        frais_representation = float(request.form.get("frais_representation", 0))
        frais_prealable = float(request.form.get("frais_prealable", 0))
        autres_frais = float(request.form.get("autres_frais", 0))

        # Calculate emoluments
        emoluments = 0
        if prix_adjudication < 6500:
            emoluments = prix_adjudication * 0.07256
        elif 6500 <= prix_adjudication <= 17000:
            emoluments = ((prix_adjudication - 6500) * 0.02993) + 472
        elif 17000 < prix_adjudication <= 60000:
            emoluments = ((prix_adjudication - 17000) * 0.01995) + 786
        else:
            emoluments = ((prix_adjudication - 60000) * 0.01497) + 1644
        tva = emoluments * 0.2
        emoluments_ht = emoluments
        emoluments *= 1.20  # Add 20% VAT

        # Calculate taxes based on user type
        if user_type == "particulier":
            taxe_departementale = prix_adjudication * 0.045
            taxe_communale = prix_adjudication * 0.012
            frais_assiette_recouvrement = taxe_departementale * 0.0237
            droits_enregistrement = (
                taxe_departementale + taxe_communale + frais_assiette_recouvrement
            )
        else:
            droits_enregistrement = (prix_adjudication * 0.00715) + (
                prix_adjudication * 0.0237
            )

        frais_publication = (
            max(prix_adjudication * 0.001, 15) + 12 + 46
        )  # 0.1% + 12€ + 46€
        frais_radiation = prix_adjudication * 0.001  # 1€ per 1000€

        total_frais = (
            frais_representation
            + frais_prealable
            + autres_frais
            + emoluments
            + droits_enregistrement
            + frais_publication
            + frais_radiation
        )
        cout_operation = prix_adjudication + total_frais
        return jsonify(
            {
                "prix_adjudication": prix_adjudication,
                "tva": round(tva, 2),
                "emoluments_ht": round(emoluments_ht, 2),
                "emoluments": round(emoluments, 2),
                "droits_enregistrement": round(droits_enregistrement, 2),
                "frais_publication": round(frais_publication, 2),
                "frais_radiation": round(frais_radiation, 2),
                "total_frais": round(total_frais, 2),
                "cout_operation": round(cout_operation, 2),
            }
        )

    return render_template("frais.html",form=form)

# @app.route("/test")
# def test():
#     return render_template("test.html")

@app.route("/test_auth")
def test_auth():
    if current_user.is_authenticated:
        return "User is authenticated"
    else:
        return "User is not authenticated"

@app.route("/outil")
@log_execution_time
def outil():
    user = User.query.filter_by(name="OMOLA").first()

    if user:
        print(f"User found: {user.name}, {user.email}")
    else:
        print("User not found flaskii")
    return render_template("outil.html")

@app.route("/pricing")
@log_execution_time
def pricing():
    free_report = request.args.get('free_report') or None
    userz = request.args.get('userz') or None
    package = request.args.get('package') or None
    print("pricing userz",userz,package,free_report)
    if  free_report == str(121):
        if   current_user.is_authenticated:
            db.session.query(db_models.User).filter(db_models.User.id == current_user.id).update({'free_rep':False,'reports_count':1,'subs_type':"free"})
            db.session.commit()  # Don't forget to commit the changes
            this_user_mail =  db.session.query(db_models.User.email).filter(db_models.User.id == current_user.id).scalar()
            print("this_user_mail ",this_user_mail)
            context_data = {'codevar': "you got 1  free report",'link': f"Merci d'avoir choisi notre forfait gratuit ! Nous sommes ravis de vous offrir l’accès à 1 téléchargement de rapport gratuit.",'flag_password_reset': False,'flag_confirm_email':"121"}

            html_message = render_template('confrim_email.html', **context_data) 
            msg = Message(
                subject= "Confirmation de votre abonnement gratuit – 1 téléchargement de rapport gratuit",
                sender=os.getenv("EMAIL_SENDER"),
                recipients=[this_user_mail], 
                html=html_message
            )
            # msg = Message(
            #     "Confirmation de votre abonnement gratuit – 1 téléchargement de rapport gratuit",
            #     sender=os.getenv(
            #         "EMAIL_SENDER"
            #     ),  # Use environment variable for sender email
            #     recipients=[this_user_mail],
            #     body=f"Merci d'avoir choisi notre forfait gratuit ! Nous sommes ravis de vous offrir l’accès à 1 téléchargement de rapport gratuit.",
            # )
            try:
                mail.send(msg)
            except Exception as e:
                logging.error(f"free report confi Failed to send email to {this_user_mail}: {e}")
            subs_flag = True
            user = User.query.filter_by(id=current_user.id).first()
            if  user.is_subscribed:
                subs_flag = False
            context = { "free_flag": False,"subs_flag":subs_flag}
            return render_template("pricing.html", **context)
        else:
            flash("Login first to complete this action","error")
            context = { "free_flag": True,"subs_flag":True}
            return render_template("pricing.html", **context)


    # else:

    if userz is None:
        pass
    elif userz:
        if int(package)  == 3:
            subs_type = "3 mois"
            subs_end = datetime.now() + relativedelta(months=+3)
            reports_count = 15
        elif int(package) == 6:
            subs_type = "6 mois"
            subs_end = datetime.now() + relativedelta(months=+6)
            reports_count = 45
        elif int(package) == 12:
            subs_type = "1 an"
            subs_end = datetime.now() + relativedelta(months=+12)
            reports_count = 80
        else:
            pass

        print("subs end",subs_end)
        updatuser = {'is_subscribed': True,'free_rep':False,'subscription_ends':subs_end,"reports_count":reports_count,
            "subs_type": subs_type,"downloaded_current":0,"subs_start": datetime.now()
        }
        db.session.query(db_models.User).filter(db_models.User.id == current_user.id).update(updatuser)
        db.session.commit()  # Don't forget to commit the changes
        this_user_mail =  db.session.query(db_models.User.email).filter(db_models.User.id == current_user.id).scalar()
        print("this_user_mail ",this_user_mail)
        #m_body = "Thank you for subscribing to our 3-month package! We're excited to have you on board."
        context_data = {'codevar': "you got " +  str(reports_count)  + " reports",'link': f"Merci de vous être abonné à notre {subs_type} emballer! Nous sommes ravis de vous avoir à bord.",'flag_password_reset': False,'flag_confirm_email':"121"}

        html_message = render_template('confrim_email.html', **context_data) 
        msg = Message(
            subject= "Confirmation d'abonnement",
            sender=os.getenv("EMAIL_SENDER"),
            recipients=[this_user_mail], 
            html=html_message
        )
        # msg = Message(
        #     "Confirmation d'abonnement",
        #     sender=os.getenv(
        #         "EMAIL_SENDER"
        #     ),  # Use environment variable for sender email
        #     recipients=[this_user_mail],
        #     body=f"Merci de vous être abonné à notre {subs_type} emballer! Nous sommes ravis de vous avoir à bord.",
        # )
        try:
            mail.send(msg)
        except Exception as e:
            logging.error(f"subs confi Failed to send email to {this_user_mail}: {e}")
            #flash("Failed to re send ip address confirmation email. Please try again later.", "error")
        flash("abonné avec succès","info")
    elif not userz:
        flash("Une erreur s'est produite lors du paiement","error")
    else:
        pass


    if current_user.is_authenticated:
        user_reports = ReportsLog.query.filter_by(user_id=current_user.id).all()
        # print("user_reports",user_reports)
    else:
        user_reports = None
    free_flag = True
    subs_flag = True
    if current_user.is_authenticated:
        user = User.query.filter_by(id=current_user.id).first()
        if  user:
            free_flag = user.free_rep
            subs_flag = True
            if  user.is_subscribed:
                subs_flag = False
    
    context = { "free_flag": free_flag,
                "user_reports":user_reports,"subs_flag":subs_flag}
    return render_template("pricing.html", **context)


@app.route("/conditions")
@log_execution_time
def conditions():

    
    return render_template("conditions.html")

@app.route("/emailtemp")
@log_execution_time
def emailtemp():

    
    return render_template("email.html")


@app.route("/backed")
@log_execution_time
def backed():
    users = User.query.all()

    
    return render_template("backed.html",users=users)

@app.route("/inscription", methods=["GET", "POST"])
@log_execution_time
def inscription():
    form=MyForm()
    if request.method == "POST":

        # Retrieve data from the form
        firstname = request.form.get("firstname")  # noqa: F841
        if not firstname:
            error_message = "Veuillez entrer votre prénom."
            return render_template("inscription.html", form=form, error_message=error_message)
        name = request.form.get("name")  # noqa: F841
        if not name:
            error_message = "Veuillez entrer votre nom."
            return render_template("inscription.html", form=form, error_message=error_message)
        
        phone = request.form.get("phone")
        if not phone:
            error_message = "Veuillez entrer votre numéro de téléphone."
            return render_template("inscription.html", form=form, error_message=error_message)
        email = request.form.get("email")  # noqa: F841
        if not email:
            error_message = "Veuillez entrer votre adresse email."
            return render_template("inscription.html", form=form, error_message=error_message)
        post_code = request.form.get("post-code")
        if not post_code:
            error_message = "Veuillez entrer votre code postal."
            return render_template("inscription.html", form=form, error_message=error_message)
        address = request.form.get("address")  # noqa: F841
        if not address:
            error_message = "Veuillez entrer votre adresse."
            return render_template("inscription.html", form=form, error_message=error_message)
        password = request.form.get("password")  # noqa: F841
        if not password:
            error_message = "Veuillez entrer votre mot de passe."
            return render_template("inscription.html", form=form, error_message=error_message)
        password_repeat = request.form.get("password-repeat")  # noqa: F841
        if not password_repeat:
            error_message = "Veuillez répéter votre mot de passe."
            return render_template("inscription.html", form=form, error_message=error_message)
        
        terms_checkbox = request.form.get("terms-checkbox")
        if not terms_checkbox:
            error_message = "Vous devez accepter les conditions d'utilisation."
            return render_template("inscription.html", form=form, error_message=error_message)
        logging.debug(f"USER INFO: {firstname}, {name}, {phone}, {email}, {post_code}, {address}")

        # Server-side validation
        if password != password_repeat:
            # Pass error message to the template if passwords don't match
            flash("Les mots de passe ne correspondent pas.", "error")
            return render_template(
                "inscription.html",
                error_message="Les mots de passe ne correspondent pas.",
            )

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            # flash("Email already registered", "error")
            # return redirect(url_for("inscription"))
            flash("Email déjà enregistré.", "error")
            return render_template("inscription.html",error_message="Email already registered",form=form )
        
        # Check if user with this phone already exists
        existing_user = User.query.filter_by(phone=phone).first()
        if existing_user:
            
            flash("Téléphone déjà enregistré.", "error")
            return render_template("inscription.html", error_message="Téléphone already registered",form=form  )

        # Create a new user and save to database
        new_user = User(firstname=firstname, name=name, phone=phone, email=email, post_code = post_code, address = address, city = address)
        new_user.set_password(password)  # Hash the password
        db.session.add(new_user)
        db.session.commit()

        userprof = db_models.UserProfile(user_id=new_user.id)
        db.session.add(userprof)
        db.session.commit()

        # Send confirmation email for activation
        send_confirmation_email(email)  # {{ edit_1 }}

        # Process the form data (e.g., save it to the database)
        # Redirect to the login page after successful submission
        flash("Veuillez vérifier votre email et valider votre profile.", "info")
        return redirect(url_for("connexion"))

    # Render the form page for GET requests
    # flash("Veuillez vérifier votre email et valider votre.", "info")
    return render_template("inscription.html",form=form)

    # Render the form page for GET requests
    # return render_template("inscription.html")

@app.route("/confirm_email/<token>")
@log_execution_time
def confirm_email(token):
    try:
        # email = s.loads(token, salt="email-confirmation-salt", max_age=3600)
        email = confirm_token(
            token, salt="email-confirmation-salt", expiration=3600
        )
    except Exception as e:
        logging.error(f"confirm_email - An error occurred: {e}")
        # confirm_email
        # return "The confirmation link is invalid or has expired."
        # flash("The confirmation link is invalid or has expired.", "error")
        flash("Le lien de confirmation est invalide ou a expiré.", "error")
        return redirect(url_for("login"))
    # Activate the user's account after email verification
    user = User.query.filter_by(email=email).first_or_404()
    try:
        if user.is_active:
            flash("Compte déjà confirmé. Veuillez vous connecter.", "info")
        else:
            user.is_active = True
            db.session.commit()
            flash(
                "Email confirmé avec succès ! Vous pouvez maintenant vous connecter.",
                "success",
            )
    except Exception as e:
        db.session.rollback()
        # flash(f"Error activating account: {e}", "error")
        logging.error(f"Error activating account: {e}")
    # return 'Email confirmed. You can now log in.'
    return redirect(url_for("connexion"))

@app.route("/connexion", methods=["GET", "POST"])
@log_execution_time
def connexion():
    form=MyForm()
    if request.method == "POST":
        # Retrieve form data
        email = request.form.get("email")
        if not email:
            error_message = "Veuillez entrer votre adresse email."
            return render_template("connexion.html", form=form, error_message=error_message)
        password = request.form.get("psw")
        if not password:
            error_message = "Veuillez entrer votre mot de passe."
            return render_template("connexion.html", form=form, error_message=error_message)
        next = request.form.get("next")
        remember_me = request.form.get("remember_me")
        print("remember_me",remember_me)
        # Perform login logic here (e.g., authenticate user)
        # For demonstration, let's check a dummy condition
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password) and user.is_active:
            remad = request.remote_addr
            print("request.remote_addr",remad,type(remad))
            if  user.ip_ad is None:
                pass
            else:
                if  user.ip_ad ==  str(remad):
                    pass
                else:
                    code_timer = datetime.now() + timedelta(minutes=2) 
                    codevar = ''.join(random.choices(string.ascii_letters + string.digits, k=5))     #str(uuid.uuid4())
                    db.session.query(db_models.User).filter(db_models.User.id == user.id).update({'verif_code': codevar,"code_timer":code_timer})
                    db.session.commit()  # Don't forget to commit the changes
                    context_data = {'codevar':codevar,'link': f"Pour confirmer la nouvelle adresse IP, entrez ce code: ",'flag_password_reset': False,'flag_confirm_email':"121"}

                    html_message = render_template('confrim_email.html', **context_data) 
                    msg = Message(
                        subject= "Confirmation de l'adresse IP",
                        sender=os.getenv("EMAIL_SENDER"),
                        recipients=[user.email], 
                        html=html_message
                    )
                    # msg = Message(
                    #     "Ip Address Confirmation",
                    #     sender=os.getenv(
                    #         "EMAIL_SENDER"
                    #     ),  # Use environment variable for sender email
                    #     recipients=[user.email],
                    #     body=f"To Confirm new ip address enter this code: {codevar}",
                    # )
                    try:
                        mail.send(msg)
                    except Exception as e:
                        logging.error(f"from ip addres Failed to send email to {user.email}: {e}")
                        flash("Failed to send ip address confirmation email. Please try again later.", "error")
                    return  redirect(url_for('code_form',userz=user.id))
                    
            if remember_me:
                print("rem me")
                login_user(user)
                session.permanent = True
            else:
                print("no rem me")
                login_user(user)

            db.session.query(db_models.User).filter(db_models.User.id == user.id).update({'ip_ad': remad})
            db.session.commit()  # Don't forget to commit the changes


            session['email'] = email
            session['password'] = password
            logging.debug(f"User {email} logged in successfully.")
            # current_user.is_authenticated = True

            # return redirect(url_for("preparer"))

            logging.debug(f"Next page {next}.")

            # if not url_has_allowed_host_and_scheme(next, request.host):
            #     return abort(400)
            flash("Connexion réussie !", "success")
            print("next   b",next)
            if next == "/preparer":
                # flash("Connexion réussie.", "success")
                # flash("Connexion réussie !", "info")
                rep_count = False
                if  db.session.query(db_models.User.query.filter(db_models.User.id==current_user.id).filter(db_models.User.reports_count==0).exists()).scalar():
                    rep_count = True
                return render_template(
                    "preparerc.html",
                    cities=cities,
                    # success_message="Connexion réussie.",
                    user=current_user,
                    form=form,
                    rep_count=rep_count,
                )
            
            elif next == "/paym":
                if  user.is_subscribed:
                    return redirect(url_for("pricing"))
                else:
                    return redirect(url_for("paym_form"))
            elif next == "/paym?package=12":
                if  user.is_subscribed:
                    return redirect(url_for("pricing"))
                else:
                    return redirect(url_for("paym_form",package=12))
            elif next == "/paym?package=3":
                if  user.is_subscribed:
                    return redirect(url_for("pricing"))
                else:
                    return redirect(url_for("paym_form",package=3))
            elif next == "/paym?package=6":
                if  user.is_subscribed:
                    return redirect(url_for("pricing"))
                else:
                    return redirect(url_for("paym_form",package=6))
            elif next == "/frais":
                # flash("Connexion réussie.", "success")
                return render_template(
                    "frais.html",
                    # success_message="Connexion réussie.",
                )
            else:
                # flash("Connexion réussie.", "success")
                return render_template(
                    "index.html",
                    # success_message="Connexion réussie.",
                )
        elif user and user.check_password(password) and not user.is_active:
            # send_confirmation_email(user.email)

            flash("Vérifiez votre email pour valider votre compte.", "warning")
            return render_template(
                "connexion.html",form=form
                # error_message="Vérifiez votre email pour valider votre compte.",
            )
        else:
            # flash("Invalid credentials. Please try again.", "error")
            # return redirect(url_for("connexion"))
            logging.warning(f"Failed login attempt for {email}.")
            flash("Identifiants invalides. Veuillez réessayer.", "error")
            return render_template(
                "connexion.html",form=form
                # error_message="Identifiants invalides. Veuillez réessayer.",
            )
    email = ''
    email_f = False
    if 'email' in session:
        print("email in ses")
        email = session["email"]
        email_f = True
    password = ''
    pass_f = False
    if 'password' in session:
        print("pass in ses")
        password = session["password"]
        pass_f = False
    return render_template("connexion.html",form=form,email=email,password=password,pass_f=pass_f,email_f=email_f)

@app.route("/logout")
@log_execution_time
def logout():
    logout_user()
    flash("Déconnexion.", "success")
    return redirect(url_for("index"))

def send_password_reset_email(user_email: str):
    """Send a password reset email to the user."""

    token = generate_token_expiration(user_email, salt="password-reset-salt", expiration=180)  # {{ edit_1 }}
    user = User.query.filter_by(email=user_email).first()
    if user:
        user.token_reset_pass = token 
        db.session.commit()           
        print("Token updated successfully.")
    else:
        print("User not found.")

    link = url_for("reset_password_get", token=token, _external=True)
    flag_password_reset= True
    flag_confirm_email = False
    context_data = { 'link': link,'flag_password_reset':flag_password_reset,'flag_confirm_email':flag_confirm_email}

    html_message = render_template('confrim_email.html', **context_data)
    # plain_message = render_template('confrim_email.txt', **context_data)
    email_subject = "Réinitialisez votre mot de passe"
    msg = Message(
        subject=email_subject,
        sender=os.getenv("EMAIL_SENDER"),
        recipients=[user_email],
        # body=plain_message,
        html=html_message
    )
    # msg = Message(
    #     "Réinitialisez votre mot de passe",
    #     sender=os.getenv("EMAIL_SENDER"),
    #     recipients=[user_email],
    #     body=f"Veuillez cliquer sur le lien suivant pour réinitialiser votre mot de passe. {link}",
    # )
    try:
        mail.send(msg)
    except Exception as e:
        logging.error(f"Failed to send password reset email to {user_email}: {e}")
        flash(
            "Failed to send password reset email. Please try again later.", "error"
        )

@app.route(
    "/reinitialisation", methods=["GET", "POST"]
)  # Route for requesting a password reset
@log_execution_time
def reinitialisation():
    form= MyForm()
    if request.method == "POST":
        email = request.form["email"]
        if not email:
            error_message = "Veuillez entrer votre email."
            return render_template("reinitialisation.html", form=form, error_message=error_message)
        phone = request.form["phone"]
        if not phone:
            error_message = "Veuillez entrer votre téléphone."
            return render_template("reinitialisation.html", form=form, error_message=error_message)
        
        user = User.query.filter_by(email=email,phone=phone).first()
        if user:
            send_password_reset_email(user.email)  # {{ edit_2 }}
            flash("Check your email for the password reset link.", "info")
            return redirect(url_for("connexion"))
        else:
            flash("User not found or phone number/email does not match. Please try again.", "warning")
    return render_template("reinitialisation.html", form=form)




# @app.route("/updatepassword")
# @log_execution_time
# def updatepassword():

#     # Handle POST request when the user submits the form
#     if request.method == "POST":
#         email = request.form["email"]
#         new_password = request.form["new_password"]
#         user = User.query.filter_by(email=email).first()
#         if user:
#             user.set_password(new_password)  # Update the password
#             db.session.commit()
            
#             flash("Your password has been reset successfully. You can now log in.", "success")
#             return redirect(url_for("connexion"))
#         else:
#             flash("User not found. Please try again.", "warning")

    
#     return render_template("email.html")

@app.route("/reset_password/<token>", methods=["POST"])
@log_execution_time
def reset_password_post(token):

    form = MyForm()
    
    email = request.form.get("email")  # Ensure the email is retrieved securely
    new_password = request.form.get("new_password")
    user = User.query.filter_by(email=email).first()
    
    if user:
        user.set_password(new_password)  # Update the user's password
        db.session.commit()
        flash("Your password has been reset successfully. You can now log in.", "success")
        return redirect(url_for("connexion"))
    else:
        flash("User not found. Please try again.", "warning")
        return redirect(url_for("reset_password_get", token=token))
    

@app.route("/reset_password/<token>", methods=["GET"])
@log_execution_time
def reset_password_get(token):
    """
    Displays the reset password form (GET request).
    """
    try:
        # Validate token and extract email
        email = confirm_token_expire(token, salt="password-reset-salt")
        print("Email in reset password GET:", email)
    except Exception as e:
        print("Error in reset password GET:", e)
        logging.error(f"reset_password_get - An error occurred: {e}")
        flash("The password reset link is invalid or has expired.", "error")
        return redirect(url_for("connexion"))

    
    form = MyForm()
    return render_template("reset_password.html", email=email, token = token ,form=form)

# def reset_password(token):
#     form= MyForm()

#     if "email" not in session:
#         try:
#             email = confirm_token_expire(token, salt="password-reset-salt")
#             print("Email in reset password:", email)
#             session["email"] = email

            

#         except Exception as e:
#             print("No email gets in reset password")
#             logging.error(f"reset_password - An error occurred: {e}")
#             flash("The password reset link is invalid or has expired.", "error")
#             return redirect(url_for("connexion"))
    
#     else:
#         email = session["email"]

#         if request.method == "POST":
#             logging.debug(f"reset_password - User email: {email}, Token {token}")
#             new_password = request.form["new_password"]
#             user = User.query.filter_by(email=email).first()
#             if user:
#                 user.set_password(new_password)  
#                 db.session.commit()
#                 session.pop("email", None)
#                 flash("Your password has been reset successfully. You can now log in.", "success",)
#                 return redirect(url_for("connexion"))
#             else:
#                 flash("User not found. Please try again.", "warning")

#         return render_template("reset_password.html", token=token,form=form)

# @auth_bp.route('/connexion')
# def connexion():
#     return 'Login page'

@app.route("/contact")
@log_execution_time
def contact():
    form=MyForm()
    return render_template("contact.html",form=form)

@app.route("/submit_contact", methods=["POST"])  # {{ edit_1 }}
@log_execution_time
def submit_contact():
    form=MyForm()

    name = request.form["name"]  # Get the name from the form
    if not name:
        error_message = "Veuillez entrer votre nom."
        return render_template("contact.html", form=form, error_message=error_message)
    
    email = request.form["email"]  # Get the email from the form
    if not email:
        error_message = "Veuillez entrer votre email."
        return render_template("contact.html", form=form, error_message=error_message)
    
    subject = request.form["subject"]  # Get the subject from the form
    if not subject:
        error_message = "Veuillez entrer votre sujet."
        return render_template("contact.html", form=form, error_message=error_message)
    
    message = request.form["message"]  # Get the message from the form
    if not message:
        error_message = "Veuillez entrer votre message."
        return render_template("contact.html", form=form, error_message=error_message)

    # Save the message to the database
    contact_message = ContactMessage(
        name=name, email=email, subject=subject, message=message
    )  # {{ edit_3 

    db.session.add(contact_message)  # Add the message to the session
    db.session.commit()  # Commit the session to save the message

    # Create the email message
    msg = Message(
        f"Contact Utilisateur : {subject}",
        sender=MAIL_DEFAULT_SENDER,
        # recipients=[email],
        recipients=[app.config['MAIL_DEFAULT_SENDER']],
    )
    msg.body = f"Nom: {name}\nEmail: {email}\nMessage: {message}"

    try:
        mail.send(msg)  # Send the email
        flash(
            "Votre message a été envoyé avec succès!", "success"
        )  # Success message
    except Exception as e:
        logging.error(f"Failed to send email: {e}")
        flash(
            "Échec de l'envoi du message. Veuillez réessayer.", "error"
        )  # Error message

    return redirect(url_for("contact"))  # Redirect back to the contact page

# @app.route("/update_profile", methods=["GET", "POST"])
# @login_required
# @log_execution_time
# def update_profile():
#     if request.method == "POST":
#         name = request.form.get("name")
#         firstname = request.form.get("firstname")
#         city = request.form.get("city")
#         password = request.form.get("password")
#         logo = request.files.get("logo")

#         # Update user information
#         if name:
#             current_user.name = name

#         if password:
#             current_user.set_password(
#                 password
#             )  # Assuming you have a method to set the password

#         if logo:
#             # Handle logo upload (save to a directory or cloud storage)
#             logo_path = save_logo(logo)  # Implement this function to save the logo
#             current_user.logo_url = logo_path  # Update the user's logo URL

#         db.session.commit()
#         flash("Profil mis à jour avec succès!", "success")
#         return redirect(url_for("profile"))

#     # GET method: render the profile page with current user info
#     return render_template("profile.html", user=current_user)  # {{ edit_1 }}

@app.context_processor
def inject_user():
    return dict(is_authenticated=current_user.is_authenticated)

# @app.route("/upload_logo", methods=["POST"])
# def upload_logo_route():
#     logo = request.files.get("logo")
#     if logo:
#         # Assuming you have the same upload logic as before
#         logo_path = upload_logo(logo=logo, logoLink=None, user=current_user)
#         current_user.logo = logo_path
#         db.session.commit()
#         return jsonify({"url": logo_path})
#     return jsonify({"error": "Logo upload failed"}), 400

@app.route("/profile", methods=["GET", "POST"])
@login_required
@log_execution_time
def profile():
    form=MyForm()
    if request.method == "POST":
        # Retrieve data from the form
        name = request.form.get("name")
        firstname = request.form.get("firstname")
        email = request.form.get("email")
        city = request.form.get("city")
        website = request.form.get("website")
        # logo = request.files.get("logo")
        logoLink = request.form.get("logoLink")

        # Retrieve color selections
        bg_color = request.form.get("bg_color")
        title_color = request.form.get("title_color")
        attribut_color = request.form.get("attribut_color")

        bg_font_color = request.form.get("bg_font_color")
        title_font_color = request.form.get("title_font_color")
        attribut_font_color = request.form.get("attribut_font_color")

        fontFamily = request.form.get("fontFamily")

        message = "Profile updated successfully!"
        changed_email = False

        # Update user information
        if name:
            current_user.name = name
        if firstname:
            current_user.firstname = firstname
        if email and (current_user.email != email):
            changed_email = True
            message += "<br>Check your email for new email validation."
            current_user.email = email
            current_user.is_active = 0
        if city:
            current_user.city = city
        if website:
            current_user.website = website
        # if logo:
        #     logo_path = upload_logo(logo=logo, logoLink=None, user=current_user)
        #     current_user.logo = logo_path
        #     logging.debug(f"LOGO: {logo_path}")
        # if logoLink:
        #     logo_path = upload_logo(logo=None, logoLink=logoLink, user=current_user)
        #     current_user.logo = logo_path
        #     logging.debug(f"LOGOLINK: {logo_path}")

        # Save the selected colors
        if bg_color:
            current_user.bg_color = bg_color
        if title_color:
            current_user.title_color = title_color
        if attribut_color:
            current_user.attribut_color = attribut_color

        if bg_font_color:
            current_user.bg_font_color = bg_font_color
        if title_font_color:
            current_user.title_font_color = title_font_color
        if attribut_font_color:
            current_user.attribut_font_color = attribut_font_color

        if fontFamily:
            current_user.fontFamily = fontFamily

        db.session.commit()
        # if changed_email:
        #     # send_confirmation_email(email)

        flash(message, "success")
        return redirect(url_for("profile"))

    return render_template("profile.html", form=form, user=current_user)

# {{ edit_2 }}

# @app.route('/color', methods=['POST'])
# def handle_color():
#     color = request.json.get('color')  # Get the color value from the AJAX request
#     return jsonify(success=True, color=color)

# login_manager = LoginManager()
# login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) or None

# Initialize DB and migrations here
db.init_app(app)

# Session setup
app.config["SESSION_TYPE"] = "sqlalchemy"
app.config["SESSION_SQLALCHEMY"] = db

# Initialize Session
Session(app)

# migrate = Migrate(app, db)
migrate = Migrate(app, db)  # noqa: F841

# mail = Mail(app)  # Initialize earlier in the function

# return app

# Initialize the database with the Flask app
# db.init_app(app)

# Set up Flask-Migrate for handling database migrations
# migrate = Migrate(app, db)  # noqa: F841

# Create the tables in the database
# with app.app_context():
#     db.create_all()  # This will create tables based on your models

# mail = Mail(app)


if __name__ == "__main__":
    # app = create_app()

    # Database configuration

    # # Initialize the database with the Flask app
    # db.init_app(app)

    # # Set up Flask-Migrate for handling database migrations
    # migrate = Migrate(app, db)

    # # Create the tables in the database
    # with app.app_context():
    #     db.create_all()  # This will create tables based on your models

    # # mail = Mail(app)

    app.run(host='192.168.18.85', port=8007,debug=True)
