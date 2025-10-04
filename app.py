from flask import Flask, render_template
from datetime import datetime
from logic import projet1, projet2, projet3, projet4, projet5, projet6, projet8, projet10, projet9, projet10
from logic.projet7 import projet7_bp
from routes.crystal_reports_routes import crystal_reports
import os





app = Flask(__name__)

# Injection automatique de la variable "now" dans tous les templates
@app.context_processor
def inject_now():
    return {"now": datetime.utcnow()}

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
app.register_blueprint(crystal_reports, url_prefix='/crystal')


@app.route("/")
def index():
    return render_template("index.html")  # plus besoin d'ajouter now ici
app.secret_key = 'vraiment-secret-et-unique'

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
