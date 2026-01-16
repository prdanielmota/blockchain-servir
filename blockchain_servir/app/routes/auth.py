from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from ..models import db, User

auth = Blueprint('auth', __name__)

@auth.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    return render_template('landing.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Login inválido. Verifique suas credenciais.')
            
    return render_template('login.html')

@auth.route('/cadastro', methods=['GET', 'POST'])
def register():
    # Pre-fill phone from URL (default to empty string)
    prefill_phone = request.args.get('phone', '')
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        
        # Update prefill_phone in case of error (so user doesn't lose input)
        prefill_phone = phone
        
        # Sanitize phone (remove non-digits)
        # Basic validation
        user_exists = User.query.filter((User.email == email) | (User.phone == phone)).first()
        if user_exists:
            flash('Email ou Telefone já cadastrado.')
            return redirect(url_for('auth.register'))
            
        new_user = User(name=name, email=email, phone=phone)
        new_user.set_password(password)
        
        # Check if it's the FIRST user in the system
        if User.query.count() == 0:
            new_user.role = 'admin'
            flash('Primeiro usuário registrado! Você é ADMIN.')
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Cadastro realizado com sucesso! Faça login.')
        return redirect(url_for('auth.login'))
        
    return render_template('register.html', prefill_phone=prefill_phone)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
