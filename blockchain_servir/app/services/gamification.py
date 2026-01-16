from ..models import db, User

STAGES = {
    'Caminho': (0, 100, '🌱'),
    'Formação': (101, 300, '📖'),
    'Serviço': (301, 600, '🏹'),
    'Fruto': (601, 999999, '🌳')
}

def update_user_progress(user_id, points_earned):
    user = User.query.get(user_id)
    if not user:
        return

    # Add points
    user.points += points_earned
    
    # Check Stage
    new_stage = user.stage
    new_badge = user.badge
    
    for stage_name, (min_p, max_p, badge) in STAGES.items():
        if min_p <= user.points <= max_p:
            new_stage = stage_name
            new_badge = badge
            break
            
    user.stage = new_stage
    user.badge = new_badge
    
    db.session.commit()
    return user
