from flask import Blueprint, request, jsonify, current_app
from ..models import db, User, ActionDefinition, Ministry
from ..services.blockchain import BlockchainService
import re

webhook = Blueprint('webhook', __name__)

@webhook.route('/webhook', methods=['POST'])
def handle_message():
    data = request.json
    print(f"DEBUG FULL PAYLOAD: {data}") # Log everything
    
    sender = None
    text = None
    
    # 1. Try Simplified Format (n8n)
    if 'remoteJid' in data:
        sender = data.get('remoteJid')
        text = data.get('text') or data.get('message')
        
    # 2. Try Evolution API Format (Direct)
    elif 'data' in data:
        key = data.get('data', {}).get('key', {})
        sender = key.get('remoteJid')
        
        # HANDLE GROUPS: If message is from group, sender is the participant
        if sender and sender.endswith('@g.us'):
             participant = key.get('participant')
             print(f"DEBUG: Group Message. Sender: {sender}, Participant: {participant}")
             if participant:
                 sender = participant

        msg_content = data.get('data', {}).get('message', {})
        text = msg_content.get('conversation') or msg_content.get('extendedTextMessage', {}).get('text')
    
    print(f"DEBUG: Extracted Sender: {sender}")
    
    if not sender:
        return jsonify({"status": "ignored", "reason": "no_sender"}), 200
        
    if not text:
        return jsonify({"status": "ignored", "reason": "no_text"}), 200
        
    try:
        # Clean phone number (remove @s.whatsapp.net if present)
        phone = sender.split('@')[0]
        
        # Identify User with Flexible Search (Handle 9th digit issue)
        print(f"DEBUG: Searching user for phone: {phone}")
        user = User.query.filter_by(phone=phone).first()
        
        # Scenario A: Webhook sends 12 digits (No 9th digit), but DB has 13
        if not user and len(phone) == 12:
            phone_with_9 = phone[:4] + '9' + phone[4:]
            print(f"DEBUG: Not found. Trying with 9: {phone_with_9}")
            user = User.query.filter_by(phone=phone_with_9).first()
            
        # Scenario B: Webhook sends 13 digits (With 9th digit), but DB has 12
        if not user and len(phone) == 13:
            phone_without_9 = phone[:4] + phone[5:]
            print(f"DEBUG: Not found. Trying without 9: {phone_without_9}")
            user = User.query.filter_by(phone=phone_without_9).first()
        
        response_text = ""
        
        if not user:
            print(f"DEBUG: User NOT found for {phone}")
            base_url = current_app.config.get('BASE_URL', 'http://localhost:5001')
            # Pass the received phone to pre-fill the form
            response_text = f"👋 Olá! Você ainda não tem cadastro no *Servir*.\nPor favor, cadastre-se em: {base_url}/cadastro?phone={phone}"
        else:
            print(f"DEBUG: User FOUND: {user.name} ({user.id})")
            response_text = process_command(user, text)
            
        # In a real scenario, you would send this response back via Evolution API
        # sending a POST request to the sender.
        # For this MVP, we just return it in the webhook response (some APIs support this)
        # or we print it to logs to show it worked.
        print(f"TO: {phone} | MSG: {response_text}")
        
        return jsonify({"reply": response_text}), 200
        
    except Exception as e:
        print(f"Error processing webhook: {e}")
        return jsonify({"status": "error"}), 500

# State Machine Logic

def set_state(user, state, context=None):
    user.menu_state = state
    user.menu_context = str(context) if context else None
    db.session.commit()

