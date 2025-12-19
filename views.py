from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from . import db
import json
from .models import Pdescription
import os
import shutil
from datetime import date
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import time

#Maak een bleuprint voor algemene views
views = Blueprint('views', __name__)

REGIONS = [
    'Buytenwegh', 'De Leyens', 'Dorp', 'Driemanspolder', 'Meerzicht',
    'Noordhove', 'Oosterheem', 'Palenstein', 'Rokkeveen', 'Seghwaert', 'Stadscentrum'
]

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
MAX_FILE_SIZE = 5 * 1024 * 1024

def calculate_age(born):
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_profile_picture(file, user_id):
    if not file or file.filename == '':
        return None
    
    if not allowed_file(file.filename):
        return None
    
    if len(file.read()) > MAX_FILE_SIZE:
        file.seek(0)
        return None
    
    file.seek(0)
    
    profile_pictures_dir = os.path.join(os.path.dirname(__file__), 'static', 'profile_pictures')
    os.makedirs(profile_pictures_dir, exist_ok=True)
    
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"user_{user_id}_{int(time.time())}.{ext}"
    filepath = os.path.join(profile_pictures_dir, filename)
    file.save(filepath)
    
    return f"profile_pictures/{filename}"

def delete_old_profile_picture(picture_path):
    if not picture_path:
        return
    try:
        full_path = os.path.join(os.path.dirname(__file__), 'static', picture_path)
        if os.path.exists(full_path):
            os.remove(full_path)
    except Exception:
        pass

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

#Route voor homepagina (dit is ook de default pagina/route)
@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    return render_template("home.html", user=current_user)


@views.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        dob_str = request.form.get('dateOfBirth', '')
        region = request.form.get('region', '')
        profile_picture = request.files.get('profilePicture')
        
        if not name or len(name) < 2:
            flash('Name must be at least 2 characters.', category='error')
        elif not dob_str:
            flash('Date of birth is required.', category='error')
        elif not region or region not in REGIONS:
            flash('Please select a valid region.', category='error')
        else:
            try:
                dob = date.fromisoformat(dob_str)
                age = calculate_age(dob)
                if age < 18:
                    flash('You must be at least 18 years old.', category='error')
                else:
                    current_user.first_name = name
                    current_user.date_of_birth = dob
                    current_user.region = region
                    current_user.account_setup_complete = True
                    
                    if profile_picture and profile_picture.filename != '':
                        if not allowed_file(profile_picture.filename):
                            flash('Profile picture must be JPG or PNG.', category='error')
                            return render_template("account.html", user=current_user, regions=REGIONS)
                        
                        file_content = profile_picture.read()
                        profile_picture.seek(0)
                        if len(file_content) > MAX_FILE_SIZE:
                            flash('Profile picture is too large. Maximum 5MB.', category='error')
                            return render_template("account.html", user=current_user, regions=REGIONS)
                        
                        old_picture = current_user.profile_picture_path
                        new_picture_path = save_profile_picture(profile_picture, current_user.id)
                        if new_picture_path:
                            current_user.profile_picture_path = new_picture_path
                            delete_old_profile_picture(old_picture)
                    
                    db.session.commit()
                    flash('Account information updated!', category='success')
                    return redirect(url_for('views.home'))
            except ValueError:
                flash('Invalid date format.', category='error')
    
    is_first_setup = not current_user.account_setup_complete
    return render_template("account.html", user=current_user, regions=REGIONS, is_first_setup=is_first_setup)


@views.route('/delete-project', methods=['POST'])
@login_required
def delete_project():
    project_data = request.get_json(silent=True)
    if not project_data:
        return jsonify({}), 400
    projectId = project_data.get('projectId')
    if projectId is None:
        return jsonify({}), 400
    project = Pdescription.query.get(projectId)
    if project:
        if project.user_id == current_user.id:
            db.session.delete(project)
            db.session.commit()

    return jsonify({})

