"""
Tests unitaires pour le Message Broker.

Couvre:
- Envoi/réception de messages dans les queues
- Publication/souscription aux topics
- Dead Letter Queue (DLQ)
- Statistiques et métriques
- Gestion des erreurs et retries
"""
import pytest
import asyncio
from app.integration.events.broker import (
    MessageBroker, Message, MessageStatus, Subscription,
    get_broker, reset_broker
)


@pytest.fixture
def broker():
    """Crée une nouvelle instance de broker pour chaque test."""
    return MessageBroker()


@pytest.fixture(autouse=True)
def reset_singleton():
    """Réinitialise le singleton avant chaque test."""
    reset_broker()
    yield
    reset_broker()


# ========== TESTS QUEUE (Point-à-Point) ==========

class TestQueueOperations:
    """Tests des opérations de queue point-à-point."""

    @pytest.mark.asyncio
    async def test_send_to_queue_creates_message(self, broker):
        """Vérifie que l'envoi crée bien un message."""
        message = await broker.send_to_queue(
            "test_queue",
            {"action": "test", "value": 42},
            source="test_service"
        )

        assert message is not None
        assert message.id.startswith("MSG-")
        assert message.payload == {"action": "test", "value": 42}
        assert message.source == "test_service"
        assert message.status == MessageStatus.PENDING

    @pytest.mark.asyncio
    async def test_send_to_queue_increments_stats(self, broker):
        """Vérifie que les statistiques sont mises à jour."""
        initial_stats = broker.get_stats()
        assert initial_stats["messages_sent"] == 0

        await broker.send_to_queue("test_queue", {"data": "test"})

        stats = broker.get_stats()
        assert stats["messages_sent"] == 1

    @pytest.mark.asyncio
    async def test_receive_from_queue_returns_message(self, broker):
        """Vérifie la réception d'un message."""
        await broker.send_to_queue("test_queue", {"key": "value"})

        message = await broker.receive_from_queue("test_queue", timeout=1.0)

        assert message is not None
        assert message.payload == {"key": "value"}
        assert message.status == MessageStatus.PROCESSING

    @pytest.mark.asyncio
    async def test_receive_from_empty_queue_returns_none(self, broker):
        """Vérifie le timeout sur queue vide."""
        message = await broker.receive_from_queue("empty_queue", timeout=0.1)
        assert message is None

    @pytest.mark.asyncio
    async def test_queue_fifo_order(self, broker):
        """Vérifie l'ordre FIFO des messages."""
        await broker.send_to_queue("test_queue", {"order": 1})
        await broker.send_to_queue("test_queue", {"order": 2})
        await broker.send_to_queue("test_queue", {"order": 3})

        msg1 = await broker.receive_from_queue("test_queue", timeout=1.0)
        msg2 = await broker.receive_from_queue("test_queue", timeout=1.0)
        msg3 = await broker.receive_from_queue("test_queue", timeout=1.0)

        assert msg1.payload["order"] == 1
        assert msg2.payload["order"] == 2
        assert msg3.payload["order"] == 3

    @pytest.mark.asyncio
    async def test_get_queue_size(self, broker):
        """Vérifie le comptage de taille de queue."""
        assert broker.get_queue_size("test_queue") == 0

        await broker.send_to_queue("test_queue", {"data": 1})
        await broker.send_to_queue("test_queue", {"data": 2})

        assert broker.get_queue_size("test_queue") == 2

    @pytest.mark.asyncio
    async def test_get_queue_messages(self, broker):
        """Vérifie la récupération des messages de la queue."""
        await broker.send_to_queue("test_queue", {"data": "test1"})
        await broker.send_to_queue("test_queue", {"data": "test2"})

        messages = broker.get_queue_messages("test_queue")

        assert len(messages) == 2
        assert messages[0]["payload"]["data"] == "test1"
        assert messages[1]["payload"]["data"] == "test2"

    @pytest.mark.asyncio
    async def test_send_with_headers(self, broker):
        """Vérifie l'envoi avec headers."""
        message = await broker.send_to_queue(
            "test_queue",
            {"data": "test"},
            headers={"correlation-id": "123", "priority": "high"}
        )

        assert message.headers == {"correlation-id": "123", "priority": "high"}


# ========== TESTS TOPIC (Pub/Sub) ==========

