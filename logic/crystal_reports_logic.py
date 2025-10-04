from flask import send_file
import win32com.client
import pythoncom
import os
import tempfile
import sys
from db import get_db_cursor, DB_CONFIG

class CrystalReportManager:
    def __init__(self):
        self.reports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'crystalreport')

    def init_crystal_report(self):
        """Initialise le moteur Crystal Reports 14.4"""
        try:
            # Initialisation du COM pour le thread
            pythoncom.CoInitialize()
            
            # Utiliser la version 14.4 spécifiquement
            app = win32com.client.Dispatch('CrystalDesignRunTime.Application.14')
            print("Version de Crystal Reports:", getattr(app, 'Version', 'Inconnue'))
            return app

        except Exception as e:
            print(f"Erreur détaillée d'initialisation: {str(e)}", file=sys.stderr)
            # Essayer une alternative
            try:
                app = win32com.client.Dispatch('Crystal.CRPE.Application')
                return app
            except Exception as e2:
                raise Exception(f"Erreur d'initialisation Crystal Reports: {str(e2)}")

    def get_export_format(self, format_name):
        """Retourne le code format d'export Crystal Reports"""
        formats = {
            'PDF': 31,            # crEDIExportFormatPDF
            'Excel': 29,          # crEDIExportFormatExcel97
            'Word': 17,           # crEDIExportFormatWordForWindows
            'CSV': 24,            # crEDIExportFormatText
            'RTF': 14,            # crEDIExportFormatRTF
            'XML': 33            # crEDIExportFormatXML
        }
        return formats.get(format_name.upper(), 31)

    def setup_database_connection(self, report):
        """Configure la connexion à la base de données pour le rapport"""
        try:
            # Configuration de la connexion à la base de données
            for table in report.Database.Tables:
                try:
                    # Créer une nouvelle connexion pour chaque table
                    connection_info = table.LogOnInfo.ConnectionInfo
                    
                    # Configurer les paramètres de connexion SQL Server
                    connection_info.ServerName = DB_CONFIG["SERVER"]
                    connection_info.DatabaseName = DB_CONFIG["DATABASE"]
                    connection_info.IntegratedSecurity = True
                    connection_info.Type = 1  # crDBMSMSSQL
                    
                    # Appliquer les paramètres de connexion
                    table.LogOnInfo.ConnectionInfo = connection_info
                    success = table.TestConnectivity()
                    
                    if not success:
                        print(f"Avertissement: La connexion à la table {table.Name} a échoué")
                        
                except Exception as e:
                    print(f"Erreur de configuration pour la table {table.Name}: {str(e)}")
                    continue
                    
        except Exception as e:
            raise Exception(f"Erreur de configuration de la base de données: {str(e)}")

    def generate_report(self, report_name, output_format='PDF', parameters=None):
        """Génère un rapport Crystal Reports"""
        report_path = os.path.join(self.reports_dir, report_name)
        if not os.path.exists(report_path):
            raise FileNotFoundError(f"Le rapport {report_name} n'existe pas")

        crystal = None
        try:
            print("Initialisation de Crystal Reports...")
            crystal = self.init_crystal_report()
            
            print(f"Ouverture du rapport: {report_path}")
            report = crystal.OpenReport(report_path)
            
            print("Configuration de la connexion...")
            # Configuration de la connexion SQL Server
            tables = report.Database.Tables
            for table in tables:
                try:
                    logon_info = table.LogOnInfo
                    conn_info = logon_info.ConnectionInfo

                    # Configuration SQL Server
                    conn_info.ServerName = DB_CONFIG["SERVER"]
                    conn_info.DatabaseName = DB_CONFIG["DATABASE"]
                    conn_info.IntegratedSecurity = True
                    conn_info.Type = 1  # SQL Server
                    
                    # Appliquer les paramètres
                    table.ApplyLogOnInfo(logon_info)
                    
                    print(f"Table configurée: {table.Name}")
                except Exception as table_error:
                    print(f"Erreur configuration table {table.Name}: {str(table_error)}")

            # Paramètres du rapport
            if parameters:
                for param_name, param_value in parameters.items():
                    try:
                        param_field = report.ParameterFields.Item(param_name)
                        param_field.AddCurrentValue(param_value)
                    except Exception as param_error:
                        print(f"Erreur paramètre {param_name}: {str(param_error)}")

            # Export
            temp_dir = tempfile.gettempdir()
            temp_file = os.path.join(temp_dir, f"report_output.{output_format.lower()}")
            print(f"Fichier de sortie: {temp_file}")

            # Configuration de l'export
            export_options = report.ExportOptions
            export_options.DestinationType = 1  # Fichier disque
            export_options.DiskFileName = temp_file
            export_options.FormatType = 31  # PDF

            print("Exportation du rapport...")
            report.Export(False)
            print("Exportation terminée")

            return temp_file

        except Exception as e:
            print(f"Erreur détaillée: {str(e)}", file=sys.stderr)
            raise Exception(f"Erreur lors de la génération du rapport: {str(e)}")
        
        finally:
            try:
                if crystal:
                    pythoncom.CoUninitialize()
            except:
                pass
