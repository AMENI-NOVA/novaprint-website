import win32com.client
import pythoncom
import os
import sys

def test_crystal():
    try:
        print("Test d'initialisation Crystal Reports 14.4")
        pythoncom.CoInitialize()
        
        # Test des différentes versions possibles
        versions = [
            'CrystalDesignRunTime.Application.14',
            'Crystal.CRPE.Application',
            'CrystalRunTime.Application.14'
        ]
        
        for version in versions:
            try:
                print(f"\nTest de {version}...")
                app = win32com.client.Dispatch(version)
                print(f"✅ Succès avec {version}")
                try:
                    print(f"Version: {app.Version}")
                except:
                    print("Version non disponible")
                return True
            except Exception as e:
                print(f"❌ Échec avec {version}: {str(e)}")
        
        return False
        
    except Exception as e:
        print(f"Erreur générale: {str(e)}", file=sys.stderr)
        return False
    finally:
        pythoncom.CoUninitialize()

if __name__ == "__main__":
    if test_crystal():
        print("\n✅ Test Crystal Reports réussi!")
    else:
        print("\n❌ Échec du test Crystal Reports")
