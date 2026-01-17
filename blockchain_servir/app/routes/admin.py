from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from ..models import db, User, Block, ActionDefinition, Ministry

admin = Blueprint('admin', __name__)

@admin.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        users = User.query.all()
        # Get last 20 blocks (latest first)
        blocks = Block.query.order_by(Block.id.desc()).limit(20).all()
        actions = ActionDefinition.query.all()
        
        # Global Ranking (Top 10)
        ranking = User.query.order_by(User.points.desc()).limit(10).all()
        
        # Ministries
        ministries = Ministry.query.all()
        
        # Blockchain Stats
        total_blocks = Block.query.count()
        # Sum points from all blocks (MVP: iterate, but better with SQL func)
        # Using SQLalchemy func would be better: db.session.query(func.sum(User.points)).scalar()
        # But User.points is current state. Let's sum Block data? 
        # For now, let's just use Sum of all User points as "Market Cap"
        total_points = sum(u.points for u in users)
        
        return render_template(
            'dashboard.html', 
            users=users, 
            blocks=blocks, 
            actions=actions, 
            ranking=ranking, 
            ministries=ministries,
            total_blocks=total_blocks,
            total_points=total_points
        )
    else:
        # User View: Only own blocks
        blocks = Block.query.filter_by(user_id=current_user.id).order_by(Block.id.desc()).all()
        return render_template('dashboard.html', blocks=blocks)

@admin.route('/block/<int:id>')
def block_detail(id):
    # Public or Protected? Let's make it public for transparency, or protected.
    # User asked for Etherscan-like, so maybe public? 
    # For now, let's keep login required for simplicity, or allow public if desired.
    # Let's assume login required as it's under admin blueprint but we can allow all users.
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
        
    block = Block.query.get_or_404(id)
    return render_template('block_detail.html', block=block)

# --- NEW CRUD ROUTES ---

# 1. MINISTRIES
@admin.route('/admin/ministries')
@login_required
def list_ministries():
    if current_user.role != 'admin': return "Acesso Negado", 403
    ministries = Ministry.query.all()
    return render_template('admin/ministries_list.html', ministries=ministries)

@admin.route('/admin/ministries/new', methods=['GET', 'POST'])
@login_required
def new_ministry():
    if current_user.role != 'admin': return "Acesso Negado", 403
    
    if request.method == 'POST':
        name = request.form.get('name')
        if Ministry.query.filter_by(name=name).first():
            flash('Ministério já existe.')
        else:
            db.session.add(Ministry(name=name))
            db.session.commit()
            flash('Ministério criado!')
            return redirect(url_for('admin.list_ministries'))
            
    return render_template('admin/ministry_form.html', ministry=None)

@admin.route('/admin/ministries/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_ministry(id):
    if current_user.role != 'admin': return "Acesso Negado", 403
    ministry = Ministry.query.get_or_404(id)
    
    if request.method == 'POST':
        ministry.name = request.form.get('name')
        db.session.commit()
        flash('Atualizado com sucesso!')
        return redirect(url_for('admin.list_ministries'))
        
    return render_template('admin/ministry_form.html', ministry=ministry)

@admin.route('/admin/ministries/delete/<int:id>')
@login_required
def delete_ministry(id):
    if current_user.role != 'admin': return "Acesso Negado", 403
    if id == 1:
        flash('Não é possível excluir o ministério Geral.')
        return redirect(url_for('admin.list_ministries'))
        
    ministry = Ministry.query.get_or_404(id)
    # Move actions to General (1) before deleting
    actions = ActionDefinition.query.filter_by(ministry_id=id).all()
    for a in actions:
        a.ministry_id = 1
    
    db.session.delete(ministry)
    db.session.commit()
    flash('Ministério excluído. Missões movidas para Geral.')
    return redirect(url_for('admin.list_ministries'))

# 2. USERS
@admin.route('/admin/users')
@login_required
def list_users():
    if current_user.role != 'admin': return "Acesso Negado", 403
    users = User.query.all()
    return render_template('admin/users_list.html', users=users)

@admin.route('/admin/users/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    if current_user.role != 'admin': return "Acesso Negado", 403
    user = User.query.get_or_404(id)
    
    if request.method == 'POST':
        user.name = request.form.get('name')
        user.email = request.form.get('email')
        user.phone = request.form.get('phone')
        user.role = request.form.get('role')
        
        # Update Ministries
        selected_ids = request.form.getlist('ministries') # list of strings ['1', '3']
        
        # Clear current ministries
        user.ministries = []
        
        for mid in selected_ids:
            ministry = Ministry.query.get(int(mid))
            if ministry:
                user.ministries.append(ministry)
        
        db.session.commit()
        flash(f'Usuário {user.name} atualizado!')
        return redirect(url_for('admin.list_users'))
        
    ministries = Ministry.query.all()
    return render_template('admin/user_form.html', user=user, ministries=ministries)

@admin.route('/admin/users/delete/<int:id>')
@login_required
def delete_user(id):
    if current_user.role != 'admin': return "Acesso Negado", 403
    if id == current_user.id:
        flash('Você não pode se excluir.')
        return redirect(url_for('admin.list_users'))
        
    user = User.query.get_or_404(id)
    # Caution: Cascading deletes might be needed if user has blocks
    # For now, let's just delete the user. SQLite might error if blocks exist without cascade.
    # Safe approach: Nullify user_id in blocks? No, block needs user.
    # Let's delete blocks too? Or keep user but mark inactive?
    # MVP: Hard Delete
    db.session.delete(user)
    db.session.commit()
    flash('Usuário excluído.')
    return redirect(url_for('admin.list_users'))

# 3. ACTIONS (MISSIONS)
@admin.route('/admin/actions')
@login_required
def list_actions():
    if current_user.role != 'admin': return "Acesso Negado", 403
    actions = ActionDefinition.query.all()
    return render_template('admin/actions_list.html', actions=actions)

@admin.route('/admin/actions/new', methods=['GET', 'POST'])
@login_required
def new_action():
    if current_user.role != 'admin': return "Acesso Negado", 403
    
    if request.method == 'POST':
        name = request.form.get('name')
        points = int(request.form.get('points'))
        ministry_id = int(request.form.get('ministry_id'))
        status = request.form.get('status')
        
        new_action = ActionDefinition(
            name=name, 
            points=points, 
            ministry_id=ministry_id, 
            status=status,
            created_by_id=current_user.id
        )
        db.session.add(new_action)
        db.session.commit()
        flash('Missão criada!')
        return redirect(url_for('admin.list_actions'))
        
    ministries = Ministry.query.all()
    return render_template('admin/action_form.html', action=None, ministries=ministries)

@admin.route('/admin/actions/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_action(id):
    if current_user.role != 'admin': return "Acesso Negado", 403
    action = ActionDefinition.query.get_or_404(id)
    
    if request.method == 'POST':
        action.name = request.form.get('name')
        action.points = int(request.form.get('points'))
        action.ministry_id = int(request.form.get('ministry_id'))
        action.status = request.form.get('status')
        db.session.commit()
        flash('Missão atualizada!')
        return redirect(url_for('admin.list_actions'))
        
    ministries = Ministry.query.all()
    return render_template('admin/action_form.html', action=action, ministries=ministries)

@admin.route('/admin/actions/delete/<int:id>')
@login_required
def delete_action(id):
    if current_user.role != 'admin': return "Acesso Negado", 403
    action = ActionDefinition.query.get_or_404(id)
    db.session.delete(action)
    db.session.commit()
    flash('Missão excluída.')
    return redirect(url_for('admin.list_actions'))
