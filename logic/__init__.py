from flask import send_file
import win32com.client
import os
import tempfile
from db import get_db_cursor, DB_CONFIG

class CrystalReportManager:
    def __init__(self):
        self.reports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'crystalreport')

    def init_crystal_report(self):
        """Initialise le moteur Crystal Reports"""
        return win32com.client.Dispatch('CrystalRuntime.Application')

    def get_export_format(self, format_name):
        """Retourne le code format d'export Crystal Reports"""
        formats = {
            'PDF': 31,
            'Excel': 29,
            'Word': 17,
            'CSV': 24
        }
        return formats.get(format_name.upper(), 31)

    def get_all_reports(self):
        """Retourne la liste de tous les rapports disponibles"""
        return [f for f in os.listdir(self.reports_dir) if f.endswith('.rpt')]

    def generate_report(self, report_name, output_format='PDF', parameters=None):
        """
        Génère un rapport Crystal Reports
        
        Args:
            report_name (str): Nom du fichier .rpt
            output_format (str): Format de sortie ('PDF', 'Excel', etc.)
            parameters (dict): Paramètres du rapport
        """
        report_path = os.path.join(self.reports_dir, report_name)
        if not os.path.exists(report_path):
            raise FileNotFoundError(f"Le rapport {report_name} n'existe pas")

        try:
            crystal = self.init_crystal_report()
            report = crystal.OpenReport(report_path)

            # Configuration de la connexion à la base de données
            for table in report.Database.Tables:
                table.LogOnInfo.ConnectionInfo.ServerName = DB_CONFIG["SERVER"]
                table.LogOnInfo.ConnectionName = DB_CONFIG["DATABASE"]
                table.LogOnInfo.ConnectionInfo.IntegratedSecurity = True

            if parameters:
                for param_name, param_value in parameters.items():
                    report.ParameterFields(param_name).AddCurrentValue(param_value)

            temp_dir = tempfile.gettempdir()
            temp_file = os.path.join(temp_dir, f"report_output.{output_format.lower()}")

            report.ExportOptions.DiskFileName = temp_file
            report.ExportOptions.FormatType = self.get_export_format(output_format)
            report.Export(False)

            return temp_file

        except Exception as e:
            raise Exception(f"Erreur lors de la génération du rapport: {str(e)}")
