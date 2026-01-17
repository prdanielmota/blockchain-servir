from flask import Blueprint, request, jsonify, current_app
from ..models import db, User, ActionDefinition, Ministry
from ..services.blockchain import BlockchainService
import re

webhook = Blueprint('webhook', __name__)

DEFAULT_MINISTRY_ID = 1  # 'Comunidade SER'

# --- Helpers ---

def extract_message_data(data):
    """
    Extracts sender and text from various webhook payloads (n8n, Evolution API).
    Returns tuple (sender, text).
    """
    sender = None
    text = None
    
    # 1. Simplified Format (n8n)
    if 'remoteJid' in data:
        sender = data.get('remoteJid')
        text = data.get('text') or data.get('message')
        
    # 2. Evolution API Format
    elif 'data' in data:
        key = data.get('data', {}).get('key', {})
        sender = key.get('remoteJid')
        
        # Handle Groups
        if sender and sender.endswith('@g.us'):
             participant = key.get('participant')
             if participant:
                 sender = participant
                 print(f"DEBUG: Group Message. Sender: {sender} (Participant)")

        msg_content = data.get('data', {}).get('message', {})
        text = msg_content.get('conversation') or msg_content.get('extendedTextMessage', {}).get('text')
        
    return sender, text

def find_user_by_phone(phone_raw):
    """
    Finds a user by phone number, handling the 9th digit ambiguity.
    Returns User object or None.
    """
    # Clean phone (remove suffix)
    phone = phone_raw.split('@')[0]
    
    print(f"DEBUG: Searching user for phone: {phone}")
    
    # 1. Exact Match
    user = User.query.filter_by(phone=phone).first()
    if user: return user
    
    # 2. Try adding 9 (Webhook has 12, DB has 13)
    if len(phone) == 12:
        phone_with_9 = phone[:4] + '9' + phone[4:]
        print(f"DEBUG: Trying with 9: {phone_with_9}")
        user = User.query.filter_by(phone=phone_with_9).first()
        if user: return user
            
    # 3. Try removing 9 (Webhook has 13, DB has 12)
    if len(phone) == 13:
        phone_without_9 = phone[:4] + phone[5:]
        print(f"DEBUG: Trying without 9: {phone_without_9}")
        user = User.query.filter_by(phone=phone_without_9).first()
        
    return user

def set_state(user, state, context=None):
    user.menu_state = state
    user.menu_context = str(context) if context else None
    db.session.commit()

# --- Main Handler ---

@webhook.route('/webhook', methods=['POST'])
def handle_message():
    data = request.json
    print(f"DEBUG PAYLOAD: {data}")
    
    sender, text = extract_message_data(data)
    
    print(f"DEBUG: Extracted Sender: {sender}")
    
    if not sender:
        return jsonify({"status": "ignored", "reason": "no_sender"}), 200
        
    if not text:
        return jsonify({"status": "ignored", "reason": "no_text"}), 200
        
    try:
        user = find_user_by_phone(sender)
        response_text = ""
        
        if not user:
            print(f"DEBUG: User NOT found for {sender}")
            base_url = current_app.config.get('BASE_URL', 'http://localhost:5001')
            # Clean phone for URL (digits only)
            clean_phone = re.sub(r'\D', '', sender.split('@')[0])
            response_text = f"👋 Olá! Você ainda não tem cadastro no *Servir*.\nPor favor, cadastre-se em: {base_url}/cadastro?phone={clean_phone}"
        else:
            print(f"DEBUG: User FOUND: {user.name} ({user.id})")
            response_text = process_command(user, text)
            
        print(f"TO: {sender} | MSG: {response_text}")
        return jsonify({"reply": response_text}), 200
        
    except Exception as e:
        print(f"Error processing webhook: {e}")
        return jsonify({"status": "error"}), 500

# --- State Handlers ---

