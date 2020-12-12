from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import current_user
from ..utils import current_time

misc = Blueprint("misc", __name__)
