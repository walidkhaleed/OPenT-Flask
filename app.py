from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length
from werkzeug.security import generate_password_hash, check_password_hash
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import Resource
import pycountry
from wtforms import SelectField

# Initialize Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'b45cd4603569ffaa30cdd28e33731ee7c5f2c01a9323ed7b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
admin = Admin(app, name='MyApp Admin', template_mode='bootstrap3')

# Setup OpenTelemetry
service_name = 'flask-app'
resource = Resource(attributes={"service.name": service_name})
trace.set_tracer_provider(TracerProvider(resource=resource))
jaeger_exporter = JaegerExporter(agent_host_name='localhost', agent_port=6831)
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(jaeger_exporter))
FlaskInstrumentor().instrument_app(app)
tracer = trace.get_tracer(__name__)

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    password = db.Column(db.String(80))
    email = db.Column(db.String(50), unique=True)  # Added email field
    nationality = db.Column(db.String(30))  # Added nationality field


class UserModelView(ModelView):
    # column_exclude_list = ['password']  # Excluding the password from being displayed
    # form_excluded_columns = ['password']  # Excluding the password field in forms
    column_searchable_list = ['username', 'email', 'nationality']  # Making username and email searchable
    column_filters = ['username', 'email', 'nationality']  # Allowing filtering by username, email, and nationality

    # Optionally, you can explicitly define the columns to include
    column_list = ['id', 'username', 'email', 'nationality']

    def is_accessible(self):
        return current_user.is_authenticated and current_user.username == 'adminexample' # Assuming admin has ID 1
    


admin.add_view(UserModelView(User, db.session))

def get_country_choices():
    countries = [(country.alpha_2, country.name) for country in pycountry.countries]
    countries.insert(0, ('', 'Select Nationality'))  # Add default empty choice
    return countries

# User loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Forms
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired()])  # Added email field
    nationality = SelectField('Nationality', choices=get_country_choices())
    submit = SubmitField('Register')


# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.username.data == 'adminexample' and form.password.data == '123456':
            user = User.query.filter_by(username='adminexample').first()
            if not user:
                # Optionally, create the admin user in the database if not exists
                user = User(username='adminexample')  # You might need to set other required fields
                db.session.add(user)
                db.session.commit()

            login_user(user)
            return redirect(url_for('admin.index'))  # Redirect to /admin page
        else:
            flash('Invalid username or password')
    return render_template('login.html', form=form)



    
@app.route('/register', methods=['GET', 'POST'])
def register():
    with tracer.start_as_current_span("register"):
        form = RegisterForm()
        if form.validate_on_submit():
            hashed_password = generate_password_hash(form.password.data)
            # Include email and nationality in the new user instance
            new_user = User(username=form.username.data, password=hashed_password, 
                            email=form.email.data, nationality=form.nationality.data)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.username)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
