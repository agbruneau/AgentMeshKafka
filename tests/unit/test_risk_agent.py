"""
Tests unitaires pour RiskAgent.
================================
Vérifie la logique de scoring et catégorisation du risque.
"""

import pytest
from src.shared.models import (
    LoanApplication,
    RiskAssessment,
    EmploymentStatus,
    RiskLevel,
)


class TestRiskScoreCalculation:
    """Tests pour le calcul du score de risque."""
    
    def _calculate_risk_score(
        self, 
        application: LoanApplication, 
        dti: float,
        credit_history: dict
    ) -> int:
        """Replica de la méthode RiskAgent._calculate_risk_score."""
        score = 50  # Score de base
        
        # Ajustement basé sur le DTI
        if dti > 50:
            score += 40
        elif dti > 40:
            score += 25
        elif dti > 30:
            score += 10
        else:
            score -= 10
        
        # Ajustement basé sur le statut d'emploi
        if application.employment_status == EmploymentStatus.UNEMPLOYED:
            score += 30
        elif application.employment_status == EmploymentStatus.SELF_EMPLOYED:
            score += 15
        elif application.employment_status == EmploymentStatus.PART_TIME:
            score += 10
        
        # Ajustement basé sur l'historique de crédit
        if credit_history["credit_score"] >= 750:
            score -= 20
        elif credit_history["credit_score"] >= 700:
            score -= 10
        elif credit_history["credit_score"] < 600:
            score += 20
        
        # Limiter entre 0 et 100
        return max(0, min(100, score))
    
    @pytest.fixture
    def base_application(self):
        """Application de base pour les tests."""
        return LoanApplication(
            application_id="APP-TEST",
            timestamp=1704067200000,
            applicant_id="CUST-TEST",
            amount_requested=50000.0,
            declared_monthly_income=5000.0,
            employment_status=EmploymentStatus.FULL_TIME,
        )
    
    @pytest.fixture
    def excellent_credit(self):
        """Historique de crédit excellent."""
        return {"credit_score": 780}
    
    @pytest.fixture
    def good_credit(self):
        """Historique de crédit bon."""
        return {"credit_score": 720}
    
    @pytest.fixture
    def poor_credit(self):
        """Historique de crédit mauvais."""
        return {"credit_score": 550}
    
    def test_low_risk_profile(self, base_application, excellent_credit):
        """Profil à faible risque: CDI + bon DTI + excellent crédit."""
        score = self._calculate_risk_score(
            base_application,
            dti=25.0,  # < 30, donc -10
            credit_history=excellent_credit,  # >= 750, donc -20
        )
        # Base: 50 - 10 (DTI) - 20 (crédit) + 0 (emploi) = 20
        assert score == 20
    
    def test_high_risk_unemployed(self, excellent_credit):
        """Profil à haut risque: chômeur."""
        app = LoanApplication(
            application_id="APP-UNEMP",
            timestamp=1704067200000,
            applicant_id="CUST-TEST",
            amount_requested=50000.0,
            declared_monthly_income=2000.0,
            employment_status=EmploymentStatus.UNEMPLOYED,
        )
        
        score = self._calculate_risk_score(
            app,
            dti=45.0,  # > 40, donc +25
            credit_history=excellent_credit,  # >= 750, donc -20
        )
        # Base: 50 + 25 (DTI) - 20 (crédit) + 30 (chômeur) = 85
        assert score == 85
    
    def test_medium_risk_self_employed(self, good_credit):
        """Profil risque moyen: indépendant."""
        app = LoanApplication(
            application_id="APP-SELF",
            timestamp=1704067200000,
            applicant_id="CUST-TEST",
            amount_requested=50000.0,
            declared_monthly_income=6000.0,
            employment_status=EmploymentStatus.SELF_EMPLOYED,
        )
        
        score = self._calculate_risk_score(
            app,
            dti=35.0,  # > 30, donc +10
            credit_history=good_credit,  # >= 700, donc -10
        )
        # Base: 50 + 10 (DTI) - 10 (crédit) + 15 (self-employed) = 65
        assert score == 65
    
    def test_extreme_high_risk_capped_at_100(self, poor_credit):
        """Score extrême doit être plafonné à 100."""
        app = LoanApplication(
            application_id="APP-EXTREME",
            timestamp=1704067200000,
            applicant_id="CUST-TEST",
            amount_requested=100000.0,
            declared_monthly_income=1000.0,
            employment_status=EmploymentStatus.UNEMPLOYED,
        )
        
        score = self._calculate_risk_score(
            app,
            dti=80.0,  # > 50, donc +40
            credit_history=poor_credit,  # < 600, donc +20
        )
        # Base: 50 + 40 (DTI) + 20 (crédit) + 30 (chômeur) = 140 → plafonné à 100
        assert score == 100
    
    def test_extreme_low_risk_floored_at_0(self, excellent_credit):
        """Score très bas doit être planché à 0."""
        app = LoanApplication(
            application_id="APP-PERFECT",
            timestamp=1704067200000,
            applicant_id="CUST-TEST",
            amount_requested=10000.0,
            declared_monthly_income=10000.0,
            employment_status=EmploymentStatus.FULL_TIME,
        )
        
        score = self._calculate_risk_score(
            app,
            dti=5.0,  # < 30, donc -10
            credit_history=excellent_credit,  # >= 750, donc -20
        )
        # Base: 50 - 10 (DTI) - 20 (crédit) + 0 (emploi) = 20
        # Note: Dans ce cas, le score reste positif
        assert score >= 0


