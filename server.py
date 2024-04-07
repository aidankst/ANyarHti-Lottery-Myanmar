import pyrebase
import random
import qrcode
import os
import json
from flask import Flask, redirect, url_for, session, render_template, flash
from flask import current_app as app
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from PIL import Image, ImageDraw, ImageFont
from form_classes import LoginForm, RegistrationForm, PasswordResetForm, LotteryApplicationForm, OwnTicketNumForm
from send_email import send_email

firebaseConfig = {
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firebase.database()

app = Flask(__name__)
app.secret_key = 'anyarhtiproject'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, uid, display_name, email):
        self.id = uid
        self.displayName = display_name
        self.email = email

def get_user_details_from_firebase(user_id):
    try:
        return db.child('users').child(user_id).get().val()
    except:
        return None
    
def start_ticket_process():
    process_info = session.get('ticket_process')
    if process_info['type'] == 'own_number':
            if process_info['current'] < process_info['total']:
                return redirect(url_for('own_lottery_number'))
    elif process_info['type'] == 'random_number':
        while process_info['current'] < process_info['total']:
            ticket_num = generate_random_ticket_number(session['ticket']['lottery_sequence'])
            session['ticket']['ticket_number'] = ticket_num
            session.modified = True
            db.child('tickets').child(session['ticket']['lottery_sequence']).child(ticket_num).set(session['ticket'], session['user']['idToken'])
            session['ticket_process']['current'] += 1
            session.modified = True
            create_lottery_ticket()
        return redirect(url_for('successful'))
    else:
        return redirect(url_for('successful'))
    
def generate_random_ticket_number(lottery_sequence):
    status = True
    while status:
        ticket_num = random.randint(100000, 999999)
        status = check_duplicating(lottery_sequence, ticket_num)
        if not status:
            break
    return ticket_num

def check_duplicating(lottery_sequence, ticket_num):
    if db.child('tickets').child(lottery_sequence).child(ticket_num).get().val():
        return True
    else:
        return False
    
def create_qrcode():
    qr = qrcode.QRCode(
        version=10,
        error_correction = qrcode.constants.ERROR_CORRECT_L,
        box_size = 6,
        border = 2,
    )
    ticket_data = {
        'name': session['ticket']['name'],
        # 'email': session['ticket']['email'],
        'ticket_number': session['ticket']['ticket_number'],
        'lottery_sequence': session['ticket']['lottery_sequence'],
        'seller': session['ticket']['seller'],
    }
    ticket_data_json = json.dumps(ticket_data)
    qr.add_data(ticket_data_json)
    img = qr.make_image(fill='black', back_color='white')
    return img
    
    
def create_lottery_ticket():
    template_path = os.path.join(app.root_path, 'static', 'images', 'ticket.png')
    template_image = Image.open(template_path)
    draw = ImageDraw.Draw(template_image)
    roboto_regular = os.path.join(app.root_path, 'static', 'roboto_regular.ttf')
    roboto_bold_italic = os.path.join(app.root_path, 'static', 'roboto_bold_italic.ttf')
    myanmar_font = os.path.join(app.root_path, 'static', 'myanmar_font.ttf')
    font_large = ImageFont.truetype(roboto_regular, size=150)
    font_myanmar = ImageFont.truetype(myanmar_font, size=80)
    font_small = ImageFont.truetype(roboto_bold_italic, size=60)

    details = [
        {'text': str(session['ticket']['ticket_number']), 'position': (2500, 195), 'font': font_large},
        {'text': str(session['ticket']['lottery_sequence_mm']), 'position': (1450, 200), 'font': font_myanmar},
        {'text': f"Ticket Buyer: {session['ticket']['name']}", 'position': (2160, 450), 'font': font_small},
        {'text': f"Ticket Seller: {session['ticket']['seller']}", 'position': (2160, 550), 'font': font_small},
    ]
    
    for detail in details:
        draw.text(detail['position'], detail['text'], fill='black', font=detail['font'])
    
    qrcode_img = create_qrcode()
    qrcode_position = (2765, 1183)
    template_image.paste(qrcode_img, qrcode_position)

    static_dir = os.path.join(app.root_path, 'static')
    save_dir = os.path.join(static_dir, f'tickets/{session["ticket"]["lottery_sequence"]}')
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, f"{session['ticket']['ticket_number']}.png")
    template_image.save(save_path)
    send_email(f'အညာထီ | Ticket Number: {session['ticket']['ticket_number']}', session['ticket']['email'], save_path)

@app.route('/')
def index():
    return render_template('/index.html')

@login_manager.user_loader
def load_user(user_id):
    user_details = get_user_details_from_firebase(user_id)
    if user_details:
        return User(user_id, user_details['displayName'], user_details['email'])
    return None

def refresh_token_if_needed():
    user = session.get('user')
    if user:
        id_token = user['idToken']
        refresh_token = user['refreshToken']
        from requests import post
        api_url = ""
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
        response = post(api_url, data=payload)
        response_data = response.json()
        
        if response.status_code == 200:
            session['user'] = {
                'idToken': response_data['id_token'],
                'refreshToken': response_data['refresh_token']
            }
            session.modified = True
        else:
            logout_user()
            unsuccessful = "Session Expired"
            return render_template('/login.html', unsuccessful=unsuccessful, form=LoginForm())