def handle_main_menu(user, text):
    if text == '1' or 'perfil' in text:
        # Stay in MAIN
        return f"👤 *{user.name}*\n🏆 Estágio: {user.badge} {user.stage}\n⭐ Pontos: {user.points}\n\n1️⃣ Ver Perfil\n2️⃣ Ver Missões\n3️⃣ Propor Missão" + ("\n4️⃣ 🛡️ Aprovar Pendentes" if user.role == 'admin' else "")
        
    elif text == '2' or 'missoes' in text or 'missões' in text:
        set_state(user, 'LIST_ACTIONS')
        return get_actions_list(user)
        
    elif text == '3':
        if user.role == 'admin':
            set_state(user, 'PROPOSE_CATEGORY')
            return get_ministries_list(user, for_proposal=True)
        else:
            # User goes directly to General (ID 1)
            set_state(user, 'PROPOSE_NAME', '1')
            return "💡 *Propor Missão (Geral)*\n\nDigite o **Nome** da missão:\n(ou digite 0 para voltar)"
        
    elif text == '4' and user.role == 'admin':
        set_state(user, 'ADMIN_PENDING_LIST')
        return get_pending_list()
        
    else:
        # Default Message (Main Menu)
        if user.role == 'admin':
            return (
                "🤖 *Servir*\n\n"
                "1️⃣ Ver meu Perfil\n"
                "2️⃣ Ver Missões Disponíveis\n"
                "3️⃣ Criar Nova Missão\n"
                "4️⃣ Aprovar Pendentes\n\n"
                "Digite o número da opção desejada."
            )
        else:
            return (
                "🤖 *Servir*\n\n"
                "1️⃣ Ver meu Perfil\n"
                "2️⃣ Ver Missões Disponíveis\n"
                "3️⃣ Propor Nova Missão\n\n"
                "Digite o número da opção desejada."
            )

def get_ministries_list(user, for_proposal=False):
    if for_proposal and user.role == 'admin':
        # Admins can propose for any ministry
        ministries = Ministry.query.all()
    else:
        # Users see: 'Geral' (1) + Their assigned ministries
        # Assuming Geral is always ID 1
        user_ministries = user.ministries
        geral = Ministry.query.get(1)
        
        ministries = list(set([geral] + user_ministries)) if geral else user_ministries
        # Sort by ID
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
    # Get User's allowed ministries
    user_ministries_ids = [m.id for m in user.ministries]
    # Always include Geral (1)
    if 1 not in user_ministries_ids:
        user_ministries_ids.append(1)
        
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
        
        # Add header if ministry changes
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
        
    # Try to find action ID
    try:
        action_id = int(text)
        action = ActionDefinition.query.get(action_id)
        if action and action.status == 'approved':
            # Check if user has access to this ministry
            user_ministries_ids = [m.id for m in user.ministries] + [1] # Always include Geral (1)
            if action.ministry_id not in user_ministries_ids:
                return "🔒 Você não tem acesso a esta missão.\n\n" + get_actions_list(user)

            set_state(user, 'ACTION_DETAIL', action_id)
            return (
                f"📌 *Detalhes da Missão*\n\n"
                f"Nome: {action.name}\n"
                f"Área: {action.ministry.name if action.ministry else 'Geral'}\n"
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
        # Check if needs feedback (Created by Admin)
        action_id = int(user.menu_context)
        action = ActionDefinition.query.get(action_id)
        
        # Determine if creator is admin
        creator = User.query.get(action.created_by_id) if action.created_by_id else None
        creator_is_admin = creator and creator.role == 'admin'
        
        if creator_is_admin:
            set_state(user, 'ACTION_FEEDBACK', action_id)
            return (
                "⭐ *Avaliação (Opcional)*\n\n"
                "De 1 a 5, qual nota você dá para esta missão?\n"
                "(Digite 0 para pular)"
            )
        else:
            # Execute directly
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
    
    if rating:
        payload['rating'] = rating
        
    BlockchainService.add_block(user.id, action.id, payload)
    
    set_state(user, 'MAIN')
    return f"✅ Parabéns! Missão *{action.name}* registrada.\n+ {action.points} pontos!\n\n" + handle_main_menu(user, "menu")

def handle_feedback(user, text):
    try:
        rating = int(text)
        if 0 <= rating <= 5:
            action_id = int(user.menu_context)
            action = ActionDefinition.query.get(action_id)
            # 0 means skip, but we pass None or 0
            final_rating = rating if rating > 0 else None
            return execute_action(user, action, final_rating)
        else:
            return "❌ Digite uma nota entre 1 e 5 (ou 0 para pular)."
    except ValueError:
        return "❌ Digite apenas o número."

# Proposal Flow
def handle_propose_name(user, text):
    if text == '0':
        set_state(user, 'MAIN')
        return handle_main_menu(user, "menu")
        
    if user.role == 'admin':
        # Admin: Continue to define points
        set_state(user, 'PROPOSE_POINTS', text)
        return "💰 *Pontuação*\n\nQuantos pontos essa missão deve valer?\n(Digite um número)"
    else:
        # User: Save directly with 0 points (Pending)
        new_action = ActionDefinition(
            name=text, 
            points=0, 
            created_by_id=user.id,
            status='pending',
            ministry_id=1 # Default to 'Comunidade SER'
        )
        db.session.add(new_action)
        db.session.commit()
        
        set_state(user, 'MAIN')
        return "✅ *Proposta Enviada!*\nSua missão será analisada por um Admin.\n\n" + handle_main_menu(user, "menu")

def handle_propose_points(user, text):
    try:
        points = int(text)
        if points <= 0: return "❌ Pontos devem ser maior que zero."
        
        name = user.menu_context # Retrieved from previous step
        
        # Admin creating 'approved' action directly
        new_action = ActionDefinition(
            name=name, 
            points=points, 
            created_by_id=user.id,
            status='approved'
        )
        db.session.add(new_action)
        db.session.commit()
        
        set_state(user, 'MAIN')
        return f"✅ *Missão Criada!*\nA missão *{name}* ({points} pts) já está disponível.\n\n" + handle_main_menu(user, "menu")
        
    except ValueError:
        return "❌ Digite um número válido."

# Admin Approval Flow
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
                f"🛡️ *Análise de Proposta*\n\n"
                f"Nome: {action.name}\n"
                f"Pontos Sugeridos: {action.points}\n\n"
                f"1️⃣ Aprovar (Definir Pontos)\n"
                f"2️⃣ Rejeitar\n"
                f"0️⃣ Voltar"
            )
        else:
            return "❌ Pendência não encontrada."
    except ValueError:
        return "❌ Digite o ID."