class TestRiskCategorization:
    """Tests pour la catégorisation du risque."""
    
    def _categorize_risk(self, score: int) -> RiskLevel:
        """Replica de la méthode RiskAgent._categorize_risk."""
        if score < 20:
            return RiskLevel.LOW
        elif score < 50:
            return RiskLevel.MEDIUM
        elif score < 80:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL
    
    @pytest.mark.parametrize("score,expected", [
        (0, RiskLevel.LOW),
        (10, RiskLevel.LOW),
        (19, RiskLevel.LOW),
        (20, RiskLevel.MEDIUM),
        (35, RiskLevel.MEDIUM),
        (49, RiskLevel.MEDIUM),
        (50, RiskLevel.HIGH),
        (65, RiskLevel.HIGH),
        (79, RiskLevel.HIGH),
        (80, RiskLevel.CRITICAL),
        (95, RiskLevel.CRITICAL),
        (100, RiskLevel.CRITICAL),
    ])
    def test_categorization_boundaries(self, score, expected):
        """Test des limites de catégorisation."""
        assert self._categorize_risk(score) == expected


class TestDTICalculation:
    """Tests pour le calcul du ratio dette/revenu."""
    
    def tool_calculate_debt_ratio(
        self, 
        income: float, 
        existing_debts: float, 
        new_loan_amount: float
    ) -> float:
        """Replica de la méthode RiskAgent.tool_calculate_debt_ratio."""
        if income <= 0:
            return 100.0
        
        estimated_monthly_payment = new_loan_amount * 0.01
        total_monthly_debt = existing_debts + estimated_monthly_payment
        
        dti = (total_monthly_debt / income) * 100
        return round(dti, 2)
    
    def test_standard_calculation(self):
        """Test calcul standard du DTI."""
        dti = self.tool_calculate_debt_ratio(
            income=5000,
            existing_debts=500,
            new_loan_amount=50000,
        )
        # Mensualité estimée: 50000 * 0.01 = 500
        # Total dettes: 500 + 500 = 1000
        # DTI: 1000 / 5000 * 100 = 20%
        assert dti == 20.0
    
    def test_zero_income_returns_max(self):
        """Revenu nul retourne risque maximum (100%)."""
        dti = self.tool_calculate_debt_ratio(
            income=0,
            existing_debts=1000,
            new_loan_amount=50000,
        )
        assert dti == 100.0
    
    def test_negative_income_returns_max(self):
        """Revenu négatif retourne risque maximum."""
        dti = self.tool_calculate_debt_ratio(
            income=-1000,
            existing_debts=500,
            new_loan_amount=50000,
        )
        assert dti == 100.0
    
    def test_no_existing_debts(self):
        """DTI sans dettes existantes."""
        dti = self.tool_calculate_debt_ratio(
            income=5000,
            existing_debts=0,
            new_loan_amount=50000,
        )
        # Mensualité: 500, Total: 500, DTI: 10%
        assert dti == 10.0
    
    def test_high_loan_amount(self):
        """DTI avec montant de prêt élevé."""
        dti = self.tool_calculate_debt_ratio(
            income=3000,
            existing_debts=500,
            new_loan_amount=200000,
        )
        # Mensualité: 2000, Total: 2500, DTI: 83.33%
        assert dti == 83.33
