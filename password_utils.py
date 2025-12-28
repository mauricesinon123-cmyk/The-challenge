import re

# Functie om de complexiteit van het wachtwoord te valideren
def validate_password_complexity(password):
    """
    Controleer of het wachtwoord voldoet aan de beveiligingseisen.
    
    Eisen:
    - Minimaal 8 tekens
    - Minimaal 1 hoofdletter
    - Minimaal 1 kleine letter
    - Minimaal 1 cijfer
    - Minimaal 1 speciaal teken (!@#$%^&*)
    
    Returns: (is_valid, error_message)
    """
    if not password:
        return False, "Wachtwoord is verplicht."
    
    # Controleer de lengte
    if len(password) < 8:
        return False, "Wachtwoord moet minimaal 8 tekens lang zijn."
    
    # Controleer op hoofdletters
    if not re.search(r'[A-Z]', password):
        return False, "Wachtwoord moet minimaal één hoofdletter bevatten."
    
    # Controleer op kleine letters
    if not re.search(r'[a-z]', password):
        return False, "Wachtwoord moet minimaal één kleine letter bevatten."
    
    # Controleer op cijfers
    if not re.search(r'\d', password):
        return False, "Wachtwoord moet minimaal één cijfer bevatten."
    
    # Controleer op speciale tekens
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', password):
        return False, "Wachtwoord moet minimaal één speciaal teken bevatten."
    
    return True, None


# Functie om de wachtwoordeisen in tekstvorm terug te geven
def get_password_requirements():
    """Geeft een geformatteerde string terug met de wachtwoordeisen."""
    return (
        "Minimaal 8 tekens, "
        "1 hoofdletter, "
        "1 kleine letter, "
        "1 cijfer, "
        "en 1 speciaal teken"
    )
