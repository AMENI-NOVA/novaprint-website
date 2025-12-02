-- ============================================================================
-- Script de création de la table WEB_TRAITEMENTS pour le Projet 11
-- Base de données: novaprint_restored
-- ============================================================================

USE [novaprint_restored]
GO

-- Supprimer la table si elle existe déjà (pour tests)
IF OBJECT_ID('dbo.WEB_TRAITEMENTS', 'U') IS NOT NULL
BEGIN
    DROP TABLE [dbo].[WEB_TRAITEMENTS]
    PRINT 'Table WEB_TRAITEMENTS supprimée'
END
GO

-- Création de la table WEB_TRAITEMENTS
CREATE TABLE [dbo].[WEB_TRAITEMENTS] (
    -- ===== Champ ID principal =====
    [ID] INT IDENTITY(1,1) PRIMARY KEY,
    
    -- ===== Nouveaux champs spécifiques au web =====
    [DteDeb] DATETIME NULL,                      -- Date de début du traitement
    [DteFin] DATETIME NULL,                      -- Date de fin du traitement
    [NbOp] INT NULL,                             -- Nombre d'opérations réalisées
    [NbPers] INT NULL,                           -- Nombre de personnes affectées
    
    -- ===== Champ de liaison clé (unique, non dupliqué) =====
    [ID_FICHE_TRAVAIL] INT NOT NULL,            -- Clé de liaison principale
    
    -- ===== Champs importés de COMMANDES =====
    [ID_COMMANDES] INT NULL,
    [ID_SOCIETE_COMMANDES] INT NULL,
    [Numero_COMMANDES] VARCHAR(20) NULL,
    [Reference_COMMANDES] VARCHAR(200) NULL,
    [QteComm_COMMANDES] INT NULL,
    
    -- ===== Champs importés de SOCIETES =====
    [ID_SOCIETES] INT NULL,
    [RaiSocTri_SOCIETES] VARCHAR(50) NULL,
    
    -- ===== Champs importés de personel =====
    [Matricule_personel] INT NULL,
    [Nom_personel] NVARCHAR(50) NULL,
    [Prenom_personel] NVARCHAR(50) NULL,
    
    -- ===== Champs importés de GP_SERVICES =====
    [ID_GP_SERVICES] INT NULL,
    [Nom_GP_SERVICES] VARCHAR(50) NULL,
    
    -- ===== Champs importés de GP_POSTES =====
    [ID_GP_POSTES] INT NULL,
    [Nom_GP_POSTES] VARCHAR(50) NULL,
    [ID_SERVICE_GP_POSTES] INT NULL,
    
    -- ===== Champs importés de GP_FICHES_TRAVAIL =====
    [ID_GP_FICHES_TRAVAIL] INT NULL,
    [ID_COMMANDE_GP_FICHES_TRAVAIL] INT NULL,
    [ID_POSTE_GP_FICHES_TRAVAIL] INT NULL,
    
    -- ===== Champs importés de GP_FICHES_OPERATIONS =====
    [ID_OPERATION_GP_FICHES_OPERATIONS] INT NULL,
    [OpPrevDev_GP_FICHES_OPERATIONS] REAL NULL,
    [TpsPrevDev_GP_FICHES_OPERATIONS] REAL NULL,
    
    -- ===== Champs importés de GP_TRAITEMENTS =====
    [ID_GP_TRAITEMENTS] INT NULL,
    
    -- ===== Métadonnées =====
    [DateCreation] DATETIME DEFAULT GETDATE(),
    [DateModification] DATETIME DEFAULT GETDATE()
)
GO

-- ============================================================================
-- Ajout des clés étrangères pour maintenir l'intégrité référentielle
-- ============================================================================

-- Clé étrangère vers GP_FICHES_TRAVAIL (lien principal)
ALTER TABLE [dbo].[WEB_TRAITEMENTS]
ADD CONSTRAINT FK_WEB_TRAITEMENTS_GP_FICHES_TRAVAIL 
FOREIGN KEY ([ID_FICHE_TRAVAIL]) REFERENCES [dbo].[GP_FICHES_TRAVAIL]([ID])
GO

-- Clé étrangère vers COMMANDES
ALTER TABLE [dbo].[WEB_TRAITEMENTS]
ADD CONSTRAINT FK_WEB_TRAITEMENTS_COMMANDES 
FOREIGN KEY ([ID_COMMANDES]) REFERENCES [dbo].[COMMANDES]([ID])
GO

-- Clé étrangère vers SOCIETES
ALTER TABLE [dbo].[WEB_TRAITEMENTS]
ADD CONSTRAINT FK_WEB_TRAITEMENTS_SOCIETES 
FOREIGN KEY ([ID_SOCIETES]) REFERENCES [dbo].[SOCIETES]([ID])
GO

-- Clé étrangère vers personel
ALTER TABLE [dbo].[WEB_TRAITEMENTS]
ADD CONSTRAINT FK_WEB_TRAITEMENTS_personel 
FOREIGN KEY ([Matricule_personel]) REFERENCES [dbo].[personel]([Matricule])
GO

-- Clé étrangère vers GP_SERVICES
ALTER TABLE [dbo].[WEB_TRAITEMENTS]
ADD CONSTRAINT FK_WEB_TRAITEMENTS_GP_SERVICES 
FOREIGN KEY ([ID_GP_SERVICES]) REFERENCES [dbo].[GP_SERVICES]([ID])
GO

-- Clé étrangère vers GP_POSTES
ALTER TABLE [dbo].[WEB_TRAITEMENTS]
ADD CONSTRAINT FK_WEB_TRAITEMENTS_GP_POSTES 
FOREIGN KEY ([ID_GP_POSTES]) REFERENCES [dbo].[GP_POSTES]([ID])
GO

-- Clé étrangère vers GP_TRAITEMENTS
ALTER TABLE [dbo].[WEB_TRAITEMENTS]
ADD CONSTRAINT FK_WEB_TRAITEMENTS_GP_TRAITEMENTS 
FOREIGN KEY ([ID_GP_TRAITEMENTS]) REFERENCES [dbo].[GP_TRAITEMENTS]([ID])
GO

-- ============================================================================
-- Création d'index pour améliorer les performances
-- ============================================================================

-- Index sur ID_FICHE_TRAVAIL (recherches fréquentes)
CREATE INDEX IDX_WEB_TRAITEMENTS_ID_FICHE_TRAVAIL 
ON [dbo].[WEB_TRAITEMENTS]([ID_FICHE_TRAVAIL])
GO

-- Index sur Numero_COMMANDES (recherches par numéro de commande)
CREATE INDEX IDX_WEB_TRAITEMENTS_NUMERO_COMMANDES 
ON [dbo].[WEB_TRAITEMENTS]([Numero_COMMANDES])
GO

-- Index sur dates
CREATE INDEX IDX_WEB_TRAITEMENTS_DATES 
ON [dbo].[WEB_TRAITEMENTS]([DteDeb], [DteFin])
GO

PRINT 'Table WEB_TRAITEMENTS créée avec succès!'
PRINT 'Clés étrangères ajoutées pour maintenir l''intégrité référentielle'
PRINT 'Index créés pour optimiser les performances'
GO


