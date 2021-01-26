from flask import Blueprint, redirect, url_for, render_template, flash, request
from flask_login import current_user, login_required
from ..models import User, Group, Poll
from ..forms import CreatePollForm
from ..utils import new_id
import plotly.graph_objects as go
import io

polls = Blueprint("polls", __name__)

@login_required
@polls.route("/add-poll/<group_id>", methods=['GET', 'POST'])
def add_poll(group_id):
    group = Group.objects(group_id=group_id).first()
    if group is None:
        flash("That group does not exist.", 'error')
        return redirect(url_for("groups.index"))

    form = CreatePollForm()
    if form.validate_on_submit():
        poll = Poll(
            poll_id = new_id(),
            question=form.question.data,
            group = group.to_dbref(),
            responses={},
            poll_type=form.poll_type.data
        )
        print(f"Poll Type {poll.poll_type}")
        poll.save()
        poll.add_choice("Yes")
        poll.add_choice("No")
        poll.add_choice("Abstain")
        group.update(push__polls=poll.to_dbref())
        flash("Poll has been added", 'success')
        return redirect(url_for("groups.group_detail", group_id=group_id))
    
    return render_template("create_poll.html", form=form)

@login_required
@polls.route("/chart/<poll_id>", methods=['GET', 'POST'])
def generate_chart(poll_id):
    poll = Poll.objects(poll_id=poll_id).first()
    if poll is None:
        flash("That poll does not exist.", 'error')
        return redirect(url_for("groups.index"))

    # Make bar chart of current vote using Plotly
    counts = poll.get_counts()
    fig = go.Figure([
        go.Bar(x = list(counts.keys()), y=list(counts.values()))
    ])

    f = io.StringIO()
    fig.write_html(f)
    plot = f.getvalue()

    print(counts)
    print(poll.group.group_id)
    return render_template("chart.html", plot=plot, poll=poll)