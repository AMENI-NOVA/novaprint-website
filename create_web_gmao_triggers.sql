-- ============================================================================
-- TRIGGERS DE SYNCHRONISATION pour la table WEB_GMAO
-- Base de données: novaprint_restored
-- ============================================================================

USE [novaprint_restored]
GO

-- Configuration des options SQL nécessaires
SET QUOTED_IDENTIFIER ON
SET ANSI_NULLS ON
GO

-- ============================================================================
-- TRIGGERS DE SYNCHRONISATION AUTOMATIQUE
-- ============================================================================

-- TRIGGER 1: Synchronisation avec GP_POSTES
IF OBJECT_ID('TR_WEB_GMAO_SYNC_POSTES', 'TR') IS NOT NULL
    DROP TRIGGER TR_WEB_GMAO_SYNC_POSTES
GO

CREATE TRIGGER TR_WEB_GMAO_SYNC_POSTES
ON [dbo].[WEB_GMAO]
AFTER INSERT, UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Mise à jour du nom du poste depuis GP_POSTES
    UPDATE w
    SET PostesReel = p.Nom,
        DateModification = GETDATE()
    FROM [dbo].[WEB_GMAO] w
    INNER JOIN inserted i ON w.ID = i.ID
    INNER JOIN [dbo].[GP_POSTES] p ON w.PostesReel = p.Nom
    WHERE w.PostesReel IS NOT NULL
END
GO

-- TRIGGER 2: Synchronisation avec personel (Opérateur Réclamant)
IF OBJECT_ID('TR_WEB_GMAO_SYNC_OPREC', 'TR') IS NOT NULL
    DROP TRIGGER TR_WEB_GMAO_SYNC_OPREC
GO

CREATE TRIGGER TR_WEB_GMAO_SYNC_OPREC
ON [dbo].[WEB_GMAO]
AFTER INSERT, UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Mise à jour du nom complet de l'opérateur réclamant
    UPDATE w
    SET OperRec = LTRIM(RTRIM(ISNULL(p.Nom, '') + ' ' + ISNULL(p.Prenom, ''))),
        DateModification = GETDATE()
    FROM [dbo].[WEB_GMAO] w
    INNER JOIN inserted i ON w.ID = i.ID
    INNER JOIN [dbo].[personel] p ON w.MatrOpRec = p.Matricule
    WHERE w.MatrOpRec IS NOT NULL
END
GO

-- TRIGGER 3: Synchronisation avec personel (Exécuteur)
IF OBJECT_ID('TR_WEB_GMAO_SYNC_EXEC', 'TR') IS NOT NULL
    DROP TRIGGER TR_WEB_GMAO_SYNC_EXEC
GO

CREATE TRIGGER TR_WEB_GMAO_SYNC_EXEC
ON [dbo].[WEB_GMAO]
AFTER INSERT, UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Mise à jour du nom complet de l'exécuteur
    UPDATE w
    SET Internvenant = LTRIM(RTRIM(ISNULL(p.Nom, '') + ' ' + ISNULL(p.Prenom, ''))),
        DateModification = GETDATE()
    FROM [dbo].[WEB_GMAO] w
    INNER JOIN inserted i ON w.ID = i.ID
    INNER JOIN [dbo].[personel] p ON w.MatInter = p.Matricule
    WHERE w.MatInter IS NOT NULL
END
GO

-- TRIGGER 4: Synchronisation avec GS_ARTICLES
IF OBJECT_ID('TR_WEB_GMAO_SYNC_ARTICLES', 'TR') IS NOT NULL
    DROP TRIGGER TR_WEB_GMAO_SYNC_ARTICLES
GO

