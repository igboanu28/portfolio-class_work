from app import app,db
from flask_login import current_user, login_user, logout_user,login_required
from app.models import User,Portfolio
from flask import render_template, flash, redirect, url_for,request
from app.forms import LoginForm,PasswordForm,RegistrationForm,EditPortfoiloForm
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from flask import send_from_directory,send_file
import os
from datetime import datetime


@app.get('/')
@app.get('/home')
def home():

    view = Portfolio.query.all()
    
    return render_template('home.html',view=view)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        next_page = request.args.get('next')
        login_user(user)
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.get('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    form = PasswordForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user: User = User.query.get(current_user.id)
            user.set_password(form.password.data)
            db.session.commit()
            flash ('Password has been updated!')
        
    return render_template('change_password.html', form=form)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        
@app.get('/user_dashboard/<username>')
@login_required
def user_dashboard(username):
    view = Portfolio.query.all()
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('dashboard.html', user=user, view=view)

# @app.route('/add_portfolio', methods=['GET', 'POST'])
# @login_required
# def add_portfolio():
#     if request.method == 'POST':
#         portfolio_file = request.files['file']

     
#         filename =secure_filename(portfolio_file.filename)

#         adding_portfolio= Portfolio(image_file=portfolio_file.read(), name=filename, user_id=current_user.id)
    
#         db.session.add(adding_portfolio)
#         db.session.commit()

#         flash('file uploaded successfully')

#         return render_template('s.html')
#     return render_template('add_portfolio.html')

UPLOAD_FOLDER = "/home/paul/Desktop/my portfolio/app/static/uploads"
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/add_portfolio', methods=['GET', 'POST'])
def add_portfolio():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash ('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            name=request.form.get("name")
            urls=request.form.get("urls")
            newFile = Portfolio(image_file=file.filename, user_id=current_user.id,name=name,urls=urls)
            db.session.add(newFile)
            db.session.commit()          
            return redirect(url_for('download_file',name=filename ))
 
    return render_template('add_portfolio.html')


@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)
app.add_url_rule(
    "/uploads/<name>", endpoint="download_file", build_only=True
)
@app.get('/user_dashboard/<username>')
@app.get('/show')
def show_images():
    upload = Portfolio.query.all()
    return render_template('dashboard.html', upload=upload)

@app.route('/edit_portfolio/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_portfolio(id):
    form = EditPortfoiloForm()
    edits = Portfolio.query.get(id)

    if request.method == "POST":
        if form.validate_on_submit():

            edits.name = request.form.get("name") 
            edits.urls = request.form.get("urls")
            db.session.commit()
            flash('Your changes have been Updated.')
    return render_template('edit_portfolio.html',edits=edits,form=form)

@app.route("/change/<int:id>", methods=['GET', 'POST'])
def change_images(id):
    change = Portfolio.query.get(id)
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash ('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], change.image_file))
            change.image_file = filename
            db.session.commit()
            flash ('done')
    return render_template('change.html',change=change)
@app.route("/delete/<int:id>")
def delete(id):
    delete = Portfolio.query.get(id)
    db.session.delete(delete)
    db.session.commit()
    flash('You have successfully deleted your item')
    return redirect(url_for('user_dashboard', username=current_user.username))

@app.route('/download')
def download():
    path = '/home/paul/Desktop/all/Modern Python Cookbook - Second Edition_01.pdf'
    return send_file(path, as_attachment=True)
