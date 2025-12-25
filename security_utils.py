from datetime import datetime, timedelta
from . import db
from .models import User, LoginAttempt, AuditLog
from flask import request
import logging

logger = logging.getLogger(__name__)

MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15


def get_client_ip():
    """Get the client IP address from the request."""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr or 'unknown'


def record_login_attempt(email, success=False):
    """Record a login attempt in the database."""
    try:
        attempt = LoginAttempt(
            email=email,
            success=success,
            ip_address=get_client_ip()
        )
        db.session.add(attempt)
        db.session.commit()
    except Exception as e:
        logger.error(f'Failed to record login attempt: {str(e)}')
        db.session.rollback()


def check_account_lockout(email):
    """
    Check if an account is locked due to too many failed attempts.
    Returns: (is_locked, message)
    """
    user = User.query.filter_by(email=email).first()
    
    if not user:
        return False, None
    
    if user.is_locked:
        if user.locked_until and user.locked_until > datetime.utcnow():
            remaining_time = (user.locked_until - datetime.utcnow()).total_seconds() / 60
            return True, f"Account is locked. Try again in {int(remaining_time)} minutes."
        else:
            user.is_locked = False
            user.locked_until = None
            db.session.commit()
    
    return False, None


def check_failed_login_attempts(email):
    """
    Check recent failed login attempts. If too many, lock the account.
    Returns: (is_locked, message)
    """
    is_locked, msg = check_account_lockout(email)
    if is_locked:
        return True, msg
    
    recent_attempts = LoginAttempt.query.filter(
        LoginAttempt.email == email,
        LoginAttempt.success == False,
        LoginAttempt.timestamp >= datetime.utcnow() - timedelta(minutes=LOCKOUT_DURATION_MINUTES)
    ).count()
    
    if recent_attempts >= MAX_LOGIN_ATTEMPTS:
        user = User.query.filter_by(email=email).first()
        if user:
            user.is_locked = True
            user.locked_until = datetime.utcnow() + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
            db.session.commit()
            logger.warning(f'Account locked due to too many failed login attempts: {email}')
        
        return True, f"Too many failed login attempts. Account locked for {LOCKOUT_DURATION_MINUTES} minutes."
    
    return False, None


def log_audit_event(user_id, action, resource_type, resource_id=None, details=None):
    """
    Log an audit event for security and compliance.
    
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
        logger.info(f'Audit: User {user_id} {action} {resource_type} {resource_id}')
    except Exception as e:
        logger.error(f'Failed to log audit event: {str(e)}')
        db.session.rollback()


def get_audit_log(user_id=None, limit=100):
    """Retrieve audit logs for a user or all users."""
    query = AuditLog.query
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    return query.order_by(AuditLog.timestamp.desc()).limit(limit).all()