def handle_main_menu(user, text):
    if text == '1' or 'perfil' in text:
        # Stay in MAIN
        admin_opt = "\n4️⃣ 🛡️ Aprovar Pendentes" if user.role == 'admin' else ""
        return (
            f"👤 *{user.name}*\n"
            f"🏆 Estágio: {user.badge} {user.stage}\n"
            f"⭐ Pontos: {user.points}\n\n"
            f"1️⃣ Ver Perfil\n"
            f"2️⃣ Ver Missões\n"
            f"3️⃣ Propor Missão"
            f"{admin_opt}"
        )
        
    elif text == '2' or 'missoes' in text or 'missões' in text:
        set_state(user, 'LIST_ACTIONS')
        return get_actions_list(user)
        
    elif text == '3':
        if user.role == 'admin':
            set_state(user, 'PROPOSE_CATEGORY')
            return get_ministries_list(user, for_proposal=True)
        else:
            # User goes directly to Default Ministry
            set_state(user, 'PROPOSE_NAME', str(DEFAULT_MINISTRY_ID))
            return "💡 *Propor Missão (Comunidade SER)*\n\nDigite o **Nome** da missão:\n(ou digite 0 para voltar)"
        
    elif text == '4' and user.role == 'admin':
        set_state(user, 'ADMIN_PENDING_LIST')
        return get_pending_list()
        
    else:
        # Default Message (Main Menu)
        menu_items = (
            "1️⃣ Ver meu Perfil\n"
            "2️⃣ Ver Missões Disponíveis\n"
            "3️⃣ Criar Nova Missão\n"
            "4️⃣ Aprovar Pendentes"
        ) if user.role == 'admin' else (
            "1️⃣ Ver meu Perfil\n"
            "2️⃣ Ver Missões Disponíveis\n"
            "3️⃣ Propor Nova Missão"
        )
        
        return f"🤖 *Servir*\n\n{menu_items}\n\nDigite o número da opção desejada."

def get_ministries_list(user, for_proposal=False):
    if for_proposal and user.role == 'admin':
        ministries = Ministry.query.all()
    else:
        # Users see: Default + Their assigned ministries
        user_ministries = user.ministries
        default_min = Ministry.query.get(DEFAULT_MINISTRY_ID)
        
        ministries = list(set([default_min] + user_ministries)) if default_min else user_ministries
        ministries.sort(key=lambda x: x.id)

    if not ministries:
        return "⚠️ Nenhum ministério disponível para você."
        
    title = "💡 *Escolha o Ministério:*" if for_proposal else "📂 *Ver Missões de:*"
    msg = f"{title}\n\n"
    for m in ministries:
        msg += f"{m.id}. {m.name}\n"
    
    msg += "\n0️⃣ Voltar"
    return msg

def get_actions_list(user):
    user_ministries_ids = [m.id for m in user.ministries]
    if DEFAULT_MINISTRY_ID not in user_ministries_ids:
        user_ministries_ids.append(DEFAULT_MINISTRY_ID)
        
    actions = ActionDefinition.query.filter(
        ActionDefinition.is_active == True,
        ActionDefinition.status == 'approved',
        ActionDefinition.ministry_id.in_(user_ministries_ids)
    ).all()
    
    if not actions:
        return "📋 *Missões:*\nNenhuma missão disponível para você no momento.\n\n0️⃣ Voltar"
        
    msg = "📋 *Missões Disponíveis:*\n\n"
    
    # Sort by Ministry then Name
    actions.sort(key=lambda x: (x.ministry_id, x.name))
    
    current_ministry = None
    
    for a in actions:
        ministry_name = a.ministry.name if a.ministry else "Geral"
        
        if ministry_name != current_ministry:
            msg += f"\n📂 *{ministry_name}*\n"
            current_ministry = ministry_name
            
        msg += f"{a.id}. {a.name} ({a.points} pts)\n"
        
    msg += "\nDigite o número da missão para selecionar.\n0️⃣ Voltar ao Menu Principal"
    return msg

