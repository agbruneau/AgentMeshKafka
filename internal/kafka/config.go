package kafka

import (
	"os"
	"strconv"
	"time"
)

// Config contient la configuration Kafka
type Config struct {
	// Brokers est la liste des brokers Kafka
	Brokers []string

	// SchemaRegistryURL est l'URL du Schema Registry
	SchemaRegistryURL string

	// ClientID est l'identifiant du client
	ClientID string

	// GroupID est l'identifiant du consumer group (pour les consommateurs)
	GroupID string

	// Producer settings
	RequiredAcks    int           // -1: all, 0: none, 1: leader only
	RetryMax        int           // Nombre maximum de tentatives
	RetryBackoff    time.Duration // Délai entre les tentatives
	FlushFrequency  time.Duration // Fréquence de flush
	FlushMessages   int           // Nombre de messages avant flush
	FlushMaxMessages int          // Nombre maximum de messages en attente

	// Consumer settings
	OffsetInitial   int64         // Offset initial (-1: newest, -2: oldest)
	SessionTimeout  time.Duration // Timeout de session
	HeartbeatInterval time.Duration // Intervalle de heartbeat
	MaxPollInterval time.Duration // Intervalle maximum entre les polls
}

// DefaultConfig retourne la configuration par défaut
func DefaultConfig() *Config {
	return &Config{
		Brokers:           []string{getEnv("KAFKA_BROKERS", "localhost:9092")},
		SchemaRegistryURL: getEnv("SCHEMA_REGISTRY_URL", "http://localhost:8081"),
		ClientID:          getEnv("KAFKA_CLIENT_ID", "kafka-eda-lab"),
		GroupID:           getEnv("KAFKA_GROUP_ID", "kafka-eda-lab-group"),
		RequiredAcks:      -1, // all
		RetryMax:          3,
		RetryBackoff:      100 * time.Millisecond,
		FlushFrequency:    500 * time.Millisecond,
		FlushMessages:     10,
		FlushMaxMessages:  100,
		OffsetInitial:     -2, // oldest
		SessionTimeout:    30 * time.Second,
		HeartbeatInterval: 3 * time.Second,
		MaxPollInterval:   5 * time.Minute,
	}
}

// NewConfigFromEnv crée une configuration à partir des variables d'environnement
func NewConfigFromEnv() *Config {
	config := DefaultConfig()

	if brokers := os.Getenv("KAFKA_BROKERS"); brokers != "" {
		config.Brokers = splitBrokers(brokers)
	}

	if schemaRegistry := os.Getenv("SCHEMA_REGISTRY_URL"); schemaRegistry != "" {
		config.SchemaRegistryURL = schemaRegistry
	}

	if clientID := os.Getenv("KAFKA_CLIENT_ID"); clientID != "" {
		config.ClientID = clientID
	}

	if groupID := os.Getenv("KAFKA_GROUP_ID"); groupID != "" {
		config.GroupID = groupID
	}

	if acks := os.Getenv("KAFKA_REQUIRED_ACKS"); acks != "" {
		if v, err := strconv.Atoi(acks); err == nil {
			config.RequiredAcks = v
		}
	}

	return config
}

// getEnv retourne la valeur d'une variable d'environnement ou une valeur par défaut
func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

// splitBrokers sépare une chaîne de brokers en liste
func splitBrokers(brokers string) []string {
	var result []string
	current := ""
	for _, c := range brokers {
		if c == ',' {
			if current != "" {
				result = append(result, current)
				current = ""
			}
		} else {
			current += string(c)
		}
	}
	if current != "" {
		result = append(result, current)
	}
	return result
}
