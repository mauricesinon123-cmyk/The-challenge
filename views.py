from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from . import db, limiter
from .models import Pdescription
from .security_utils import log_audit_event
import os
import shutil
from datetime import date
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import time
import logging

# Configureer de logger voor views
logger = logging.getLogger(__name__)

# Maak een blueprint voor de algemene pagina's
views = Blueprint('views', __name__)

# Lijst met beschikbare wijken/regio's
REGIONS = [
    'Buytenwegh', 'De Leyens', 'Dorp', 'Driemanspolder', 'Meerzicht',
    'Noordhove', 'Oosterheem', 'Palenstein', 'Rokkeveen', 'Seghwaert', 'Stadscentrum'
]

# Beperkingen voor bestanden en tekst
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
MAX_FILE_SIZE = 5 * 1024 * 1024
MAX_PROJECT_TITLE = 200
MAX_PROJECT_TEXT = 10000

# Bereken de leeftijd op basis van geboortedatum
def calculate_age(born):
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

# Controleer of een bestandstype is toegestaan
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Sla een profielfoto op in de static map
def save_profile_picture(file, user_id):
    if not file or file.filename == '':
        return None
    
    if not allowed_file(file.filename):
        return None
    
    # Controleer bestandsgrootte
    if len(file.read()) > MAX_FILE_SIZE:
        file.seek(0)
        return None
    
    file.seek(0)
    
    # Maak de map aan als deze nog niet bestaat
    profile_pictures_dir = os.path.join(os.path.dirname(__file__), 'static', 'profile_pictures')
    os.makedirs(profile_pictures_dir, exist_ok=True)
    
    # Genereer een unieke bestandsnaam
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"user_{user_id}_{int(time.time())}.{ext}"
    filepath = os.path.join(profile_pictures_dir, filename)
    file.save(filepath)
    
    return f"profile_pictures/{filename}"

# Verwijder een oude profielfoto
def delete_old_profile_picture(picture_path):
    if not picture_path:
        return
    try:
        full_path = os.path.join(os.path.dirname(__file__), 'static', picture_path)
        if os.path.exists(full_path):
            os.remove(full_path)
    except Exception:
        pass

# Zoek naar de aangesloten Microbit schijf
def find_microbit_drive():
    for drive in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        path = drive + ':\\'
        if os.path.exists(path):
            details = os.path.join(path, 'details.txt')
            if os.path.exists(details):
                with open(details, 'r') as f:
                    content = f.read().lower()
                    if 'microbit' in content:
                        return path
    return None

# Route voor de homepagina
@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    return render_template("home.html", user=current_user)

# Route voor instructies
@views.route('/instructies')
@login_required
def instructies():
    return render_template("instructies.html", user=current_user)

# Route voor accountbeheer
@views.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        dob_str = request.form.get('dateOfBirth', '')
        region = request.form.get('region', '')
        profile_picture = request.files.get('profilePicture')
        
        # Validatie van accountgegevens
        if not name or len(name) < 2:
            flash('Naam moet minimaal 2 tekens zijn.', category='error')
        elif not dob_str:
            flash('Geboortedatum is verplicht.', category='error')
        elif not region or region not in REGIONS:
            flash('Selecteer een geldige regio.', category='error')
        else:
            try:
                dob = date.fromisoformat(dob_str)
                age = calculate_age(dob)
                if age < 18:
                    flash('U moet minimaal 18 jaar oud zijn.', category='error')
                else:
                    # Profielfoto verwerken indien aanwezig
                    if profile_picture and profile_picture.filename != '':
                        if not allowed_file(profile_picture.filename):
                            flash('Profielfoto moet JPG of PNG zijn.', category='error')
                            return render_template("account.html", user=current_user, regions=REGIONS)
                        
                        file_content = profile_picture.read()
                        profile_picture.seek(0)
                        if len(file_content) > MAX_FILE_SIZE:
                            flash('Profielfoto is te groot. Maximum 5MB.', category='error')
                            return render_template("account.html", user=current_user, regions=REGIONS)
                    
                    # Gegevens opslaan in de gebruikersobject
                    current_user.first_name = name
                    current_user.date_of_birth = dob
                    current_user.region = region
                    current_user.account_setup_complete = True
                    
                    if profile_picture and profile_picture.filename != '':
                        old_picture = current_user.profile_picture_path
                        new_picture_path = save_profile_picture(profile_picture, current_user.id)
                        if new_picture_path:
                            current_user.profile_picture_path = new_picture_path
                            delete_old_profile_picture(old_picture)
                    
                    db.session.commit()
                    flash('Accountgegevens bijgewerkt!', category='success')
                    return redirect(url_for('views.home'))
            except ValueError:
                flash('Ongeldig datumformaat.', category='error')
            except Exception as e:
                db.session.rollback()
                flash('Er is een fout opgetreden bij het bijwerken van uw account.', category='error')
    
    is_first_setup = not current_user.account_setup_complete
    return render_template("account.html", user=current_user, regions=REGIONS, is_first_setup=is_first_setup)

