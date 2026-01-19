package souscription

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"sync"
	"time"

	"github.com/agbru/kafka-eda-lab/internal/database"
	"github.com/agbru/kafka-eda-lab/internal/kafka"
	"github.com/agbru/kafka-eda-lab/internal/models"
	"github.com/google/uuid"
)

// Service gère la logique métier des contrats
type Service struct {
	repo     database.ContratRepository
	producer *kafka.Producer
	consumer *kafka.Consumer
	stopChan chan struct{}
	wg       sync.WaitGroup
	mu       sync.RWMutex
	running  bool
}

// NewService crée un nouveau service Souscription
func NewService(repo database.ContratRepository, producer *kafka.Producer, consumer *kafka.Consumer) *Service {
	return &Service{
		repo:     repo,
		producer: producer,
		consumer: consumer,
		stopChan: make(chan struct{}),
	}
}

// Start démarre le service et la consommation des événements
func (s *Service) Start(ctx context.Context) error {
	s.mu.Lock()
	if s.running {
		s.mu.Unlock()
		return fmt.Errorf("service déjà démarré")
	}
	s.running = true
	s.mu.Unlock()

	// Enregistrer le handler pour les événements DevisGenere
	s.consumer.RegisterHandler(models.TopicDevisGenere, s.handleDevisGenere)

	// Démarrer la consommation
	topics := []string{models.TopicDevisGenere}
	if err := s.consumer.Start(ctx, topics); err != nil {
		return fmt.Errorf("erreur lors du démarrage du consommateur: %w", err)
	}

	log.Println("[Souscription] Service démarré")
	return nil
}

// Stop arrête le service
func (s *Service) Stop() error {
	s.mu.Lock()
	if !s.running {
		s.mu.Unlock()
		return nil
	}
	s.running = false
	s.mu.Unlock()

	close(s.stopChan)
	s.wg.Wait()

	if err := s.consumer.Close(); err != nil {
		return fmt.Errorf("erreur lors de la fermeture du consommateur: %w", err)
	}

	log.Println("[Souscription] Service arrêté")
	return nil
}

// handleDevisGenere traite les événements DevisGenere
func (s *Service) handleDevisGenere(ctx context.Context, msg *kafka.ReceivedMessage) error {
	log.Printf("[Souscription] Événement DevisGenere reçu: partition=%d offset=%d",
		msg.Partition, msg.Offset)

	// Parser l'événement
	var event struct {
		ID        string `json:"id"`
		Type      string `json:"type"`
		Source    string `json:"source"`
		Timestamp string `json:"timestamp"`
		Data      models.DevisGenere `json:"data"`
	}

	if err := json.Unmarshal(msg.Value, &event); err != nil {
		log.Printf("[Souscription] Erreur de parsing: %v", err)
		return err
	}

	data := event.Data

	// Simuler un délai de traitement (conversion automatique pour la démo)
	// Dans un vrai système, il y aurait une validation manuelle
	log.Printf("[Souscription] Traitement du devis %s pour client %s",
		data.DevisID, data.ClientID)

	// Auto-conversion pour la simulation (70% de chances)
	// Dans un vrai système, ce serait un processus manuel
	if shouldAutoConvert() {
		_, err := s.CreateContratFromDevis(ctx, data.DevisID, data.ClientID,
			models.TypeBien(data.TypeBien), data.Prime)
		if err != nil {
			log.Printf("[Souscription] Erreur lors de la création du contrat: %v", err)
			return err
		}
	} else {
		log.Printf("[Souscription] Devis %s non converti automatiquement", data.DevisID)
	}

	return nil
}

// shouldAutoConvert simule une décision de conversion (70% de chances)
func shouldAutoConvert() bool {
	return time.Now().UnixNano()%10 < 7
}

// CreateContratFromDevis crée un contrat à partir d'un devis
func (s *Service) CreateContratFromDevis(ctx context.Context, devisID, clientID string, typeBien models.TypeBien, prime float64) (*models.Contrat, error) {
	// Vérifier si un contrat existe déjà pour ce devis
	existing, err := s.repo.GetByDevisID(ctx, devisID)
	if err != nil {
		return nil, fmt.Errorf("erreur lors de la vérification du contrat existant: %w", err)
	}
	if existing != nil {
		return nil, fmt.Errorf("un contrat existe déjà pour le devis %s", devisID)
	}

	// Générer un ID unique pour le contrat
	contratID := fmt.Sprintf("CTR-%s", uuid.New().String()[:8])

	// Créer le contrat
	contrat := models.NewContrat(contratID, devisID, clientID, typeBien, prime)

	// Persister en base
	if err := s.repo.Create(ctx, contrat); err != nil {
		return nil, fmt.Errorf("erreur lors de la création du contrat: %w", err)
	}

	// Publier l'événement ContratEmis
	event := models.ContratEmis{
		ContratID: contrat.ID,
		DevisID:   contrat.DevisID,
		ClientID:  contrat.ClientID,
		TypeBien:  string(contrat.TypeBien),
		Prime:     contrat.Prime,
		DateEffet: contrat.DateEffet,
		Timestamp: time.Now(),
	}

	if err := s.producer.SendEvent(ctx, models.TopicContratEmis, "ContratEmis", "souscription", event); err != nil {
		log.Printf("[Souscription] Erreur lors de la publication de l'événement: %v", err)
	}

	log.Printf("[Souscription] Contrat créé: %s pour devis %s", contrat.ID, devisID)

	return contrat, nil
}

