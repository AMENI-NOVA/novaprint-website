from flask import Flask, render_template
from datetime import datetime, timezone
from logic import projet1, projet2, projet3, projet4, projet5, projet6, projet8, projet9, projet10
from logic.projet7 import projet7_bp
from routes.crystal_reports_routes import crystal_reports
from routes.projet11_routes import projet11_bp
from routes.projet12_routes import projet12_bp
from routes.projet14_routes import projet14_bp
from routes.projet15_routes import projet15_bp
from routes.projet16_routes import projet16_bp
from routes.projet17_routes import projet17_bp
import os

# Forcer le rechargement des modules - 20 Oct 2025 16:10
import importlib
import sys
if 'logic.projet11' in sys.modules:
    importlib.reload(sys.modules['logic.projet11'])
if 'routes.projet11_routes' in sys.modules:
    importlib.reload(sys.modules['routes.projet11_routes'])





app = Flask(__name__)

# Injection automatique de la variable "now" dans tous les templates
@app.context_processor
def inject_now():
    return {"now": datetime.now(timezone.utc)}

# Configuration pour Crystal Reports
app.config['CRYSTAL_REPORTS_DIR'] = os.path.join(app.root_path, 'crystalreport')

# Enregistrement des blueprints
app.register_blueprint(projet1.bp)
app.register_blueprint(projet2.bp)
app.register_blueprint(projet3.bp)
app.register_blueprint(projet4.bp)
app.register_blueprint(projet5.bp)
app.register_blueprint(projet6.projet6_bp)
app.register_blueprint(projet7_bp)
app.register_blueprint(projet8.bp)
app.register_blueprint(projet9.bp)
app.register_blueprint(projet10.bp)
app.register_blueprint(projet11_bp)
app.register_blueprint(projet12_bp)
app.register_blueprint(projet14_bp)
app.register_blueprint(projet15_bp)
app.register_blueprint(projet16_bp)
app.register_blueprint(projet17_bp)
app.register_blueprint(crystal_reports, url_prefix='/crystal')

# Import et enregistrement du projet 18
try:
    from routes.projet18_routes import projet18_bp
    app.register_blueprint(projet18_bp)
except ImportError as e:
    print(f"Attention: Impossible d'importer projet18_bp: {e}")


@app.route("/")
def index():
    return render_template("index.html")  # plus besoin d'ajouter now ici

@app.route('/favicon.ico')
def favicon():
    """Gestion du favicon - retourne 204 No Content pour éviter les erreurs 404"""
    return '', 204

app.secret_key = 'vraiment-secret-et-unique'

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
