package quotation

import (
	"context"
	"os"
	"testing"

	"github.com/agbru/kafka-eda-lab/internal/database"
	"github.com/agbru/kafka-eda-lab/internal/models"
)

// MockProducer simule le producteur Kafka pour les tests
type MockProducer struct {
	sentMessages []interface{}
}

func (m *MockProducer) SendEvent(ctx context.Context, topic, eventType, source string, data interface{}) error {
	m.sentMessages = append(m.sentMessages, data)
	return nil
}

func setupTestService(t *testing.T) (*Service, func()) {
	t.Helper()

	// Créer une base de données temporaire
	tmpFile, err := os.CreateTemp("", "test_quotation_*.db")
	if err != nil {
		t.Fatalf("Impossible de créer le fichier temporaire: %v", err)
	}
	tmpFile.Close()

	db, err := database.NewSQLiteDB(tmpFile.Name())
	if err != nil {
		os.Remove(tmpFile.Name())
		t.Fatalf("Impossible de créer la base de données: %v", err)
	}

	if err := db.InitSchema(); err != nil {
		db.Close()
		os.Remove(tmpFile.Name())
		t.Fatalf("Impossible d'initialiser le schéma: %v", err)
	}

	repo := database.NewQuotationRepository(db)

	// Créer le service sans producteur Kafka réel
	service := &Service{
		repo:     repo,
		producer: nil, // Pas de producteur pour les tests unitaires
		stopChan: make(chan struct{}),
	}

	cleanup := func() {
		db.Close()
		os.Remove(tmpFile.Name())
	}

	return service, cleanup
}

func TestService_CreateDevis(t *testing.T) {
	service, cleanup := setupTestService(t)
	defer cleanup()

	ctx := context.Background()

	// Test création d'un devis AUTO
	devis, err := service.CreateDevisWithoutKafka(ctx, "CLI-001", models.TypeBienAuto, 25000.0)
	if err != nil {
		t.Fatalf("Erreur lors de la création du devis: %v", err)
	}

	if devis.ClientID != "CLI-001" {
		t.Errorf("ClientID attendu CLI-001, obtenu %s", devis.ClientID)
	}

	if devis.TypeBien != models.TypeBienAuto {
		t.Errorf("TypeBien attendu AUTO, obtenu %s", devis.TypeBien)
	}

	if devis.Valeur != 25000.0 {
		t.Errorf("Valeur attendue 25000.0, obtenue %f", devis.Valeur)
	}

	// Prime devrait être 2% de la valeur pour AUTO
	expectedPrime := 25000.0 * 0.02
	if devis.Prime != expectedPrime {
		t.Errorf("Prime attendue %f, obtenue %f", expectedPrime, devis.Prime)
	}

	if devis.Statut != models.StatutDevisGenere {
		t.Errorf("Statut attendu GENERE, obtenu %s", devis.Statut)
	}
}

func TestService_GetDevis(t *testing.T) {
	service, cleanup := setupTestService(t)
	defer cleanup()

	ctx := context.Background()

	// Créer un devis
	created, _ := service.CreateDevisWithoutKafka(ctx, "CLI-001", models.TypeBienHabitation, 150000.0)

	// Récupérer le devis
	retrieved, err := service.GetDevis(ctx, created.ID)
	if err != nil {
		t.Fatalf("Erreur lors de la récupération du devis: %v", err)
	}

	if retrieved == nil {
		t.Fatal("Devis non trouvé")
	}

	if retrieved.ID != created.ID {
		t.Errorf("ID attendu %s, obtenu %s", created.ID, retrieved.ID)
	}
}

func TestService_GetDevis_NotFound(t *testing.T) {
	service, cleanup := setupTestService(t)
	defer cleanup()

	ctx := context.Background()

	devis, err := service.GetDevis(ctx, "INEXISTANT")
	if err != nil {
		t.Fatalf("Erreur inattendue: %v", err)
	}

	if devis != nil {
		t.Error("Un devis inexistant ne devrait pas être retourné")
	}
}

