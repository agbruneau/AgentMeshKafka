package quotation

import (
	"encoding/json"
	"log"
	"net/http"
	"strconv"

	"github.com/agbru/kafka-eda-lab/internal/models"
)

// Handlers contient les handlers HTTP pour le service Quotation
type Handlers struct {
	service *Service
}

// NewHandlers crée un nouveau gestionnaire de handlers
func NewHandlers(service *Service) *Handlers {
	return &Handlers{service: service}
}

// CreateDevisRequest représente la requête de création de devis
type CreateDevisRequest struct {
	ClientID string  `json:"clientId"`
	TypeBien string  `json:"typeBien"`
	Valeur   float64 `json:"valeur"`
}

// Response représente une réponse API standard
type Response struct {
	Success bool        `json:"success"`
	Data    interface{} `json:"data,omitempty"`
	Error   string      `json:"error,omitempty"`
}

// RegisterRoutes enregistre les routes HTTP
func (h *Handlers) RegisterRoutes(mux *http.ServeMux) {
	mux.HandleFunc("POST /api/v1/devis", h.CreateDevis)
	mux.HandleFunc("GET /api/v1/devis", h.ListDevis)
	mux.HandleFunc("GET /api/v1/devis/{id}", h.GetDevis)
	mux.HandleFunc("POST /api/v1/devis/{id}/convert", h.ConvertDevis)
	mux.HandleFunc("GET /api/v1/devis/client/{clientId}", h.GetDevisByClient)
	mux.HandleFunc("GET /api/v1/quotation/stats", h.GetStats)
	mux.HandleFunc("GET /api/v1/quotation/health", h.Health)
}

// CreateDevis crée un nouveau devis
func (h *Handlers) CreateDevis(w http.ResponseWriter, r *http.Request) {
	var req CreateDevisRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		h.sendError(w, http.StatusBadRequest, "requête invalide: "+err.Error())
		return
	}

	// Validation
	if req.ClientID == "" {
		h.sendError(w, http.StatusBadRequest, "clientId requis")
		return
	}
	if req.Valeur <= 0 {
		h.sendError(w, http.StatusBadRequest, "valeur doit être positive")
		return
	}

	// Convertir le type de bien
	typeBien := models.TypeBien(req.TypeBien)
	if typeBien != models.TypeBienAuto && typeBien != models.TypeBienHabitation && typeBien != models.TypeBienAutre {
		h.sendError(w, http.StatusBadRequest, "typeBien invalide (AUTO, HABITATION, AUTRE)")
		return
	}

	// Créer le devis
	devis, err := h.service.CreateDevis(r.Context(), req.ClientID, typeBien, req.Valeur)
	if err != nil {
		log.Printf("[Quotation API] Erreur création devis: %v", err)
		h.sendError(w, http.StatusInternalServerError, "erreur lors de la création du devis")
		return
	}

	h.sendJSON(w, http.StatusCreated, Response{Success: true, Data: devis})
}

// GetDevis récupère un devis par son ID
func (h *Handlers) GetDevis(w http.ResponseWriter, r *http.Request) {
	id := r.PathValue("id")
	if id == "" {
		h.sendError(w, http.StatusBadRequest, "id requis")
		return
	}

	devis, err := h.service.GetDevis(r.Context(), id)
	if err != nil {
		log.Printf("[Quotation API] Erreur récupération devis: %v", err)
		h.sendError(w, http.StatusInternalServerError, "erreur lors de la récupération du devis")
		return
	}

	if devis == nil {
		h.sendError(w, http.StatusNotFound, "devis non trouvé")
		return
	}

	h.sendJSON(w, http.StatusOK, Response{Success: true, Data: devis})
}

// ListDevis liste les devis avec pagination
func (h *Handlers) ListDevis(w http.ResponseWriter, r *http.Request) {
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

	devis, err := h.service.ListDevis(r.Context(), limit, offset)
	if err != nil {
		log.Printf("[Quotation API] Erreur liste devis: %v", err)
		h.sendError(w, http.StatusInternalServerError, "erreur lors de la récupération des devis")
		return
	}

	h.sendJSON(w, http.StatusOK, Response{Success: true, Data: devis})
}

// GetDevisByClient récupère les devis d'un client
func (h *Handlers) GetDevisByClient(w http.ResponseWriter, r *http.Request) {
	clientID := r.PathValue("clientId")
	if clientID == "" {
		h.sendError(w, http.StatusBadRequest, "clientId requis")
		return
	}

	devis, err := h.service.GetDevisByClient(r.Context(), clientID)
	if err != nil {
		log.Printf("[Quotation API] Erreur récupération devis client: %v", err)
		h.sendError(w, http.StatusInternalServerError, "erreur lors de la récupération des devis")
		return
	}

	h.sendJSON(w, http.StatusOK, Response{Success: true, Data: devis})
}

// ConvertDevis convertit un devis en contrat
func (h *Handlers) ConvertDevis(w http.ResponseWriter, r *http.Request) {
	id := r.PathValue("id")
	if id == "" {
		h.sendError(w, http.StatusBadRequest, "id requis")
		return
	}

	if err := h.service.ConvertDevis(r.Context(), id); err != nil {
		log.Printf("[Quotation API] Erreur conversion devis: %v", err)
		h.sendError(w, http.StatusBadRequest, err.Error())
		return
	}

	h.sendJSON(w, http.StatusOK, Response{Success: true, Data: map[string]string{"message": "devis converti"}})
}

// GetStats retourne les statistiques
func (h *Handlers) GetStats(w http.ResponseWriter, r *http.Request) {
	stats, err := h.service.GetStats(r.Context())
	if err != nil {
		log.Printf("[Quotation API] Erreur stats: %v", err)
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
			"service": "quotation",
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
