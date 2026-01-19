package models

import (
	"time"
)

// =============================================================================
// Événements Quotation
// =============================================================================

// DevisGenere est émis quand un nouveau devis est créé
type DevisGenere struct {
	DevisID   string    `json:"devisId" avro:"devisId"`
	ClientID  string    `json:"clientId" avro:"clientId"`
	TypeBien  string    `json:"typeBien" avro:"typeBien"`
	Valeur    float64   `json:"valeur" avro:"valeur"`
	Prime     float64   `json:"prime" avro:"prime"`
	Timestamp time.Time `json:"timestamp" avro:"timestamp"`
}

// DevisExpire est émis quand un devis expire sans être converti
type DevisExpire struct {
	DevisID        string    `json:"devisId" avro:"devisId"`
	DateExpiration time.Time `json:"dateExpiration" avro:"dateExpiration"`
	Timestamp      time.Time `json:"timestamp" avro:"timestamp"`
}

// =============================================================================
// Événements Souscription
// =============================================================================

// ContratEmis est émis quand un nouveau contrat est créé
type ContratEmis struct {
	ContratID string    `json:"contratId" avro:"contratId"`
	DevisID   string    `json:"devisId" avro:"devisId"`
	ClientID  string    `json:"clientId" avro:"clientId"`
	TypeBien  string    `json:"typeBien" avro:"typeBien"`
	Prime     float64   `json:"prime" avro:"prime"`
	DateEffet time.Time `json:"dateEffet" avro:"dateEffet"`
	Timestamp time.Time `json:"timestamp" avro:"timestamp"`
}

// ContratModifie est émis quand un contrat est modifié (avenant)
type ContratModifie struct {
	ContratID      string      `json:"contratId" avro:"contratId"`
	Modification   string      `json:"modification" avro:"modification"`
	NouvelleValeur interface{} `json:"nouvelleValeur" avro:"nouvelleValeur"`
	Timestamp      time.Time   `json:"timestamp" avro:"timestamp"`
}

// ContratResilie est émis quand un contrat est résilié
type ContratResilie struct {
	ContratID       string    `json:"contratId" avro:"contratId"`
	Motif           string    `json:"motif" avro:"motif"`
	DateResiliation time.Time `json:"dateResiliation" avro:"dateResiliation"`
	Timestamp       time.Time `json:"timestamp" avro:"timestamp"`
}

// =============================================================================
// Événements Réclamation
// =============================================================================

// SinistreDeclare est émis quand un sinistre est déclaré
type SinistreDeclare struct {
	SinistreID     string    `json:"sinistreId" avro:"sinistreId"`
	ContratID      string    `json:"contratId" avro:"contratId"`
	TypeSinistre   string    `json:"typeSinistre" avro:"typeSinistre"`
	Description    string    `json:"description" avro:"description"`
	MontantEstime  float64   `json:"montantEstime" avro:"montantEstime"`
	DateSurvenance time.Time `json:"dateSurvenance" avro:"dateSurvenance"`
	Timestamp      time.Time `json:"timestamp" avro:"timestamp"`
}

// SinistreEvalue est émis quand l'expertise d'un sinistre est terminée
type SinistreEvalue struct {
	SinistreID    string    `json:"sinistreId" avro:"sinistreId"`
	MontantEvalue float64   `json:"montantEvalue" avro:"montantEvalue"`
	Timestamp     time.Time `json:"timestamp" avro:"timestamp"`
}

// IndemnisationEffectuee est émis quand le paiement est effectué
type IndemnisationEffectuee struct {
	SinistreID      string    `json:"sinistreId" avro:"sinistreId"`
	ContratID       string    `json:"contratId" avro:"contratId"`
	MontantIndemnise float64   `json:"montantIndemnise" avro:"montantIndemnise"`
	DatePaiement    time.Time `json:"datePaiement" avro:"datePaiement"`
	Timestamp       time.Time `json:"timestamp" avro:"timestamp"`
}

// =============================================================================
// Enveloppe d'événement générique
// =============================================================================

// Event représente un événement générique avec ses métadonnées
type Event struct {
	ID        string      `json:"id"`
	Type      string      `json:"type"`
	Source    string      `json:"source"`
	Timestamp time.Time   `json:"timestamp"`
	Data      interface{} `json:"data"`
}

// Topics Kafka
const (
	TopicDevisGenere            = "quotation.devis-genere"
	TopicDevisExpire            = "quotation.devis-expire"
	TopicContratEmis            = "souscription.contrat-emis"
	TopicContratModifie         = "souscription.contrat-modifie"
	TopicContratResilie         = "souscription.contrat-resilie"
	TopicSinistreDeclare        = "reclamation.sinistre-declare"
	TopicSinistreEvalue         = "reclamation.sinistre-evalue"
	TopicIndemnisationEffectuee = "reclamation.indemnisation-effectuee"
	TopicDLQErrors              = "dlq.errors"
)
