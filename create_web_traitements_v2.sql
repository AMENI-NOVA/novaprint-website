-- ============================================================================
-- Script de création de la table WEB_TRAITEMENTS pour le Projet 11 (VERSION 2)
-- Base de données: novaprint_restored
-- 
-- IMPORTANT: Cette version ne stocke QUE les données métier, pas les ID de liaison
-- Les ID sont utilisés uniquement pour les jointures lors de la récupération
-- ============================================================================

USE [novaprint_restored]
GO

-- Supprimer la table si elle existe déjà
IF OBJECT_ID('dbo.WEB_TRAITEMENTS', 'U') IS NOT NULL
BEGIN
    DROP TABLE [dbo].[WEB_TRAITEMENTS]
    PRINT 'Table WEB_TRAITEMENTS supprimée'
END
GO

-- Création de la table WEB_TRAITEMENTS (VERSION SIMPLIFIÉE)
CREATE TABLE [dbo].[WEB_TRAITEMENTS] (
    -- ===== Champ ID principal =====
    [ID] INT IDENTITY(1,1) PRIMARY KEY,
    
    -- ===== Nouveaux champs spécifiques au web =====
    [DteDeb] DATETIME NULL,                      -- Date de début du traitement
    [DteFin] DATETIME NULL,                      -- Date de fin du traitement
    [NbOp] INT NULL,                             -- Nombre d'opérations réalisées
    [NbPers] INT NULL,                           -- Nombre de personnes affectées
    
    -- ===== Champ de liaison clé (unique, non dupliqué) =====
    [ID_FICHE_TRAVAIL] INT NOT NULL,            -- Clé de liaison principale UNIQUEMENT
    
    -- ===== Champs MÉTIER importés de COMMANDES (SANS les ID) =====
    [Numero_COMMANDES] VARCHAR(20) NULL,
    [Reference_COMMANDES] VARCHAR(200) NULL,
    [QteComm_COMMANDES] INT NULL,
    
    -- ===== Champs MÉTIER importés de SOCIETES (SANS les ID) =====
    [RaiSocTri_SOCIETES] VARCHAR(50) NULL,
    
    -- ===== Champs MÉTIER importés de personel (SANS les ID) =====
    [Matricule_personel] INT NULL,
    [Nom_personel] NVARCHAR(50) NULL,
    [Prenom_personel] NVARCHAR(50) NULL,
    
    -- ===== Champs MÉTIER importés de GP_SERVICES (SANS les ID) =====
    [Nom_GP_SERVICES] VARCHAR(50) NULL,
    
    -- ===== Champs MÉTIER importés de GP_POSTES (SANS les ID) =====
    [Nom_GP_POSTES] VARCHAR(50) NULL,
    
    -- ===== Champs MÉTIER importés de GP_FICHES_OPERATIONS (SANS les ID) =====
    [OpPrevDev_GP_FICHES_OPERATIONS] REAL NULL,
    [TpsPrevDev_GP_FICHES_OPERATIONS] REAL NULL,
    
    -- ===== Métadonnées =====
    [DateCreation] DATETIME DEFAULT GETDATE(),
    [DateModification] DATETIME DEFAULT GETDATE()
)
GO

-- ============================================================================
-- Ajout de la clé étrangère UNIQUEMENT vers GP_FICHES_TRAVAIL
-- C'est la seule liaison stockée, les autres sont faites par jointure
-- ============================================================================

ALTER TABLE [dbo].[WEB_TRAITEMENTS]
ADD CONSTRAINT FK_WEB_TRAITEMENTS_GP_FICHES_TRAVAIL 
FOREIGN KEY ([ID_FICHE_TRAVAIL]) REFERENCES [dbo].[GP_FICHES_TRAVAIL]([ID])
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

-- Index sur Matricule_personel
CREATE INDEX IDX_WEB_TRAITEMENTS_MATRICULE 
ON [dbo].[WEB_TRAITEMENTS]([Matricule_personel])
GO

PRINT 'Table WEB_TRAITEMENTS créée avec succès (VERSION SIMPLIFIÉE)!'
PRINT 'Seules les données métier sont stockées, pas les ID de liaison'
PRINT 'Les jointures se font via ID_FICHE_TRAVAIL uniquement'
GO


