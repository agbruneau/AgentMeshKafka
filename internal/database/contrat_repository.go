package database

import (
	"context"
	"database/sql"
	"fmt"
	"time"

	"github.com/agbru/kafka-eda-lab/internal/models"
)

// ContratRepository définit l'interface pour la gestion des contrats
type ContratRepository interface {
	// Create crée un nouveau contrat
	Create(ctx context.Context, contrat *models.Contrat) error

	// GetByID récupère un contrat par son ID
	GetByID(ctx context.Context, id string) (*models.Contrat, error)

	// GetByDevisID récupère un contrat par l'ID du devis
	GetByDevisID(ctx context.Context, devisID string) (*models.Contrat, error)

	// GetByClientID récupère tous les contrats d'un client
	GetByClientID(ctx context.Context, clientID string) ([]*models.Contrat, error)

	// GetActive récupère tous les contrats actifs
	GetActive(ctx context.Context) ([]*models.Contrat, error)

	// UpdateStatus met à jour le statut d'un contrat
	UpdateStatus(ctx context.Context, id string, statut models.StatutContrat) error

	// Resilier résilie un contrat
	Resilier(ctx context.Context, id string, dateFin time.Time) error

	// List récupère tous les contrats avec pagination
	List(ctx context.Context, limit, offset int) ([]*models.Contrat, error)

	// Count retourne le nombre total de contrats
	Count(ctx context.Context) (int, error)

	// CountByStatus retourne le nombre de contrats par statut
	CountByStatus(ctx context.Context, statut models.StatutContrat) (int, error)
}

// SQLiteContratRepository implémente ContratRepository avec SQLite
type SQLiteContratRepository struct {
	db *DB
}

// NewContratRepository crée un nouveau repository pour les contrats
func NewContratRepository(db *DB) ContratRepository {
	return &SQLiteContratRepository{db: db}
}

// Create crée un nouveau contrat
func (r *SQLiteContratRepository) Create(ctx context.Context, contrat *models.Contrat) error {
	query := `
		INSERT INTO contrats (id, devis_id, client_id, type_bien, prime, date_effet, date_fin, statut)
		VALUES (?, ?, ?, ?, ?, ?, ?, ?)
	`

	_, err := r.db.ExecContext(ctx, query,
		contrat.ID,
		contrat.DevisID,
		contrat.ClientID,
		string(contrat.TypeBien),
		contrat.Prime,
		contrat.DateEffet,
		contrat.DateFin,
		string(contrat.Statut),
	)

	if err != nil {
		return fmt.Errorf("erreur lors de la création du contrat: %w", err)
	}

	return nil
}

// GetByID récupère un contrat par son ID
func (r *SQLiteContratRepository) GetByID(ctx context.Context, id string) (*models.Contrat, error) {
	query := `
		SELECT id, devis_id, client_id, type_bien, prime, date_effet, date_fin, statut
		FROM contrats
		WHERE id = ?
	`

	contrat := &models.Contrat{}
	var typeBien, statut string
	var dateFin sql.NullTime

	err := r.db.QueryRowContext(ctx, query, id).Scan(
		&contrat.ID,
		&contrat.DevisID,
		&contrat.ClientID,
		&typeBien,
		&contrat.Prime,
		&contrat.DateEffet,
		&dateFin,
		&statut,
	)

	if err == sql.ErrNoRows {
		return nil, nil
	}
	if err != nil {
		return nil, fmt.Errorf("erreur lors de la récupération du contrat: %w", err)
	}

	contrat.TypeBien = models.TypeBien(typeBien)
	contrat.Statut = models.StatutContrat(statut)
	if dateFin.Valid {
		contrat.DateFin = &dateFin.Time
	}

	return contrat, nil
}

// GetByDevisID récupère un contrat par l'ID du devis
func (r *SQLiteContratRepository) GetByDevisID(ctx context.Context, devisID string) (*models.Contrat, error) {
	query := `
		SELECT id, devis_id, client_id, type_bien, prime, date_effet, date_fin, statut
		FROM contrats
		WHERE devis_id = ?
	`

	contrat := &models.Contrat{}
	var typeBien, statut string
	var dateFin sql.NullTime

	err := r.db.QueryRowContext(ctx, query, devisID).Scan(
		&contrat.ID,
		&contrat.DevisID,
		&contrat.ClientID,
		&typeBien,
		&contrat.Prime,
		&contrat.DateEffet,
		&dateFin,
		&statut,
	)

	if err == sql.ErrNoRows {
		return nil, nil
	}
	if err != nil {
		return nil, fmt.Errorf("erreur lors de la récupération du contrat: %w", err)
	}

	contrat.TypeBien = models.TypeBien(typeBien)
	contrat.Statut = models.StatutContrat(statut)
	if dateFin.Valid {
		contrat.DateFin = &dateFin.Time
	}

	return contrat, nil
}

