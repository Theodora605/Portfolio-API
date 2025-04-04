from flask import Flask, jsonify, request, abort, session
from flask_restful import Api, Resource
from flask_cors import CORS, cross_origin
from flask_bcrypt import Bcrypt
from flask_session import Session

from config import ApplicationConfig
from models import db, Moderator, Project, Technology

from sqlalchemy.engine import Engine
from sqlalchemy import event

app = Flask(__name__)
app.config.from_object(ApplicationConfig)
CORS(app, supports_credentials=True)

api = Api(app)
bcrypt = Bcrypt(app)
server_session = Session(app)

db.init_app(app)

with app.app_context():
    db.create_all()

class ModeratorsResource(Resource):
    def get(self):

        if "user_id" not in session:
            abort(401)

        moderators = Moderator.query.all()
        res = []
        for mod in moderators:
            res.append({
                'id': mod.id,
                'username': mod.username,
                'password': mod.password
            })

        return jsonify(res)
    
    def post(self):

        if "user_id" not in session:
            abort(401)

        data = request.get_json()

        username = data['username']
        password = data['password']

        user_exists = Moderator.query.filter_by(username=username).first() is not None

        if user_exists:
            abort(409)

        mod = Moderator(username=username, password=bcrypt.generate_password_hash(password).decode('utf-8'))
        db.session.add(mod)
        db.session.commit()

        return jsonify({
            'username': username,
            'password': password,
            'pass_hash': bcrypt.generate_password_hash(password).decode('utf-8')
        })
            
class ModeratorResource(Resource):
    def delete(self, id):

        if "user_id" not in session:
            abort(401)

        mod = Moderator.query.get_or_404(id)

        if mod is None:
            abort(404)

        db.session.delete(mod)
        db.session.commit()

        return jsonify({
            "message": f"Moderator {mod.username} was deleted."
        })

class ProjectsResource(Resource):
    def get(self):
        projects = Project.query.all()
        res = []
        for project in projects:
            technologies = []
            for tech in project.technologies:
                technologies.append({
                    "id": tech.id,
                    "img_uri": tech.img_uri,
                    "description": tech.description
                })

            res.append({
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "img_uri": project.img_uri,
                "server_endpoint": project.server_endpoint,
                "github_url": project.github_url,
                "demo_url": project.demo_url,
                "technologies": technologies
            })

        return jsonify(res)

    def post(self):

        if "user_id" not in session:
            abort(401)

        data = request.get_json()
        
        name =  data['name']
        description = data['description']
        img_uri = data['img_uri']
        server_endpoint = data['server_endpoint']
        github_url = data['github_url']
        
        demo_url = None
        if 'demo_url' in data:
            demo_url = data['demo_url']

        project = Project(name=name, description=description, img_uri=img_uri, server_endpoint=server_endpoint, github_url=github_url, demo_url=demo_url)

        db.session.add(project)
        db.session.commit()

        technologies = data['technologies']

        for t in technologies:
            tech = Technology(img_uri=t['img_uri'], description=t['description'], project_id=project.id)
            db.session.add(tech)

        db.session.commit()

        return jsonify({
            "message": f"Project {name} has been added."
        })
        


class ProjectResource(Resource):

    def get(self, id):
        project = Project.query.get_or_404(id)

        techs = []
        for t in project.technologies:
            techs.append({
                "id": t.id,
                "img_uri": t.img_uri,
                "description": t.description
            })

        return jsonify({
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "img_uri": project.img_uri,
            "server_endpoint": project.server_endpoint,
            "github_url": project.github_url,
            "demo_url": project.demo_url,
            "technologies": techs
        })

    def put(self, id):

        if "user_id" not in session:
            abort(401)

        oldProject = Project.query.get_or_404(id)

        if oldProject is None:
            abort(404)
        
        data = request.get_json()

        newTech = data['technologies']

        # Compare associated technologies to see if tech has been removed, updated, or added to the project
        # id = None => new entry
        # id missing from newTech => delete the entry
        # otherwise, update the entry 

        new_tech_ids = set([])
        for t in newTech:
            new_tech_ids.add(t['id'])

        for t in oldProject.technologies:
            if t.id not in new_tech_ids:
                print(f"Delete {t.id}")
                oldTech = Technology.query.get_or_404(t.id)
                db.session.delete(oldTech)
                db.session.commit()
            
        for t in newTech:
            if t['id'] is None:
                print(f"Add {t['id']}")
                newTech = Technology(img_uri=t['img_uri'], description=t['description'], project_id=oldProject.id)
                db.session.add(newTech)
                db.session.commit()

            else:
                oldTech = Technology.query.get_or_404(t['id'])
                print(f"Update {t['id']}")
                oldTech.description = t['description']
                oldTech.img_uri = t['img_uri']
                db.session.commit()
        
        oldProject.name = data['name']
        oldProject.description = data['description']
        oldProject.server_endpoint = data['server_endpoint']
        oldProject.img_uri = data['img_uri']
        oldProject.github_url = data['github_url']
        oldProject.demo_url = data['demo_url']

        db.session.commit()

        return jsonify({
            "message": f"Project {id} has been updated."
        })
        
    def delete(self, id):

        if "user_id" not in session:
            abort(401)

        project = Project.query.get_or_404(id)

        if project is None:
            abort(404)

        db.session.delete(project)
        db.session.commit()

        return jsonify({
            "message": f"Project {project.name} was deleted successfully."
        })

api.add_resource(ModeratorsResource, "/mods")
api.add_resource(ModeratorResource, "/mods/<id>")
api.add_resource(ProjectsResource, "/projects")
api.add_resource(ProjectResource, "/projects/<id>")

@app.route("/login", methods=["POST"])
@cross_origin(supports_credentials=True)
def login_moderator():
    data = request.get_json()

    username = data['username']
    password = data['password']

    user = Moderator.query.filter_by(username=username).first()

    if user is None:
        abort(401)

    if not bcrypt.check_password_hash(user.password, password):
        abort(401)

    session['user_id'] = user.id

    return jsonify({
        "id": user.id,
        "username": user.username
    })

@app.route("/logout", methods=["POST"])
def logout_moderator():
    if "user_id" not in session:
        abort(401)

    session.pop("user_id")
    return jsonify({
        "message": "Logged out successfully."
    })

@app.route("/me", methods=["GET"])
def check_logged_in():
    user_id = session.get('user_id')

    if not user_id:
        abort(401)

    user = Moderator.query.filter_by(id=user_id).first()

    return jsonify({
        "message": f"Logged in as {user.username}."
    })

if __name__ == "__main__":
    app.run(debug=True)