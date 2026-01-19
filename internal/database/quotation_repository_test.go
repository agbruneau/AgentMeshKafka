package database

import (
	"context"
	"os"
	"testing"
	"time"

	"github.com/agbru/kafka-eda-lab/internal/models"
)

func setupTestDB(t *testing.T) (*DB, func()) {
	t.Helper()

	// Créer une base de données temporaire
	tmpFile, err := os.CreateTemp("", "test_*.db")
	if err != nil {
		t.Fatalf("Impossible de créer le fichier temporaire: %v", err)
	}
	tmpFile.Close()

	db, err := NewSQLiteDB(tmpFile.Name())
	if err != nil {
		os.Remove(tmpFile.Name())
		t.Fatalf("Impossible de créer la base de données: %v", err)
	}

	if err := db.InitSchema(); err != nil {
		db.Close()
		os.Remove(tmpFile.Name())
		t.Fatalf("Impossible d'initialiser le schéma: %v", err)
	}

	cleanup := func() {
		db.Close()
		os.Remove(tmpFile.Name())
	}

	return db, cleanup
}

func TestQuotationRepository_Create(t *testing.T) {
	db, cleanup := setupTestDB(t)
	defer cleanup()

	repo := NewQuotationRepository(db)
	ctx := context.Background()

	devis := models.NewDevis("DEV-001", "CLI-001", models.TypeBienAuto, 25000.0, 500.0)

	err := repo.Create(ctx, devis)
	if err != nil {
		t.Fatalf("Erreur lors de la création du devis: %v", err)
	}

	// Vérifier que le devis a été créé
	retrieved, err := repo.GetByID(ctx, "DEV-001")
	if err != nil {
		t.Fatalf("Erreur lors de la récupération du devis: %v", err)
	}

	if retrieved == nil {
		t.Fatal("Le devis n'a pas été trouvé")
	}

	if retrieved.ID != devis.ID {
		t.Errorf("ID attendu %s, obtenu %s", devis.ID, retrieved.ID)
	}

	if retrieved.ClientID != devis.ClientID {
		t.Errorf("ClientID attendu %s, obtenu %s", devis.ClientID, retrieved.ClientID)
	}

	if retrieved.TypeBien != devis.TypeBien {
		t.Errorf("TypeBien attendu %s, obtenu %s", devis.TypeBien, retrieved.TypeBien)
	}

	if retrieved.Valeur != devis.Valeur {
		t.Errorf("Valeur attendue %f, obtenue %f", devis.Valeur, retrieved.Valeur)
	}

	if retrieved.Prime != devis.Prime {
		t.Errorf("Prime attendue %f, obtenue %f", devis.Prime, retrieved.Prime)
	}

	if retrieved.Statut != models.StatutDevisGenere {
		t.Errorf("Statut attendu %s, obtenu %s", models.StatutDevisGenere, retrieved.Statut)
	}
}

func TestQuotationRepository_GetByID_NotFound(t *testing.T) {
	db, cleanup := setupTestDB(t)
	defer cleanup()

	repo := NewQuotationRepository(db)
	ctx := context.Background()

	devis, err := repo.GetByID(ctx, "INEXISTANT")
	if err != nil {
		t.Fatalf("Erreur inattendue: %v", err)
	}

	if devis != nil {
		t.Error("Un devis inexistant ne devrait pas être retourné")
	}
}

func TestQuotationRepository_GetByClientID(t *testing.T) {
	db, cleanup := setupTestDB(t)
	defer cleanup()

	repo := NewQuotationRepository(db)
	ctx := context.Background()

	// Créer plusieurs devis pour le même client
	devis1 := models.NewDevis("DEV-001", "CLI-001", models.TypeBienAuto, 25000.0, 500.0)
	devis2 := models.NewDevis("DEV-002", "CLI-001", models.TypeBienHabitation, 150000.0, 2250.0)
	devis3 := models.NewDevis("DEV-003", "CLI-002", models.TypeBienAuto, 30000.0, 600.0)

	repo.Create(ctx, devis1)
	repo.Create(ctx, devis2)
	repo.Create(ctx, devis3)

	// Récupérer les devis du client CLI-001
	devisList, err := repo.GetByClientID(ctx, "CLI-001")
	if err != nil {
		t.Fatalf("Erreur lors de la récupération des devis: %v", err)
	}

	if len(devisList) != 2 {
		t.Errorf("Nombre de devis attendu 2, obtenu %d", len(devisList))
	}
}

func TestQuotationRepository_GetExpired(t *testing.T) {
	db, cleanup := setupTestDB(t)
	defer cleanup()

	repo := NewQuotationRepository(db)
	ctx := context.Background()

	// Créer un devis expiré
	expiredDevis := &models.Devis{
		ID:             "DEV-EXPIRE",
		ClientID:       "CLI-001",
		TypeBien:       models.TypeBienAuto,
		Valeur:         25000.0,
		Prime:          500.0,
		DateCreation:   time.Now().AddDate(0, 0, -60),
		DateExpiration: time.Now().AddDate(0, 0, -30),
		Statut:         models.StatutDevisGenere,
	}

	// Créer un devis valide
	validDevis := models.NewDevis("DEV-VALIDE", "CLI-002", models.TypeBienAuto, 25000.0, 500.0)

	repo.Create(ctx, expiredDevis)
	repo.Create(ctx, validDevis)

	// Récupérer les devis expirés
	expiredList, err := repo.GetExpired(ctx)
	if err != nil {
		t.Fatalf("Erreur lors de la récupération des devis expirés: %v", err)
	}

	if len(expiredList) != 1 {
		t.Errorf("Nombre de devis expirés attendu 1, obtenu %d", len(expiredList))
	}

	if len(expiredList) > 0 && expiredList[0].ID != "DEV-EXPIRE" {
		t.Errorf("ID attendu DEV-EXPIRE, obtenu %s", expiredList[0].ID)
	}
}

