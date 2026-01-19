package database

import (
	"context"
	"database/sql"
	"fmt"
	"time"

	"github.com/agbru/kafka-eda-lab/internal/models"
)

// SinistreRepository définit l'interface pour la gestion des sinistres
type SinistreRepository interface {
	// Create crée un nouveau sinistre
	Create(ctx context.Context, sinistre *models.Sinistre) error

	// GetByID récupère un sinistre par son ID
	GetByID(ctx context.Context, id string) (*models.Sinistre, error)

	// GetByContratID récupère tous les sinistres d'un contrat
	GetByContratID(ctx context.Context, contratID string) ([]*models.Sinistre, error)

	// GetPending récupère les sinistres en attente d'évaluation
	GetPending(ctx context.Context) ([]*models.Sinistre, error)

	// GetEvaluated récupère les sinistres évalués en attente de paiement
	GetEvaluated(ctx context.Context) ([]*models.Sinistre, error)

	// UpdateStatus met à jour le statut d'un sinistre
	UpdateStatus(ctx context.Context, id string, statut models.StatutSinistre) error

	// Evaluer marque un sinistre comme évalué
	Evaluer(ctx context.Context, id string, montantEvalue float64) error

	// Indemniser marque un sinistre comme indemnisé
	Indemniser(ctx context.Context, id string, montantIndemnise float64) error

	// List récupère tous les sinistres avec pagination
	List(ctx context.Context, limit, offset int) ([]*models.Sinistre, error)

	// Count retourne le nombre total de sinistres
	Count(ctx context.Context) (int, error)

	// CountByStatus retourne le nombre de sinistres par statut
	CountByStatus(ctx context.Context, statut models.StatutSinistre) (int, error)

	// SumIndemnisations retourne le montant total des indemnisations
	SumIndemnisations(ctx context.Context) (float64, error)
}

// SQLiteSinistreRepository implémente SinistreRepository avec SQLite
type SQLiteSinistreRepository struct {
	db *DB
}

// NewSinistreRepository crée un nouveau repository pour les sinistres
func NewSinistreRepository(db *DB) SinistreRepository {
	return &SQLiteSinistreRepository{db: db}
}

// Create crée un nouveau sinistre
func (r *SQLiteSinistreRepository) Create(ctx context.Context, sinistre *models.Sinistre) error {
	query := `
		INSERT INTO sinistres (id, contrat_id, type_sinistre, description, montant_estime,
			date_survenance, date_declaration, statut)
		VALUES (?, ?, ?, ?, ?, ?, ?, ?)
	`

	_, err := r.db.ExecContext(ctx, query,
		sinistre.ID,
		sinistre.ContratID,
		string(sinistre.TypeSinistre),
		sinistre.Description,
		sinistre.MontantEstime,
		sinistre.DateSurvenance,
		sinistre.DateDeclaration,
		string(sinistre.Statut),
	)

	if err != nil {
		return fmt.Errorf("erreur lors de la création du sinistre: %w", err)
	}

	return nil
}

// GetByID récupère un sinistre par son ID
func (r *SQLiteSinistreRepository) GetByID(ctx context.Context, id string) (*models.Sinistre, error) {
	query := `
		SELECT id, contrat_id, type_sinistre, description, montant_estime, montant_evalue,
			montant_indemnise, date_survenance, date_declaration, date_evaluation, date_paiement, statut
		FROM sinistres
		WHERE id = ?
	`

	sinistre := &models.Sinistre{}
	var typeSinistre, statut string
	var montantEvalue, montantIndemnise sql.NullFloat64
	var dateEvaluation, datePaiement sql.NullTime

	err := r.db.QueryRowContext(ctx, query, id).Scan(
		&sinistre.ID,
		&sinistre.ContratID,
		&typeSinistre,
		&sinistre.Description,
		&sinistre.MontantEstime,
		&montantEvalue,
		&montantIndemnise,
		&sinistre.DateSurvenance,
		&sinistre.DateDeclaration,
		&dateEvaluation,
		&datePaiement,
		&statut,
	)

	if err == sql.ErrNoRows {
		return nil, nil
	}
	if err != nil {
		return nil, fmt.Errorf("erreur lors de la récupération du sinistre: %w", err)
	}

	sinistre.TypeSinistre = models.TypeSinistre(typeSinistre)
	sinistre.Statut = models.StatutSinistre(statut)

	if montantEvalue.Valid {
		sinistre.MontantEvalue = &montantEvalue.Float64
	}
	if montantIndemnise.Valid {
		sinistre.MontantIndemnise = &montantIndemnise.Float64
	}
	if dateEvaluation.Valid {
		sinistre.DateEvaluation = &dateEvaluation.Time
	}
	if datePaiement.Valid {
		sinistre.DatePaiement = &datePaiement.Time
	}

	return sinistre, nil
}

