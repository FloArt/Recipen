import json
import hashlib
from flask import Blueprint, render_template, request, Response, jsonify
from flask_babel import gettext as _
from mongoengine.errors import NotUniqueError

from settings import site_name

from mail import send_mail
from model.user import User

page = Blueprint('register', __name__)


@page.route('/register', methods=['GET'])
def register_page():
    return render_template("web/register.html", title=_("Register") + " | " + site_name)


@page.route('/register', methods=['POST'])
def register():
    data = json.loads(request.data)
    if data["email"] is None or data["email"] == "" or data["password"] is None or data["password"] == ""\
            or data["name"] is None or data["name"] == "":
        return Response(json.dumps({"success": False, "message": _("Missing required fields")}), status=409)
    role = "basic"
    nb_user = User.objects().count()
    if nb_user == 0:
        role = "admin"
    user = User(name=data["name"], email=data["email"],
                password=hashlib.sha3_512(data["password"].encode()).hexdigest(), role=role, active=False)
    try:
        user.save()
        token = "?token=" + hashlib.md5((data["name"] + data["email"]).encode()).hexdigest() + "&mail=" + data["email"]
        send_mail(data["email"], f"{site_name} - " + _("please activate your account"),
                  _("Welcome %s,\n\nPlease click on this link to activate your account on %s:\n") %
                  (data["name"], site_name) + request.url_root + "activate" + token)
        return jsonify(success=True,
                       message=_("User successfully created. Please check your mail to validate your account."))
    except NotUniqueError:
        return Response(json.dumps({"success": False,
                                     "message": _("There is already a user with this mail address")}), status=409)