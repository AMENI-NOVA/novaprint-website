/*
================================================================================
CRÉATION DE LA TABLE WEB_GMAO_ARTICLES
================================================================================
Objectif : Enregistrer les articles utilisés dans les fiches de réparation
Une fiche (ID_WEB_GMAO) peut avoir plusieurs articles
Chaque ligne = 1 article utilisé
*/

USE novaprint_restored;
GO

-- Vérifier si la table existe déjà et la supprimer si nécessaire
IF OBJECT_ID('dbo.WEB_GMAO_ARTICLES', 'U') IS NOT NULL
BEGIN
    PRINT 'Suppression de la table existante WEB_GMAO_ARTICLES...'
    DROP TABLE dbo.WEB_GMAO_ARTICLES;
END
GO

-- Création de la table WEB_GMAO_ARTICLES
PRINT 'Création de la table WEB_GMAO_ARTICLES...'
CREATE TABLE dbo.WEB_GMAO_ARTICLES (
    -- Clé primaire
    ID INT IDENTITY(1,1) PRIMARY KEY,
    
    -- Référence à la fiche de réparation
    ID_WEB_GMAO INT NOT NULL,
    
    -- Référence à l'article (pour maintenir la liaison)
    ID_GS_ARTICLES INT NULL,
    
    -- Colonnes dénormalisées (copies pour historique et performance)
    Designation_GS_ARTICLES VARCHAR(200) NULL,
    Designation_GS_FAMILLES VARCHAR(100) NULL,
    Designation_GS_TYPES_ARTICLE VARCHAR(100) NULL,
    
    -- Quantité utilisée
    Quantite DECIMAL(10, 3) NULL,
    
    -- Métadonnées
    DateCreation DATETIME DEFAULT GETDATE(),
    DateModification DATETIME DEFAULT GETDATE(),
    
    -- Contraintes
    CONSTRAINT FK_WEB_GMAO_ARTICLES_WEB_GMAO 
        FOREIGN KEY (ID_WEB_GMAO) REFERENCES WEB_GMAO(ID) ON DELETE CASCADE,
    
    CONSTRAINT FK_WEB_GMAO_ARTICLES_GS_ARTICLES 
        FOREIGN KEY (ID_GS_ARTICLES) REFERENCES GS_ARTICLES(ID) ON DELETE SET NULL
);
GO

-- Index pour améliorer les performances
PRINT 'Création des index...'
CREATE NONCLUSTERED INDEX IX_WEB_GMAO_ARTICLES_ID_WEB_GMAO 
    ON dbo.WEB_GMAO_ARTICLES(ID_WEB_GMAO);
GO

CREATE NONCLUSTERED INDEX IX_WEB_GMAO_ARTICLES_ID_GS_ARTICLES 
    ON dbo.WEB_GMAO_ARTICLES(ID_GS_ARTICLES);
GO

-- Trigger pour synchroniser les désignations lors de l'insertion
PRINT 'Création du trigger de synchronisation INSERT...'
GO
CREATE TRIGGER TR_WEB_GMAO_ARTICLES_SYNC_INSERT
ON dbo.WEB_GMAO_ARTICLES
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;
    
    UPDATE wa
    SET 
        wa.Designation_GS_ARTICLES = a.Designation,
        wa.Designation_GS_FAMILLES = f.Designation,
        wa.Designation_GS_TYPES_ARTICLE = t.Designation
    FROM WEB_GMAO_ARTICLES wa
    INNER JOIN INSERTED i ON wa.ID = i.ID
    LEFT JOIN GS_ARTICLES a ON wa.ID_GS_ARTICLES = a.ID
    LEFT JOIN GS_FAMILLES f ON a.ID_FAMILLE = f.ID
    LEFT JOIN GS_TYPES_ARTICLE t ON f.ID_TYPE_ARTICLE = t.ID
    WHERE wa.ID_GS_ARTICLES IS NOT NULL;
END;
GO