CREATE TRIGGER TR_WEB_GMAO_SYNC_ARTICLES
ON [dbo].[WEB_GMAO]
AFTER INSERT, UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Mise à jour des désignations d'articles
    UPDATE w
    SET DesignArt1 = a1.Designation,
        DesignArt2 = a2.Designation,
        DesignArt3 = a3.Designation,
        DateModification = GETDATE()
    FROM [dbo].[WEB_GMAO] w
    INNER JOIN inserted i ON w.ID = i.ID
    LEFT JOIN [dbo].[GS_ARTICLES] a1 ON w.DesignArt1_FK = a1.ID
    LEFT JOIN [dbo].[GS_ARTICLES] a2 ON w.DesignArt2_FK = a2.ID
    LEFT JOIN [dbo].[GS_ARTICLES] a3 ON w.DesignArt3_FK = a3.ID
    
    -- Vérification que les articles appartiennent aux bonnes familles (ID ∈ {2, 8})
    IF EXISTS (
        SELECT 1 FROM inserted i
        INNER JOIN [dbo].[WEB_GMAO] w ON i.ID = w.ID
        LEFT JOIN [dbo].[GS_ARTICLES] a1 ON w.DesignArt1_FK = a1.ID
        LEFT JOIN [dbo].[GS_FAMILLES] f1 ON a1.ID_FAMILLE = f1.ID
        LEFT JOIN [dbo].[GS_TYPES_ARTICLE] t1 ON f1.ID_TYPE_ARTICLE = t1.ID
        LEFT JOIN [dbo].[GS_ARTICLES] a2 ON w.DesignArt2_FK = a2.ID
        LEFT JOIN [dbo].[GS_FAMILLES] f2 ON a2.ID_FAMILLE = f2.ID
        LEFT JOIN [dbo].[GS_TYPES_ARTICLE] t2 ON f2.ID_TYPE_ARTICLE = t2.ID
        LEFT JOIN [dbo].[GS_ARTICLES] a3 ON w.DesignArt3_FK = a3.ID
        LEFT JOIN [dbo].[GS_FAMILLES] f3 ON a3.ID_FAMILLE = f3.ID
        LEFT JOIN [dbo].[GS_TYPES_ARTICLE] t3 ON f3.ID_TYPE_ARTICLE = t3.ID
        WHERE (w.DesignArt1_FK IS NOT NULL AND t1.ID NOT IN (2, 8))
           OR (w.DesignArt2_FK IS NOT NULL AND t2.ID NOT IN (2, 8))
           OR (w.DesignArt3_FK IS NOT NULL AND t3.ID NOT IN (2, 8))
    )
    BEGIN
        RAISERROR('Les articles sélectionnés doivent appartenir uniquement aux familles de type 2 ou 8.', 16, 1)
        ROLLBACK TRANSACTION
        RETURN
    END
END
GO

-- ============================================================================
-- TRIGGERS DE SYNCHRONISATION INVERSE (Mise à jour depuis les tables sources)
-- ============================================================================

-- TRIGGER 5: Mise à jour automatique depuis GP_POSTES
IF OBJECT_ID('TR_GP_POSTES_UPDATE_WEB_GMAO', 'TR') IS NOT NULL
    DROP TRIGGER TR_GP_POSTES_UPDATE_WEB_GMAO
GO

CREATE TRIGGER TR_GP_POSTES_UPDATE_WEB_GMAO
ON [dbo].[GP_POSTES]
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Mise à jour des noms de postes dans WEB_GMAO
    UPDATE w
    SET PostesReel = i.Nom,
        DateModification = GETDATE()
    FROM [dbo].[WEB_GMAO] w
    INNER JOIN inserted i ON w.PostesReel = i.Nom
END
GO

-- TRIGGER 6: Mise à jour automatique depuis personel
IF OBJECT_ID('TR_PERSONEL_UPDATE_WEB_GMAO', 'TR') IS NOT NULL
    DROP TRIGGER TR_PERSONEL_UPDATE_WEB_GMAO
GO

CREATE TRIGGER TR_PERSONEL_UPDATE_WEB_GMAO
ON [dbo].[personel]
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Mise à jour des noms d'opérateurs réclamants
    UPDATE w
    SET OperRec = LTRIM(RTRIM(ISNULL(i.Nom, '') + ' ' + ISNULL(i.Prenom, ''))),
        DateModification = GETDATE()
    FROM [dbo].[WEB_GMAO] w
    INNER JOIN inserted i ON w.MatrOpRec = i.Matricule
    
    -- Mise à jour des noms d'exécuteurs
    UPDATE w
    SET Internvenant = LTRIM(RTRIM(ISNULL(i.Nom, '') + ' ' + ISNULL(i.Prenom, ''))),
        DateModification = GETDATE()
    FROM [dbo].[WEB_GMAO] w
    INNER JOIN inserted i ON w.MatInter = i.Matricule
END
GO

-- TRIGGER 7: Mise à jour automatique depuis GS_ARTICLES
IF OBJECT_ID('TR_GS_ARTICLES_UPDATE_WEB_GMAO', 'TR') IS NOT NULL
    DROP TRIGGER TR_GS_ARTICLES_UPDATE_WEB_GMAO
GO

CREATE TRIGGER TR_GS_ARTICLES_UPDATE_WEB_GMAO
ON [dbo].[GS_ARTICLES]
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Mise à jour des désignations d'articles
    UPDATE w
    SET DesignArt1 = i.Designation,
        DateModification = GETDATE()
    FROM [dbo].[WEB_GMAO] w
    INNER JOIN inserted i ON w.DesignArt1_FK = i.ID
    
    UPDATE w
    SET DesignArt2 = i.Designation,
        DateModification = GETDATE()
    FROM [dbo].[WEB_GMAO] w
    INNER JOIN inserted i ON w.DesignArt2_FK = i.ID
    
    UPDATE w
    SET DesignArt3 = i.Designation,
        DateModification = GETDATE()
    FROM [dbo].[WEB_GMAO] w
    INNER JOIN inserted i ON w.DesignArt3_FK = i.ID
