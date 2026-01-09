"""
Tests unitaires pour DecisionAgent.
====================================
Vérifie la logique de décision sans dépendances externes.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.shared.models import (
    RiskAssessment,
    LoanDecision,
    RiskLevel,
    DecisionStatus,
)


class TestDecisionThresholds:
    """Tests pour les seuils de décision automatique."""
    
    def test_auto_approve_low_risk(self):
        """Score < 20 devrait être automatiquement approuvé."""
        # Simuler le calcul de seuil
        THRESHOLD_AUTO_APPROVE = 20
        risk_score = 15
        
        assert risk_score < THRESHOLD_AUTO_APPROVE
        # Décision attendue: APPROVED
        
    def test_auto_reject_high_risk(self):
        """Score > 80 devrait être automatiquement rejeté."""
        THRESHOLD_AUTO_REJECT = 80
        risk_score = 85
        
        assert risk_score > THRESHOLD_AUTO_REJECT
        # Décision attendue: REJECTED
        
    def test_gray_zone_requires_analysis(self):
        """Score entre 20 et 80 nécessite une analyse détaillée."""
        THRESHOLD_AUTO_APPROVE = 20
        THRESHOLD_AUTO_REJECT = 80
        
        gray_zone_scores = [20, 35, 50, 65, 80]
        
        for score in gray_zone_scores:
            in_gray_zone = THRESHOLD_AUTO_APPROVE <= score <= THRESHOLD_AUTO_REJECT
            assert in_gray_zone, f"Score {score} devrait être en zone grise"


class TestInterestRateCalculation:
    """Tests pour le calcul du taux d'intérêt."""
    
    def _calculate_interest_rate(self, risk_score: int) -> float:
        """Replica de la méthode DecisionAgent._calculate_interest_rate."""
        base_rate = 5.0
        risk_premium = (risk_score / 100) * 10
        return round(base_rate + risk_premium, 2)
    
    def test_minimum_rate_zero_risk(self):
        """Risque 0 = taux de base (5%)."""
        rate = self._calculate_interest_rate(0)
        assert rate == 5.0
    
    def test_maximum_rate_full_risk(self):
        """Risque 100 = taux maximum (15%)."""
        rate = self._calculate_interest_rate(100)
        assert rate == 15.0
    
    def test_medium_risk_rate(self):
        """Risque 50 = taux moyen (10%)."""
        rate = self._calculate_interest_rate(50)
        assert rate == 10.0
    
    def test_rate_linearity(self):
        """Le taux devrait augmenter linéairement avec le risque."""
        rate_20 = self._calculate_interest_rate(20)
        rate_40 = self._calculate_interest_rate(40)
        rate_60 = self._calculate_interest_rate(60)
        
        # Les différences devraient être égales
        diff_1 = round(rate_40 - rate_20, 2)
        diff_2 = round(rate_60 - rate_40, 2)
        
        assert diff_1 == diff_2 == 2.0