# Route om een project te verwijderen
@views.route('/delete-project', methods=['POST'])
@login_required
def delete_project():
    project_data = request.get_json(silent=True)
    if not project_data:
        return jsonify({'success': False, 'message': 'Ongeldig verzoek'}), 400
    
    projectId = project_data.get('projectId')
    if projectId is None:
        return jsonify({'success': False, 'message': 'Project ID vereist'}), 400
    
    try:
        project_id = int(projectId)
        project = Pdescription.query.get(project_id)
        if not project:
            return jsonify({'success': False, 'message': 'Project niet gevonden'}), 444
        
        # Controleer of de gebruiker eigenaar is van het project
        if project.user_id != current_user.id:
            logger.warning(f'Ongeautoriseerde verwijderpoging door {current_user.email} op project {project_id}')
            return jsonify({'success': False, 'message': 'Niet geautoriseerd'}), 403
        
        project_title = project.title
        db.session.delete(project)
        db.session.commit()
        
        # Log de verwijdering
        log_audit_event(
            current_user.id, 'DELETE', 'PROJECT',
            project_id,
            f"Project verwijderd: {project_title}"
        )
        logger.info(f'Project verwijderd door {current_user.email}: {project_id}')
        return jsonify({'success': True})
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'Ongeldig project ID'}), 400
    except Exception as e:
        db.session.rollback()
        logger.error(f'Fout bij verwijderen project: {str(e)}')
        return jsonify({'success': False, 'message': 'Fout bij verwijderen project'}), 500

# Route om te controleren of de Microbit is aangesloten
@views.route('/check-microbit', methods=['POST'])
@login_required
def check_microbit():
    microbit_drive = find_microbit_drive()
    if microbit_drive:
        return jsonify({'connected': True})
    else:
        return jsonify({'connected': False, 'error': 'Microbit niet aangesloten'})

# Route voor hulp met Microbit en kopiëren van projecten
@views.route('/help', methods=['GET', 'POST'])
@login_required
def help_page():
    if request.method == 'POST':
        mode = request.form.get('mode')  # 'help' of 'need'
        group = request.form.get('group')
        project_id = request.form.get('project_id')
        skip = request.form.get('skipHandleiding')

        if not mode or not group:
            return jsonify({'success': False, 'error': 'Ongeldig verzoek'})
        try:
            group_num = int(group)
            if group_num < 1 or group_num > 16:
                raise ValueError
        except ValueError:
            return jsonify({'success': False, 'error': 'Ongeldig SDG nummer'})
        
        # Selecteer het juiste hex bestand
        if mode == 'help':
            filename = 'full_send.hex'
        elif mode == 'need':
            filename = 'full_receive.hex'
        else:
            return jsonify({'success': False, 'error': 'Ongeldige modus'})
        
        hex_path = os.path.join(os.path.dirname(__file__), 'hex_files', filename)
        if not os.path.exists(hex_path):
            return jsonify({'success': False, 'error': 'Hex bestand niet gevonden'})
        
        # Zoek Microbit en kopieer bestand
        microbit_drive = find_microbit_drive()
        if not microbit_drive:
            return jsonify({'success': False, 'error': 'Microbit niet aangesloten'})
        
        dest = os.path.join(microbit_drive, filename)
        try:
            shutil.copy2(hex_path, dest)
        except PermissionError:
            return jsonify({'success': False, 'error': 'Microbit is bezig. Probeer het over een moment opnieuw.'})
        except Exception as e:
            logger.error(f'Fout bij kopiëren naar Microbit: {str(e)}')
            return jsonify({'success': False, 'error': 'Bestand kopiëren naar Microbit mislukt.'})
        
        # Als de gebruiker iemand helpt, kopieer dan het project naar hun lijst
        try:
            if mode == 'help' and project_id:
                proj_id = int(project_id)
                project = Pdescription.query.get(proj_id)
                if project and project.user_id != current_user.id:
                    # Maak een kopie van het project voor de helper
                    new_project = Pdescription(
                        title=project.title,
                        text=project.text,
                        group=project.group,
                        user_id=current_user.id
                    )
                    db.session.add(new_project)
                    db.session.commit()
        except Exception as e:
            logger.warning(f'Project kopiëren mislukt: {str(e)}')
        
        return jsonify({'success': True, 'message': 'Overgezet naar microbit!', 'skip': skip == "true"})
    
    return render_template("help.html", user=current_user)

