package reclamation

import (
	"encoding/json"
	"log"
	"net/http"
	"strconv"
	"time"

	"github.com/agbru/kafka-eda-lab/internal/models"
)

// Handlers contient les handlers HTTP pour le service Réclamation
type Handlers struct {
	service *Service
}

// NewHandlers crée un nouveau gestionnaire de handlers
func NewHandlers(service *Service) *Handlers {
	return &Handlers{service: service}
}

// DeclarerSinistreRequest représente la requête de déclaration de sinistre
type DeclarerSinistreRequest struct {
	ContratID      string  `json:"contratId"`
	TypeSinistre   string  `json:"typeSinistre"`
	Description    string  `json:"description"`
	MontantEstime  float64 `json:"montantEstime"`
	DateSurvenance string  `json:"dateSurvenance"` // Format: 2006-01-02
}

// EvaluerSinistreRequest représente la requête d'évaluation
type EvaluerSinistreRequest struct {
	MontantEvalue float64 `json:"montantEvalue"`
}

// IndemniserSinistreRequest représente la requête d'indemnisation
type IndemniserSinistreRequest struct {
	MontantIndemnise float64 `json:"montantIndemnise"`
}

// Response représente une réponse API standard
type Response struct {
	Success bool        `json:"success"`
	Data    interface{} `json:"data,omitempty"`
	Error   string      `json:"error,omitempty"`
}

// RegisterRoutes enregistre les routes HTTP
func (h *Handlers) RegisterRoutes(mux *http.ServeMux) {
	mux.HandleFunc("POST /api/v1/sinistres", h.DeclarerSinistre)
	mux.HandleFunc("GET /api/v1/sinistres", h.ListSinistres)
	mux.HandleFunc("GET /api/v1/sinistres/{id}", h.GetSinistre)
	mux.HandleFunc("POST /api/v1/sinistres/{id}/evaluer", h.EvaluerSinistre)
	mux.HandleFunc("POST /api/v1/sinistres/{id}/indemniser", h.IndemniserSinistre)
	mux.HandleFunc("POST /api/v1/sinistres/{id}/rejeter", h.RejeterSinistre)
	mux.HandleFunc("GET /api/v1/sinistres/contrat/{contratId}", h.GetSinistresByContrat)
	mux.HandleFunc("GET /api/v1/reclamation/stats", h.GetStats)
	mux.HandleFunc("GET /api/v1/reclamation/health", h.Health)
}

// DeclarerSinistre déclare un nouveau sinistre
func (h *Handlers) DeclarerSinistre(w http.ResponseWriter, r *http.Request) {
	var req DeclarerSinistreRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		h.sendError(w, http.StatusBadRequest, "requête invalide: "+err.Error())
		return
	}

	// Validation
	if req.ContratID == "" {
		h.sendError(w, http.StatusBadRequest, "contratId requis")
		return
	}
	if req.MontantEstime <= 0 {
		h.sendError(w, http.StatusBadRequest, "montantEstime doit être positif")
		return
	}

	// Parser le type de sinistre
	typeSinistre := models.TypeSinistre(req.TypeSinistre)
	validTypes := map[models.TypeSinistre]bool{
		models.TypeSinistreVol:        true,
		models.TypeSinistreIncendie:   true,
		models.TypeSinistreDegatsEaux: true,
		models.TypeSinistreAccident:   true,
		models.TypeSinistreAutre:      true,
	}
	if !validTypes[typeSinistre] {
		h.sendError(w, http.StatusBadRequest, "typeSinistre invalide (VOL, INCENDIE, DEGATS_EAUX, ACCIDENT, AUTRE)")
		return
	}

	// Parser la date de survenance
	dateSurvenance := time.Now()
	if req.DateSurvenance != "" {
		parsed, err := time.Parse("2006-01-02", req.DateSurvenance)
		if err != nil {
			h.sendError(w, http.StatusBadRequest, "dateSurvenance invalide (format: YYYY-MM-DD)")
			return
		}
		dateSurvenance = parsed
	}

	// Créer le sinistre
	sinistre, err := h.service.DeclarerSinistre(r.Context(), req.ContratID, typeSinistre, req.Description, req.MontantEstime, dateSurvenance)
	if err != nil {
		log.Printf("[Réclamation API] Erreur déclaration sinistre: %v", err)
		h.sendError(w, http.StatusInternalServerError, "erreur lors de la déclaration du sinistre")
		return
	}

	h.sendJSON(w, http.StatusCreated, Response{Success: true, Data: sinistre})
}

// GetSinistre récupère un sinistre par son ID
func (h *Handlers) GetSinistre(w http.ResponseWriter, r *http.Request) {
	id := r.PathValue("id")
	if id == "" {
		h.sendError(w, http.StatusBadRequest, "id requis")
		return
	}

	sinistre, err := h.service.GetSinistre(r.Context(), id)
	if err != nil {
		log.Printf("[Réclamation API] Erreur récupération sinistre: %v", err)
		h.sendError(w, http.StatusInternalServerError, "erreur lors de la récupération du sinistre")
		return
	}

	if sinistre == nil {
		h.sendError(w, http.StatusNotFound, "sinistre non trouvé")
		return
	}

	h.sendJSON(w, http.StatusOK, Response{Success: true, Data: sinistre})
}