class TestTopicOperations:
    """Tests des opérations de topic pub/sub."""

    @pytest.mark.asyncio
    async def test_subscribe_returns_subscription_id(self, broker):
        """Vérifie que la souscription retourne un ID."""
        async def handler(payload):
            pass

        sub_id = await broker.subscribe("test_topic", handler)

        assert sub_id is not None
        assert sub_id.startswith("SUB-")

    @pytest.mark.asyncio
    async def test_publish_delivers_to_subscriber(self, broker):
        """Vérifie que la publication atteint les abonnés."""
        received = []

        async def handler(payload):
            received.append(payload)

        await broker.subscribe("test_topic", handler)
        await broker.publish("test_topic", {"message": "hello"})

        # Attendre la livraison asynchrone
        await asyncio.sleep(0.1)

        assert len(received) == 1
        assert received[0] == {"message": "hello"}

    @pytest.mark.asyncio
    async def test_publish_delivers_to_multiple_subscribers(self, broker):
        """Vérifie la livraison à plusieurs abonnés."""
        received_1 = []
        received_2 = []

        async def handler_1(payload):
            received_1.append(payload)

        async def handler_2(payload):
            received_2.append(payload)

        await broker.subscribe("test_topic", handler_1)
        await broker.subscribe("test_topic", handler_2)
        await broker.publish("test_topic", {"msg": "broadcast"})

        await asyncio.sleep(0.1)

        assert len(received_1) == 1
        assert len(received_2) == 1

    @pytest.mark.asyncio
    async def test_unsubscribe_stops_delivery(self, broker):
        """Vérifie que le désabonnement arrête la livraison."""
        received = []

        async def handler(payload):
            received.append(payload)

        sub_id = await broker.subscribe("test_topic", handler)
        result = broker.unsubscribe("test_topic", sub_id)

        assert result is True

        await broker.publish("test_topic", {"msg": "should not receive"})
        await asyncio.sleep(0.1)

        assert len(received) == 0

    @pytest.mark.asyncio
    async def test_unsubscribe_nonexistent_returns_false(self, broker):
        """Vérifie le retour false pour un désabonnement invalide."""
        result = broker.unsubscribe("nonexistent_topic", "SUB-INVALID")
        assert result is False

    @pytest.mark.asyncio
    async def test_get_topics(self, broker):
        """Vérifie la liste des topics."""
        async def handler(payload):
            pass

        await broker.subscribe("topic_1", handler)
        await broker.subscribe("topic_2", handler)

        topics = broker.get_topics()

        assert len(topics) == 2
        topic_names = [t["name"] for t in topics]
        assert "topic_1" in topic_names
        assert "topic_2" in topic_names


# ========== TESTS DLQ (Dead Letter Queue) ==========

class TestDeadLetterQueue:
    """Tests de la Dead Letter Queue."""

    @pytest.mark.asyncio
    async def test_failed_delivery_goes_to_dlq(self, broker):
        """Vérifie que les messages échoués vont en DLQ."""
        async def failing_handler(payload):
            raise Exception("Handler failed")

        await broker.subscribe("test_topic", failing_handler, max_retries=1)
        await broker.publish("test_topic", {"msg": "will fail"})

        # Attendre les retries et le passage en DLQ
        await asyncio.sleep(0.5)

        dlq_size = broker.get_dlq_size("test_topic")
        assert dlq_size == 1

    @pytest.mark.asyncio
    async def test_receive_from_dlq(self, broker):
        """Vérifie la récupération depuis la DLQ."""
        async def failing_handler(payload):
            raise Exception("Always fails")

        await broker.subscribe("test_topic", failing_handler, max_retries=0)
        await broker.publish("test_topic", {"msg": "dlq test"})

        await asyncio.sleep(0.2)

        dlq_message = await broker.receive_from_dlq("test_topic")

        assert dlq_message is not None
        assert dlq_message.status == MessageStatus.DEAD_LETTER
        assert dlq_message.payload == {"msg": "dlq test"}

    @pytest.mark.asyncio
    async def test_dlq_messages_contain_error(self, broker):
        """Vérifie que les messages DLQ contiennent l'erreur."""
        async def failing_handler(payload):
            raise ValueError("Specific error message")

        await broker.subscribe("test_topic", failing_handler, max_retries=0)
        await broker.publish("test_topic", {"msg": "test"})

        await asyncio.sleep(0.2)

        messages = broker.get_dlq_messages("test_topic")

        assert len(messages) == 1
        assert "Specific error message" in messages[0]["error"]

    @pytest.mark.asyncio
    async def test_empty_dlq_returns_none(self, broker):
        """Vérifie le retour None sur DLQ vide."""
        message = await broker.receive_from_dlq("nonexistent")
        assert message is None


# ========== TESTS MÉTRIQUES ET CONTRÔLE ==========