// GetByClientID récupère tous les contrats d'un client
func (r *SQLiteContratRepository) GetByClientID(ctx context.Context, clientID string) ([]*models.Contrat, error) {
	query := `
		SELECT id, devis_id, client_id, type_bien, prime, date_effet, date_fin, statut
		FROM contrats
		WHERE client_id = ?
		ORDER BY date_effet DESC
	`

	rows, err := r.db.QueryContext(ctx, query, clientID)
	if err != nil {
		return nil, fmt.Errorf("erreur lors de la récupération des contrats: %w", err)
	}
	defer rows.Close()

	return r.scanContratList(rows)
}

// GetActive récupère tous les contrats actifs
func (r *SQLiteContratRepository) GetActive(ctx context.Context) ([]*models.Contrat, error) {
	query := `
		SELECT id, devis_id, client_id, type_bien, prime, date_effet, date_fin, statut
		FROM contrats
		WHERE statut = 'ACTIF'
		ORDER BY date_effet DESC
	`

	rows, err := r.db.QueryContext(ctx, query)
	if err != nil {
		return nil, fmt.Errorf("erreur lors de la récupération des contrats actifs: %w", err)
	}
	defer rows.Close()

	return r.scanContratList(rows)
}

// UpdateStatus met à jour le statut d'un contrat
func (r *SQLiteContratRepository) UpdateStatus(ctx context.Context, id string, statut models.StatutContrat) error {
	query := `UPDATE contrats SET statut = ? WHERE id = ?`

	result, err := r.db.ExecContext(ctx, query, string(statut), id)
	if err != nil {
		return fmt.Errorf("erreur lors de la mise à jour du statut: %w", err)
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("erreur lors de la vérification des lignes affectées: %w", err)
	}

	if rowsAffected == 0 {
		return fmt.Errorf("aucun contrat trouvé avec l'ID %s", id)
	}

	return nil
}

// Resilier résilie un contrat
func (r *SQLiteContratRepository) Resilier(ctx context.Context, id string, dateFin time.Time) error {
	query := `UPDATE contrats SET statut = 'RESILIE', date_fin = ? WHERE id = ?`

	result, err := r.db.ExecContext(ctx, query, dateFin, id)
	if err != nil {
		return fmt.Errorf("erreur lors de la résiliation: %w", err)
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("erreur lors de la vérification des lignes affectées: %w", err)
	}

	if rowsAffected == 0 {
		return fmt.Errorf("aucun contrat trouvé avec l'ID %s", id)
	}

	return nil
}

// List récupère tous les contrats avec pagination
func (r *SQLiteContratRepository) List(ctx context.Context, limit, offset int) ([]*models.Contrat, error) {
	query := `
		SELECT id, devis_id, client_id, type_bien, prime, date_effet, date_fin, statut
		FROM contrats
		ORDER BY date_effet DESC
		LIMIT ? OFFSET ?
	`

	rows, err := r.db.QueryContext(ctx, query, limit, offset)
	if err != nil {
		return nil, fmt.Errorf("erreur lors de la récupération des contrats: %w", err)
	}
	defer rows.Close()

	return r.scanContratList(rows)
}

// Count retourne le nombre total de contrats
func (r *SQLiteContratRepository) Count(ctx context.Context) (int, error) {
	query := `SELECT COUNT(*) FROM contrats`

	var count int
	err := r.db.QueryRowContext(ctx, query).Scan(&count)
	if err != nil {
		return 0, fmt.Errorf("erreur lors du comptage des contrats: %w", err)
	}

	return count, nil
}

// CountByStatus retourne le nombre de contrats par statut
func (r *SQLiteContratRepository) CountByStatus(ctx context.Context, statut models.StatutContrat) (int, error) {
	query := `SELECT COUNT(*) FROM contrats WHERE statut = ?`

	var count int
	err := r.db.QueryRowContext(ctx, query, string(statut)).Scan(&count)
	if err != nil {
		return 0, fmt.Errorf("erreur lors du comptage des contrats: %w", err)
	}

	return count, nil
}

// scanContratList est une fonction utilitaire pour scanner plusieurs contrats
func (r *SQLiteContratRepository) scanContratList(rows *sql.Rows) ([]*models.Contrat, error) {
	var contrats []*models.Contrat

	for rows.Next() {
		contrat := &models.Contrat{}
		var typeBien, statut string
		var dateFin sql.NullTime

		err := rows.Scan(
			&contrat.ID,
			&contrat.DevisID,
			&contrat.ClientID,
			&typeBien,
			&contrat.Prime,
			&contrat.DateEffet,
			&dateFin,
			&statut,
		)
		if err != nil {
			return nil, fmt.Errorf("erreur lors du scan du contrat: %w", err)
		}

		contrat.TypeBien = models.TypeBien(typeBien)
		contrat.Statut = models.StatutContrat(statut)
		if dateFin.Valid {
			contrat.DateFin = &dateFin.Time
		}

		contrats = append(contrats, contrat)
	}

	if err := rows.Err(); err != nil {
		return nil, fmt.Errorf("erreur lors de l'itération des résultats: %w", err)
	}

	return contrats, nil
}
