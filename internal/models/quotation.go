package models

import (
	"time"
)

// TypeBien représente le type de bien assuré
type TypeBien string

const (
	TypeBienAuto       TypeBien = "AUTO"
	TypeBienHabitation TypeBien = "HABITATION"
	TypeBienAutre      TypeBien = "AUTRE"
)

// StatutDevis représente le statut d'un devis
type StatutDevis string

const (
	StatutDevisGenere  StatutDevis = "GENERE"
	StatutDevisConverti StatutDevis = "CONVERTI"
	StatutDevisExpire  StatutDevis = "EXPIRE"
)

// Devis représente un devis d'assurance
type Devis struct {
	ID             string      `json:"id" db:"id"`
	ClientID       string      `json:"clientId" db:"client_id"`
	TypeBien       TypeBien    `json:"typeBien" db:"type_bien"`
	Valeur         float64     `json:"valeur" db:"valeur"`
	Prime          float64     `json:"prime" db:"prime"`
	DateCreation   time.Time   `json:"dateCreation" db:"date_creation"`
	DateExpiration time.Time   `json:"dateExpiration" db:"date_expiration"`
	Statut         StatutDevis `json:"statut" db:"statut"`
}

// NewDevis crée un nouveau devis avec les valeurs par défaut
func NewDevis(id, clientID string, typeBien TypeBien, valeur, prime float64) *Devis {
	now := time.Now()
	return &Devis{
		ID:             id,
		ClientID:       clientID,
		TypeBien:       typeBien,
		Valeur:         valeur,
		Prime:          prime,
		DateCreation:   now,
		DateExpiration: now.AddDate(0, 0, 30), // Expire dans 30 jours
		Statut:         StatutDevisGenere,
	}
}

// IsExpired vérifie si le devis est expiré
func (d *Devis) IsExpired() bool {
	return time.Now().After(d.DateExpiration) && d.Statut == StatutDevisGenere
}

// CalculerPrime calcule la prime en fonction du type de bien et de la valeur
func CalculerPrime(typeBien TypeBien, valeur float64) float64 {
	var taux float64
	switch typeBien {
	case TypeBienAuto:
		taux = 0.02 // 2% pour auto
	case TypeBienHabitation:
		taux = 0.015 // 1.5% pour habitation
	default:
		taux = 0.025 // 2.5% pour autre
	}
	return valeur * taux
}
