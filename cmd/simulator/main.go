package main

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"log"
	"math/rand"
	"net/http"
	"os"
	"os/signal"
	"sync"
	"syscall"
	"time"
)

const (
	defaultRate         = 1.0 // événements par seconde
	quotationURL        = "http://localhost:8081/api/v1/devis"
	souscriptionURL     = "http://localhost:8082/api/v1/contrats"
	reclamationURL      = "http://localhost:8083/api/v1/sinistres"
)

// Simulator génère des événements de simulation
type Simulator struct {
	rate       float64
	httpClient *http.Client
	running    bool
	stopChan   chan struct{}
	wg         sync.WaitGroup
	mu         sync.RWMutex

	// Stats
	devisGeneres       int
	contratsCreés      int
	sinistresDeclarés  int
	erreurs            int
}

// NewSimulator crée un nouveau simulateur
func NewSimulator(rate float64) *Simulator {
	return &Simulator{
		rate: rate,
		httpClient: &http.Client{
			Timeout: 10 * time.Second,
		},
		stopChan: make(chan struct{}),
	}
}

// Start démarre la simulation
func (s *Simulator) Start(ctx context.Context) {
	s.mu.Lock()
	if s.running {
		s.mu.Unlock()
		return
	}
	s.running = true
	s.mu.Unlock()

	s.wg.Add(1)
	go s.run(ctx)

	log.Println("[Simulator] Démarré")
}

// Stop arrête la simulation
func (s *Simulator) Stop() {
	s.mu.Lock()
	if !s.running {
		s.mu.Unlock()
		return
	}
	s.running = false
	s.mu.Unlock()

	close(s.stopChan)
	s.wg.Wait()

	log.Println("[Simulator] Arrêté")
}

// run exécute la boucle de simulation
func (s *Simulator) run(ctx context.Context) {
	defer s.wg.Done()

	interval := time.Duration(float64(time.Second) / s.rate)
	ticker := time.NewTicker(interval)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return
		case <-s.stopChan:
			return
		case <-ticker.C:
			s.generateEvent(ctx)
		}
	}
}

// generateEvent génère un événement aléatoire
func (s *Simulator) generateEvent(ctx context.Context) {
	// Distribution des événements:
	// 60% - Créer un devis
	// 20% - Déclarer un sinistre (si des contrats existent)
	// 20% - Modifier/Résilier un contrat (si des contrats existent)

	r := rand.Float64()

	if r < 0.6 {
		s.createDevis(ctx)
	} else if r < 0.8 {
		s.declarerSinistre(ctx)
	} else {
		s.modifierContrat(ctx)
	}
}