def get_pending_list():
    actions = ActionDefinition.query.filter_by(status='pending').all()
    if not actions:
        return "🛡️ *Pendências:*\nNenhuma missão aguardando aprovação.\n\n0️⃣ Voltar"
        
    msg = "🛡️ *Missões Pendentes:*\n\n"
    for a in actions:
        msg += f"{a.id}. {a.name} ({a.points} pts)\n"
    msg += "\nDigite o ID para avaliar ou 0 para voltar."
    return msg

def handle_list_actions(user, text):
    if text == '0' or 'voltar' in text:
        set_state(user, 'MAIN')
        return handle_main_menu(user, "menu")
        
    try:
        action_id = int(text)
        action = ActionDefinition.query.get(action_id)
        if action and action.status == 'approved':
            # Permission Check
            user_ministries_ids = [m.id for m in user.ministries] + [DEFAULT_MINISTRY_ID]
            if action.ministry_id not in user_ministries_ids:
                return "🔒 Você não tem acesso a esta missão.\n\n" + get_actions_list(user)

            set_state(user, 'ACTION_DETAIL', action_id)
            min_name = action.ministry.name if action.ministry else 'Geral'
            return (
                f"📌 *Detalhes da Missão*\n\n"
                f"Nome: {action.name}\n"
                f"Área: {min_name}\n"
                f"Pontos: {action.points}\n\n"
                f"1️⃣ ✅ Marcar como Cumprida\n"
                f"2️⃣ 🔙 Escolher outra missão\n"
                f"0️⃣ 🏠 Menu Principal"
            )
        else:
            return "❌ Missão não encontrada ou não aprovada."
    except ValueError:
        return "❌ Digite apenas o número da missão."

def handle_action_detail(user, text):
    if text == '0':
        set_state(user, 'MAIN')
        return handle_main_menu(user, "menu")
    elif text == '2':
        set_state(user, 'LIST_ACTIONS')
        return get_actions_list(user)
    elif text == '1':
        action_id = int(user.menu_context)
        action = ActionDefinition.query.get(action_id)
        
        # Check if feedback is needed (Creator is Admin)
        creator = User.query.get(action.created_by_id) if action.created_by_id else None
        if creator and creator.role == 'admin':
            set_state(user, 'ACTION_FEEDBACK', action_id)
            return "⭐ *Avaliação (Opcional)*\n\nDe 1 a 5, qual nota você dá?\n(0 para pular)"
        else:
            return execute_action(user, action)
    else:
        return "❌ Opção inválida.\n1️⃣ Confirmar\n2️⃣ Voltar\n0️⃣ Menu Principal"

def execute_action(user, action, rating=None):
    payload = {
        "type": "action_completed",
        "action_name": action.name,
        "points": action.points,
        "user_name": user.name
    }
    if rating: payload['rating'] = rating
        
    BlockchainService.add_block(user.id, action.id, payload)
    
    set_state(user, 'MAIN')
    return f"✅ Parabéns! Missão *{action.name}* registrada.\n+ {action.points} pontos!\n\n" + handle_main_menu(user, "menu")

def handle_feedback(user, text):
    try:
        rating = int(text)
        if 0 <= rating <= 5:
            action_id = int(user.menu_context)
            action = ActionDefinition.query.get(action_id)
            final_rating = rating if rating > 0 else None
            return execute_action(user, action, final_rating)
        return "❌ Digite uma nota entre 1 e 5 (ou 0 para pular)."
    except ValueError:
        return "❌ Digite apenas o número."

def handle_propose_name(user, text):
    if text == '0':
        set_state(user, 'MAIN')
        return handle_main_menu(user, "menu")
        
    if user.role == 'admin':
        set_state(user, 'PROPOSE_POINTS', text)
        return "💰 *Pontuação*\n\nQuantos pontos vale?\n(Digite um número)"
    else:
        new_action = ActionDefinition(
            name=text, 
            points=0, 
            created_by_id=user.id,
            status='pending',
            ministry_id=DEFAULT_MINISTRY_ID
        )
        db.session.add(new_action)
        db.session.commit()
        
        set_state(user, 'MAIN')
        return "✅ *Proposta Enviada!*\nSua missão será analisada por um Admin.\n\n" + handle_main_menu(user, "menu")

