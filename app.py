import os
import io
import csv
import base64
import secrets
import string
from datetime import datetime, timedelta
from functools import wraps

import qrcode
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, Response
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


class ApiKey(db.Model):
    __tablename__ = 'api_keys'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used_at = db.Column(db.DateTime, nullable=True)
    request_count = db.Column(db.Integer, default=0)


def generate_code(length=12, prefix=''):
    chars = string.ascii_uppercase + string.digits
    chars = chars.replace('O', '').replace('0', '').replace('I', '').replace('1', '').replace('L', '')
    code = ''.join(secrets.choice(chars) for _ in range(length))
    if prefix:
        code = f"{prefix}-{code}"
    formatted = '-'.join([code[i:i+4] for i in range(0, len(code), 4)])
    return formatted


def generate_api_key_string():
    return 'cvk_' + secrets.token_hex(24)


def generate_qr_code_base64(data):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#00ff88", back_color="#0a0f0a")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode('utf-8')


def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        if not api_key:
            return jsonify({'error': 'API key required'}), 401
        
        key = ApiKey.query.filter_by(key=api_key, is_active=True).first()
        if not key:
            return jsonify({'error': 'Invalid API key'}), 401
        
        key.last_used_at = datetime.utcnow()
        key.request_count += 1
        db.session.commit()
        
        return f(*args, **kwargs)
    return decorated


def get_daily_stats(days=7):
    daily_labels = []
    daily_generated = []
    daily_used = []
    
    for i in range(days - 1, -1, -1):
        day = datetime.utcnow().date() - timedelta(days=i)
        day_start = datetime.combine(day, datetime.min.time())
        day_end = datetime.combine(day, datetime.max.time())
        
        generated = ActivationCode.query.filter(
            ActivationCode.created_at >= day_start,
            ActivationCode.created_at <= day_end
        ).count()
        
        used = ActivationCode.query.filter(
            ActivationCode.used_at >= day_start,
            ActivationCode.used_at <= day_end
        ).count()
        
        daily_labels.append(day.strftime('%b %d'))
        daily_generated.append(generated)
        daily_used.append(used)
    
    return daily_labels, daily_generated, daily_used


def get_stats():
    total = ActivationCode.query.count()
    used = ActivationCode.query.filter_by(is_used=True).count()
    active = ActivationCode.query.filter_by(is_active=True, is_used=False).count()
    inactive = ActivationCode.query.filter_by(is_active=False).count()
    
    today = datetime.utcnow().date()
    today_start = datetime.combine(today, datetime.min.time())
    generated_today = ActivationCode.query.filter(ActivationCode.created_at >= today_start).count()
    used_today = ActivationCode.query.filter(ActivationCode.used_at >= today_start).count()
    
    return {
        'total': total,
        'used': used,
        'active': active,
        'inactive': inactive,
        'generated_today': generated_today,
        'used_today': used_today,
        'usage_rate': round((used / total * 100) if total > 0 else 0, 1)
    }


with app.app_context():
    db.create_all()


@app.route('/')
def index():
    stats = get_stats()
    recent_codes = ActivationCode.query.order_by(ActivationCode.created_at.desc()).limit(5).all()
    recent_activations = ActivationCode.query.filter(
        ActivationCode.used_at.isnot(None)
    ).order_by(ActivationCode.used_at.desc()).limit(5).all()
    
    return render_template('index.html', stats=stats, recent_codes=recent_codes, recent_activations=recent_activations)


def safe_int(value, default=1, min_val=1, max_val=None):
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
    qr_codes = {}
    if request.method == 'POST':
        count = safe_int(request.form.get('count'), default=1, min_val=1, max_val=100)
        prefix = request.form.get('prefix', '').upper().strip()
        name = request.form.get('name', '').strip()
        uses_allowed = safe_int(request.form.get('uses_allowed'), default=1, min_val=1, max_val=1000)
        expires_days = request.form.get('expires_days', '')
        generate_qr = request.form.get('generate_qr') == 'on'
        
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
                    if generate_qr:
                        qr_codes[code] = generate_qr_code_base64(code)
                    break
                attempts += 1
        
        db.session.commit()
        flash(f'Successfully generated {len(generated_codes)} activation code(s)!', 'success')
        return render_template('generate.html', generated_codes=generated_codes, qr_codes=qr_codes)
    
    return render_template('generate.html', generated_codes=None, qr_codes=qr_codes)


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
    search = request.args.get('search', '').strip()
    
    query = ActivationCode.query.order_by(ActivationCode.created_at.desc())
    
    if search:
        query = query.filter(
            db.or_(
                ActivationCode.code.ilike(f'%{search}%'),
                ActivationCode.name.ilike(f'%{search}%'),
                ActivationCode.used_by.ilike(f'%{search}%')
            )
        )
    
    if filter_status == 'valid':
        query = query.filter_by(is_active=True, is_used=False)
    elif filter_status == 'used':
        query = query.filter_by(is_used=True)
    elif filter_status == 'inactive':
        query = query.filter_by(is_active=False)
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    all_codes = pagination.items
    
    return render_template('codes.html', codes=all_codes, pagination=pagination, filter_status=filter_status, search=search, now=datetime.utcnow())


