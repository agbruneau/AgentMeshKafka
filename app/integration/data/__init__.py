"""
Pilier Données - Intégration des données pour l'écosystème d'entreprise.

Ce module implémente les patterns d'intégration de données:
- ETL (Extract-Transform-Load)
- CDC (Change Data Capture)
- Data Quality (Contrôles qualité)
- MDM (Master Data Management)
- Data Lineage (Traçabilité)
"""

from .etl_pipeline import ETLPipeline, ETLStep, ETLStatus
from .cdc_simulator import CDCSimulator, ChangeEvent, ChangeOperation
from .data_quality import DataQuality, QualityRule, QualityDimension
from .mdm import MDM, GoldenRecord, MatchResult
from .lineage import DataLineage, LineageNode, LineageEdge

__all__ = [
    # ETL
    "ETLPipeline",
    "ETLStep",
    "ETLStatus",
    # CDC
    "CDCSimulator",
    "ChangeEvent",
    "ChangeOperation",
    # Data Quality
    "DataQuality",
    "QualityRule",
    "QualityDimension",
    # MDM
    "MDM",
    "GoldenRecord",
    "MatchResult",
    # Lineage
    "DataLineage",
    "LineageNode",
    "LineageEdge",
]