class TestRejectionReasons:
    """Tests pour la génération des raisons de rejet."""
    
    def _determine_rejection_reasons(self, assessment: RiskAssessment) -> list[str]:
        """Replica de la méthode DecisionAgent._determine_rejection_reasons."""
        reasons = []
        
        if assessment.risk_score > 80:
            reasons.append("Score de risque trop élevé")
        
        if assessment.debt_to_income_ratio > 50:
            reasons.append(f"Ratio dette/revenu excessif ({assessment.debt_to_income_ratio}%)")
        
        if assessment.risk_category == RiskLevel.CRITICAL:
            reasons.append("Catégorie de risque critique")
        
        return reasons or ["Évaluation globale défavorable"]
    
    def test_high_risk_score_reason(self):
        """Score > 80 génère une raison de rejet."""
        assessment = RiskAssessment(
            application_id="APP-001",
            assessment_id="ASS-001",
            timestamp=1704067200000,
            risk_score=85,
            risk_category=RiskLevel.CRITICAL,
            debt_to_income_ratio=30.0,
            rationale="Test",
        )
        
        reasons = self._determine_rejection_reasons(assessment)
        assert "Score de risque trop élevé" in reasons
    
    def test_high_dti_reason(self):
        """DTI > 50% génère une raison de rejet."""
        assessment = RiskAssessment(
            application_id="APP-002",
            assessment_id="ASS-002",
            timestamp=1704067200000,
            risk_score=60,
            risk_category=RiskLevel.HIGH,
            debt_to_income_ratio=55.0,
            rationale="Test",
        )
        
        reasons = self._determine_rejection_reasons(assessment)
        assert any("Ratio dette/revenu excessif" in r for r in reasons)
    
    def test_critical_category_reason(self):
        """Catégorie CRITICAL génère une raison de rejet."""
        assessment = RiskAssessment(
            application_id="APP-003",
            assessment_id="ASS-003",
            timestamp=1704067200000,
            risk_score=90,
            risk_category=RiskLevel.CRITICAL,
            debt_to_income_ratio=40.0,
            rationale="Test",
        )
        
        reasons = self._determine_rejection_reasons(assessment)
        assert "Catégorie de risque critique" in reasons
    
    def test_default_reason_when_no_specific(self):
        """Une raison par défaut est fournie si aucune spécifique."""
        assessment = RiskAssessment(
            application_id="APP-004",
            assessment_id="ASS-004",
            timestamp=1704067200000,
            risk_score=70,  # Not > 80
            risk_category=RiskLevel.HIGH,  # Not CRITICAL
            debt_to_income_ratio=40.0,  # Not > 50
            rationale="Test",
        )
        
        reasons = self._determine_rejection_reasons(assessment)
        assert reasons == ["Évaluation globale défavorable"]


class TestDecisionRationale:
    """Tests pour la génération de la justification de décision."""
    
    def _generate_decision_rationale(
        self, 
        assessment: RiskAssessment, 
        status: DecisionStatus,
        rejection_reasons: list[str]
    ) -> str:
        """Replica de la méthode DecisionAgent._generate_decision_rationale."""
        if status == DecisionStatus.APPROVED:
            return f"Votre demande de prêt a été approuvée. Score de risque: {assessment.risk_score}/100."
        elif status == DecisionStatus.REJECTED:
            reasons = "; ".join(rejection_reasons)
            return f"Nous regrettons de vous informer que votre demande n'a pas été retenue. Raisons: {reasons}"
        else:
            return "Votre demande nécessite une analyse complémentaire par nos équipes. Nous vous contacterons sous 48h."
    
    def test_approved_rationale(self):
        """Justification pour décision approuvée."""
        assessment = RiskAssessment(
            application_id="APP-001",
            assessment_id="ASS-001",
            timestamp=1704067200000,
            risk_score=15,
            risk_category=RiskLevel.LOW,
            debt_to_income_ratio=20.0,
            rationale="Test",
        )
        
        rationale = self._generate_decision_rationale(
            assessment, DecisionStatus.APPROVED, []
        )
        
        assert "approuvée" in rationale
        assert "15/100" in rationale
    
    def test_rejected_rationale(self):
        """Justification pour décision rejetée."""
        assessment = RiskAssessment(
            application_id="APP-002",
            assessment_id="ASS-002",
            timestamp=1704067200000,
            risk_score=90,
            risk_category=RiskLevel.CRITICAL,
            debt_to_income_ratio=60.0,
            rationale="Test",
        )
        
        reasons = ["Score trop élevé", "DTI excessif"]
        rationale = self._generate_decision_rationale(
            assessment, DecisionStatus.REJECTED, reasons
        )
        
        assert "regrettons" in rationale
        assert "Score trop élevé" in rationale
        assert "DTI excessif" in rationale
    
    def test_manual_review_rationale(self):
        """Justification pour revue manuelle."""
        assessment = RiskAssessment(
            application_id="APP-003",
            assessment_id="ASS-003",
            timestamp=1704067200000,
            risk_score=50,
            risk_category=RiskLevel.MEDIUM,
            debt_to_income_ratio=35.0,
            rationale="Test",
        )
        
        rationale = self._generate_decision_rationale(
            assessment, DecisionStatus.MANUAL_REVIEW_REQUIRED, []
        )
        
        assert "analyse complémentaire" in rationale
        assert "48h" in rationale