func TestService_ConvertDevis(t *testing.T) {
	service, cleanup := setupTestService(t)
	defer cleanup()

	ctx := context.Background()

	// Créer un devis
	devis, _ := service.CreateDevisWithoutKafka(ctx, "CLI-001", models.TypeBienAuto, 25000.0)

	// Convertir le devis
	err := service.ConvertDevisWithoutNotification(ctx, devis.ID)
	if err != nil {
		t.Fatalf("Erreur lors de la conversion du devis: %v", err)
	}

	// Vérifier le statut
	updated, _ := service.GetDevis(ctx, devis.ID)
	if updated.Statut != models.StatutDevisConverti {
		t.Errorf("Statut attendu CONVERTI, obtenu %s", updated.Statut)
	}
}

func TestService_ConvertDevis_AlreadyConverted(t *testing.T) {
	service, cleanup := setupTestService(t)
	defer cleanup()

	ctx := context.Background()

	// Créer et convertir un devis
	devis, _ := service.CreateDevisWithoutKafka(ctx, "CLI-001", models.TypeBienAuto, 25000.0)
	service.ConvertDevisWithoutNotification(ctx, devis.ID)

	// Essayer de convertir à nouveau
	err := service.ConvertDevisWithoutNotification(ctx, devis.ID)
	if err == nil {
		t.Error("Une erreur était attendue pour un devis déjà converti")
	}
}

func TestService_GetStats(t *testing.T) {
	service, cleanup := setupTestService(t)
	defer cleanup()

	ctx := context.Background()

	// Créer quelques devis
	service.CreateDevisWithoutKafka(ctx, "CLI-001", models.TypeBienAuto, 25000.0)
	devis2, _ := service.CreateDevisWithoutKafka(ctx, "CLI-002", models.TypeBienHabitation, 150000.0)
	service.CreateDevisWithoutKafka(ctx, "CLI-003", models.TypeBienAutre, 50000.0)

	// Convertir un devis
	service.ConvertDevisWithoutNotification(ctx, devis2.ID)

	// Vérifier les stats
	stats, err := service.GetStats(ctx)
	if err != nil {
		t.Fatalf("Erreur lors de la récupération des stats: %v", err)
	}

	if stats.Total != 3 {
		t.Errorf("Total attendu 3, obtenu %d", stats.Total)
	}

	if stats.Generes != 2 {
		t.Errorf("Generes attendu 2, obtenu %d", stats.Generes)
	}

	if stats.Convertis != 1 {
		t.Errorf("Convertis attendu 1, obtenu %d", stats.Convertis)
	}
}

// CreateDevisWithoutKafka crée un devis sans envoyer d'événement Kafka (pour les tests)
func (s *Service) CreateDevisWithoutKafka(ctx context.Context, clientID string, typeBien models.TypeBien, valeur float64) (*models.Devis, error) {
	// Générer un ID unique
	devisID := "DEV-TEST-" + clientID

	// Calculer la prime
	prime := models.CalculerPrime(typeBien, valeur)

	// Créer le devis
	devis := models.NewDevis(devisID, clientID, typeBien, valeur, prime)

	// Persister en base
	if err := s.repo.Create(ctx, devis); err != nil {
		return nil, err
	}

	return devis, nil
}

// ConvertDevisWithoutNotification convertit un devis sans notification (pour les tests)
func (s *Service) ConvertDevisWithoutNotification(ctx context.Context, devisID string) error {
	devis, err := s.repo.GetByID(ctx, devisID)
	if err != nil {
		return err
	}

	if devis == nil {
		return err
	}

	if devis.Statut != models.StatutDevisGenere {
		return err
	}

	return s.repo.UpdateStatus(ctx, devisID, models.StatutDevisConverti)
}
