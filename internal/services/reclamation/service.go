package reclamation

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

// Service gère la logique métier des sinistres
type Service struct {
	repo           database.SinistreRepository
	producer       *kafka.Producer
	consumer       *kafka.Consumer
	processInterval time.Duration
	stopChan       chan struct{}
	wg             sync.WaitGroup
	mu             sync.RWMutex
	running        bool
}

// NewService crée un nouveau service Réclamation
func NewService(repo database.SinistreRepository, producer *kafka.Producer, consumer *kafka.Consumer) *Service {
	return &Service{
		repo:            repo,
		producer:        producer,
		consumer:        consumer,
		processInterval: 30 * time.Second, // Traitement automatique toutes les 30 secondes
		stopChan:        make(chan struct{}),
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

	// Enregistrer les handlers pour les événements de contrats
	s.consumer.RegisterHandler(models.TopicContratEmis, s.handleContratEmis)
	s.consumer.RegisterHandler(models.TopicContratResilie, s.handleContratResilie)

	// Démarrer la consommation
	topics := []string{models.TopicContratEmis, models.TopicContratResilie}
	if err := s.consumer.Start(ctx, topics); err != nil {
		return fmt.Errorf("erreur lors du démarrage du consommateur: %w", err)
	}

	// Démarrer le processus de traitement automatique
	s.wg.Add(1)
	go s.autoProcess(ctx)

	log.Println("[Réclamation] Service démarré")
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

	log.Println("[Réclamation] Service arrêté")
	return nil
}

// handleContratEmis traite les événements ContratEmis
func (s *Service) handleContratEmis(ctx context.Context, msg *kafka.ReceivedMessage) error {
	log.Printf("[Réclamation] Événement ContratEmis reçu: partition=%d offset=%d",
		msg.Partition, msg.Offset)

	var event struct {
		Data models.ContratEmis `json:"data"`
	}

	if err := json.Unmarshal(msg.Value, &event); err != nil {
		log.Printf("[Réclamation] Erreur de parsing ContratEmis: %v", err)
		return err
	}

	// Pour l'instant, juste logger - le contrat est noté pour référence future
	log.Printf("[Réclamation] Nouveau contrat enregistré: %s", event.Data.ContratID)

	return nil
}

// handleContratResilie traite les événements ContratResilie
func (s *Service) handleContratResilie(ctx context.Context, msg *kafka.ReceivedMessage) error {
	log.Printf("[Réclamation] Événement ContratResilie reçu: partition=%d offset=%d",
		msg.Partition, msg.Offset)

	var event struct {
		Data models.ContratResilie `json:"data"`
	}

	if err := json.Unmarshal(msg.Value, &event); err != nil {
		log.Printf("[Réclamation] Erreur de parsing ContratResilie: %v", err)
		return err
	}

	// Logger la résiliation - les sinistres en cours peuvent être impactés
	log.Printf("[Réclamation] Contrat résilié: %s (motif: %s)", event.Data.ContratID, event.Data.Motif)

	return nil
}

// autoProcess effectue le traitement automatique des sinistres
func (s *Service) autoProcess(ctx context.Context) {
	defer s.wg.Done()

	ticker := time.NewTicker(s.processInterval)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return
		case <-s.stopChan:
			return
		case <-ticker.C:
			s.processEvaluations(ctx)
			s.processIndemnisations(ctx)
		}
	}
}

// processEvaluations traite automatiquement les sinistres en attente d'évaluation
func (s *Service) processEvaluations(ctx context.Context) {
	pending, err := s.repo.GetPending(ctx)
	if err != nil {
		log.Printf("[Réclamation] Erreur lors de la récupération des sinistres en attente: %v", err)
		return
	}

	for _, sinistre := range pending {
		// Simuler un délai d'évaluation (auto-évaluation pour la démo)
		// Dans un vrai système, ce serait fait par un expert
		if time.Since(sinistre.DateDeclaration) > 10*time.Second {
			// Évaluer avec 90% du montant estimé
			montantEvalue := sinistre.MontantEstime * 0.9
			if err := s.EvaluerSinistre(ctx, sinistre.ID, montantEvalue); err != nil {
				log.Printf("[Réclamation] Erreur lors de l'évaluation automatique: %v", err)
			}
		}
	}
}