@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        # try: 
        while(1):
            firebase_user = auth.sign_in_with_email_and_password(login_form.email.data, login_form.password.data)
            user_info = auth.get_account_info(firebase_user["idToken"])
            if user_info['users'][0]['emailVerified'] == False:
                verify_message = "Please verify your email to continue."
                return render_template('/login.html', verify_message=verify_message, form=login_form)
            if user_info['users'][0]['emailVerified'] == True:
                user_id = user_info['users'][0]['localId']
                user_dict = dict(db.child('users').child(user_id).get().val())
                user_name = user_dict['displayName']
                email = user_info['users'][0]['email']
                session['user'] = {
                    'idToken': firebase_user['idToken'],
                    'userName': user_name,
                    'email': email,
                    'refreshToken': firebase_user['refreshToken']
                }
                user = User(user_id, user_name, email)
                if user:
                    login_user(user, remember=True)
                    return redirect(url_for('sell_lottery'))
            else:
                unsuccessful = 'User not found.'
                return render_template('login.html', form=login_form, unsuccessful=unsuccessful)
        # except:
        #     unsuccessful = 'Please check your credentials and try again.'
        #     return render_template('/login.html', form=login_form, unsuccessful=unsuccessful)
    return render_template('/login.html', form=login_form)



@app.route('/register', methods=['GET', 'POST'])
def register():
    register_form = RegistrationForm()
    if register_form.validate_on_submit():
        if register_form.password.data == register_form.confirm_password.data:
            try:
                new_user = auth.create_user_with_email_and_password(register_form.email.data, register_form.password.data)
                user_info = auth.get_account_info(new_user["idToken"])
                db.child('users').child(user_info['users'][0]['localId']).set({'displayName': register_form.name.data, 'email': register_form.email.data}, new_user["idToken"])
                auth.send_email_verification(new_user["idToken"])
                return render_template('/verify_email.html')
            except:
                existing_user = "This email is already registered."
                return render_template('/register.html', existing_user=existing_user, form=register_form)
        else:
            unsuccessful = 'Passwords do not match.'
            return render_template('/register.html', unsuccessful=unsuccessful, form=register_form)
    return render_template('/register.html', form=register_form)

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    password_reset_form = PasswordResetForm()
    if password_reset_form.validate_on_submit():
        try:
            auth.send_password_reset_email(password_reset_form.email.data)
            return render_template('/login.html', form=LoginForm())
        except:
            unsuccessful = 'Please check your email and try again.'
            return render_template('/reset_password.html', unsuccessful=unsuccessful, formatt=password_reset_form)
    return render_template('/reset_password.html', form=password_reset_form)

@app.route('/admin')
@login_required
def admin():
    return render_template('/admin.html')

@app.route('/sell_lottery', methods=['GET', 'POST'])
@login_required
def sell_lottery():
    lottery_application_form = LotteryApplicationForm()
    lottery_application_form.seller.data = session.get('user')['userName']
    lottery_application_form.seller.render_kw = {'readonly': True}
    choices = db.child('lottery_sequence').get().val()
    lottery_application_form.lottery_sequence.choices = [(value, value) for key, value in choices.items()]

    if lottery_application_form.validate_on_submit():
            lottery_sequence = lottery_application_form.lottery_sequence.data
            for key, value in choices.items():
                if value == lottery_sequence:
        # try:
                    session['ticket'] = {
                        'name': lottery_application_form.name.data, 
                        'email': lottery_application_form.email.data,
                        'seller': lottery_application_form.seller.data,
                        'lottery_sequence': lottery_sequence,
                        'lottery_sequence_mm': key
                    }
            num_of_tickets = lottery_application_form.number_of_tickets.data
            session['ticket_process'] = {
                'total': num_of_tickets,
                'current': 0,
                'type': lottery_application_form.lottery_number_type.data,
                'tickets': []
            }
            return start_ticket_process()
           
        # except:
        #     unsuccessful = 'Error Occurs!'
        #     return render_template('/sell_lottery.html', form=lottery_application_form, unsuccessful=unsuccessful)

    return render_template('/sell_lottery.html', form=lottery_application_form)

@app.route('/own_lottery_number', methods=['GET', 'POST'])
@login_required
def own_lottery_number():
    own_ticket_num_form = OwnTicketNumForm()
    refresh_token_if_needed()
    ticket_num = session['ticket_process']['current']+1
    if own_ticket_num_form.validate_on_submit():
        ticket_num = own_ticket_num_form.lottery_number.data
        lottery_sequence = session['ticket']['lottery_sequence']
        if check_duplicating(lottery_sequence, ticket_num):
            flash('Ticket Number Duplicating! Please enter a new one', 'error')
        else:
            session['ticket']['ticket_number'] = ticket_num
            session['ticket_process']['current'] += 1
            session.modified = True
            db.child('tickets').child(lottery_sequence).child(ticket_num).set(session['ticket'], session['user']['idToken'])
            create_lottery_ticket()
            return start_ticket_process()
    return render_template('/own_lottery_number.html', ticket_num=ticket_num, form=own_ticket_num_form)

@app.route('/successful')
@login_required
def successful():
    return render_template('/successful.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)