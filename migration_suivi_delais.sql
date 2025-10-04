-- Migration pour ajouter les colonnes de suivi des délais
-- À exécuter sur la base de données SQL Server

-- Vérifier si les colonnes existent déjà
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'COMMANDES' AND COLUMN_NAME = 'DteLivReelle')
BEGIN
    ALTER TABLE COMMANDES ADD DteLivReelle DATE NULL;
    PRINT 'Colonne DteLivReelle ajoutée à la table COMMANDES';
END
ELSE
BEGIN
    PRINT 'Colonne DteLivReelle existe déjà';
END

-- Vérifier si la colonne TypeModification existe dans HISTORIQUE_LIVRAISON
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'HISTORIQUE_LIVRAISON' AND COLUMN_NAME = 'TypeModification')
BEGIN
    ALTER TABLE HISTORIQUE_LIVRAISON ADD TypeModification VARCHAR(50) NULL;
    PRINT 'Colonne TypeModification ajoutée à la table HISTORIQUE_LIVRAISON';
END
ELSE
BEGIN
    PRINT 'Colonne TypeModification existe déjà';
END

-- Mettre à jour les valeurs par défaut pour TypeModification
UPDATE HISTORIQUE_LIVRAISON 
SET TypeModification = 'Modification Date' 
WHERE TypeModification IS NULL;

-- Afficher la structure de la table COMMANDES
SELECT 
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    COLUMN_DEFAULT
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'COMMANDES'
ORDER BY ORDINAL_POSITION;

PRINT 'Migration terminée avec succès!';