// ListSinistres liste les sinistres avec pagination
func (h *Handlers) ListSinistres(w http.ResponseWriter, r *http.Request) {
	limit := 50
	offset := 0

	if l := r.URL.Query().Get("limit"); l != "" {
		if v, err := strconv.Atoi(l); err == nil && v > 0 && v <= 100 {
			limit = v
		}
	}

	if o := r.URL.Query().Get("offset"); o != "" {
		if v, err := strconv.Atoi(o); err == nil && v >= 0 {
			offset = v
		}
	}

	sinistres, err := h.service.ListSinistres(r.Context(), limit, offset)
	if err != nil {
		log.Printf("[Réclamation API] Erreur liste sinistres: %v", err)
		h.sendError(w, http.StatusInternalServerError, "erreur lors de la récupération des sinistres")
		return
	}

	h.sendJSON(w, http.StatusOK, Response{Success: true, Data: sinistres})
}

// GetSinistresByContrat récupère les sinistres d'un contrat
func (h *Handlers) GetSinistresByContrat(w http.ResponseWriter, r *http.Request) {
	contratID := r.PathValue("contratId")
	if contratID == "" {
		h.sendError(w, http.StatusBadRequest, "contratId requis")
		return
	}

	sinistres, err := h.service.GetSinistresByContrat(r.Context(), contratID)
	if err != nil {
		log.Printf("[Réclamation API] Erreur récupération sinistres contrat: %v", err)
		h.sendError(w, http.StatusInternalServerError, "erreur lors de la récupération des sinistres")
		return
	}

	h.sendJSON(w, http.StatusOK, Response{Success: true, Data: sinistres})
}

// EvaluerSinistre évalue un sinistre
func (h *Handlers) EvaluerSinistre(w http.ResponseWriter, r *http.Request) {
	id := r.PathValue("id")
	if id == "" {
		h.sendError(w, http.StatusBadRequest, "id requis")
		return
	}

	var req EvaluerSinistreRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		h.sendError(w, http.StatusBadRequest, "requête invalide: "+err.Error())
		return
	}

	if req.MontantEvalue <= 0 {
		h.sendError(w, http.StatusBadRequest, "montantEvalue doit être positif")
		return
	}

	if err := h.service.EvaluerSinistre(r.Context(), id, req.MontantEvalue); err != nil {
		log.Printf("[Réclamation API] Erreur évaluation sinistre: %v", err)
		h.sendError(w, http.StatusBadRequest, err.Error())
		return
	}

	h.sendJSON(w, http.StatusOK, Response{Success: true, Data: map[string]string{"message": "sinistre évalué"}})
}

// IndemniserSinistre indemnise un sinistre
func (h *Handlers) IndemniserSinistre(w http.ResponseWriter, r *http.Request) {
	id := r.PathValue("id")
	if id == "" {
		h.sendError(w, http.StatusBadRequest, "id requis")
		return
	}

	var req IndemniserSinistreRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		h.sendError(w, http.StatusBadRequest, "requête invalide: "+err.Error())
		return
	}

	if req.MontantIndemnise <= 0 {
		h.sendError(w, http.StatusBadRequest, "montantIndemnise doit être positif")
		return
	}

	// Récupérer le sinistre pour avoir le contratID
	sinistre, err := h.service.GetSinistre(r.Context(), id)
	if err != nil || sinistre == nil {
		h.sendError(w, http.StatusNotFound, "sinistre non trouvé")
		return
	}

	if err := h.service.IndemniserSinistre(r.Context(), id, sinistre.ContratID, req.MontantIndemnise); err != nil {
		log.Printf("[Réclamation API] Erreur indemnisation sinistre: %v", err)
		h.sendError(w, http.StatusBadRequest, err.Error())
		return
	}

	h.sendJSON(w, http.StatusOK, Response{Success: true, Data: map[string]string{"message": "sinistre indemnisé"}})
}

// RejeterSinistre rejette un sinistre
func (h *Handlers) RejeterSinistre(w http.ResponseWriter, r *http.Request) {
	id := r.PathValue("id")
	if id == "" {
		h.sendError(w, http.StatusBadRequest, "id requis")
		return
	}

	if err := h.service.RejeterSinistre(r.Context(), id); err != nil {
		log.Printf("[Réclamation API] Erreur rejet sinistre: %v", err)
		h.sendError(w, http.StatusBadRequest, err.Error())
		return
	}

	h.sendJSON(w, http.StatusOK, Response{Success: true, Data: map[string]string{"message": "sinistre rejeté"}})
}

// GetStats retourne les statistiques
func (h *Handlers) GetStats(w http.ResponseWriter, r *http.Request) {
	stats, err := h.service.GetStats(r.Context())
	if err != nil {
		log.Printf("[Réclamation API] Erreur stats: %v", err)
		h.sendError(w, http.StatusInternalServerError, "erreur lors de la récupération des statistiques")
		return
	}

	h.sendJSON(w, http.StatusOK, Response{Success: true, Data: stats})
}

// Health vérifie l'état du service
func (h *Handlers) Health(w http.ResponseWriter, r *http.Request) {
	h.sendJSON(w, http.StatusOK, Response{
		Success: true,
		Data: map[string]string{
			"status":  "healthy",
			"service": "reclamation",
		},
	})
}

// sendJSON envoie une réponse JSON
func (h *Handlers) sendJSON(w http.ResponseWriter, status int, data interface{}) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	json.NewEncoder(w).Encode(data)
}

// sendError envoie une réponse d'erreur
func (h *Handlers) sendError(w http.ResponseWriter, status int, message string) {
	h.sendJSON(w, status, Response{Success: false, Error: message})
}
