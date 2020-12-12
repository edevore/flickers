from flask import Blueprint, redirect, url_for, render_template, flash, request
from flask_login import current_user, login_required
#from ..forms import RegistrationForm, LoginForm, UpdateUsernameForm
from ..models import User, Group, Poll
from ..forms import PollForm
from ..utils import new_id

polls = Blueprint("polls", __name__)

@login_required
@polls.route("/add-poll/<group_id>", methods=['GET', 'POST'])
def add_poll(group_id):
    group = Group.objects(group_id=group_id).first()
    if group is None:
        flash("That group does not exist.", 'error')
        return redirect(url_for("groups.index"))
    #elif current_user is not group.leader:
    #    flash("You must be the group leader to make a poll.")
    #    return redirect(url_for("groups.group_detail", group_id=group_id))

    form = PollForm()
    if form.validate_on_submit():
        poll = Poll(
            poll_id = new_id(),
            question=form.question.data,
            #poll_type = form.poll_type.data,
            group = group.to_dbref(),
        )
        poll.save()
        group.update(push__polls=poll.to_dbref())
        flash("Poll has been added", 'success')
        return redirect(url_for("groups.group_detail", group_id=group_id))
    
    return render_template("create_poll.html", form=form)