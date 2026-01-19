package quotation

import (
	"context"
	"fmt"
	"log"
	"sync"
	"time"

	"github.com/agbru/kafka-eda-lab/internal/database"
	"github.com/agbru/kafka-eda-lab/internal/kafka"
	"github.com/agbru/kafka-eda-lab/internal/models"
	"github.com/google/uuid"
)

// Service gère la logique métier des devis
type Service struct {
	repo           database.QuotationRepository
	producer       *kafka.Producer
	expiryInterval time.Duration
	stopChan       chan struct{}
	wg             sync.WaitGroup
	mu             sync.RWMutex
	running        bool
}

// NewService crée un nouveau service Quotation
func NewService(repo database.QuotationRepository, producer *kafka.Producer) *Service {
	return &Service{
		repo:           repo,
		producer:       producer,
		expiryInterval: 1 * time.Minute, // Vérifier les expirations chaque minute
		stopChan:       make(chan struct{}),
	}
}

// Start démarre le service (incluant la vérification des expirations)
func (s *Service) Start(ctx context.Context) error {
	s.mu.Lock()
	if s.running {
		s.mu.Unlock()
		return fmt.Errorf("service déjà démarré")
	}
	s.running = true
	s.mu.Unlock()

	// Démarrer la goroutine de vérification des expirations
	s.wg.Add(1)
	go s.checkExpirations(ctx)

	log.Println("[Quotation] Service démarré")
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

	log.Println("[Quotation] Service arrêté")
	return nil
}

// CreateDevis crée un nouveau devis et publie l'événement
func (s *Service) CreateDevis(ctx context.Context, clientID string, typeBien models.TypeBien, valeur float64) (*models.Devis, error) {
	// Générer un ID unique
	devisID := fmt.Sprintf("DEV-%s", uuid.New().String()[:8])

	// Calculer la prime
	prime := models.CalculerPrime(typeBien, valeur)

	// Créer le devis
	devis := models.NewDevis(devisID, clientID, typeBien, valeur, prime)

	// Persister en base
	if err := s.repo.Create(ctx, devis); err != nil {
		return nil, fmt.Errorf("erreur lors de la création du devis: %w", err)
	}

	// Publier l'événement DevisGenere
	event := models.DevisGenere{
		DevisID:   devis.ID,
		ClientID:  devis.ClientID,
		TypeBien:  string(devis.TypeBien),
		Valeur:    devis.Valeur,
		Prime:     devis.Prime,
		Timestamp: time.Now(),
	}

	if err := s.producer.SendEvent(ctx, models.TopicDevisGenere, "DevisGenere", "quotation", event); err != nil {
		log.Printf("[Quotation] Erreur lors de la publication de l'événement: %v", err)
		// Ne pas échouer la création du devis si Kafka échoue
	}

	log.Printf("[Quotation] Devis créé: %s pour client %s (type=%s, valeur=%.2f, prime=%.2f)",
		devis.ID, devis.ClientID, devis.TypeBien, devis.Valeur, devis.Prime)

	return devis, nil
}

// GetDevis récupère un devis par son ID
func (s *Service) GetDevis(ctx context.Context, id string) (*models.Devis, error) {
	return s.repo.GetByID(ctx, id)
}

// GetDevisByClient récupère tous les devis d'un client
func (s *Service) GetDevisByClient(ctx context.Context, clientID string) ([]*models.Devis, error) {
	return s.repo.GetByClientID(ctx, clientID)
}

// ListDevis récupère tous les devis avec pagination
func (s *Service) ListDevis(ctx context.Context, limit, offset int) ([]*models.Devis, error) {
	return s.repo.List(ctx, limit, offset)
}

// ConvertDevis convertit un devis en contrat
func (s *Service) ConvertDevis(ctx context.Context, devisID string) error {
	// Récupérer le devis
	devis, err := s.repo.GetByID(ctx, devisID)
	if err != nil {
		return fmt.Errorf("erreur lors de la récupération du devis: %w", err)
	}

	if devis == nil {
		return fmt.Errorf("devis non trouvé: %s", devisID)
	}

	// Vérifier que le devis n'est pas expiré
	if devis.IsExpired() {
		return fmt.Errorf("le devis %s est expiré", devisID)
	}

	// Vérifier que le devis n'est pas déjà converti
	if devis.Statut != models.StatutDevisGenere {
		return fmt.Errorf("le devis %s n'est pas dans un état convertible (statut=%s)", devisID, devis.Statut)
	}

	// Mettre à jour le statut
	if err := s.repo.UpdateStatus(ctx, devisID, models.StatutDevisConverti); err != nil {
		return fmt.Errorf("erreur lors de la mise à jour du statut: %w", err)
	}

	log.Printf("[Quotation] Devis converti: %s", devisID)

	return nil
}

// GetStats retourne les statistiques des devis
func (s *Service) GetStats(ctx context.Context) (*Stats, error) {
	total, err := s.repo.Count(ctx)
	if err != nil {
		return nil, err
	}

	generes, err := s.repo.CountByStatus(ctx, models.StatutDevisGenere)
	if err != nil {
		return nil, err
	}

	convertis, err := s.repo.CountByStatus(ctx, models.StatutDevisConverti)
	if err != nil {
		return nil, err
	}

	expires, err := s.repo.CountByStatus(ctx, models.StatutDevisExpire)
	if err != nil {
		return nil, err
	}

	return &Stats{
		Total:      total,
		Generes:    generes,
		Convertis:  convertis,
		Expires:    expires,
		TauxConversion: calculateConversionRate(convertis, total-generes),
	}, nil
}

// Stats contient les statistiques des devis
type Stats struct {
	Total          int     `json:"total"`
	Generes        int     `json:"generes"`
	Convertis      int     `json:"convertis"`
	Expires        int     `json:"expires"`
	TauxConversion float64 `json:"tauxConversion"`
}

// calculateConversionRate calcule le taux de conversion
func calculateConversionRate(convertis, traites int) float64 {
	if traites == 0 {
		return 0
	}
	return float64(convertis) / float64(traites) * 100
}

// checkExpirations vérifie et marque les devis expirés
func (s *Service) checkExpirations(ctx context.Context) {
	defer s.wg.Done()

	ticker := time.NewTicker(s.expiryInterval)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return
		case <-s.stopChan:
			return
		case <-ticker.C:
			s.processExpirations(ctx)
		}
	}
}

// processExpirations traite les devis expirés
func (s *Service) processExpirations(ctx context.Context) {
	expiredDevis, err := s.repo.GetExpired(ctx)
	if err != nil {
		log.Printf("[Quotation] Erreur lors de la récupération des devis expirés: %v", err)
		return
	}

	for _, devis := range expiredDevis {
		// Mettre à jour le statut
		if err := s.repo.UpdateStatus(ctx, devis.ID, models.StatutDevisExpire); err != nil {
			log.Printf("[Quotation] Erreur lors de la mise à jour du statut expiré: %v", err)
			continue
		}

		// Publier l'événement DevisExpire
		event := models.DevisExpire{
			DevisID:        devis.ID,
			DateExpiration: devis.DateExpiration,
			Timestamp:      time.Now(),
		}

		if err := s.producer.SendEvent(ctx, models.TopicDevisExpire, "DevisExpire", "quotation", event); err != nil {
			log.Printf("[Quotation] Erreur lors de la publication de l'événement expiration: %v", err)
		}

		log.Printf("[Quotation] Devis expiré: %s", devis.ID)
	}

	if len(expiredDevis) > 0 {
		log.Printf("[Quotation] %d devis marqués comme expirés", len(expiredDevis))
	}
}