@views.route('/help', methods=['GET', 'POST'])
@login_required
def help_page():
    if request.method == 'POST':
        mode = request.form.get('mode')  # 'help' or 'need'
        group = request.form.get('group')
        project_id = request.form.get('project_id')
        if not mode or not group:
            return jsonify({'success': False, 'error': 'Invalid request'})
        try:
            group_num = int(group)
            if group_num < 1 or group_num > 16:
                raise ValueError
        except ValueError:
            return jsonify({'success': False, 'error': 'Invalid group'})
        
        # Determine file
        if mode == 'help':
            filename = f'send_{group_num}.hex'
        elif mode == 'need':
            filename = f'receive_{group_num}.hex'
        else:
            return jsonify({'success': False, 'error': 'Invalid mode'})
        
        hex_path = os.path.join(os.path.dirname(__file__), 'hex_files', filename)
        if not os.path.exists(hex_path):
            return jsonify({'success': False, 'error': 'Hex file not found'})
        
        # Find microbit drive
        microbit_drive = find_microbit_drive()
        if not microbit_drive:
            return jsonify({'success': False, 'error': 'Microbit not connected'})
        
        # Copy file
        dest = os.path.join(microbit_drive, filename)
        try:
            shutil.copy2(hex_path, dest)
            # If helping and project_id provided, add to my projects
            if mode == 'help' and project_id:
                try:
                    proj_id = int(project_id)
                    project = Pdescription.query.get(proj_id)
                    if project and project.user_id != current_user.id:
                        # Copy the project
                        new_project = Pdescription(
                            title=project.title,
                            text=project.text,
                            group=project.group,
                            user_id=current_user.id
                        )
                        db.session.add(new_project)
                        db.session.commit()
                except ValueError:
                    pass  # Ignore invalid project_id
            return jsonify({'success': True, 'message': 'Hex file sent to microbit!'})
        except PermissionError:
            return jsonify({'success': False, 'error': 'Microbit drive is busy. Please wait a moment and try again, or reconnect the microbit.'})
    
    return render_template("help.html", user=current_user)

@views.route('/projects')
@login_required
def projects():
    return render_template("projects.html", user=current_user)

@views.route('/wijk-projecten')
@login_required
def wijk_projecten():
    all_projects = Pdescription.query.all()
    return render_template("wijk_projecten.html", user=current_user, projects=all_projects)

@views.route('/mijn-projecten', methods=['GET', 'POST'])
@login_required
def mijn_projecten():
    if request.method == 'POST':
        project_title = request.form.get('projectTitle')
        project_text = request.form.get('projectText')
        project_group = request.form.get('projectGroup')

        if not project_title or len(project_title.strip()) == 0:
            flash('Project title is required!', category='error')
        elif not project_text or len(project_text.strip()) == 0:
            flash('Project description is required!', category='error')
        elif not project_group:
            flash('Project group is required!', category='error')
        else:
            try:
                group_num = int(project_group)
                if group_num < 1 or group_num > 16:
                    raise ValueError
            except ValueError:
                flash('Invalid group number!', category='error')
            else:
                new_project = Pdescription(title=project_title, text=project_text, group=group_num, user_id=current_user.id)
                db.session.add(new_project)
                db.session.commit()
                flash('Project toegevoegd!', category='success')
    return render_template("mijn_projecten.html", user=current_user)

@views.route('/edit-project', methods=['POST'])
@login_required
def edit_project():
    project_data = request.get_json(silent=True)
    if not project_data:
        return jsonify({'success': False}), 400
    
    project_id = project_data.get('projectId')
    project_title = project_data.get('title', '').strip()
    project_text = project_data.get('text', '').strip()
    project_group = project_data.get('group')
    
    if not project_id or not project_title or not project_text or not project_group:
        return jsonify({'success': False, 'message': 'All fields are required'}), 400
    
    try:
        project = Pdescription.query.get(int(project_id))
        if not project or project.user_id != current_user.id:
            return jsonify({'success': False, 'message': 'Project not found'}), 404
        
        group_num = int(project_group)
        if group_num < 1 or group_num > 16:
            return jsonify({'success': False, 'message': 'Invalid group number'}), 400
        
        project.title = project_title
        project.text = project_text
        project.group = group_num
        project.date = db.func.now()
        db.session.commit()
        
        return jsonify({'success': True})
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'Invalid data'}), 400

