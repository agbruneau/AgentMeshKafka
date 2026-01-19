package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/agbru/kafka-eda-lab/internal/database"
	"github.com/agbru/kafka-eda-lab/internal/kafka"
	"github.com/agbru/kafka-eda-lab/internal/services/reclamation"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

const (
	defaultHTTPPort = "8083"
	defaultDBPath   = "data/reclamation.db"
)

func main() {
	log.SetOutput(os.Stdout)
	log.SetFlags(log.Ldate | log.Ltime | log.Lshortfile)

	fmt.Println("=======================================")
	fmt.Println("  kafka-eda-lab - Service Réclamation")
	fmt.Println("=======================================")
	fmt.Println()

	// Configuration
	httpPort := getEnv("HTTP_PORT", defaultHTTPPort)
	dbPath := getEnv("DB_PATH", defaultDBPath)

	// Initialiser la base de données
	log.Println("[Réclamation] Initialisation de la base de données...")
	db, err := database.NewSQLiteDB(dbPath)
	if err != nil {
		log.Fatalf("Erreur lors de l'initialisation de la base de données: %v", err)
	}
	defer db.Close()

	if err := db.InitSchema(); err != nil {
		log.Fatalf("Erreur lors de l'initialisation du schéma: %v", err)
	}

	// Initialiser le repository
	repo := database.NewSinistreRepository(db)

	// Configuration Kafka
	kafkaConfig := kafka.NewConfigFromEnv()
	kafkaConfig.ClientID = "reclamation-service"
	kafkaConfig.GroupID = "reclamation-group"

	// Initialiser le producteur Kafka
	log.Println("[Réclamation] Initialisation du producteur Kafka...")
	producer, err := kafka.NewProducer(kafkaConfig)
	if err != nil {
		log.Fatalf("Erreur lors de l'initialisation du producteur Kafka: %v", err)
	}
	defer producer.Close()

	// Initialiser le consommateur Kafka
	log.Println("[Réclamation] Initialisation du consommateur Kafka...")
	consumer, err := kafka.NewConsumer(kafkaConfig)
	if err != nil {
		log.Fatalf("Erreur lors de l'initialisation du consommateur Kafka: %v", err)
	}

	// Initialiser le service
	service := reclamation.NewService(repo, producer, consumer)

	// Démarrer le service
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	if err := service.Start(ctx); err != nil {
		log.Fatalf("Erreur lors du démarrage du service: %v", err)
	}

	// Initialiser les handlers HTTP
	handlers := reclamation.NewHandlers(service)

	// Configurer le router
	mux := http.NewServeMux()
	handlers.RegisterRoutes(mux)

	// Ajouter l'endpoint des métriques Prometheus
	mux.Handle("GET /metrics", promhttp.Handler())

	// Créer le serveur HTTP
	server := &http.Server{
		Addr:         ":" + httpPort,
		Handler:      corsMiddleware(loggingMiddleware(mux)),
		ReadTimeout:  15 * time.Second,
		WriteTimeout: 15 * time.Second,
		IdleTimeout:  60 * time.Second,
	}

	// Démarrer le serveur HTTP dans une goroutine
	go func() {
		log.Printf("[Réclamation] Serveur HTTP démarré sur le port %s", httpPort)
		if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("Erreur du serveur HTTP: %v", err)
		}
	}()

	fmt.Println()
	fmt.Println("Service Réclamation prêt!")
	fmt.Printf("  - API: http://localhost:%s/api/v1/sinistres\n", httpPort)
	fmt.Printf("  - Métriques: http://localhost:%s/metrics\n", httpPort)
	fmt.Printf("  - Health: http://localhost:%s/api/v1/reclamation/health\n", httpPort)
	fmt.Println()
	fmt.Println("En écoute sur les topics:")
	fmt.Println("  - souscription.contrat-emis")
	fmt.Println("  - souscription.contrat-resilie")
	fmt.Println()

	// Attendre un signal d'arrêt
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)
	<-sigChan

	fmt.Println()
	log.Println("[Réclamation] Arrêt en cours...")

	// Arrêter proprement
	shutdownCtx, shutdownCancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer shutdownCancel()

	if err := server.Shutdown(shutdownCtx); err != nil {
		log.Printf("Erreur lors de l'arrêt du serveur HTTP: %v", err)
	}

	if err := service.Stop(); err != nil {
		log.Printf("Erreur lors de l'arrêt du service: %v", err)
	}

	log.Println("[Réclamation] Service arrêté")
}

// getEnv retourne la valeur d'une variable d'environnement ou une valeur par défaut
func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

// loggingMiddleware ajoute le logging des requêtes
func loggingMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		next.ServeHTTP(w, r)
		log.Printf("[HTTP] %s %s - %v", r.Method, r.URL.Path, time.Since(start))
	})
}

// corsMiddleware ajoute les headers CORS
func corsMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")

		if r.Method == "OPTIONS" {
			w.WriteHeader(http.StatusOK)
			return
		}

		next.ServeHTTP(w, r)
	})
}