// GetByContratID récupère tous les sinistres d'un contrat
func (r *SQLiteSinistreRepository) GetByContratID(ctx context.Context, contratID string) ([]*models.Sinistre, error) {
	query := `
		SELECT id, contrat_id, type_sinistre, description, montant_estime, montant_evalue,
			montant_indemnise, date_survenance, date_declaration, date_evaluation, date_paiement, statut
		FROM sinistres
		WHERE contrat_id = ?
		ORDER BY date_declaration DESC
	`

	rows, err := r.db.QueryContext(ctx, query, contratID)
	if err != nil {
		return nil, fmt.Errorf("erreur lors de la récupération des sinistres: %w", err)
	}
	defer rows.Close()

	return r.scanSinistreList(rows)
}

// GetPending récupère les sinistres en attente d'évaluation
func (r *SQLiteSinistreRepository) GetPending(ctx context.Context) ([]*models.Sinistre, error) {
	query := `
		SELECT id, contrat_id, type_sinistre, description, montant_estime, montant_evalue,
			montant_indemnise, date_survenance, date_declaration, date_evaluation, date_paiement, statut
		FROM sinistres
		WHERE statut = 'DECLARE'
		ORDER BY date_declaration ASC
	`

	rows, err := r.db.QueryContext(ctx, query)
	if err != nil {
		return nil, fmt.Errorf("erreur lors de la récupération des sinistres en attente: %w", err)
	}
	defer rows.Close()

	return r.scanSinistreList(rows)
}

// GetEvaluated récupère les sinistres évalués en attente de paiement
func (r *SQLiteSinistreRepository) GetEvaluated(ctx context.Context) ([]*models.Sinistre, error) {
	query := `
		SELECT id, contrat_id, type_sinistre, description, montant_estime, montant_evalue,
			montant_indemnise, date_survenance, date_declaration, date_evaluation, date_paiement, statut
		FROM sinistres
		WHERE statut = 'EVALUE'
		ORDER BY date_evaluation ASC
	`

	rows, err := r.db.QueryContext(ctx, query)
	if err != nil {
		return nil, fmt.Errorf("erreur lors de la récupération des sinistres évalués: %w", err)
	}
	defer rows.Close()

	return r.scanSinistreList(rows)
}

// UpdateStatus met à jour le statut d'un sinistre
func (r *SQLiteSinistreRepository) UpdateStatus(ctx context.Context, id string, statut models.StatutSinistre) error {
	query := `UPDATE sinistres SET statut = ? WHERE id = ?`

	result, err := r.db.ExecContext(ctx, query, string(statut), id)
	if err != nil {
		return fmt.Errorf("erreur lors de la mise à jour du statut: %w", err)
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("erreur lors de la vérification des lignes affectées: %w", err)
	}

	if rowsAffected == 0 {
		return fmt.Errorf("aucun sinistre trouvé avec l'ID %s", id)
	}

	return nil
}

// Evaluer marque un sinistre comme évalué
func (r *SQLiteSinistreRepository) Evaluer(ctx context.Context, id string, montantEvalue float64) error {
	query := `UPDATE sinistres SET statut = 'EVALUE', montant_evalue = ?, date_evaluation = ? WHERE id = ?`

	result, err := r.db.ExecContext(ctx, query, montantEvalue, time.Now(), id)
	if err != nil {
		return fmt.Errorf("erreur lors de l'évaluation: %w", err)
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("erreur lors de la vérification des lignes affectées: %w", err)
	}

	if rowsAffected == 0 {
		return fmt.Errorf("aucun sinistre trouvé avec l'ID %s", id)
	}

	return nil
}