@app.route('/statistics')
def statistics():
    stats = get_stats()
    daily_labels, daily_generated, daily_used = get_daily_stats(7)
    
    recent_codes = ActivationCode.query.order_by(ActivationCode.created_at.desc()).limit(5).all()
    recent_activations = ActivationCode.query.filter(
        ActivationCode.used_at.isnot(None)
    ).order_by(ActivationCode.used_at.desc()).limit(5).all()
    
    return render_template('statistics.html', 
                           stats=stats, 
                           recent_codes=recent_codes, 
                           recent_activations=recent_activations,
                           daily_labels=daily_labels,
                           daily_generated=daily_generated,
                           daily_used=daily_used)


@app.route('/api-docs')
def api_docs():
    api_key = ApiKey.query.filter_by(is_active=True).first()
    return render_template('api_docs.html', api_key=api_key)


@app.route('/generate-api-key', methods=['POST'])
def generate_api_key():
    name = request.form.get('name', 'Default API Key').strip()
    
    new_key = ApiKey(
        key=generate_api_key_string(),
        name=name
    )
    db.session.add(new_key)
    db.session.commit()
    
    flash(f'API key generated successfully!', 'success')
    return redirect(url_for('api_docs'))


@app.route('/regenerate-api-key', methods=['POST'])
def regenerate_api_key():
    old_key = ApiKey.query.filter_by(is_active=True).first()
    if old_key:
        old_key.is_active = False
        db.session.commit()
    
    new_key = ApiKey(
        key=generate_api_key_string(),
        name='Regenerated API Key'
    )
    db.session.add(new_key)
    db.session.commit()
    
    flash('API key regenerated successfully!', 'success')
    return redirect(url_for('api_docs'))


@app.route('/export-codes')
def export_codes():
    filter_status = request.args.get('status', 'all')
    
    query = ActivationCode.query.order_by(ActivationCode.created_at.desc())
    
    if filter_status == 'valid':
        query = query.filter_by(is_active=True, is_used=False)
    elif filter_status == 'used':
        query = query.filter_by(is_used=True)
    elif filter_status == 'inactive':
        query = query.filter_by(is_active=False)
    
    all_codes = query.all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Code', 'Name', 'Status', 'Uses', 'Max Uses', 'Created', 'Expires', 'Used By', 'Used At'])
    
    for code in all_codes:
        valid, status_msg = code.is_valid()
        status = 'Valid' if valid else ('Used' if code.is_used else 'Inactive')
        writer.writerow([
            code.code,
            code.name or '',
            status,
            code.uses_count,
            code.uses_allowed,
            code.created_at.strftime('%Y-%m-%d %H:%M'),
            code.expires_at.strftime('%Y-%m-%d') if code.expires_at else 'Never',
            code.used_by or '',
            code.used_at.strftime('%Y-%m-%d %H:%M') if code.used_at else ''
        ])
    
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=activation_codes_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.csv'}
    )


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


@app.route('/api/qr/<code_string>')
def get_qr_code(code_string):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(code_string)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#00ff88", back_color="#0a0f0a")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return Response(buffer.getvalue(), mimetype='image/png')


@app.route('/api/stats')
def api_stats():
    stats = get_stats()
    return jsonify(stats)


@app.route('/api/code/<code_string>/check')
def check_code(code_string):
    activation = ActivationCode.query.filter_by(code=code_string.upper()).first()
    if not activation:
        return jsonify({'found': False, 'message': 'Code not found'}), 404
    
    is_valid, message = activation.is_valid()
    return jsonify({
        'found': True,
        'valid': is_valid,
        'message': message,
        'uses_remaining': max(0, activation.uses_allowed - activation.uses_count),
        'expires_at': activation.expires_at.isoformat() if activation.expires_at else None
    })


@app.route('/api/validate', methods=['POST'])
def api_validate():
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({'error': 'Invalid JSON payload'}), 400
    
    code = str(data.get('code', '')).upper().strip()
    user_name = str(data.get('user_name', '')).strip()
    
    if not code:
        return jsonify({'error': 'Code is required'}), 400
    
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


@app.route('/api/generate', methods=['POST'])
@require_api_key
def api_generate():
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        data = {}
    
    count = safe_int(data.get('count'), default=1, min_val=1, max_val=100)
    prefix = str(data.get('prefix', '')).upper().strip()
    name = str(data.get('name', '')).strip()
    uses_allowed = safe_int(data.get('uses_allowed'), default=1, min_val=1, max_val=1000)
    expires_days = safe_int(data.get('expires_days'), default=0, min_val=0, max_val=365)
    
    expires_at = None
    if expires_days > 0:
        expires_at = datetime.utcnow() + timedelta(days=expires_days)
    
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
    return jsonify({
        'success': True,
        'count': len(generated_codes),
        'codes': generated_codes
    })


@app.route('/api/codes/search')
def api_search_codes():
    search = request.args.get('q', '').strip()
    limit = safe_int(request.args.get('limit'), default=20, min_val=1, max_val=100)
    
    if not search:
        return jsonify({'codes': []})
    
    codes = ActivationCode.query.filter(
        db.or_(
            ActivationCode.code.ilike(f'%{search}%'),
            ActivationCode.name.ilike(f'%{search}%'),
            ActivationCode.used_by.ilike(f'%{search}%')
        )
    ).order_by(ActivationCode.created_at.desc()).limit(limit).all()
    
    return jsonify({'codes': [c.to_dict() for c in codes]})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