// processIndemnisations traite automatiquement les sinistres évalués
func (s *Service) processIndemnisations(ctx context.Context) {
	evaluated, err := s.repo.GetEvaluated(ctx)
	if err != nil {
		log.Printf("[Réclamation] Erreur lors de la récupération des sinistres évalués: %v", err)
		return
	}

	for _, sinistre := range evaluated {
		// Simuler un délai de paiement
		if sinistre.DateEvaluation != nil && time.Since(*sinistre.DateEvaluation) > 10*time.Second {
			// Indemniser avec le montant évalué
			if sinistre.MontantEvalue != nil {
				if err := s.IndemniserSinistre(ctx, sinistre.ID, sinistre.ContratID, *sinistre.MontantEvalue); err != nil {
					log.Printf("[Réclamation] Erreur lors de l'indemnisation automatique: %v", err)
				}
			}
		}
	}
}

// DeclarerSinistre déclare un nouveau sinistre
func (s *Service) DeclarerSinistre(ctx context.Context, contratID string, typeSinistre models.TypeSinistre, description string, montantEstime float64, dateSurvenance time.Time) (*models.Sinistre, error) {
	// Générer un ID unique
	sinistreID := fmt.Sprintf("SIN-%s", uuid.New().String()[:8])

	// Créer le sinistre
	sinistre := models.NewSinistre(sinistreID, contratID, typeSinistre, description, montantEstime, dateSurvenance)

	// Persister en base
	if err := s.repo.Create(ctx, sinistre); err != nil {
		return nil, fmt.Errorf("erreur lors de la création du sinistre: %w", err)
	}

	// Publier l'événement SinistreDeclare
	event := models.SinistreDeclare{
		SinistreID:     sinistre.ID,
		ContratID:      sinistre.ContratID,
		TypeSinistre:   string(sinistre.TypeSinistre),
		Description:    sinistre.Description,
		MontantEstime:  sinistre.MontantEstime,
		DateSurvenance: sinistre.DateSurvenance,
		Timestamp:      time.Now(),
	}

	if err := s.producer.SendEvent(ctx, models.TopicSinistreDeclare, "SinistreDeclare", "reclamation", event); err != nil {
		log.Printf("[Réclamation] Erreur lors de la publication de l'événement: %v", err)
	}

	log.Printf("[Réclamation] Sinistre déclaré: %s pour contrat %s (type=%s, montant=%.2f)",
		sinistre.ID, contratID, typeSinistre, montantEstime)

	return sinistre, nil
}

// EvaluerSinistre évalue un sinistre
func (s *Service) EvaluerSinistre(ctx context.Context, sinistreID string, montantEvalue float64) error {
	// Récupérer le sinistre
	sinistre, err := s.repo.GetByID(ctx, sinistreID)
	if err != nil {
		return fmt.Errorf("erreur lors de la récupération du sinistre: %w", err)
	}

	if sinistre == nil {
		return fmt.Errorf("sinistre non trouvé: %s", sinistreID)
	}

	if sinistre.Statut != models.StatutSinistreDeclare {
		return fmt.Errorf("le sinistre %s n'est pas en attente d'évaluation", sinistreID)
	}

	// Évaluer le sinistre
	if err := s.repo.Evaluer(ctx, sinistreID, montantEvalue); err != nil {
		return fmt.Errorf("erreur lors de l'évaluation: %w", err)
	}

	// Publier l'événement SinistreEvalue
	event := models.SinistreEvalue{
		SinistreID:    sinistreID,
		MontantEvalue: montantEvalue,
		Timestamp:     time.Now(),
	}

	if err := s.producer.SendEvent(ctx, models.TopicSinistreEvalue, "SinistreEvalue", "reclamation", event); err != nil {
		log.Printf("[Réclamation] Erreur lors de la publication de l'événement: %v", err)
	}

	log.Printf("[Réclamation] Sinistre évalué: %s (montant=%.2f)", sinistreID, montantEvalue)

	return nil
}

