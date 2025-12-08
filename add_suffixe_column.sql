/*
================================================================================
AJOUT DE LA COLONNE SUFFIXE DANS WEB_GMAO
================================================================================
Objectif : Ajouter une colonne Suffixe pour suivre les versions d'une fiche
- Valeur par défaut = 0
- S'incrémente à chaque modification d'une fiche de demande d'intervention
*/

USE novaprint_restored;
GO

-- Vérifier si la colonne existe déjà
IF NOT EXISTS (
    SELECT 1 
    FROM sys.columns 
    WHERE object_id = OBJECT_ID('dbo.WEB_GMAO') 
    AND name = 'Suffixe'
)
BEGIN
    PRINT 'Ajout de la colonne Suffixe...'
    
    -- Ajouter la colonne avec valeur par défaut = 0
    ALTER TABLE dbo.WEB_GMAO
    ADD Suffixe INT NOT NULL DEFAULT 0;
    
    PRINT '✅ Colonne Suffixe ajoutée avec succès!'
END
ELSE
BEGIN
    PRINT '⚠️ La colonne Suffixe existe déjà.'
END
GO

-- Mettre à jour les enregistrements existants pour avoir Suffixe = 0
UPDATE dbo.WEB_GMAO
SET Suffixe = 0
WHERE Suffixe IS NULL;
GO

-- Afficher un résumé
SELECT 
    Code,
    COUNT(*) as NombreFiches,
    MIN(Suffixe) as SuffixeMin,
    MAX(Suffixe) as SuffixeMax,
    AVG(CAST(Suffixe AS FLOAT)) as SuffixeMoyen
FROM dbo.WEB_GMAO
GROUP BY Code;
GO

PRINT ''
PRINT '📌 Structure mise à jour:'
PRINT '   - Colonne Suffixe ajoutée (INT, NOT NULL, DEFAULT 0)'
PRINT '   - Toutes les fiches existantes ont Suffixe = 0'
PRINT ''
PRINT '📌 Comportement:'
PRINT '   - À chaque modification d''une fiche, Suffixe s''incrémente de 1'
PRINT '   - La création d''une nouvelle fiche commence avec Suffixe = 0'
GO