def handle_admin_review(user, text):
    action_id = int(user.menu_context)
    action = ActionDefinition.query.get(action_id)
    
    if not action:
        set_state(user, 'MAIN')
        return "❌ Erro: Ação sumiu."
        
    if text == '1': # Approve -> Ask for Points
        set_state(user, 'ADMIN_SET_POINTS', action_id)
        return f"💰 *Definir Pontuação*\n\nQuantos pontos a missão *{action.name}* vai valer?\n(Digite o valor)"
        
    elif text == '2': # Reject
        action.status = 'rejected'
        db.session.commit()
        set_state(user, 'ADMIN_PENDING_LIST')
        return f"🚫 Missão *{action.name}* REJEITADA.\n\n" + get_pending_list()
        
    elif text == '0':
        set_state(user, 'ADMIN_PENDING_LIST')
        return get_pending_list()
        
    else:
        return "❌ Opção inválida."

def handle_admin_set_points(user, text):
    try:
        points = int(text)
        if points <= 0: return "❌ Pontos devem ser maior que zero."
        
        action_id = int(user.menu_context)
        action = ActionDefinition.query.get(action_id)
        
        if action:
            action.points = points
            action.status = 'approved'
            db.session.commit()
            
            set_state(user, 'ADMIN_PENDING_LIST')
            return f"✅ Missão *{action.name}* APROVADA com {points} pontos!\n\n" + get_pending_list()
        else:
            set_state(user, 'MAIN')
            return "❌ Erro ao salvar."
            
    except ValueError:
        return "❌ Digite um número."

def process_command(user, raw_text):
    # Normalize command check, but keep original text for content
    text = raw_text.lower().strip()
    state = user.menu_state or 'MAIN'
    
    if state == 'MAIN':
        return handle_main_menu(user, text)
    # SELECT_VIEW_CATEGORY removed
    elif state == 'LIST_ACTIONS':
        return handle_list_actions(user, text)
    elif state == 'ACTION_DETAIL':
        return handle_action_detail(user, text)
    elif state == 'ACTION_FEEDBACK':
        return handle_feedback(user, text)
    elif state == 'PROPOSE_NAME':
        # Pass raw_text to preserve case for Mission Name
        return handle_propose_name(user, raw_text.strip())
    elif state == 'PROPOSE_POINTS':
        return handle_propose_points(user, text)
    elif state == 'ADMIN_PENDING_LIST':
        return handle_admin_pending_list(user, text)
    elif state == 'ADMIN_REVIEW':
        return handle_admin_review(user, text)
    elif state == 'ADMIN_SET_POINTS':
        return handle_admin_set_points(user, text)
    else:
        # Reset if invalid state
        set_state(user, 'MAIN')
        return handle_main_menu(user, text)