def handle_propose_points(user, text):
    try:
        points = int(text)
        if points <= 0: return "❌ Pontos devem ser maior que zero."
        
        name = user.menu_context
        new_action = ActionDefinition(
            name=name, 
            points=points, 
            created_by_id=user.id,
            status='approved'
        )
        db.session.add(new_action)
        db.session.commit()
        
        set_state(user, 'MAIN')
        return f"✅ *Missão Criada!*\n*{name}* ({points} pts).\n\n" + handle_main_menu(user, "menu")
    except ValueError:
        return "❌ Digite um número válido."

def handle_admin_pending_list(user, text):
    if text == '0':
        set_state(user, 'MAIN')
        return handle_main_menu(user, "menu")
    try:
        action_id = int(text)
        action = ActionDefinition.query.get(action_id)
        if action and action.status == 'pending':
            set_state(user, 'ADMIN_REVIEW', action_id)
            return (
                f"🛡️ *Análise*\n\n"
                f"Nome: {action.name}\n"
                f"1️⃣ Aprovar (Definir Pontos)\n"
                f"2️⃣ Rejeitar\n"
                f"0️⃣ Voltar"
            )
        return "❌ Pendência não encontrada."
    except ValueError:
        return "❌ Digite o ID."

def handle_admin_review(user, text):
    action_id = int(user.menu_context)
    action = ActionDefinition.query.get(action_id)
    
    if not action:
        set_state(user, 'MAIN')
        return "❌ Erro: Ação sumiu."
        
    if text == '1': # Approve
        set_state(user, 'ADMIN_SET_POINTS', action_id)
        return f"💰 *Definir Pontuação*\n\nQuantos pontos para *{action.name}*?"
    elif text == '2': # Reject
        action.status = 'rejected'
        db.session.commit()
        set_state(user, 'ADMIN_PENDING_LIST')
        return f"🚫 REJEITADA.\n\n" + get_pending_list()
    elif text == '0':
        set_state(user, 'ADMIN_PENDING_LIST')
        return get_pending_list()
    return "❌ Opção inválida."

def handle_admin_set_points(user, text):
    try:
        points = int(text)
        if points <= 0: return "❌ Pontos > 0."
        
        action_id = int(user.menu_context)
        action = ActionDefinition.query.get(action_id)
        
        if action:
            action.points = points
            action.status = 'approved'
            db.session.commit()
            set_state(user, 'ADMIN_PENDING_LIST')
            return f"✅ APROVADA ({points} pts)!\n\n" + get_pending_list()
        return "❌ Erro ao salvar."
    except ValueError:
        return "❌ Digite um número."

# --- Dispatcher ---

STATE_HANDLERS = {
    'MAIN': handle_main_menu,
    'LIST_ACTIONS': handle_list_actions,
    'ACTION_DETAIL': handle_action_detail,
    'ACTION_FEEDBACK': handle_feedback,
    'PROPOSE_POINTS': handle_propose_points,
    'ADMIN_PENDING_LIST': handle_admin_pending_list,
    'ADMIN_REVIEW': handle_admin_review,
    'ADMIN_SET_POINTS': handle_admin_set_points
    # 'PROPOSE_NAME' is special because it needs raw_text
}

def process_command(user, raw_text):
    text = raw_text.lower().strip()
    state = user.menu_state or 'MAIN'
    
    # Special case for Propose Name (Case Sensitive)
    if state == 'PROPOSE_NAME':
        return handle_propose_name(user, raw_text.strip())
        
    handler = STATE_HANDLERS.get(state, handle_main_menu)
    
    # If state is invalid or handler missing, reset to MAIN
    if state not in STATE_HANDLERS and state != 'PROPOSE_NAME':
        set_state(user, 'MAIN')
        handler = handle_main_menu
        
    return handler(user, text)
