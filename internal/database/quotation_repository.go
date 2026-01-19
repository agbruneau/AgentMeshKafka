package database

import (
	"context"
	"database/sql"
	"fmt"
	"time"

	"github.com/agbru/kafka-eda-lab/internal/models"
)

// QuotationRepository définit l'interface pour la gestion des devis
type QuotationRepository interface {
	// Create crée un nouveau devis
	Create(ctx context.Context, devis *models.Devis) error

	// GetByID récupère un devis par son ID
	GetByID(ctx context.Context, id string) (*models.Devis, error)

	// GetByClientID récupère tous les devis d'un client
	GetByClientID(ctx context.Context, clientID string) ([]*models.Devis, error)

	// GetExpired récupère les devis expirés non encore marqués
	GetExpired(ctx context.Context) ([]*models.Devis, error)

	// UpdateStatus met à jour le statut d'un devis
	UpdateStatus(ctx context.Context, id string, statut models.StatutDevis) error

	// List récupère tous les devis avec pagination
	List(ctx context.Context, limit, offset int) ([]*models.Devis, error)

	// Count retourne le nombre total de devis
	Count(ctx context.Context) (int, error)

	// CountByStatus retourne le nombre de devis par statut
	CountByStatus(ctx context.Context, statut models.StatutDevis) (int, error)
}

// SQLiteQuotationRepository implémente QuotationRepository avec SQLite
type SQLiteQuotationRepository struct {
	db *DB
}

// NewQuotationRepository crée un nouveau repository pour les devis
func NewQuotationRepository(db *DB) QuotationRepository {
	return &SQLiteQuotationRepository{db: db}
}

// Create crée un nouveau devis
func (r *SQLiteQuotationRepository) Create(ctx context.Context, devis *models.Devis) error {
	query := `
		INSERT INTO devis (id, client_id, type_bien, valeur, prime, date_creation, date_expiration, statut)
		VALUES (?, ?, ?, ?, ?, ?, ?, ?)
	`

	_, err := r.db.ExecContext(ctx, query,
		devis.ID,
		devis.ClientID,
		string(devis.TypeBien),
		devis.Valeur,
		devis.Prime,
		devis.DateCreation,
		devis.DateExpiration,
		string(devis.Statut),
	)

	if err != nil {
		return fmt.Errorf("erreur lors de la création du devis: %w", err)
	}

	return nil
}

// GetByID récupère un devis par son ID
func (r *SQLiteQuotationRepository) GetByID(ctx context.Context, id string) (*models.Devis, error) {
	query := `
		SELECT id, client_id, type_bien, valeur, prime, date_creation, date_expiration, statut
		FROM devis
		WHERE id = ?
	`

	devis := &models.Devis{}
	var typeBien, statut string

	err := r.db.QueryRowContext(ctx, query, id).Scan(
		&devis.ID,
		&devis.ClientID,
		&typeBien,
		&devis.Valeur,
		&devis.Prime,
		&devis.DateCreation,
		&devis.DateExpiration,
		&statut,
	)

	if err == sql.ErrNoRows {
		return nil, nil
	}
	if err != nil {
		return nil, fmt.Errorf("erreur lors de la récupération du devis: %w", err)
	}

	devis.TypeBien = models.TypeBien(typeBien)
	devis.Statut = models.StatutDevis(statut)

	return devis, nil
}

// GetByClientID récupère tous les devis d'un client
func (r *SQLiteQuotationRepository) GetByClientID(ctx context.Context, clientID string) ([]*models.Devis, error) {
	query := `
		SELECT id, client_id, type_bien, valeur, prime, date_creation, date_expiration, statut
		FROM devis
		WHERE client_id = ?
		ORDER BY date_creation DESC
	`

	rows, err := r.db.QueryContext(ctx, query, clientID)
	if err != nil {
		return nil, fmt.Errorf("erreur lors de la récupération des devis: %w", err)
	}
	defer rows.Close()

	return r.scanDevisList(rows)
}

