"""Connectors that can be run. Empty until the first connector lands in Phase 2.

Only sources whose status allows collection may be registered here.
"""

from gta6_intelligence.connectors.base import BaseConnector

CONNECTORS: dict[str, type[BaseConnector]] = {}