END
GO

-- ============================================================================
-- TRIGGERS DE GESTION DES SUPPRESSIONS
-- ============================================================================

-- TRIGGER 8: Gestion des suppressions dans GP_POSTES
IF OBJECT_ID('TR_GP_POSTES_DELETE_WEB_GMAO', 'TR') IS NOT NULL
    DROP TRIGGER TR_GP_POSTES_DELETE_WEB_GMAO
GO

CREATE TRIGGER TR_GP_POSTES_DELETE_WEB_GMAO
ON [dbo].[GP_POSTES]
AFTER DELETE
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Mise à NULL des références supprimées
    UPDATE [dbo].[WEB_GMAO]
    SET PostesReel = NULL,
        DateModification = GETDATE()
    FROM deleted d
    WHERE PostesReel = d.Nom
END
GO

-- TRIGGER 9: Gestion des suppressions dans personel
IF OBJECT_ID('TR_PERSONEL_DELETE_WEB_GMAO', 'TR') IS NOT NULL
    DROP TRIGGER TR_PERSONEL_DELETE_WEB_GMAO
GO

CREATE TRIGGER TR_PERSONEL_DELETE_WEB_GMAO
ON [dbo].[personel]
AFTER DELETE
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Mise à NULL des références supprimées (opérateurs réclamants)
    UPDATE [dbo].[WEB_GMAO]
    SET OperRec = NULL,
        MatrOpRec = NULL,
        DateModification = GETDATE()
    FROM deleted d
    WHERE MatrOpRec = d.Matricule
    
    -- Mise à NULL des références supprimées (exécuteurs)
    UPDATE [dbo].[WEB_GMAO]
    SET Internvenant = NULL,
        MatInter = NULL,
        DateModification = GETDATE()
    FROM deleted d
    WHERE MatInter = d.Matricule
END
GO

-- TRIGGER 10: Gestion des suppressions dans GS_ARTICLES
IF OBJECT_ID('TR_GS_ARTICLES_DELETE_WEB_GMAO', 'TR') IS NOT NULL
    DROP TRIGGER TR_GS_ARTICLES_DELETE_WEB_GMAO
GO

CREATE TRIGGER TR_GS_ARTICLES_DELETE_WEB_GMAO
ON [dbo].[GS_ARTICLES]
AFTER DELETE
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Mise à NULL des références supprimées
    UPDATE [dbo].[WEB_GMAO]
    SET DesignArt1 = NULL,
        DesignArt1_FK = NULL,
        DateModification = GETDATE()
    FROM deleted d
    WHERE DesignArt1_FK = d.ID
    
    UPDATE [dbo].[WEB_GMAO]
    SET DesignArt2 = NULL,
        DesignArt2_FK = NULL,
        DateModification = GETDATE()
    FROM deleted d
    WHERE DesignArt2_FK = d.ID
    
    UPDATE [dbo].[WEB_GMAO]
    SET DesignArt3 = NULL,
        DesignArt3_FK = NULL,
        DateModification = GETDATE()
    FROM deleted d
    WHERE DesignArt3_FK = d.ID
END
GO

PRINT '============================================================================'
PRINT 'TRIGGERS DE SYNCHRONISATION WEB_GMAO créés avec succès!'
PRINT '============================================================================'
PRINT 'Triggers créés:'
PRINT '✓ TR_WEB_GMAO_SYNC_POSTES - Synchronisation postes'
PRINT '✓ TR_WEB_GMAO_SYNC_OPREC - Synchronisation opérateurs réclamants'
PRINT '✓ TR_WEB_GMAO_SYNC_EXEC - Synchronisation exécuteurs'
PRINT '✓ TR_WEB_GMAO_SYNC_ARTICLES - Synchronisation articles'
PRINT '✓ TR_GP_POSTES_UPDATE_WEB_GMAO - Mise à jour depuis GP_POSTES'
PRINT '✓ TR_PERSONEL_UPDATE_WEB_GMAO - Mise à jour depuis personel'
PRINT '✓ TR_GS_ARTICLES_UPDATE_WEB_GMAO - Mise à jour depuis GS_ARTICLES'
PRINT '✓ TR_GP_POSTES_DELETE_WEB_GMAO - Gestion suppressions GP_POSTES'
PRINT '✓ TR_PERSONEL_DELETE_WEB_GMAO - Gestion suppressions personel'
PRINT '✓ TR_GS_ARTICLES_DELETE_WEB_GMAO - Gestion suppressions GS_ARTICLES'
PRINT '============================================================================'
PRINT 'La synchronisation automatique est maintenant ACTIVE!'
PRINT '============================================================================'
GO
