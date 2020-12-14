from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import current_user, login_required

#from .. import movie_client
from ..forms import SearchForm, GroupForm, JoinForm, PollResponseForm, NextPollForm, GoToNewPollForm, ChartForm
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
    
    if group is None:
        flash("That group does not exist.", 'error')
        return redirect(url_for("groups.index"))

    join_form=JoinForm()
    if join_form.join.data and join_form.validate():
        group.add_follower(current_user.username)
        return redirect(url_for("groups.group_detail", group_id=group_id))

    next_poll_form = NextPollForm()
    if next_poll_form.next.data and next_poll_form.validate():
        group.next_poll()
        return redirect(url_for("groups.group_detail", group_id=group_id))

    go_to_new_poll_form = GoToNewPollForm()
    if go_to_new_poll_form.new_poll.data and go_to_new_poll_form.validate():
        return redirect(url_for("polls.add_poll", group_id=group.group_id))

   


    # Build poll from leader for followers to see
    current_poll=None
    poll_response_form=None
    chart_form=None
    if len(group.polls) != 0:
        current_poll = group.polls[0]
        
        # Button to generate chart
        chart_form = ChartForm()
        if chart_form.gen_chart.data and chart_form.validate():
            return redirect(url_for("polls.generate_chart", poll_id=current_poll.poll_id))

        # Poll response form
        poll_response_form = PollResponseForm()
        if poll_response_form and poll_response_form.submit.data and poll_response_form.validate():
            selection = poll_response_form.choices.data
            flash(f"You voted for: " + str(selection))
            print(f"{current_user.username} voted for: " + str(selection))
            current_poll.submit_vote(current_user.username, selection)
            return redirect(url_for("groups.group_detail", group_id=group_id))

    return render_template("group_detail.html", group=group, join_form=join_form, current_poll=current_poll, 
        poll_response_form=poll_response_form, next_poll_form = next_poll_form, go_to_new_poll_form=go_to_new_poll_form, chart_form=chart_form)

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
