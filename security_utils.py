from datetime import datetime, timedelta
from . import db
from .models import User, LoginAttempt, AuditLog
from flask import request
import logging

# Configureer de logger voor beveiligingstaken
logger = logging.getLogger(__name__)

# Instellingen voor inlogpogingen en blokkades
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15


def get_client_ip():
    """Haal het IP-adres van de client op uit het verzoek."""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr or 'onbekend'


def record_login_attempt(email, success=False):
    """Registreer een inlogpoging in de database."""
    try:
        attempt = LoginAttempt(
            email=email,
            success=success,
            ip_address=get_client_ip()
        )
        db.session.add(attempt)
        db.session.commit()
    except Exception as e:
        logger.error(f'Registreren inlogpoging mislukt: {str(e)}')
        db.session.rollback()


def check_account_lockout(email):
    """
    Controleer of een account is geblokkeerd door teveel foute pogingen.
    Returns: (is_locked, message)
    """
    user = User.query.filter_by(email=email).first()
    
    if not user:
        return False, None
    
    # Controleer of de blokkade nog actief is
    if user.is_locked:
        if user.locked_until and user.locked_until > datetime.utcnow():
            remaining_time = (user.locked_until - datetime.utcnow()).total_seconds() / 60
            return True, f"Account is tijdelijk geblokkeerd. Probeer het over {int(remaining_time)} minuten opnieuw."
        else:
            # Deblokkeer het account als de tijd voorbij is
            user.is_locked = False
            user.locked_until = None
            db.session.commit()
    
    return False, None


def check_failed_login_attempts(email):
    """
    Controleer recente foute inlogpogingen. Bij teveel pogingen wordt het account geblokkeerd.
    Returns: (is_locked, message)
    """
    is_locked, msg = check_account_lockout(email)
    if is_locked:
        return True, msg
    
    # Tel het aantal foute pogingen in de laatste X minuten
    recent_attempts = LoginAttempt.query.filter(
        LoginAttempt.email == email,
        LoginAttempt.success == False,
        LoginAttempt.timestamp >= datetime.utcnow() - timedelta(minutes=LOCKOUT_DURATION_MINUTES)
    ).count()
    
    # Blokkeer het account bij het overschrijden van de limiet
    if recent_attempts >= MAX_LOGIN_ATTEMPTS:
        user = User.query.filter_by(email=email).first()
        if user:
            user.is_locked = True
            user.locked_until = datetime.utcnow() + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
            db.session.commit()
            logger.warning(f'Account geblokkeerd door teveel foute inlogpogingen: {email}')
        
        return True, f"Teveel foute inlogpogingen. Account is geblokkeerd voor {LOCKOUT_DURATION_MINUTES} minuten."
    
    return False, None


def log_audit_event(user_id, action, resource_type, resource_id=None, details=None):
    """
    Registreer een audit event voor beveiliging en controle.
    
    action: 'CREATE', 'READ', 'UPDATE', 'DELETE', 'LOGIN', 'LOGOUT', etc.
    resource_type: 'PROJECT', 'USER', 'PROFILE', etc.
    """
    try:
        audit_entry = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=get_client_ip()
        )
        db.session.add(audit_entry)
        db.session.commit()
        logger.info(f'Audit: Gebruiker {user_id} voerde {action} uit op {resource_type} {resource_id}')
    except Exception as e:
        logger.error(f'Loggen audit event mislukt: {str(e)}')
        db.session.rollback()


def get_audit_log(user_id=None, limit=100):
    """Haal de audit logs op voor een specifieke gebruiker of voor iedereen."""
    query = AuditLog.query
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    return query.order_by(AuditLog.timestamp.desc()).limit(limit).all()
