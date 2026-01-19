package quotation

import (
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
)

// Metrics contient les métriques Prometheus pour le service Quotation
type Metrics struct {
	DevisCreated   prometheus.Counter
	DevisConverted prometheus.Counter
	DevisExpired   prometheus.Counter
	DevisTotal     prometheus.Gauge
	DevisByStatus  *prometheus.GaugeVec
	DevisByType    *prometheus.GaugeVec
	RequestsTotal  *prometheus.CounterVec
	RequestLatency *prometheus.HistogramVec
}

// NewMetrics crée les métriques Prometheus
func NewMetrics(namespace string) *Metrics {
	return &Metrics{
		DevisCreated: promauto.NewCounter(prometheus.CounterOpts{
			Namespace: namespace,
			Subsystem: "quotation",
			Name:      "devis_created_total",
			Help:      "Nombre total de devis créés",
		}),
		DevisConverted: promauto.NewCounter(prometheus.CounterOpts{
			Namespace: namespace,
			Subsystem: "quotation",
			Name:      "devis_converted_total",
			Help:      "Nombre total de devis convertis en contrats",
		}),
		DevisExpired: promauto.NewCounter(prometheus.CounterOpts{
			Namespace: namespace,
			Subsystem: "quotation",
			Name:      "devis_expired_total",
			Help:      "Nombre total de devis expirés",
		}),
		DevisTotal: promauto.NewGauge(prometheus.GaugeOpts{
			Namespace: namespace,
			Subsystem: "quotation",
			Name:      "devis_total",
			Help:      "Nombre total de devis en base",
		}),
		DevisByStatus: promauto.NewGaugeVec(prometheus.GaugeOpts{
			Namespace: namespace,
			Subsystem: "quotation",
			Name:      "devis_by_status",
			Help:      "Nombre de devis par statut",
		}, []string{"status"}),
		DevisByType: promauto.NewGaugeVec(prometheus.GaugeOpts{
			Namespace: namespace,
			Subsystem: "quotation",
			Name:      "devis_by_type",
			Help:      "Nombre de devis par type de bien",
		}, []string{"type_bien"}),
		RequestsTotal: promauto.NewCounterVec(prometheus.CounterOpts{
			Namespace: namespace,
			Subsystem: "quotation",
			Name:      "http_requests_total",
			Help:      "Nombre total de requêtes HTTP",
		}, []string{"method", "endpoint", "status"}),
		RequestLatency: promauto.NewHistogramVec(prometheus.HistogramOpts{
			Namespace: namespace,
			Subsystem: "quotation",
			Name:      "http_request_duration_seconds",
			Help:      "Latence des requêtes HTTP en secondes",
			Buckets:   prometheus.DefBuckets,
		}, []string{"method", "endpoint"}),
	}
}

// RecordDevisCreated enregistre la création d'un devis
func (m *Metrics) RecordDevisCreated() {
	m.DevisCreated.Inc()
}

// RecordDevisConverted enregistre la conversion d'un devis
func (m *Metrics) RecordDevisConverted() {
	m.DevisConverted.Inc()
}

// RecordDevisExpired enregistre l'expiration d'un devis
func (m *Metrics) RecordDevisExpired() {
	m.DevisExpired.Inc()
}

// UpdateDevisStats met à jour les statistiques
func (m *Metrics) UpdateDevisStats(stats *Stats) {
	m.DevisTotal.Set(float64(stats.Total))
	m.DevisByStatus.WithLabelValues("GENERE").Set(float64(stats.Generes))
	m.DevisByStatus.WithLabelValues("CONVERTI").Set(float64(stats.Convertis))
	m.DevisByStatus.WithLabelValues("EXPIRE").Set(float64(stats.Expires))
}

// RecordRequest enregistre une requête HTTP
func (m *Metrics) RecordRequest(method, endpoint, status string) {
	m.RequestsTotal.WithLabelValues(method, endpoint, status).Inc()
}

// ObserveLatency observe la latence d'une requête
func (m *Metrics) ObserveLatency(method, endpoint string, seconds float64) {
	m.RequestLatency.WithLabelValues(method, endpoint).Observe(seconds)
}