func TestQuotationRepository_UpdateStatus(t *testing.T) {
	db, cleanup := setupTestDB(t)
	defer cleanup()

	repo := NewQuotationRepository(db)
	ctx := context.Background()

	devis := models.NewDevis("DEV-001", "CLI-001", models.TypeBienAuto, 25000.0, 500.0)
	repo.Create(ctx, devis)

	// Mettre à jour le statut
	err := repo.UpdateStatus(ctx, "DEV-001", models.StatutDevisConverti)
	if err != nil {
		t.Fatalf("Erreur lors de la mise à jour du statut: %v", err)
	}

	// Vérifier le nouveau statut
	updated, _ := repo.GetByID(ctx, "DEV-001")
	if updated.Statut != models.StatutDevisConverti {
		t.Errorf("Statut attendu %s, obtenu %s", models.StatutDevisConverti, updated.Statut)
	}
}

func TestQuotationRepository_UpdateStatus_NotFound(t *testing.T) {
	db, cleanup := setupTestDB(t)
	defer cleanup()

	repo := NewQuotationRepository(db)
	ctx := context.Background()

	err := repo.UpdateStatus(ctx, "INEXISTANT", models.StatutDevisConverti)
	if err == nil {
		t.Error("Une erreur était attendue pour un ID inexistant")
	}
}

func TestQuotationRepository_List(t *testing.T) {
	db, cleanup := setupTestDB(t)
	defer cleanup()

	repo := NewQuotationRepository(db)
	ctx := context.Background()

	// Créer plusieurs devis
	for i := 1; i <= 5; i++ {
		devis := models.NewDevis(
			"DEV-00"+string(rune('0'+i)),
			"CLI-001",
			models.TypeBienAuto,
			float64(i*10000),
			float64(i*200),
		)
		repo.Create(ctx, devis)
	}

	// Test avec pagination
	devisList, err := repo.List(ctx, 3, 0)
	if err != nil {
		t.Fatalf("Erreur lors de la récupération de la liste: %v", err)
	}

	if len(devisList) != 3 {
		t.Errorf("Nombre de devis attendu 3, obtenu %d", len(devisList))
	}

	// Test avec offset
	devisList, err = repo.List(ctx, 3, 3)
	if err != nil {
		t.Fatalf("Erreur lors de la récupération de la liste: %v", err)
	}

	if len(devisList) != 2 {
		t.Errorf("Nombre de devis attendu 2, obtenu %d", len(devisList))
	}
}

func TestQuotationRepository_Count(t *testing.T) {
	db, cleanup := setupTestDB(t)
	defer cleanup()

	repo := NewQuotationRepository(db)
	ctx := context.Background()

	// Vérifier le comptage initial
	count, err := repo.Count(ctx)
	if err != nil {
		t.Fatalf("Erreur lors du comptage: %v", err)
	}

	if count != 0 {
		t.Errorf("Comptage initial attendu 0, obtenu %d", count)
	}

	// Ajouter des devis
	for i := 1; i <= 3; i++ {
		devis := models.NewDevis(
			"DEV-00"+string(rune('0'+i)),
			"CLI-001",
			models.TypeBienAuto,
			float64(i*10000),
			float64(i*200),
		)
		repo.Create(ctx, devis)
	}

	count, err = repo.Count(ctx)
	if err != nil {
		t.Fatalf("Erreur lors du comptage: %v", err)
	}

	if count != 3 {
		t.Errorf("Comptage attendu 3, obtenu %d", count)
	}
}

func TestQuotationRepository_CountByStatus(t *testing.T) {
	db, cleanup := setupTestDB(t)
	defer cleanup()

	repo := NewQuotationRepository(db)
	ctx := context.Background()

	// Créer des devis avec différents statuts
	devis1 := models.NewDevis("DEV-001", "CLI-001", models.TypeBienAuto, 25000.0, 500.0)
	devis2 := models.NewDevis("DEV-002", "CLI-001", models.TypeBienAuto, 30000.0, 600.0)
	devis3 := models.NewDevis("DEV-003", "CLI-001", models.TypeBienAuto, 35000.0, 700.0)

	repo.Create(ctx, devis1)
	repo.Create(ctx, devis2)
	repo.Create(ctx, devis3)

	// Convertir un devis
	repo.UpdateStatus(ctx, "DEV-002", models.StatutDevisConverti)

	// Vérifier les comptages
	genereCount, _ := repo.CountByStatus(ctx, models.StatutDevisGenere)
	if genereCount != 2 {
		t.Errorf("Comptage GENERE attendu 2, obtenu %d", genereCount)
	}

	convertiCount, _ := repo.CountByStatus(ctx, models.StatutDevisConverti)
	if convertiCount != 1 {
		t.Errorf("Comptage CONVERTI attendu 1, obtenu %d", convertiCount)
	}

	expireCount, _ := repo.CountByStatus(ctx, models.StatutDevisExpire)
	if expireCount != 0 {
		t.Errorf("Comptage EXPIRE attendu 0, obtenu %d", expireCount)
	}
}
