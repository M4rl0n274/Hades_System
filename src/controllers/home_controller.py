from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from src.controllers.auth_controller import login_required

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
@login_required
def index():
    return render_template('index.html')