// IndemniserSinistre indemnise un sinistre
func (s *Service) IndemniserSinistre(ctx context.Context, sinistreID, contratID string, montantIndemnise float64) error {
	// Récupérer le sinistre
	sinistre, err := s.repo.GetByID(ctx, sinistreID)
	if err != nil {
		return fmt.Errorf("erreur lors de la récupération du sinistre: %w", err)
	}

	if sinistre == nil {
		return fmt.Errorf("sinistre non trouvé: %s", sinistreID)
	}

	if sinistre.Statut != models.StatutSinistreEvalue {
		return fmt.Errorf("le sinistre %s n'est pas prêt pour indemnisation", sinistreID)
	}

	// Indemniser le sinistre
	if err := s.repo.Indemniser(ctx, sinistreID, montantIndemnise); err != nil {
		return fmt.Errorf("erreur lors de l'indemnisation: %w", err)
	}

	// Publier l'événement IndemnisationEffectuee
	event := models.IndemnisationEffectuee{
		SinistreID:       sinistreID,
		ContratID:        contratID,
		MontantIndemnise: montantIndemnise,
		DatePaiement:     time.Now(),
		Timestamp:        time.Now(),
	}

	if err := s.producer.SendEvent(ctx, models.TopicIndemnisationEffectuee, "IndemnisationEffectuee", "reclamation", event); err != nil {
		log.Printf("[Réclamation] Erreur lors de la publication de l'événement: %v", err)
	}

	log.Printf("[Réclamation] Sinistre indemnisé: %s (montant=%.2f)", sinistreID, montantIndemnise)

	return nil
}

// RejeterSinistre rejette un sinistre
func (s *Service) RejeterSinistre(ctx context.Context, sinistreID string) error {
	// Récupérer le sinistre
	sinistre, err := s.repo.GetByID(ctx, sinistreID)
	if err != nil {
		return fmt.Errorf("erreur lors de la récupération du sinistre: %w", err)
	}

	if sinistre == nil {
		return fmt.Errorf("sinistre non trouvé: %s", sinistreID)
	}

	if sinistre.IsTerminated() {
		return fmt.Errorf("le sinistre %s est déjà terminé", sinistreID)
	}

	// Rejeter le sinistre
	if err := s.repo.UpdateStatus(ctx, sinistreID, models.StatutSinistreRejete); err != nil {
		return fmt.Errorf("erreur lors du rejet: %w", err)
	}

	log.Printf("[Réclamation] Sinistre rejeté: %s", sinistreID)

	return nil
}

// GetSinistre récupère un sinistre par son ID
func (s *Service) GetSinistre(ctx context.Context, id string) (*models.Sinistre, error) {
	return s.repo.GetByID(ctx, id)
}

// GetSinistresByContrat récupère tous les sinistres d'un contrat
func (s *Service) GetSinistresByContrat(ctx context.Context, contratID string) ([]*models.Sinistre, error) {
	return s.repo.GetByContratID(ctx, contratID)
}

// ListSinistres récupère tous les sinistres avec pagination
func (s *Service) ListSinistres(ctx context.Context, limit, offset int) ([]*models.Sinistre, error) {
	return s.repo.List(ctx, limit, offset)
}

// GetStats retourne les statistiques des sinistres
func (s *Service) GetStats(ctx context.Context) (*Stats, error) {
	total, err := s.repo.Count(ctx)
	if err != nil {
		return nil, err
	}

	declares, err := s.repo.CountByStatus(ctx, models.StatutSinistreDeclare)
	if err != nil {
		return nil, err
	}

	evalues, err := s.repo.CountByStatus(ctx, models.StatutSinistreEvalue)
	if err != nil {
		return nil, err
	}

	indemnises, err := s.repo.CountByStatus(ctx, models.StatutSinistreIndemnise)
	if err != nil {
		return nil, err
	}

	rejetes, err := s.repo.CountByStatus(ctx, models.StatutSinistreRejete)
	if err != nil {
		return nil, err
	}

	totalIndemnise, err := s.repo.SumIndemnisations(ctx)
	if err != nil {
		return nil, err
	}

	return &Stats{
		Total:           total,
		Declares:        declares,
		Evalues:         evalues,
		Indemnises:      indemnises,
		Rejetes:         rejetes,
		TotalIndemnise:  totalIndemnise,
	}, nil
}

// Stats contient les statistiques des sinistres
type Stats struct {
	Total          int     `json:"total"`
	Declares       int     `json:"declares"`
	Evalues        int     `json:"evalues"`
	Indemnises     int     `json:"indemnises"`
	Rejetes        int     `json:"rejetes"`
	TotalIndemnise float64 `json:"totalIndemnise"`
}
