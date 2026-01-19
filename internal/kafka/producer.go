package kafka

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"sync"
	"time"

	"github.com/IBM/sarama"
	"github.com/google/uuid"
)

// Producer encapsule un producteur Kafka
type Producer struct {
	syncProducer  sarama.SyncProducer
	asyncProducer sarama.AsyncProducer
	config        *Config
	metrics       *ProducerMetrics
	mu            sync.RWMutex
	closed        bool
}

// ProducerMetrics contient les métriques du producteur
type ProducerMetrics struct {
	MessagesSent     int64
	MessagesErrors   int64
	BytesSent        int64
	LastSendDuration time.Duration
	mu               sync.RWMutex
}

// Message représente un message à envoyer
type Message struct {
	Topic     string
	Key       string
	Value     interface{}
	Headers   map[string]string
	Timestamp time.Time
}

// NewProducer crée un nouveau producteur Kafka
func NewProducer(config *Config) (*Producer, error) {
	saramaConfig := sarama.NewConfig()

	// Configuration du producteur
	saramaConfig.Producer.RequiredAcks = sarama.RequiredAcks(config.RequiredAcks)
	saramaConfig.Producer.Retry.Max = config.RetryMax
	saramaConfig.Producer.Retry.Backoff = config.RetryBackoff
	saramaConfig.Producer.Return.Successes = true
	saramaConfig.Producer.Return.Errors = true
	saramaConfig.Producer.Flush.Frequency = config.FlushFrequency
	saramaConfig.Producer.Flush.Messages = config.FlushMessages
	saramaConfig.Producer.Flush.MaxMessages = config.FlushMaxMessages

	// Metadata
	saramaConfig.ClientID = config.ClientID

	// Créer le producteur synchrone
	syncProducer, err := sarama.NewSyncProducer(config.Brokers, saramaConfig)
	if err != nil {
		return nil, fmt.Errorf("impossible de créer le producteur synchrone: %w", err)
	}

	// Créer le producteur asynchrone
	asyncProducer, err := sarama.NewAsyncProducer(config.Brokers, saramaConfig)
	if err != nil {
		syncProducer.Close()
		return nil, fmt.Errorf("impossible de créer le producteur asynchrone: %w", err)
	}

	producer := &Producer{
		syncProducer:  syncProducer,
		asyncProducer: asyncProducer,
		config:        config,
		metrics:       &ProducerMetrics{},
	}

	// Démarrer la goroutine pour gérer les erreurs asynchrones
	go producer.handleAsyncErrors()
	go producer.handleAsyncSuccesses()

	return producer, nil
}

// Send envoie un message de manière synchrone
func (p *Producer) Send(ctx context.Context, msg *Message) error {
	p.mu.RLock()
	if p.closed {
		p.mu.RUnlock()
		return fmt.Errorf("producteur fermé")
	}
	p.mu.RUnlock()

	start := time.Now()

	// Sérialiser la valeur en JSON
	valueBytes, err := json.Marshal(msg.Value)
	if err != nil {
		return fmt.Errorf("erreur de sérialisation: %w", err)
	}

	// Créer le message Sarama
	saramaMsg := &sarama.ProducerMessage{
		Topic:     msg.Topic,
		Value:     sarama.ByteEncoder(valueBytes),
		Timestamp: msg.Timestamp,
	}

	if msg.Key != "" {
		saramaMsg.Key = sarama.StringEncoder(msg.Key)
	}

	// Ajouter les headers
	for k, v := range msg.Headers {
		saramaMsg.Headers = append(saramaMsg.Headers, sarama.RecordHeader{
			Key:   []byte(k),
			Value: []byte(v),
		})
	}

	// Envoyer le message
	partition, offset, err := p.syncProducer.SendMessage(saramaMsg)
	if err != nil {
		p.metrics.mu.Lock()
		p.metrics.MessagesErrors++
		p.metrics.mu.Unlock()
		return fmt.Errorf("erreur lors de l'envoi du message: %w", err)
	}

	// Mettre à jour les métriques
	duration := time.Since(start)
	p.metrics.mu.Lock()
	p.metrics.MessagesSent++
	p.metrics.BytesSent += int64(len(valueBytes))
	p.metrics.LastSendDuration = duration
	p.metrics.mu.Unlock()

	log.Printf("[Producer] Message envoyé: topic=%s partition=%d offset=%d duration=%v",
		msg.Topic, partition, offset, duration)

	return nil
}

