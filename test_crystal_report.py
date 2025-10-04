import win32com.client
import pythoncom
import os
import sys
import traceback

def test_crystal():
    try:
        print("Test d'initialisation Crystal Reports")
        pythoncom.CoInitialize()
        
        # Test des différentes versions possibles
        versions = [
            'CrystalRunTime.Application',
            'CrystalDesignRunTime.Application',
            'CrystalReports.Application',
            'Crystal.Report.Application',
            'CrystalReport.Application'
        ]
        
        for version in versions:
            try:
                print(f"\nTest de {version}...")
                app = win32com.client.Dispatch(version)
                print(f"✅ Succès avec {version}")
                try:
                    print(f"Version: {getattr(app, 'Version', 'Non disponible')}")
                except:
                    print("Version non disponible")
                return True
            except Exception as e:
                print(f"❌ Échec avec {version}: {str(e)}")
        
        print("\nTentative avec gencache...")
        try:
            app = win32com.client.gencache.EnsureDispatch('CrystalRunTime.Application')
            print("✅ Succès avec gencache")
            return True
        except Exception as e:
            print(f"❌ Échec avec gencache: {str(e)}")
            print("Détails de l'erreur:")
            traceback.print_exc()
        
        return False
        
    except Exception as e:
        print(f"Erreur générale: {str(e)}", file=sys.stderr)
        print("Détails de l'erreur générale:")
        traceback.print_exc()
        return False
    finally:
        try:
            pythoncom.CoUninitialize()
        except:
            pass

if __name__ == "__main__":
    # Vérifier que pywin32 est installé
    try:
        import win32com
        print("✅ pywin32 est installé")
    except ImportError:
        print("❌ pywin32 n'est pas installé")
        print("Installation de pywin32...")
        import pip
        pip.main(['install', 'pywin32'])
        print("Veuillez relancer le script")
        sys.exit(1)

    # Exécuter le test
    if test_crystal():
        print("\n✅ Test Crystal Reports réussi!")
    else:
        print("\n❌ Échec du test Crystal Reports")
