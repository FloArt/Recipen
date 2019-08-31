#!/usr/bin/env python3

import json
import hashlib
from flask import Flask, render_template, request, jsonify, Response
from flask_mongoengine import MongoEngine
from settings import db_name, site_name, timezone, locale
from werkzeug.exceptions import NotFound
from mongoengine.errors import NotUniqueError
from flask_babel import Babel
from flask_babel import gettext as _
from jinja2 import ext
from model.recipe import Recipe, Ingredient, Instruction, Category
from model.user import User


app = Flask(__name__)
app.config['MONGODB_DB'] = db_name
app.config['BABEL_DEFAULT_LOCALE'] = locale
app.config['BABEL_DEFAULT_TIMEZONE'] = timezone
babel = Babel(app)
db = MongoEngine(app)


@app.context_processor
def inject_default_data():
    return dict({
        "locale": locale,
        "locales": [locale],
    })


@app.route('/')
def home():
    # recipe = Recipe(title="Première recette de test",
    #                 description="Ma description trop bien",
    #                 ingredients=[{"name": "premier ingrédient"}, {"name": "second ingrédient", "quantity": 2, "unit": "g"}],
    #                 instructions=[{"text_inst": "Faire ça"}, {"text_inst": "Puis ensuite faire ça", "level": 1}],
    #                 excerpt="Aaaaaah!!!",
    #                 time_prep=60,
    #                 picture_file="mapremiererecette.jpg",
    #                 nb_people=2,
    #                 slug="premiere_recette_de_test",
    #                 categories=[{"name": "Plat principal"}, {"name": "Entrée"}],
    #                 author={"name": "Floréal", "id": "1"})
    # recipe.save()
    return render_template("web/basisnav.html", title=_("Panel") + " | " + site_name)

@app.route('/panel')
def panel_home():
    return render_template("panel/basis.html", title=_("Panel") + " | " + site_name)


@app.route('/register', methods=['GET'])
def register_page():
    return render_template("web/register.html", title=_("Register") + " | " + site_name)


@app.route('/register', methods=['POST'])
def register():
    role = "basic"
    nb_user = User.objects().count()
    if nb_user == 0:
        role = "admin"
    data = json.loads(request.data)
    user = User(name=data["name"], email=data["email"],
                password=hashlib.sha3_512(data["password"].encode()).hexdigest(), role=role, active=False)
    try:
        user.save()
        return jsonify(success=True,
                       message=_("User successfully created. Please check your mail to validate your account."))
    except NotUniqueError:
        return Response(json.dumps({"success": False,
                                     "message": _("There is already a user with this mail address")}), status=409)


@app.errorhandler(NotFound)
def error_handle_not_found(e):
    return render_template("404.html", title=site_name)


if __name__ == "__main__":
    app.run(use_debugger=True, use_reloader=True)
