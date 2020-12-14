from flask import Blueprint, redirect
misc = Blueprint("misc", __name__)

@misc.route("/resume", methods=['GET'])
def resume():
    return redirect("static/resume.pdf")