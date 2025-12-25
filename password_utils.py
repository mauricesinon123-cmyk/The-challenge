import re


def validate_password_complexity(password):
    """
    Validate password complexity requirements.
    
    Requirements:
    - Minimaal 8 tekens
    - 1 hoofdletter
    - 1 kleine letter
    - 1 getal
    - 1 speciaal teken (!@#$%^&*)
    
    Returns: (is_valid, error_message)
    """
    if not password:
        return False, "Password is required."
    
    if len(password) < 8:
        return False, "Wachtwoord moet minimaal 8 tekens lang zijn."
    
    if not re.search(r'[A-Z]', password):
        return False, "Wachtwoord moet minimaal één hoofdletter bevatten."
    
    if not re.search(r'[a-z]', password):
        return False, "Wachtwoord moet minimaal één kleine letter bevatten."
    
    if not re.search(r'\d', password):
        return False, "Wachtwoord moet minimaal één cijfer bevatten."
    
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', password):
        return False, "Wachtwoord moet minimaal één speciaal teken bevatten."
    
    return True, None


def get_password_requirements():
    """Return formatted password requirements as a string."""
    return (
        "Minimaal 8 tekens, "
        "1 hoofdletter, "
        "1 kleine letter, "
        "1 getal, "
        "and 1 speciaal teken"
    )
