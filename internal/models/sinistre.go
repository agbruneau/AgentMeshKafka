package models

import (
	"time"
)

// StatutSinistre représente le statut d'un sinistre
type StatutSinistre string

const (
	StatutSinistreDeclare   StatutSinistre = "DECLARE"
	StatutSinistreEvalue    StatutSinistre = "EVALUE"
	StatutSinistreIndemnise StatutSinistre = "INDEMNISE"
	StatutSinistreRejete    StatutSinistre = "REJETE"
)

// TypeSinistre représente le type de sinistre
type TypeSinistre string

const (
	TypeSinistreVol        TypeSinistre = "VOL"
	TypeSinistreIncendie   TypeSinistre = "INCENDIE"
	TypeSinistreDegatsEaux TypeSinistre = "DEGATS_EAUX"
	TypeSinistreAccident   TypeSinistre = "ACCIDENT"
	TypeSinistreAutre      TypeSinistre = "AUTRE"
)

// Sinistre représente un sinistre déclaré
type Sinistre struct {
	ID               string         `json:"id" db:"id"`
	ContratID        string         `json:"contratId" db:"contrat_id"`
	TypeSinistre     TypeSinistre   `json:"typeSinistre" db:"type_sinistre"`
	Description      string         `json:"description" db:"description"`
	MontantEstime    float64        `json:"montantEstime" db:"montant_estime"`
	MontantEvalue    *float64       `json:"montantEvalue,omitempty" db:"montant_evalue"`
	MontantIndemnise *float64       `json:"montantIndemnise,omitempty" db:"montant_indemnise"`
	DateSurvenance   time.Time      `json:"dateSurvenance" db:"date_survenance"`
	DateDeclaration  time.Time      `json:"dateDeclaration" db:"date_declaration"`
	DateEvaluation   *time.Time     `json:"dateEvaluation,omitempty" db:"date_evaluation"`
	DatePaiement     *time.Time     `json:"datePaiement,omitempty" db:"date_paiement"`
	Statut           StatutSinistre `json:"statut" db:"statut"`
}

// NewSinistre crée un nouveau sinistre
func NewSinistre(id, contratID string, typeSinistre TypeSinistre, description string, montantEstime float64, dateSurvenance time.Time) *Sinistre {
	return &Sinistre{
		ID:              id,
		ContratID:       contratID,
		TypeSinistre:    typeSinistre,
		Description:     description,
		MontantEstime:   montantEstime,
		DateSurvenance:  dateSurvenance,
		DateDeclaration: time.Now(),
		Statut:          StatutSinistreDeclare,
	}
}

// IsTerminated vérifie si le sinistre est terminé
func (s *Sinistre) IsTerminated() bool {
	return s.Statut == StatutSinistreIndemnise || s.Statut == StatutSinistreRejete
}
