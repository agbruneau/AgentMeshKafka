package kafka

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"sync"

	"github.com/IBM/sarama"
)

// MessageHandler est le type de fonction pour traiter les messages
type MessageHandler func(ctx context.Context, msg *ReceivedMessage) error

// ReceivedMessage représente un message reçu
type ReceivedMessage struct {
	Topic     string
	Partition int32
	Offset    int64
	Key       string
	Value     []byte
	Headers   map[string]string
	Timestamp int64
}

// Consumer encapsule un consommateur Kafka
type Consumer struct {
	consumerGroup sarama.ConsumerGroup
	config        *Config
	handlers      map[string]MessageHandler
	metrics       *ConsumerMetrics
	mu            sync.RWMutex
	closed        bool
	ready         chan bool
}

// ConsumerMetrics contient les métriques du consommateur
type ConsumerMetrics struct {
	MessagesReceived int64
	MessagesErrors   int64
	BytesReceived    int64
	mu               sync.RWMutex
}

// ConsumerGroupHandler implémente sarama.ConsumerGroupHandler
type ConsumerGroupHandler struct {
	consumer *Consumer
	ready    chan bool
}

// NewConsumer crée un nouveau consommateur Kafka
func NewConsumer(config *Config) (*Consumer, error) {
	saramaConfig := sarama.NewConfig()

	// Configuration du consommateur
	saramaConfig.Consumer.Group.Rebalance.Strategy = sarama.NewBalanceStrategyRoundRobin()
	saramaConfig.Consumer.Offsets.Initial = config.OffsetInitial
	saramaConfig.Consumer.Group.Session.Timeout = config.SessionTimeout
	saramaConfig.Consumer.Group.Heartbeat.Interval = config.HeartbeatInterval
	saramaConfig.Consumer.MaxProcessingTime = config.MaxPollInterval
	saramaConfig.Consumer.Return.Errors = true

	// Metadata
	saramaConfig.ClientID = config.ClientID

	// Créer le consumer group
	consumerGroup, err := sarama.NewConsumerGroup(config.Brokers, config.GroupID, saramaConfig)
	if err != nil {
		return nil, fmt.Errorf("impossible de créer le consumer group: %w", err)
	}

	consumer := &Consumer{
		consumerGroup: consumerGroup,
		config:        config,
		handlers:      make(map[string]MessageHandler),
		metrics:       &ConsumerMetrics{},
		ready:         make(chan bool),
	}

	return consumer, nil
}

// RegisterHandler enregistre un handler pour un topic
func (c *Consumer) RegisterHandler(topic string, handler MessageHandler) {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.handlers[topic] = handler
}

// Start démarre la consommation des topics
func (c *Consumer) Start(ctx context.Context, topics []string) error {
	c.mu.RLock()
	if c.closed {
		c.mu.RUnlock()
		return fmt.Errorf("consommateur fermé")
	}
	c.mu.RUnlock()

	handler := &ConsumerGroupHandler{
		consumer: c,
		ready:    c.ready,
	}

	// Boucle de consommation
	go func() {
		for {
			select {
			case <-ctx.Done():
				return
			default:
				if err := c.consumerGroup.Consume(ctx, topics, handler); err != nil {
					if err != context.Canceled {
						log.Printf("[Consumer] Erreur de consommation: %v", err)
					}
				}
				// Vérifier si le contexte est annulé
				if ctx.Err() != nil {
					return
				}
				c.ready = make(chan bool)
			}
		}
	}()

	// Gérer les erreurs
	go func() {
		for err := range c.consumerGroup.Errors() {
			c.metrics.mu.Lock()
			c.metrics.MessagesErrors++
			c.metrics.mu.Unlock()
			log.Printf("[Consumer] Erreur: %v", err)
		}
	}()

	// Attendre que le consommateur soit prêt
	<-c.ready
	log.Printf("[Consumer] Consommateur prêt pour les topics: %v", topics)

	return nil
}

// GetMetrics retourne les métriques du consommateur
func (c *Consumer) GetMetrics() ConsumerMetrics {
	c.metrics.mu.RLock()
	defer c.metrics.mu.RUnlock()
	return ConsumerMetrics{
		MessagesReceived: c.metrics.MessagesReceived,
		MessagesErrors:   c.metrics.MessagesErrors,
		BytesReceived:    c.metrics.BytesReceived,
	}
}

// Close ferme le consommateur
func (c *Consumer) Close() error {
	c.mu.Lock()
	defer c.mu.Unlock()

	if c.closed {
		return nil
	}

	c.closed = true

	if err := c.consumerGroup.Close(); err != nil {
		return fmt.Errorf("erreur lors de la fermeture du consumer group: %w", err)
	}

	return nil
}

// Setup est appelé au début d'une nouvelle session
func (h *ConsumerGroupHandler) Setup(session sarama.ConsumerGroupSession) error {
	close(h.ready)
	return nil
}

// Cleanup est appelé à la fin d'une session
func (h *ConsumerGroupHandler) Cleanup(session sarama.ConsumerGroupSession) error {
	return nil
}

// ConsumeClaim traite les messages d'une partition
func (h *ConsumerGroupHandler) ConsumeClaim(session sarama.ConsumerGroupSession, claim sarama.ConsumerGroupClaim) error {
	for msg := range claim.Messages() {
		// Construire le message reçu
		receivedMsg := &ReceivedMessage{
			Topic:     msg.Topic,
			Partition: msg.Partition,
			Offset:    msg.Offset,
			Key:       string(msg.Key),
			Value:     msg.Value,
			Headers:   make(map[string]string),
			Timestamp: msg.Timestamp.Unix(),
		}

		// Extraire les headers
		for _, header := range msg.Headers {
			receivedMsg.Headers[string(header.Key)] = string(header.Value)
		}

		// Mettre à jour les métriques
		h.consumer.metrics.mu.Lock()
		h.consumer.metrics.MessagesReceived++
		h.consumer.metrics.BytesReceived += int64(len(msg.Value))
		h.consumer.metrics.mu.Unlock()

		log.Printf("[Consumer] Message reçu: topic=%s partition=%d offset=%d",
			msg.Topic, msg.Partition, msg.Offset)

		// Trouver et appeler le handler
		h.consumer.mu.RLock()
		handler, exists := h.consumer.handlers[msg.Topic]
		h.consumer.mu.RUnlock()

		if exists {
			ctx := session.Context()
			if err := handler(ctx, receivedMsg); err != nil {
				h.consumer.metrics.mu.Lock()
				h.consumer.metrics.MessagesErrors++
				h.consumer.metrics.mu.Unlock()
				log.Printf("[Consumer] Erreur de traitement: topic=%s err=%v", msg.Topic, err)
				// Continuer à traiter les autres messages
			}
		} else {
			log.Printf("[Consumer] Pas de handler pour le topic: %s", msg.Topic)
		}

		// Marquer le message comme traité
		session.MarkMessage(msg, "")
	}

	return nil
}

// ParseEvent parse un événement JSON
func ParseEvent[T any](msg *ReceivedMessage) (*T, error) {
	var event struct {
		ID        string `json:"id"`
		Type      string `json:"type"`
		Source    string `json:"source"`
		Timestamp string `json:"timestamp"`
		Data      T      `json:"data"`
	}

	if err := json.Unmarshal(msg.Value, &event); err != nil {
		return nil, fmt.Errorf("erreur de parsing: %w", err)
	}

	return &event.Data, nil
}
