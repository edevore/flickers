from flask_login import UserMixin
from datetime import datetime
from . import db, login_manager
from . import config
from .utils import current_time
import base64
import mongoengine
import itertools

@login_manager.user_loader
def load_user(user_id):
    return User.objects(username=user_id).first()

#class Group(db.Document): pass # Forward declaration
#class User(db.Document, UserMixin): pass
#class Poll(db.Document): pass

class User(db.Document, UserMixin):
    username = db.StringField(required=True, unique=True)
    first_name = db.StringField(required=True)
    last_name =db.StringField(required=True)
    email = db.EmailField(required=True, unique=True)
    phone = db.StringField(required=True, unique=True, min_length=10, max_length=10)
    password = db.StringField(required=True)
    following = db.ListField(db.ReferenceField('Group'))

    # Returns unique string identifying our object
    def get_id(self):
        return self.username

    def follow_group(self, group_id):
        group = Group.objects(group_id=group_id).first()
        if group is None:
            raise ValidationError("That group does not exist.")
        
        user = User.objects(username=self.username).first()
        user.update(push__following=group)
        group.update(push__followers=user)
        print(self.username + " is now following " + group_id)

    def unfollow_group(self, group_id):
        group = Group.objects(group_id=group_id).first()
        if group is None:
            raise ValidationError("That group does not exist.")
        
        user = User.objects(username=self.username).first()
        user.update(pull__following=group)
        group.update(pull__followers=user)
        print(self.username + " has stopped following " + group_id)

class Group(db.Document):
    leader = db.ReferenceField(User, required=True, reverse_delete_rule=mongoengine.CASCADE)
    group_id = db.StringField(required=True, unique = True, min_length=5, max_length=40)
    description = db.StringField(required=True, min_length=5, max_length=500)
    date = db.StringField(required=True)
    followers = db.ListField(db.ReferenceField(User))
    polls = db.ListField(db.ReferenceField('Poll'))
    past_polls = db.ListField(db.ReferenceField('Poll'))

    # Returns unique string identifying our object
    def get_id(self):
        return self.group_id

    def add_follower(self, username):
        user = User.objects(username=username).first()
        if user is None:
            raise ValidationError("That user does not exist.")
        
        group = Group.objects(group_id=self.group_id).first()
        group.update(push__followers=user)
        user.update(push__following=group.to_dbref())
        print(username + " has been added to " + self.group_id)

    def remove_follower(self, username):
        user = User.objects(username=username).first()
        if user is None:
            raise ValidationError("That user does not exist.")
        
        group = Group.objects(group_id=self.group_id).first()
        group.update(pull__followers=user)
        user.update(pull__following=group.to_dbref())
        print(username + " has been deleted from " + self.group_id)

    def next_poll(self):
        current_poll=self.polls[0]
        group = Group.objects(group_id=self.group_id).first()
        # Remove current poll from polls and push onto past_polls
        group.update(push__past_polls=current_poll)
        group.update(pull__polls=current_poll)
        return group.polls[0]

class Poll(db.Document):
    poll_id = db.StringField(required=True, unique=True)
    question = db.StringField(required=True, min_length=5, max_length=500)
    group = db.ReferenceField(Group, required=True)
    choices = db.ListField(db.StringField(unique=True)) # Such as yes/no
    responses = db.DictField() # Key = User, Value = Vote

    # Returns unique string identifying our object
    def get_id(self):
        return self.poll_id

    # Return dict with Key = Vote, Value = Count 
    def get_counts(self):
        counts = dict()
        for choice in self.choices:
            counts[choice] = 0

        for (k,v) in self.responses.items():
            counts[v] += 1
        
        return counts

    # Returns dict with Key = Vote, Value=List(Voters)
    def get_responses(self):
        resp = dict()
        for choice in self.choices:
            resp[choice] = []

        for (k,v) in self.responses.items():
            resp[v].append(k)
        
        return resp

    def add_choice(self, choice):
        Poll.objects(poll_id=self.poll_id).first().update(push__choices=choice)
        print(f"Choice: {choice} has been added to question: {self.question}")

    def submit_vote(self, username, response):
        self.responses[username]=response
        Poll.objects(poll_id=self.poll_id).first().update(set__responses=self.responses)


