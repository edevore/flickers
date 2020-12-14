from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import current_user, login_required

#from .. import movie_client
from ..forms import SearchForm, GroupForm, JoinForm, PollResponseForm, NextPollForm, GoToNewPollForm
from ..models import User, Group
from ..utils import current_time
from mongoengine.errors import NotUniqueError
import plotly.graph_objects as go
import io


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

    if join_form.join.data and join_form.validate():
        group.add_follower(current_user.username)
        return redirect(url_for("groups.group_detail", group_id=group_id))

    next_poll_form = NextPollForm()
    if next_poll_form.next.data and next_poll_form.validate():
        current_poll = group.next_poll()
        return redirect(url_for("groups.group_detail", group_id=group_id))

    go_to_new_poll_form = GoToNewPollForm()
    if go_to_new_poll_form.new_poll.data and go_to_new_poll_form.validate():
        return redirect(url_for("polls.add_poll", group_id=group.group_id))


    # Build poll from leader for followers to see
    current_poll=None
    poll_response_form=None
    plot=None
    if len(group.polls) != 0:
        current_poll = group.polls[0]
        poll_response_form = PollResponseForm()

        # Make bar chart of current vote using Plotly
        counts = current_poll.get_counts()
        fig = go.Figure([
            go.Bar(x = list(counts.keys()), y=list(counts.values()))
        ])

        f = io.StringIO()
        fig.write_html(f)
        plot = f.getvalue()

        if poll_response_form and poll_response_form.submit.data and poll_response_form.validate():
            selection = poll_response_form.choices.data
            flash(f"You voted for: " + str(selection))
            print(f"{current_user.username} voted for: " + str(selection))
            current_poll.submit_vote(current_user.username, selection)
            return redirect(url_for("groups.group_detail", group_id=group_id))

    return render_template("group_detail.html", group=group, join_form=join_form, current_poll=current_poll, 
        poll_response_form=poll_response_form, next_poll_form = next_poll_form, go_to_new_poll_form=go_to_new_poll_form, plot=plot)

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