// SendAsync envoie un message de manière asynchrone
func (p *Producer) SendAsync(msg *Message) error {
	p.mu.RLock()
	if p.closed {
		p.mu.RUnlock()
		return fmt.Errorf("producteur fermé")
	}
	p.mu.RUnlock()

	// Sérialiser la valeur en JSON
	valueBytes, err := json.Marshal(msg.Value)
	if err != nil {
		return fmt.Errorf("erreur de sérialisation: %w", err)
	}

	// Créer le message Sarama
	saramaMsg := &sarama.ProducerMessage{
		Topic:     msg.Topic,
		Value:     sarama.ByteEncoder(valueBytes),
		Timestamp: msg.Timestamp,
	}

	if msg.Key != "" {
		saramaMsg.Key = sarama.StringEncoder(msg.Key)
	}

	// Ajouter les headers
	for k, v := range msg.Headers {
		saramaMsg.Headers = append(saramaMsg.Headers, sarama.RecordHeader{
			Key:   []byte(k),
			Value: []byte(v),
		})
	}

	// Envoyer le message de manière asynchrone
	p.asyncProducer.Input() <- saramaMsg

	return nil
}

// SendEvent envoie un événement formaté
func (p *Producer) SendEvent(ctx context.Context, topic string, eventType string, source string, data interface{}) error {
	event := map[string]interface{}{
		"id":        uuid.New().String(),
		"type":      eventType,
		"source":    source,
		"timestamp": time.Now().UTC(),
		"data":      data,
	}

	msg := &Message{
		Topic:     topic,
		Key:       extractKey(data),
		Value:     event,
		Timestamp: time.Now(),
		Headers: map[string]string{
			"event-type": eventType,
			"source":     source,
		},
	}

	return p.Send(ctx, msg)
}

// extractKey extrait une clé du payload pour le partitionnement
func extractKey(data interface{}) string {
	// Essayer d'extraire un ID du payload
	if m, ok := data.(map[string]interface{}); ok {
		if id, ok := m["id"].(string); ok {
			return id
		}
		if id, ok := m["devisId"].(string); ok {
			return id
		}
		if id, ok := m["contratId"].(string); ok {
			return id
		}
		if id, ok := m["sinistreId"].(string); ok {
			return id
		}
	}
	return ""
}

// handleAsyncErrors gère les erreurs du producteur asynchrone
func (p *Producer) handleAsyncErrors() {
	for err := range p.asyncProducer.Errors() {
		p.metrics.mu.Lock()
		p.metrics.MessagesErrors++
		p.metrics.mu.Unlock()
		log.Printf("[Producer] Erreur async: topic=%s err=%v", err.Msg.Topic, err.Err)
	}
}

// handleAsyncSuccesses gère les succès du producteur asynchrone
func (p *Producer) handleAsyncSuccesses() {
	for msg := range p.asyncProducer.Successes() {
		p.metrics.mu.Lock()
		p.metrics.MessagesSent++
		p.metrics.mu.Unlock()
		log.Printf("[Producer] Message async envoyé: topic=%s partition=%d offset=%d",
			msg.Topic, msg.Partition, msg.Offset)
	}
}

// GetMetrics retourne les métriques du producteur
func (p *Producer) GetMetrics() ProducerMetrics {
	p.metrics.mu.RLock()
	defer p.metrics.mu.RUnlock()
	return ProducerMetrics{
		MessagesSent:     p.metrics.MessagesSent,
		MessagesErrors:   p.metrics.MessagesErrors,
		BytesSent:        p.metrics.BytesSent,
		LastSendDuration: p.metrics.LastSendDuration,
	}
}

// Close ferme le producteur
func (p *Producer) Close() error {
	p.mu.Lock()
	defer p.mu.Unlock()

	if p.closed {
		return nil
	}

	p.closed = true

	var errs []error

	if err := p.asyncProducer.Close(); err != nil {
		errs = append(errs, fmt.Errorf("erreur lors de la fermeture du producteur async: %w", err))
	}

	if err := p.syncProducer.Close(); err != nil {
		errs = append(errs, fmt.Errorf("erreur lors de la fermeture du producteur sync: %w", err))
	}

	if len(errs) > 0 {
		return fmt.Errorf("erreurs lors de la fermeture: %v", errs)
	}

	return nil
}
