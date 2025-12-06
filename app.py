import os
import secrets
import string
from datetime import datetime, timedelta
from functools import wraps

from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class ActivationCode(db.Model):
    __tablename__ = 'activation_codes'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=True)
    is_used = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    uses_allowed = db.Column(db.Integer, default=1)
    uses_count = db.Column(db.Integer, default=0)
    expires_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    used_at = db.Column(db.DateTime, nullable=True)
    used_by = db.Column(db.String(100), nullable=True)
    
    def is_valid(self):
        if not self.is_active:
            return False, "Code is deactivated"
        if self.uses_count >= self.uses_allowed:
            return False, "Code has reached maximum uses"
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False, "Code has expired"
        return True, "Code is valid"
    
    def to_dict(self):
        valid, status = self.is_valid()
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'is_used': self.is_used,
            'is_active': self.is_active,
            'uses_allowed': self.uses_allowed,
            'uses_count': self.uses_count,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_at': self.created_at.isoformat(),
            'used_at': self.used_at.isoformat() if self.used_at else None,
            'used_by': self.used_by,
            'status': 'valid' if valid else 'invalid',
            'status_message': status
        }


def generate_code(length=12, prefix=''):
    chars = string.ascii_uppercase + string.digits
    chars = chars.replace('O', '').replace('0', '').replace('I', '').replace('1', '').replace('L', '')
    code = ''.join(secrets.choice(chars) for _ in range(length))
    if prefix:
        code = f"{prefix}-{code}"
    formatted = '-'.join([code[i:i+4] for i in range(0, len(code), 4)])
    return formatted


with app.app_context():
    db.create_all()


@app.route('/')
def index():
    return render_template('index.html')


def safe_int(value, default=1, min_val=1, max_val=None):
    """Safely parse an integer from form input with defaults and bounds."""
    try:
        result = int(value) if value else default
    except (ValueError, TypeError):
        result = default
    result = max(result, min_val)
    if max_val is not None:
        result = min(result, max_val)
    return result


@app.route('/generate', methods=['GET', 'POST'])
def generate():
    if request.method == 'POST':
        count = safe_int(request.form.get('count'), default=1, min_val=1, max_val=100)
        prefix = request.form.get('prefix', '').upper().strip()
        name = request.form.get('name', '').strip()
        uses_allowed = safe_int(request.form.get('uses_allowed'), default=1, min_val=1, max_val=1000)
        expires_days = request.form.get('expires_days', '')
        
        expires_at = None
        if expires_days and expires_days.isdigit():
            expires_at = datetime.utcnow() + timedelta(days=int(expires_days))
        
        generated_codes = []
        for _ in range(count):
            attempts = 0
            while attempts < 10:
                code = generate_code(prefix=prefix)
                existing = ActivationCode.query.filter_by(code=code).first()
                if not existing:
                    new_code = ActivationCode(
                        code=code,
                        name=name if name else None,
                        uses_allowed=uses_allowed,
                        expires_at=expires_at
                    )
                    db.session.add(new_code)
                    generated_codes.append(code)
                    break
                attempts += 1
        
        db.session.commit()
        flash(f'Successfully generated {len(generated_codes)} activation code(s)!', 'success')
        return render_template('generate.html', generated_codes=generated_codes)
    
    return render_template('generate.html', generated_codes=None)


@app.route('/validate', methods=['GET', 'POST'])
def validate():
    result = None
    if request.method == 'POST':
        code = request.form.get('code', '').upper().strip()
        user_name = request.form.get('user_name', '').strip()
        
        activation = ActivationCode.query.filter_by(code=code).first()
        
        if not activation:
            result = {'valid': False, 'message': 'Code not found', 'code': code}
        else:
            is_valid, message = activation.is_valid()
            if is_valid:
                activation.uses_count += 1
                if activation.uses_count >= activation.uses_allowed:
                    activation.is_used = True
                activation.used_at = datetime.utcnow()
                if user_name:
                    activation.used_by = user_name
                db.session.commit()
                result = {'valid': True, 'message': 'Code activated successfully!', 'code': code, 'data': activation.to_dict()}
            else:
                result = {'valid': False, 'message': message, 'code': code}
    
    return render_template('validate.html', result=result)


@app.route('/codes')
def codes():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    filter_status = request.args.get('status', 'all')
    
    query = ActivationCode.query.order_by(ActivationCode.created_at.desc())
    
    if filter_status == 'valid':
        query = query.filter_by(is_active=True, is_used=False)
    elif filter_status == 'used':
        query = query.filter_by(is_used=True)
    elif filter_status == 'inactive':
        query = query.filter_by(is_active=False)
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    codes = pagination.items
    
    return render_template('codes.html', codes=codes, pagination=pagination, filter_status=filter_status, now=datetime.utcnow())


@app.route('/statistics')
def statistics():
    total = ActivationCode.query.count()
    used = ActivationCode.query.filter_by(is_used=True).count()
    active = ActivationCode.query.filter_by(is_active=True, is_used=False).count()
    inactive = ActivationCode.query.filter_by(is_active=False).count()
    
    today = datetime.utcnow().date()
    today_start = datetime.combine(today, datetime.min.time())
    generated_today = ActivationCode.query.filter(ActivationCode.created_at >= today_start).count()
    used_today = ActivationCode.query.filter(ActivationCode.used_at >= today_start).count()
    
    recent_codes = ActivationCode.query.order_by(ActivationCode.created_at.desc()).limit(5).all()
    recent_activations = ActivationCode.query.filter(ActivationCode.used_at.isnot(None)).order_by(ActivationCode.used_at.desc()).limit(5).all()
    
    stats = {
        'total': total,
        'used': used,
        'active': active,
        'inactive': inactive,
        'generated_today': generated_today,
        'used_today': used_today,
        'usage_rate': round((used / total * 100) if total > 0 else 0, 1)
    }
    
    return render_template('statistics.html', stats=stats, recent_codes=recent_codes, recent_activations=recent_activations)


@app.route('/api/code/<int:code_id>/toggle', methods=['POST'])
def toggle_code(code_id):
    code = ActivationCode.query.get_or_404(code_id)
    code.is_active = not code.is_active
    db.session.commit()
    return jsonify({'success': True, 'is_active': code.is_active})


@app.route('/api/code/<int:code_id>/delete', methods=['POST'])
def delete_code(code_id):
    code = ActivationCode.query.get_or_404(code_id)
    db.session.delete(code)
    db.session.commit()
    return jsonify({'success': True})


@app.route('/api/validate', methods=['POST'])
def api_validate():
    data = request.get_json()
    code = data.get('code', '').upper().strip()
    user_name = data.get('user_name', '').strip()
    
    activation = ActivationCode.query.filter_by(code=code).first()
    
    if not activation:
        return jsonify({'valid': False, 'message': 'Code not found'}), 404
    
    is_valid, message = activation.is_valid()
    if is_valid:
        activation.uses_count += 1
        if activation.uses_count >= activation.uses_allowed:
            activation.is_used = True
        activation.used_at = datetime.utcnow()
        if user_name:
            activation.used_by = user_name
        db.session.commit()
        return jsonify({'valid': True, 'message': 'Code activated successfully!', 'data': activation.to_dict()})
    
    return jsonify({'valid': False, 'message': message}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