class TestMetricsAndControl:
    """Tests des métriques et contrôles."""

    @pytest.mark.asyncio
    async def test_get_stats(self, broker):
        """Vérifie les statistiques complètes."""
        await broker.send_to_queue("q1", {"data": 1})
        await broker.send_to_queue("q1", {"data": 2})

        async def handler(p):
            pass
        await broker.subscribe("t1", handler)
        await broker.publish("t1", {"data": "pub"})

        await asyncio.sleep(0.1)

        stats = broker.get_stats()

        assert stats["messages_sent"] == 3  # 2 queue + 1 topic
        assert "q1" in stats["queues"]
        assert "t1" in stats["topics"]

    @pytest.mark.asyncio
    async def test_get_message_history(self, broker):
        """Vérifie l'historique des messages."""
        await broker.send_to_queue("q1", {"msg": 1})
        await broker.send_to_queue("q2", {"msg": 2})

        history = broker.get_message_history(limit=10)

        assert len(history) == 2
        assert history[0]["payload"]["msg"] == 1
        assert history[1]["payload"]["msg"] == 2

    @pytest.mark.asyncio
    async def test_reset_clears_all(self, broker):
        """Vérifie que reset efface tout."""
        await broker.send_to_queue("q1", {"data": 1})
        async def handler(p):
            pass
        await broker.subscribe("t1", handler)

        broker.reset()

        stats = broker.get_stats()
        assert stats["messages_sent"] == 0
        assert len(stats["queues"]) == 0
        assert len(stats["topics"]) == 0

    @pytest.mark.asyncio
    async def test_get_queues(self, broker):
        """Vérifie la liste des queues."""
        await broker.send_to_queue("queue_a", {"data": 1})
        await broker.send_to_queue("queue_b", {"data": 2})
        await broker.send_to_queue("queue_b", {"data": 3})

        queues = broker.get_queues()

        assert len(queues) == 2
        queue_a = next(q for q in queues if q["name"] == "queue_a")
        queue_b = next(q for q in queues if q["name"] == "queue_b")

        assert queue_a["size"] == 1
        assert queue_b["size"] == 2


# ========== TESTS EVENT HANDLERS ==========

class TestEventHandlers:
    """Tests des handlers d'événements."""

    @pytest.mark.asyncio
    async def test_on_event_handler_called(self, broker):
        """Vérifie que les handlers d'événements sont appelés."""
        events = []

        def event_handler(event):
            events.append(event)

        broker.on_event(event_handler)
        await broker.send_to_queue("test", {"data": 1})

        assert len(events) >= 1
        assert events[0]["type"] == "queue_message"

    @pytest.mark.asyncio
    async def test_async_event_handler(self, broker):
        """Vérifie le support des handlers asynchrones."""
        events = []

        async def async_handler(event):
            events.append(event)

        broker.on_event(async_handler)
        await broker.send_to_queue("test", {"data": 1})

        assert len(events) >= 1


# ========== TESTS MESSAGE MODEL ==========

class TestMessageModel:
    """Tests du modèle Message."""

    def test_message_to_dict(self):
        """Vérifie la sérialisation du message."""
        message = Message(
            id="MSG-TEST123",
            payload={"key": "value"},
            source="test_source",
            headers={"header1": "val1"}
        )

        data = message.to_dict()

        assert data["id"] == "MSG-TEST123"
        assert data["payload"] == {"key": "value"}
        assert data["source"] == "test_source"
        assert data["headers"] == {"header1": "val1"}
        assert data["status"] == "pending"
        assert data["retries"] == 0

    def test_message_default_values(self):
        """Vérifie les valeurs par défaut du message."""
        message = Message(id="MSG-TEST", payload={})

        assert message.source == ""
        assert message.status == MessageStatus.PENDING
        assert message.retries == 0
        assert message.max_retries == 3
        assert message.error is None
        assert message.headers == {}


# ========== TESTS SINGLETON ==========

class TestSingleton:
    """Tests du singleton du broker."""

    def test_get_broker_returns_same_instance(self):
        """Vérifie que get_broker retourne la même instance."""
        broker1 = get_broker()
        broker2 = get_broker()

        assert broker1 is broker2

    @pytest.mark.asyncio
    async def test_reset_broker_creates_new_instance(self):
        """Vérifie que reset_broker crée une nouvelle instance."""
        broker1 = get_broker()
        await broker1.send_to_queue("test", {"data": 1})

        reset_broker()

        broker2 = get_broker()
        assert broker2.get_stats()["messages_sent"] == 0