// GetContrat récupère un contrat par son ID
func (s *Service) GetContrat(ctx context.Context, id string) (*models.Contrat, error) {
	return s.repo.GetByID(ctx, id)
}

// GetContratsByClient récupère tous les contrats d'un client
func (s *Service) GetContratsByClient(ctx context.Context, clientID string) ([]*models.Contrat, error) {
	return s.repo.GetByClientID(ctx, clientID)
}

// ListContrats récupère tous les contrats avec pagination
func (s *Service) ListContrats(ctx context.Context, limit, offset int) ([]*models.Contrat, error) {
	return s.repo.List(ctx, limit, offset)
}

// ModifierContrat modifie un contrat existant
func (s *Service) ModifierContrat(ctx context.Context, contratID string, modification string, nouvelleValeur interface{}) error {
	// Récupérer le contrat
	contrat, err := s.repo.GetByID(ctx, contratID)
	if err != nil {
		return fmt.Errorf("erreur lors de la récupération du contrat: %w", err)
	}

	if contrat == nil {
		return fmt.Errorf("contrat non trouvé: %s", contratID)
	}

	if !contrat.IsActive() {
		return fmt.Errorf("le contrat %s n'est pas actif", contratID)
	}

	// Mettre à jour le statut
	if err := s.repo.UpdateStatus(ctx, contratID, models.StatutContratModifie); err != nil {
		return fmt.Errorf("erreur lors de la mise à jour du statut: %w", err)
	}

	// Publier l'événement ContratModifie
	event := models.ContratModifie{
		ContratID:      contratID,
		Modification:   modification,
		NouvelleValeur: nouvelleValeur,
		Timestamp:      time.Now(),
	}

	if err := s.producer.SendEvent(ctx, models.TopicContratModifie, "ContratModifie", "souscription", event); err != nil {
		log.Printf("[Souscription] Erreur lors de la publication de l'événement: %v", err)
	}

	log.Printf("[Souscription] Contrat modifié: %s (%s)", contratID, modification)

	return nil
}

// ResilierContrat résilie un contrat
func (s *Service) ResilierContrat(ctx context.Context, contratID string, motif string) error {
	// Récupérer le contrat
	contrat, err := s.repo.GetByID(ctx, contratID)
	if err != nil {
		return fmt.Errorf("erreur lors de la récupération du contrat: %w", err)
	}

	if contrat == nil {
		return fmt.Errorf("contrat non trouvé: %s", contratID)
	}

	if contrat.Statut == models.StatutContratResilie {
		return fmt.Errorf("le contrat %s est déjà résilié", contratID)
	}

	// Résilier le contrat
	dateResiliation := time.Now()
	if err := s.repo.Resilier(ctx, contratID, dateResiliation); err != nil {
		return fmt.Errorf("erreur lors de la résiliation: %w", err)
	}

	// Publier l'événement ContratResilie
	event := models.ContratResilie{
		ContratID:       contratID,
		Motif:           motif,
		DateResiliation: dateResiliation,
		Timestamp:       time.Now(),
	}

	if err := s.producer.SendEvent(ctx, models.TopicContratResilie, "ContratResilie", "souscription", event); err != nil {
		log.Printf("[Souscription] Erreur lors de la publication de l'événement: %v", err)
	}

	log.Printf("[Souscription] Contrat résilié: %s (motif: %s)", contratID, motif)

	return nil
}

// GetStats retourne les statistiques des contrats
func (s *Service) GetStats(ctx context.Context) (*Stats, error) {
	total, err := s.repo.Count(ctx)
	if err != nil {
		return nil, err
	}

	actifs, err := s.repo.CountByStatus(ctx, models.StatutContratActif)
	if err != nil {
		return nil, err
	}

	modifies, err := s.repo.CountByStatus(ctx, models.StatutContratModifie)
	if err != nil {
		return nil, err
	}

	resilies, err := s.repo.CountByStatus(ctx, models.StatutContratResilie)
	if err != nil {
		return nil, err
	}

	return &Stats{
		Total:    total,
		Actifs:   actifs,
		Modifies: modifies,
		Resilies: resilies,
	}, nil
}

// Stats contient les statistiques des contrats
type Stats struct {
	Total    int `json:"total"`
	Actifs   int `json:"actifs"`
	Modifies int `json:"modifies"`
	Resilies int `json:"resilies"`
}
