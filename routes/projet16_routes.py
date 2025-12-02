"""
Routes pour le Projet 16 - GMAO
Blueprint minimal
"""
from flask import Blueprint, render_template

projet16_bp = Blueprint('projet16', __name__, url_prefix='/projet16')

@projet16_bp.route('/')
def index():
    """Page principale (vide pour le moment)"""
    return render_template('projet16.html')