// createDevis crée un nouveau devis
func (s *Simulator) createDevis(ctx context.Context) {
	// Données aléatoires
	clientID := fmt.Sprintf("CLI-%06d", rand.Intn(1000000))

	typesBien := []string{"AUTO", "HABITATION", "AUTRE"}
	typeBien := typesBien[rand.Intn(len(typesBien))]

	var valeur float64
	switch typeBien {
	case "AUTO":
		valeur = 10000 + rand.Float64()*50000 // 10k - 60k
	case "HABITATION":
		valeur = 100000 + rand.Float64()*400000 // 100k - 500k
	default:
		valeur = 5000 + rand.Float64()*45000 // 5k - 50k
	}

	payload := map[string]interface{}{
		"clientId": clientID,
		"typeBien": typeBien,
		"valeur":   valeur,
	}

	jsonData, _ := json.Marshal(payload)

	req, err := http.NewRequestWithContext(ctx, "POST", quotationURL, bytes.NewBuffer(jsonData))
	if err != nil {
		s.erreurs++
		log.Printf("[Simulator] Erreur création requête: %v", err)
		return
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := s.httpClient.Do(req)
	if err != nil {
		s.erreurs++
		log.Printf("[Simulator] Erreur envoi devis: %v", err)
		return
	}
	defer resp.Body.Close()

	if resp.StatusCode == http.StatusCreated {
		s.devisGeneres++
		log.Printf("[Simulator] Devis créé: client=%s type=%s valeur=%.2f", clientID, typeBien, valeur)
	} else {
		s.erreurs++
		log.Printf("[Simulator] Erreur création devis: status=%d", resp.StatusCode)
	}
}

// declarerSinistre déclare un sinistre sur un contrat existant
func (s *Simulator) declarerSinistre(ctx context.Context) {
	// D'abord, récupérer un contrat existant
	contratID := s.getRandomContratID(ctx)
	if contratID == "" {
		// Pas de contrat disponible, créer un devis à la place
		s.createDevis(ctx)
		return
	}

	typesSinistre := []string{"VOL", "INCENDIE", "DEGATS_EAUX", "ACCIDENT", "AUTRE"}
	typeSinistre := typesSinistre[rand.Intn(len(typesSinistre))]

	descriptions := map[string][]string{
		"VOL":         {"Vol de véhicule", "Cambriolage", "Vol à l'arraché"},
		"INCENDIE":    {"Incendie accidentel", "Court-circuit", "Feu de cuisine"},
		"DEGATS_EAUX": {"Fuite d'eau", "Inondation", "Dégât des eaux voisin"},
		"ACCIDENT":    {"Accident de la route", "Collision", "Accrochage"},
		"AUTRE":       {"Bris de glace", "Catastrophe naturelle", "Vandalisme"},
	}
	descList := descriptions[typeSinistre]
	description := descList[rand.Intn(len(descList))]

	montantEstime := 500 + rand.Float64()*9500 // 500 - 10000

	payload := map[string]interface{}{
		"contratId":      contratID,
		"typeSinistre":   typeSinistre,
		"description":    description,
		"montantEstime":  montantEstime,
		"dateSurvenance": time.Now().AddDate(0, 0, -rand.Intn(30)).Format("2006-01-02"),
	}

	jsonData, _ := json.Marshal(payload)

	req, err := http.NewRequestWithContext(ctx, "POST", reclamationURL, bytes.NewBuffer(jsonData))
	if err != nil {
		s.erreurs++
		return
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := s.httpClient.Do(req)
	if err != nil {
		s.erreurs++
		log.Printf("[Simulator] Erreur envoi sinistre: %v", err)
		return
	}
	defer resp.Body.Close()

	if resp.StatusCode == http.StatusCreated {
		s.sinistresDeclarés++
		log.Printf("[Simulator] Sinistre déclaré: contrat=%s type=%s montant=%.2f", contratID, typeSinistre, montantEstime)
	} else {
		s.erreurs++
		log.Printf("[Simulator] Erreur déclaration sinistre: status=%d", resp.StatusCode)
	}
}

// modifierContrat modifie ou résilie un contrat
func (s *Simulator) modifierContrat(ctx context.Context) {
	contratID := s.getRandomContratID(ctx)
	if contratID == "" {
		s.createDevis(ctx)
		return
	}

	// 70% modification, 30% résiliation
	if rand.Float64() < 0.7 {
		// Modification
		modifications := []string{"changement_adresse", "ajout_garantie", "modification_franchise", "mise_a_jour_valeur"}
		modification := modifications[rand.Intn(len(modifications))]

		payload := map[string]interface{}{
			"modification":   modification,
			"nouvelleValeur": fmt.Sprintf("nouvelle_valeur_%d", rand.Intn(1000)),
		}

		jsonData, _ := json.Marshal(payload)

		req, err := http.NewRequestWithContext(ctx, "PUT", souscriptionURL+"/"+contratID, bytes.NewBuffer(jsonData))
		if err != nil {
			s.erreurs++
			return
		}
		req.Header.Set("Content-Type", "application/json")

		resp, err := s.httpClient.Do(req)
		if err != nil {
			s.erreurs++
			return
		}
		defer resp.Body.Close()

		if resp.StatusCode == http.StatusOK {
			log.Printf("[Simulator] Contrat modifié: %s (%s)", contratID, modification)
		}
	} else {
		// Résiliation
		motifs := []string{"DEMANDE_CLIENT", "NON_PAIEMENT", "SINISTRE_GRAVE", "AUTRE"}
		motif := motifs[rand.Intn(len(motifs))]

		payload := map[string]interface{}{
			"motif": motif,
		}

		jsonData, _ := json.Marshal(payload)

		req, err := http.NewRequestWithContext(ctx, "DELETE", souscriptionURL+"/"+contratID, bytes.NewBuffer(jsonData))
		if err != nil {
			s.erreurs++
			return
		}
		req.Header.Set("Content-Type", "application/json")

		resp, err := s.httpClient.Do(req)
		if err != nil {
			s.erreurs++
			return
		}
		defer resp.Body.Close()

		if resp.StatusCode == http.StatusOK {
			log.Printf("[Simulator] Contrat résilié: %s (motif: %s)", contratID, motif)
		}
	}
}

// getRandomContratID récupère un ID de contrat aléatoire
func (s *Simulator) getRandomContratID(ctx context.Context) string {
	req, err := http.NewRequestWithContext(ctx, "GET", souscriptionURL+"?limit=100", nil)
	if err != nil {
		return ""
	}

	resp, err := s.httpClient.Do(req)
	if err != nil {
		return ""
	}
	defer resp.Body.Close()

	var response struct {
		Success bool `json:"success"`
		Data    []struct {
			ID     string `json:"id"`
			Statut string `json:"statut"`
		} `json:"data"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
		return ""
	}

	if !response.Success || len(response.Data) == 0 {
		return ""
	}

	// Filtrer les contrats actifs
	var activeContrats []string
	for _, c := range response.Data {
		if c.Statut == "ACTIF" || c.Statut == "MODIFIE" {
			activeContrats = append(activeContrats, c.ID)
		}
	}

	if len(activeContrats) == 0 {
		return ""
	}

	return activeContrats[rand.Intn(len(activeContrats))]
}

// GetStats retourne les statistiques de simulation
func (s *Simulator) GetStats() map[string]int {
	return map[string]int{
		"devisGeneres":       s.devisGeneres,
		"contratsCreés":      s.contratsCreés,
		"sinistresDeclarés":  s.sinistresDeclarés,
		"erreurs":            s.erreurs,
	}
}

func main() {
	log.SetOutput(os.Stdout)
	log.SetFlags(log.Ldate | log.Ltime | log.Lshortfile)

	fmt.Println("=======================================")
	fmt.Println("  kafka-eda-lab - Simulateur")
	fmt.Println("=======================================")
	fmt.Println()

	// Configuration
	rate := defaultRate
	if r := os.Getenv("SIMULATION_RATE"); r != "" {
		fmt.Sscanf(r, "%f", &rate)
	}

	log.Printf("[Simulator] Taux de simulation: %.1f événements/seconde", rate)

	// Créer le simulateur
	simulator := NewSimulator(rate)

	// Context pour l'arrêt gracieux
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	// Démarrer la simulation
	simulator.Start(ctx)

	fmt.Println()
	fmt.Println("Simulation en cours...")
	fmt.Println("  - Devis sont créés automatiquement")
	fmt.Println("  - Les contrats sont générés par Souscription")
	fmt.Println("  - Les sinistres sont déclarés sur les contrats actifs")
	fmt.Println()
	fmt.Println("Appuyez sur Ctrl+C pour arrêter")
	fmt.Println()

	// Goroutine pour afficher les stats toutes les 10 secondes
	go func() {
		ticker := time.NewTicker(10 * time.Second)
		defer ticker.Stop()
		for {
			select {
			case <-ctx.Done():
				return
			case <-ticker.C:
				stats := simulator.GetStats()
				log.Printf("[Simulator] Stats: devis=%d, sinistres=%d, erreurs=%d",
					stats["devisGeneres"], stats["sinistresDeclarés"], stats["erreurs"])
			}
		}
	}()

	// Attendre un signal d'arrêt
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)
	<-sigChan

	fmt.Println()
	log.Println("[Simulator] Arrêt en cours...")

	// Arrêter le simulateur
	cancel()
	simulator.Stop()

	// Afficher les stats finales
	stats := simulator.GetStats()
	fmt.Println()
	fmt.Println("Statistiques finales:")
	fmt.Printf("  - Devis générés:      %d\n", stats["devisGeneres"])
	fmt.Printf("  - Sinistres déclarés: %d\n", stats["sinistresDeclarés"])
	fmt.Printf("  - Erreurs:            %d\n", stats["erreurs"])
	fmt.Println()

	log.Println("[Simulator] Terminé")
}
