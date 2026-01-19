package souscription

import (
	"encoding/json"
	"log"
	"net/http"
	"strconv"
)

// Handlers contient les handlers HTTP pour le service Souscription
type Handlers struct {
	service *Service
}

// NewHandlers crée un nouveau gestionnaire de handlers
func NewHandlers(service *Service) *Handlers {
	return &Handlers{service: service}
}

// ModifierContratRequest représente la requête de modification de contrat
type ModifierContratRequest struct {
	Modification   string      `json:"modification"`
	NouvelleValeur interface{} `json:"nouvelleValeur"`
}

// ResilierContratRequest représente la requête de résiliation
type ResilierContratRequest struct {
	Motif string `json:"motif"`
}

// Response représente une réponse API standard
type Response struct {
	Success bool        `json:"success"`
	Data    interface{} `json:"data,omitempty"`
	Error   string      `json:"error,omitempty"`
}

// RegisterRoutes enregistre les routes HTTP
func (h *Handlers) RegisterRoutes(mux *http.ServeMux) {
	mux.HandleFunc("GET /api/v1/contrats", h.ListContrats)
	mux.HandleFunc("GET /api/v1/contrats/{id}", h.GetContrat)
	mux.HandleFunc("PUT /api/v1/contrats/{id}", h.ModifierContrat)
	mux.HandleFunc("DELETE /api/v1/contrats/{id}", h.ResilierContrat)
	mux.HandleFunc("GET /api/v1/contrats/client/{clientId}", h.GetContratsByClient)
	mux.HandleFunc("GET /api/v1/souscription/stats", h.GetStats)
	mux.HandleFunc("GET /api/v1/souscription/health", h.Health)
}

// GetContrat récupère un contrat par son ID
func (h *Handlers) GetContrat(w http.ResponseWriter, r *http.Request) {
	id := r.PathValue("id")
	if id == "" {
		h.sendError(w, http.StatusBadRequest, "id requis")
		return
	}

	contrat, err := h.service.GetContrat(r.Context(), id)
	if err != nil {
		log.Printf("[Souscription API] Erreur récupération contrat: %v", err)
		h.sendError(w, http.StatusInternalServerError, "erreur lors de la récupération du contrat")
		return
	}

	if contrat == nil {
		h.sendError(w, http.StatusNotFound, "contrat non trouvé")
		return
	}

	h.sendJSON(w, http.StatusOK, Response{Success: true, Data: contrat})
}

// ListContrats liste les contrats avec pagination
func (h *Handlers) ListContrats(w http.ResponseWriter, r *http.Request) {
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

	contrats, err := h.service.ListContrats(r.Context(), limit, offset)
	if err != nil {
		log.Printf("[Souscription API] Erreur liste contrats: %v", err)
		h.sendError(w, http.StatusInternalServerError, "erreur lors de la récupération des contrats")
		return
	}

	h.sendJSON(w, http.StatusOK, Response{Success: true, Data: contrats})
}

// GetContratsByClient récupère les contrats d'un client
func (h *Handlers) GetContratsByClient(w http.ResponseWriter, r *http.Request) {
	clientID := r.PathValue("clientId")
	if clientID == "" {
		h.sendError(w, http.StatusBadRequest, "clientId requis")
		return
	}

	contrats, err := h.service.GetContratsByClient(r.Context(), clientID)
	if err != nil {
		log.Printf("[Souscription API] Erreur récupération contrats client: %v", err)
		h.sendError(w, http.StatusInternalServerError, "erreur lors de la récupération des contrats")
		return
	}

	h.sendJSON(w, http.StatusOK, Response{Success: true, Data: contrats})
}

// ModifierContrat modifie un contrat
func (h *Handlers) ModifierContrat(w http.ResponseWriter, r *http.Request) {
	id := r.PathValue("id")
	if id == "" {
		h.sendError(w, http.StatusBadRequest, "id requis")
		return
	}

	var req ModifierContratRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		h.sendError(w, http.StatusBadRequest, "requête invalide: "+err.Error())
		return
	}

	if req.Modification == "" {
		h.sendError(w, http.StatusBadRequest, "modification requise")
		return
	}

	if err := h.service.ModifierContrat(r.Context(), id, req.Modification, req.NouvelleValeur); err != nil {
		log.Printf("[Souscription API] Erreur modification contrat: %v", err)
		h.sendError(w, http.StatusBadRequest, err.Error())
		return
	}

	h.sendJSON(w, http.StatusOK, Response{Success: true, Data: map[string]string{"message": "contrat modifié"}})
}

// ResilierContrat résilie un contrat
func (h *Handlers) ResilierContrat(w http.ResponseWriter, r *http.Request) {
	id := r.PathValue("id")
	if id == "" {
		h.sendError(w, http.StatusBadRequest, "id requis")
		return
	}

	var req ResilierContratRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		h.sendError(w, http.StatusBadRequest, "requête invalide: "+err.Error())
		return
	}

	if req.Motif == "" {
		h.sendError(w, http.StatusBadRequest, "motif requis")
		return
	}

	if err := h.service.ResilierContrat(r.Context(), id, req.Motif); err != nil {
		log.Printf("[Souscription API] Erreur résiliation contrat: %v", err)
		h.sendError(w, http.StatusBadRequest, err.Error())
		return
	}

	h.sendJSON(w, http.StatusOK, Response{Success: true, Data: map[string]string{"message": "contrat résilié"}})
}

// GetStats retourne les statistiques
func (h *Handlers) GetStats(w http.ResponseWriter, r *http.Request) {
	stats, err := h.service.GetStats(r.Context())
	if err != nil {
		log.Printf("[Souscription API] Erreur stats: %v", err)
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
			"service": "souscription",
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