-- Trigger pour synchroniser les désignations lors de la mise à jour
PRINT 'Création du trigger de synchronisation UPDATE...'
GO
CREATE TRIGGER TR_WEB_GMAO_ARTICLES_SYNC_UPDATE
ON dbo.WEB_GMAO_ARTICLES
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Mettre à jour les désignations si ID_GS_ARTICLES a changé
    IF UPDATE(ID_GS_ARTICLES)
    BEGIN
        UPDATE wa
        SET 
            wa.Designation_GS_ARTICLES = a.Designation,
            wa.Designation_GS_FAMILLES = f.Designation,
            wa.Designation_GS_TYPES_ARTICLE = t.Designation,
            wa.DateModification = GETDATE()
        FROM WEB_GMAO_ARTICLES wa
        INNER JOIN INSERTED i ON wa.ID = i.ID
        LEFT JOIN GS_ARTICLES a ON wa.ID_GS_ARTICLES = a.ID
        LEFT JOIN GS_FAMILLES f ON a.ID_FAMILLE = f.ID
        LEFT JOIN GS_TYPES_ARTICLE t ON f.ID_TYPE_ARTICLE = t.ID
        WHERE wa.ID_GS_ARTICLES IS NOT NULL;
    END
END;
GO

-- Trigger pour mettre à jour depuis GS_ARTICLES quand les désignations changent
PRINT 'Création du trigger de mise à jour depuis GS_ARTICLES...'
GO
CREATE TRIGGER TR_GS_ARTICLES_UPDATE_WEB_GMAO_ARTICLES
ON dbo.GS_ARTICLES
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    
    IF UPDATE(Designation) OR UPDATE(ID_FAMILLE)
    BEGIN
        UPDATE wa
        SET 
            wa.Designation_GS_ARTICLES = a.Designation,
            wa.Designation_GS_FAMILLES = f.Designation,
            wa.Designation_GS_TYPES_ARTICLE = t.Designation,
            wa.DateModification = GETDATE()
        FROM WEB_GMAO_ARTICLES wa
        INNER JOIN INSERTED i ON wa.ID_GS_ARTICLES = i.ID
        INNER JOIN GS_ARTICLES a ON wa.ID_GS_ARTICLES = a.ID
        LEFT JOIN GS_FAMILLES f ON a.ID_FAMILLE = f.ID
        LEFT JOIN GS_TYPES_ARTICLE t ON f.ID_TYPE_ARTICLE = t.ID;
    END
END;
GO

-- Vue pour afficher les articles autorisés (types 2 et 8 uniquement)
PRINT 'Création de la vue des articles autorisés...'
GO
CREATE VIEW VW_WEB_GMAO_ARTICLES_AUTORISES
AS
SELECT 
    a.ID as ID_Article,
    a.Designation as Designation_Article,
    a.ID_FAMILLE,
    f.Designation as Designation_Famille,
    f.ID_TYPE_ARTICLE,
    t.Designation as Designation_Type
FROM GS_ARTICLES a
INNER JOIN GS_FAMILLES f ON a.ID_FAMILLE = f.ID
INNER JOIN GS_TYPES_ARTICLE t ON f.ID_TYPE_ARTICLE = t.ID
WHERE t.ID IN (2, 8)
    AND a.ID IS NOT NULL;
GO

PRINT '✅ Table WEB_GMAO_ARTICLES créée avec succès!'
PRINT '✅ Triggers de synchronisation créés!'
PRINT '✅ Vue VW_WEB_GMAO_ARTICLES_AUTORISES créée!'
PRINT ''
PRINT '📌 Structure de la table:'
PRINT '   - ID : Identifiant unique'
PRINT '   - ID_WEB_GMAO : Référence à la fiche de réparation'
PRINT '   - ID_GS_ARTICLES : Référence à l''article'
PRINT '   - Designation_GS_ARTICLES : Copie de la désignation'
PRINT '   - Designation_GS_FAMILLES : Copie de la famille'
PRINT '   - Designation_GS_TYPES_ARTICLE : Copie du type'
PRINT '   - Quantite : Quantité utilisée'
PRINT ''
PRINT '📌 Règles:'
PRINT '   - Une fiche peut avoir plusieurs articles'
PRINT '   - Seuls les articles de type 2 et 8 sont autorisés'
PRINT '   - Les désignations sont synchronisées automatiquement'
GO


