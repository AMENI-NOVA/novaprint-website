/*
================================================================================
SUPPRESSION DES ANCIENNES COLONNES D'ARTICLES DE WEB_GMAO
================================================================================
Les colonnes DesignArt1/2/3 et QuantiteArt1/2/3 sont remplacées par la table WEB_GMAO_ARTICLES
*/

USE novaprint_restored;
GO

PRINT '🗑️ Suppression des anciennes colonnes d''articles de WEB_GMAO...'
PRINT ''

-- Désactiver temporairement les contraintes si nécessaire
-- (au cas où des FK ou contraintes existent sur ces colonnes)

-- Supprimer les colonnes d'articles
BEGIN TRY
    PRINT 'Suppression de DesignArt1...'
    ALTER TABLE WEB_GMAO DROP COLUMN DesignArt1;
    PRINT '   ✅ DesignArt1 supprimée'
END TRY
BEGIN CATCH
    PRINT '   ⚠️ Erreur: ' + ERROR_MESSAGE()
END CATCH

BEGIN TRY
    PRINT 'Suppression de QuantiteArt1...'
    ALTER TABLE WEB_GMAO DROP COLUMN QuantiteArt1;
    PRINT '   ✅ QuantiteArt1 supprimée'
END TRY
BEGIN CATCH
    PRINT '   ⚠️ Erreur: ' + ERROR_MESSAGE()
END CATCH

BEGIN TRY
    PRINT 'Suppression de DesignArt2...'
    ALTER TABLE WEB_GMAO DROP COLUMN DesignArt2;
    PRINT '   ✅ DesignArt2 supprimée'
END TRY
BEGIN CATCH
    PRINT '   ⚠️ Erreur: ' + ERROR_MESSAGE()
END CATCH

BEGIN TRY
    PRINT 'Suppression de QuantiteArt2...'
    ALTER TABLE WEB_GMAO DROP COLUMN QuantiteArt2;
    PRINT '   ✅ QuantiteArt2 supprimée'
END TRY
BEGIN CATCH
    PRINT '   ⚠️ Erreur: ' + ERROR_MESSAGE()
END CATCH

BEGIN TRY
    PRINT 'Suppression de DesignArt3...'
    ALTER TABLE WEB_GMAO DROP COLUMN DesignArt3;
    PRINT '   ✅ DesignArt3 supprimée'
END TRY
BEGIN CATCH
    PRINT '   ⚠️ Erreur: ' + ERROR_MESSAGE()
END CATCH

BEGIN TRY
    PRINT 'Suppression de QuantiteArt3...'
    ALTER TABLE WEB_GMAO DROP COLUMN QuantiteArt3;
    PRINT '   ✅ QuantiteArt3 supprimée'
END TRY
BEGIN CATCH
    PRINT '   ⚠️ Erreur: ' + ERROR_MESSAGE()
END CATCH

PRINT ''
PRINT '✅ Suppression des anciennes colonnes terminée!'
PRINT ''
PRINT '📌 Les articles sont maintenant gérés dans WEB_GMAO_ARTICLES'
PRINT '📌 Une fiche peut avoir un nombre illimité d''articles'
GO

-- Vérifier la structure finale de WEB_GMAO
PRINT ''
PRINT '📋 Structure finale de WEB_GMAO (colonnes restantes):'
PRINT '--------------------------------------------------------------------------------'
SELECT 
    COLUMN_NAME,
    DATA_TYPE,
    CHARACTER_MAXIMUM_LENGTH,
    IS_NULLABLE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'WEB_GMAO'
ORDER BY ORDINAL_POSITION;
GO


