package models

import (
	"time"
)

// StatutContrat représente le statut d'un contrat
type StatutContrat string

const (
	StatutContratActif   StatutContrat = "ACTIF"
	StatutContratModifie StatutContrat = "MODIFIE"
	StatutContratResilie StatutContrat = "RESILIE"
)

// Contrat représente un contrat d'assurance
type Contrat struct {
	ID        string        `json:"id" db:"id"`
	DevisID   string        `json:"devisId" db:"devis_id"`
	ClientID  string        `json:"clientId" db:"client_id"`
	TypeBien  TypeBien      `json:"typeBien" db:"type_bien"`
	Prime     float64       `json:"prime" db:"prime"`
	DateEffet time.Time     `json:"dateEffet" db:"date_effet"`
	DateFin   *time.Time    `json:"dateFin,omitempty" db:"date_fin"`
	Statut    StatutContrat `json:"statut" db:"statut"`
}

// NewContrat crée un nouveau contrat à partir d'un devis
func NewContrat(id, devisID, clientID string, typeBien TypeBien, prime float64) *Contrat {
	return &Contrat{
		ID:        id,
		DevisID:   devisID,
		ClientID:  clientID,
		TypeBien:  typeBien,
		Prime:     prime,
		DateEffet: time.Now(),
		Statut:    StatutContratActif,
	}
}

// IsActive vérifie si le contrat est actif
func (c *Contrat) IsActive() bool {
	return c.Statut == StatutContratActif
}

// MotifResiliation représente les motifs de résiliation
type MotifResiliation string

const (
	MotifResiliationClient   MotifResiliation = "DEMANDE_CLIENT"
	MotifResiliationSinistre MotifResiliation = "SINISTRE_GRAVE"
	MotifResiliationNonPaiement MotifResiliation = "NON_PAIEMENT"
	MotifResiliationAutre    MotifResiliation = "AUTRE"
)