// Indemniser marque un sinistre comme indemnisé
func (r *SQLiteSinistreRepository) Indemniser(ctx context.Context, id string, montantIndemnise float64) error {
	query := `UPDATE sinistres SET statut = 'INDEMNISE', montant_indemnise = ?, date_paiement = ? WHERE id = ?`

	result, err := r.db.ExecContext(ctx, query, montantIndemnise, time.Now(), id)
	if err != nil {
		return fmt.Errorf("erreur lors de l'indemnisation: %w", err)
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("erreur lors de la vérification des lignes affectées: %w", err)
	}

	if rowsAffected == 0 {
		return fmt.Errorf("aucun sinistre trouvé avec l'ID %s", id)
	}

	return nil
}

// List récupère tous les sinistres avec pagination
func (r *SQLiteSinistreRepository) List(ctx context.Context, limit, offset int) ([]*models.Sinistre, error) {
	query := `
		SELECT id, contrat_id, type_sinistre, description, montant_estime, montant_evalue,
			montant_indemnise, date_survenance, date_declaration, date_evaluation, date_paiement, statut
		FROM sinistres
		ORDER BY date_declaration DESC
		LIMIT ? OFFSET ?
	`

	rows, err := r.db.QueryContext(ctx, query, limit, offset)
	if err != nil {
		return nil, fmt.Errorf("erreur lors de la récupération des sinistres: %w", err)
	}
	defer rows.Close()

	return r.scanSinistreList(rows)
}

// Count retourne le nombre total de sinistres
func (r *SQLiteSinistreRepository) Count(ctx context.Context) (int, error) {
	query := `SELECT COUNT(*) FROM sinistres`

	var count int
	err := r.db.QueryRowContext(ctx, query).Scan(&count)
	if err != nil {
		return 0, fmt.Errorf("erreur lors du comptage des sinistres: %w", err)
	}

	return count, nil
}

// CountByStatus retourne le nombre de sinistres par statut
func (r *SQLiteSinistreRepository) CountByStatus(ctx context.Context, statut models.StatutSinistre) (int, error) {
	query := `SELECT COUNT(*) FROM sinistres WHERE statut = ?`

	var count int
	err := r.db.QueryRowContext(ctx, query, string(statut)).Scan(&count)
	if err != nil {
		return 0, fmt.Errorf("erreur lors du comptage des sinistres: %w", err)
	}

	return count, nil
}

// SumIndemnisations retourne le montant total des indemnisations
func (r *SQLiteSinistreRepository) SumIndemnisations(ctx context.Context) (float64, error) {
	query := `SELECT COALESCE(SUM(montant_indemnise), 0) FROM sinistres WHERE statut = 'INDEMNISE'`

	var sum float64
	err := r.db.QueryRowContext(ctx, query).Scan(&sum)
	if err != nil {
		return 0, fmt.Errorf("erreur lors du calcul des indemnisations: %w", err)
	}

	return sum, nil
}

// scanSinistreList est une fonction utilitaire pour scanner plusieurs sinistres
func (r *SQLiteSinistreRepository) scanSinistreList(rows *sql.Rows) ([]*models.Sinistre, error) {
	var sinistres []*models.Sinistre

	for rows.Next() {
		sinistre := &models.Sinistre{}
		var typeSinistre, statut string
		var montantEvalue, montantIndemnise sql.NullFloat64
		var dateEvaluation, datePaiement sql.NullTime

		err := rows.Scan(
			&sinistre.ID,
			&sinistre.ContratID,
			&typeSinistre,
			&sinistre.Description,
			&sinistre.MontantEstime,
			&montantEvalue,
			&montantIndemnise,
			&sinistre.DateSurvenance,
			&sinistre.DateDeclaration,
			&dateEvaluation,
			&datePaiement,
			&statut,
		)
		if err != nil {
			return nil, fmt.Errorf("erreur lors du scan du sinistre: %w", err)
		}

		sinistre.TypeSinistre = models.TypeSinistre(typeSinistre)
		sinistre.Statut = models.StatutSinistre(statut)

		if montantEvalue.Valid {
			sinistre.MontantEvalue = &montantEvalue.Float64
		}
		if montantIndemnise.Valid {
			sinistre.MontantIndemnise = &montantIndemnise.Float64
		}
		if dateEvaluation.Valid {
			sinistre.DateEvaluation = &dateEvaluation.Time
		}
		if datePaiement.Valid {
			sinistre.DatePaiement = &datePaiement.Time
		}

		sinistres = append(sinistres, sinistre)
	}

	if err := rows.Err(); err != nil {
		return nil, fmt.Errorf("erreur lors de l'itération des résultats: %w", err)
	}

	return sinistres, nil
}
