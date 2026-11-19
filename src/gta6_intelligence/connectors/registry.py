"""Connectors that can be run.

Registering a connector does not by itself allow collection: the runner also
refuses sources whose status is blocked, deferred, conditional or disabled.
"""

from gta6_intelligence.connectors.base import BaseConnector
from gta6_intelligence.connectors.files import EventLedgerConnector, GoogleTrendsInboxConnector
from gta6_intelligence.connectors.gdelt import GdeltConnector

CONNECTORS: dict[str, type[BaseConnector]] = {
    c.source_id: c for c in (GdeltConnector, EventLedgerConnector, GoogleTrendsInboxConnector)
}
