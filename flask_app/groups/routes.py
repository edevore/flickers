from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import current_user, login_required

#from .. import movie_client
from ..forms import SearchForm, GroupForm, JoinForm
from ..models import User, Group
from ..utils import current_time
from mongoengine.errors import NotUniqueError

groups = Blueprint("groups", __name__)

@groups.route("/", methods=["GET", "POST"])
def index():
    search_form = SearchForm()
    if search_form.validate_on_submit():
        return redirect(url_for("groups.group_detail", group_id=search_form.search_query.data))

    return render_template("home.html", search_form=search_form)

@groups.route("/groups/<group_id>", methods=["GET", "POST"])
def group_detail(group_id):
    group = Group.objects(group_id=group_id).first()
    join_form=JoinForm()
    if group is None:
        flash("That group does not exist.", 'error')
        return redirect(url_for("groups.index"))

    if join_form.validate_on_submit():
        group.add_follower(current_user.username)
        return redirect(url_for("groups.group_detail", group_id=group_id))

    return render_template("group_detail.html", group=group, join_form=join_form)

@groups.route("/create-group", methods=["GET", "POST"])
@login_required
def create_group():
    form = GroupForm()
    if form.validate_on_submit():
        group = Group(group_id=form.group_id.data.lower(), description = form.description.data,
            leader = current_user._get_current_object(), date = current_time()
        )
        group.save()
        group.add_follower(current_user.username)
        return redirect(url_for("groups.group_detail", group_id=group.group_id))

    return render_template("create_group.html", title="Create Group", form=form)

@login_required
@groups.route("/join/<group_id>", methods=['GET, POST'])
def join_group(group_id):
    group = Group.objects(group_id=group_id).first()
    if group is None:
        flash("That group does not exist.", 'error')
        return redirect(url_for("groups.index"))
    group.add_follower(current_user.username)
    return redirect(url_for("groups.group_detail", group_id=group_id))