from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from . import db
import json
from .models import Pdescription

#Maak een bleuprint voor algemene views
views = Blueprint('views', __name__)

#Route voor homepagina (dit is ook de default pagina/route)
@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        project_text = request.form.get('projectText')

        if len(project_text) <1:
            flash('Project beschrijving is te kort!', category='error')
        else:
            new_project = Pdescription(text=project_text, user_id=current_user.id)
            db.session.add(new_project)
            db.session.commit()
            flash('Project toegevoegd!', category='success')
    return render_template("home.html", user=current_user)


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
