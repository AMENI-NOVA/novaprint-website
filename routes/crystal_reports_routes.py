from flask import Blueprint, send_file, render_template, jsonify
from logic.crystal_reports_logic import CrystalReportManager
import os

crystal_reports = Blueprint('crystal_reports', __name__)
report_manager = CrystalReportManager()

@crystal_reports.route('/reports')
def list_reports():
    """Liste tous les rapports disponibles"""
    try:
        reports = report_manager.get_all_reports()
        return render_template('reports.html', reports=reports)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@crystal_reports.route('/report/<report_name>')
def view_report(report_name):
    """Génère et affiche un rapport spécifique"""
    try:
        output_file = report_manager.generate_report(report_name)
        return send_file(
            output_file,
            as_attachment=True,
            download_name=f"{os.path.splitext(report_name)[0]}.pdf"
        )
    except FileNotFoundError:
        return "Rapport non trouvé", 404
    except Exception as e:
        return f"Erreur lors de la génération du rapport: {str(e)}", 500

@crystal_reports.route('/report/<report_name>/debug')
def debug_report(report_name):
    """Affiche les informations de débogage pour un rapport"""
    try:
        report_path = os.path.join(report_manager.reports_dir, report_name)
        if not os.path.exists(report_path):
            return jsonify({"error": "Rapport non trouvé"}), 404

        crystal = report_manager.init_crystal_report()
        report = crystal.OpenReport(report_path)
        
        debug_info = {
            "tables": [],
            "parameters": []
        }

        # Récupérer les informations sur les tables
        for table in report.Database.Tables:
            table_info = {
                "name": table.Name,
                "qualified_name": table.QualifiedName,
                "exists": False
            }
            
            try:
                with get_db_cursor() as cursor:
                    cursor.execute(f"""
                        SELECT COUNT(*) 
                        FROM INFORMATION_SCHEMA.TABLES 
                        WHERE TABLE_NAME = '{table.Name}'
                    """)
                    table_info["exists"] = cursor.fetchone()[0] > 0
                    
                    if table_info["exists"]:
                        cursor.execute(f"""
                            SELECT COLUMN_NAME
                            FROM INFORMATION_SCHEMA.COLUMNS
                            WHERE TABLE_NAME = '{table.Name}'
                        """)
                        table_info["columns"] = [row[0] for row in cursor.fetchall()]
            except Exception as e:
                table_info["error"] = str(e)
                
            debug_info["tables"].append(table_info)

        # Récupérer les informations sur les paramètres
        for param in report.ParameterFields:
            debug_info["parameters"].append({
                "name": param.Name,
                "type": param.Type,
                "prompt_text": param.PromptText
            })

        return jsonify(debug_info)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