// GetExpired récupère les devis expirés non encore marqués
func (r *SQLiteQuotationRepository) GetExpired(ctx context.Context) ([]*models.Devis, error) {
	query := `
		SELECT id, client_id, type_bien, valeur, prime, date_creation, date_expiration, statut
		FROM devis
		WHERE date_expiration < ? AND statut = 'GENERE'
		ORDER BY date_expiration ASC
	`

	rows, err := r.db.QueryContext(ctx, query, time.Now())
	if err != nil {
		return nil, fmt.Errorf("erreur lors de la récupération des devis expirés: %w", err)
	}
	defer rows.Close()

	return r.scanDevisList(rows)
}

// UpdateStatus met à jour le statut d'un devis
func (r *SQLiteQuotationRepository) UpdateStatus(ctx context.Context, id string, statut models.StatutDevis) error {
	query := `UPDATE devis SET statut = ? WHERE id = ?`

	result, err := r.db.ExecContext(ctx, query, string(statut), id)
	if err != nil {
		return fmt.Errorf("erreur lors de la mise à jour du statut: %w", err)
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("erreur lors de la vérification des lignes affectées: %w", err)
	}

	if rowsAffected == 0 {
		return fmt.Errorf("aucun devis trouvé avec l'ID %s", id)
	}

	return nil
}

// List récupère tous les devis avec pagination
func (r *SQLiteQuotationRepository) List(ctx context.Context, limit, offset int) ([]*models.Devis, error) {
	query := `
		SELECT id, client_id, type_bien, valeur, prime, date_creation, date_expiration, statut
		FROM devis
		ORDER BY date_creation DESC
		LIMIT ? OFFSET ?
	`

	rows, err := r.db.QueryContext(ctx, query, limit, offset)
	if err != nil {
		return nil, fmt.Errorf("erreur lors de la récupération des devis: %w", err)
	}
	defer rows.Close()

	return r.scanDevisList(rows)
}

// Count retourne le nombre total de devis
func (r *SQLiteQuotationRepository) Count(ctx context.Context) (int, error) {
	query := `SELECT COUNT(*) FROM devis`

	var count int
	err := r.db.QueryRowContext(ctx, query).Scan(&count)
	if err != nil {
		return 0, fmt.Errorf("erreur lors du comptage des devis: %w", err)
	}

	return count, nil
}

// CountByStatus retourne le nombre de devis par statut
func (r *SQLiteQuotationRepository) CountByStatus(ctx context.Context, statut models.StatutDevis) (int, error) {
	query := `SELECT COUNT(*) FROM devis WHERE statut = ?`

	var count int
	err := r.db.QueryRowContext(ctx, query, string(statut)).Scan(&count)
	if err != nil {
		return 0, fmt.Errorf("erreur lors du comptage des devis: %w", err)
	}

	return count, nil
}

// scanDevisList est une fonction utilitaire pour scanner plusieurs devis
func (r *SQLiteQuotationRepository) scanDevisList(rows *sql.Rows) ([]*models.Devis, error) {
	var devisList []*models.Devis

	for rows.Next() {
		devis := &models.Devis{}
		var typeBien, statut string

		err := rows.Scan(
			&devis.ID,
			&devis.ClientID,
			&typeBien,
			&devis.Valeur,
			&devis.Prime,
			&devis.DateCreation,
			&devis.DateExpiration,
			&statut,
		)
		if err != nil {
			return nil, fmt.Errorf("erreur lors du scan du devis: %w", err)
		}

		devis.TypeBien = models.TypeBien(typeBien)
		devis.Statut = models.StatutDevis(statut)
		devisList = append(devisList, devis)
	}

	if err := rows.Err(); err != nil {
		return nil, fmt.Errorf("erreur lors de l'itération des résultats: %w", err)
	}

	return devisList, nil
}