# Route voor het overzicht van projecten
@views.route('/projects')
@login_required
def projects():
    return render_template("projects.html", user=current_user)

# Route voor projecten in de wijk
@views.route('/wijk-projecten')
@login_required
def wijk_projecten():
    all_projects = Pdescription.query.all()
    return render_template("wijk_projecten.html", user=current_user, projects=all_projects)

# Route voor eigen projecten beheren
@views.route('/mijn-projecten', methods=['GET', 'POST'])
@login_required
def mijn_projecten():
    if request.method == 'POST':
        project_title = request.form.get('projectTitle', '').strip()
        project_text = request.form.get('projectText', '').strip()
        project_group = request.form.get('projectGroup')

        # Validatie van projectgegevens
        if not project_title:
            flash('Projecttitel is verplicht!', category='error')
        elif len(project_title) > MAX_PROJECT_TITLE:
            flash(f'Titel mag maximaal {MAX_PROJECT_TITLE} tekens zijn.', category='error')
        elif not project_text:
            flash('Beschrijving is verplicht!', category='error')
        elif not project_group:
            flash('SDG is verplicht!', category='error')
        else:
            try:
                group_num = int(project_group)
                # Maak nieuw project aan
                new_project = Pdescription(title=project_title, text=project_text, group=group_num, user_id=current_user.id)
                db.session.add(new_project)
                db.session.commit()
                
                log_audit_event(current_user.id, 'CREATE', 'PROJECT', new_project.id, f"Project aangemaakt: {project_title}")
                flash('Project succesvol toegevoegd!', category='success')
                return redirect(url_for('views.mijn_projecten'))
            except Exception as e:
                db.session.rollback()
                logger.error(f'Project creatie fout: {str(e)}')
                flash('Er is een fout opgetreden.', category='error')
                
    return render_template("mijn_projecten.html", user=current_user)

# Route om een bestaand project aan te passen
@views.route('/edit-project', methods=['POST'])
@login_required
def edit_project():
    project_data = request.get_json(silent=True)
    if not project_data:
        return jsonify({'success': False, 'message': 'Ongeldig verzoek'}), 400
    
    project_id = project_data.get('projectId')
    project_title = project_data.get('title', '').strip()
    project_text = project_data.get('text', '').strip()
    project_group = project_data.get('group')
    
    # Validatie van de aangepaste gegevens
    if not project_id or not project_title or not project_text or not project_group:
        return jsonify({'success': False, 'message': 'Alle velden zijn verplicht'}), 400
    
    try:
        # Zoek het bestaande project op
        project = Pdescription.query.get(int(project_id))
        if not project or project.user_id != current_user.id:
            return jsonify({'success': False, 'message': 'Project niet gevonden of niet geautoriseerd'}), 404
        
        # Update de velden van het bestaande project object
        old_title = project.title
        project.title = project_title
        project.text = project_text
        project.group = int(project_group)
        project.date = db.func.now() # Werk de datum bij naar nu
        
        # Sla de wijzigingen op (SQL UPDATE wordt uitgevoerd op bestaand ID)
        db.session.commit()
        
        log_audit_event(current_user.id, 'UPDATE', 'PROJECT', project_id, f"Project gewijzigd: {old_title} -> {project_title}")
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        logger.error(f'Project update fout: {str(e)}')
        return jsonify({'success': False, 'message': 'Fout bij bijwerken project'}), 500
