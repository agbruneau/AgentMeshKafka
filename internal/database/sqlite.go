package database

import (
	"database/sql"
	"fmt"
	"os"
	"path/filepath"

	_ "github.com/mattn/go-sqlite3"
)

// DB encapsule la connexion SQLite
type DB struct {
	*sql.DB
}

// NewSQLiteDB crée une nouvelle connexion SQLite
func NewSQLiteDB(dbPath string) (*DB, error) {
	// Créer le répertoire si nécessaire
	dir := filepath.Dir(dbPath)
	if dir != "." && dir != "" {
		if err := os.MkdirAll(dir, 0755); err != nil {
			return nil, fmt.Errorf("impossible de créer le répertoire: %w", err)
		}
	}

	db, err := sql.Open("sqlite3", dbPath)
	if err != nil {
		return nil, fmt.Errorf("impossible d'ouvrir la base de données: %w", err)
	}

	// Vérifier la connexion
	if err := db.Ping(); err != nil {
		return nil, fmt.Errorf("impossible de se connecter à la base de données: %w", err)
	}

	// Configurer SQLite pour de meilleures performances
	pragmas := []string{
		"PRAGMA journal_mode=WAL",
		"PRAGMA synchronous=NORMAL",
		"PRAGMA cache_size=10000",
		"PRAGMA foreign_keys=ON",
	}

	for _, pragma := range pragmas {
		if _, err := db.Exec(pragma); err != nil {
			return nil, fmt.Errorf("erreur lors de l'exécution de %s: %w", pragma, err)
		}
	}

	return &DB{db}, nil
}

// InitSchema initialise le schéma de la base de données
func (db *DB) InitSchema() error {
	schema := `
	-- Table des devis
	CREATE TABLE IF NOT EXISTS devis (
		id TEXT PRIMARY KEY,
		client_id TEXT NOT NULL,
		type_bien TEXT NOT NULL CHECK (type_bien IN ('AUTO', 'HABITATION', 'AUTRE')),
		valeur REAL NOT NULL CHECK (valeur > 0),
		prime REAL NOT NULL CHECK (prime > 0),
		date_creation DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
		date_expiration DATETIME NOT NULL,
		statut TEXT NOT NULL DEFAULT 'GENERE' CHECK (statut IN ('GENERE', 'CONVERTI', 'EXPIRE'))
	);

	-- Index pour les requêtes fréquentes
	CREATE INDEX IF NOT EXISTS idx_devis_client_id ON devis(client_id);
	CREATE INDEX IF NOT EXISTS idx_devis_statut ON devis(statut);
	CREATE INDEX IF NOT EXISTS idx_devis_date_expiration ON devis(date_expiration);

	-- Table des contrats
	CREATE TABLE IF NOT EXISTS contrats (
		id TEXT PRIMARY KEY,
		devis_id TEXT NOT NULL,
		client_id TEXT NOT NULL,
		type_bien TEXT NOT NULL CHECK (type_bien IN ('AUTO', 'HABITATION', 'AUTRE')),
		prime REAL NOT NULL CHECK (prime > 0),
		date_effet DATETIME NOT NULL,
		date_fin DATETIME,
		statut TEXT NOT NULL DEFAULT 'ACTIF' CHECK (statut IN ('ACTIF', 'MODIFIE', 'RESILIE')),
		FOREIGN KEY (devis_id) REFERENCES devis(id)
	);

	-- Index pour les contrats
	CREATE INDEX IF NOT EXISTS idx_contrats_client_id ON contrats(client_id);
	CREATE INDEX IF NOT EXISTS idx_contrats_devis_id ON contrats(devis_id);
	CREATE INDEX IF NOT EXISTS idx_contrats_statut ON contrats(statut);

	-- Table des sinistres
	CREATE TABLE IF NOT EXISTS sinistres (
		id TEXT PRIMARY KEY,
		contrat_id TEXT NOT NULL,
		type_sinistre TEXT NOT NULL,
		description TEXT,
		montant_estime REAL NOT NULL CHECK (montant_estime >= 0),
		montant_evalue REAL,
		montant_indemnise REAL,
		date_survenance DATETIME NOT NULL,
		date_declaration DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
		date_evaluation DATETIME,
		date_paiement DATETIME,
		statut TEXT NOT NULL DEFAULT 'DECLARE' CHECK (statut IN ('DECLARE', 'EVALUE', 'INDEMNISE', 'REJETE')),
		FOREIGN KEY (contrat_id) REFERENCES contrats(id)
	);

	-- Index pour les sinistres
	CREATE INDEX IF NOT EXISTS idx_sinistres_contrat_id ON sinistres(contrat_id);
	CREATE INDEX IF NOT EXISTS idx_sinistres_statut ON sinistres(statut);

	-- Table des événements (pour l'historique/audit)
	CREATE TABLE IF NOT EXISTS events_log (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		event_id TEXT NOT NULL UNIQUE,
		event_type TEXT NOT NULL,
		source TEXT NOT NULL,
		payload TEXT NOT NULL,
		created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
	);

	-- Index pour les événements
	CREATE INDEX IF NOT EXISTS idx_events_log_type ON events_log(event_type);
	CREATE INDEX IF NOT EXISTS idx_events_log_created_at ON events_log(created_at);
	`

	_, err := db.Exec(schema)
	if err != nil {
		return fmt.Errorf("erreur lors de l'initialisation du schéma: %w", err)
	}

	return nil
}

// Close ferme la connexion à la base de données
func (db *DB) Close() error {
	return db.DB.Close()
}
