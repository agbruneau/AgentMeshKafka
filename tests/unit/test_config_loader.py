"""
Tests unitaires pour le config loader.
=======================================
Vérifie le chargement de configuration et les overrides.
"""

import os
import tempfile
from pathlib import Path

import pytest
import yaml


class TestConfigLoader:
    """Tests pour le chargement de configuration."""
    
    @pytest.fixture
    def temp_config(self, tmp_path):
        """Crée un fichier de config temporaire."""
        config = {
            "agents": {
                "risk_agent": {
                    "model": "claude-test",
                    "temperature": 0.5,
                }
            },
            "thresholds": {
                "auto_approve_score": 20,
                "auto_reject_score": 80,
            }
        }
        
        config_path = tmp_path / "test_config.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config, f)
        
        return config_path
    
    def test_load_config_basic(self, temp_config):
        """Test chargement de config basique."""
        from src.shared.config_loader import load_config
        
        config = load_config(temp_config)
        
        assert config["agents"]["risk_agent"]["model"] == "claude-test"
        assert config["thresholds"]["auto_approve_score"] == 20
    
    def test_get_agent_config(self, temp_config):
        """Test récupération de config agent."""
        from src.shared.config_loader import load_config, get_agent_config
        
        config = load_config(temp_config)
        agent_config = get_agent_config("risk_agent", config)
        
        assert agent_config["model"] == "claude-test"
        assert agent_config["temperature"] == 0.5
    
    def test_get_thresholds(self, temp_config):
        """Test récupération des seuils."""
        from src.shared.config_loader import load_config, get_thresholds
        
        config = load_config(temp_config)
        thresholds = get_thresholds(config)
        
        assert thresholds["auto_approve_score"] == 20
        assert thresholds["auto_reject_score"] == 80
    
    def test_missing_config_raises_error(self, tmp_path):
        """Test erreur si fichier manquant."""
        from src.shared.config_loader import load_config
        
        missing_path = tmp_path / "missing.yaml"
        
        with pytest.raises(FileNotFoundError):
            load_config(missing_path)
    
    def test_env_override_string(self, temp_config, monkeypatch):
        """Test override par variable d'environnement (string)."""
        from src.shared.config_loader import load_config
        
        # Override le modèle via env var
        monkeypatch.setenv("AGENTS__RISK_AGENT__MODEL", "claude-override")
        
        config = load_config(temp_config)
        
        assert config["agents"]["risk_agent"]["model"] == "claude-override"
    
    def test_env_override_int(self, temp_config, monkeypatch):
        """Test override par variable d'environnement (int)."""
        from src.shared.config_loader import load_config
        
        monkeypatch.setenv("THRESHOLDS__AUTO_APPROVE_SCORE", "25")
        
        config = load_config(temp_config)
        
        assert config["thresholds"]["auto_approve_score"] == 25
        assert isinstance(config["thresholds"]["auto_approve_score"], int)
    
    def test_env_override_float(self, temp_config, monkeypatch):
        """Test override par variable d'environnement (float)."""
        from src.shared.config_loader import load_config
        
        monkeypatch.setenv("AGENTS__RISK_AGENT__TEMPERATURE", "0.8")
        
        config = load_config(temp_config)
        
        assert config["agents"]["risk_agent"]["temperature"] == 0.8
        assert isinstance(config["agents"]["risk_agent"]["temperature"], float)


class TestDefaultThresholds:
    """Tests pour les valeurs par défaut."""
    
    def test_default_thresholds_when_missing(self, tmp_path):
        """Test valeurs par défaut si config incomplète."""
        from src.shared.config_loader import load_config, get_thresholds
        
        # Config sans thresholds
        config = {"agents": {}}
        config_path = tmp_path / "minimal.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config, f)
        
        loaded = load_config(config_path)
        thresholds = get_thresholds(loaded)
        
        # Devrait utiliser les valeurs par défaut
        assert thresholds["auto_approve_score"] == 20
        assert thresholds["auto_reject_score"] == 80
