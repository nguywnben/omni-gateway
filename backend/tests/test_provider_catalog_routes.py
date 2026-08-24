"""Management provider catalog contract tests."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.panel.providers.catalog import get_provider_catalog, router
from core.provider_registry import (
    CREDENTIAL_OPERATIONS,
    list_credential_variant_capabilities,
    list_provider_capabilities,
)
from core.utils import verify_panel_token


class ProviderCatalogRouteTests(unittest.IsolatedAsyncioTestCase):
    async def test_catalog_adds_variant_operations_without_changing_provider_records(self):
        response = await get_provider_catalog(token="session")
        body = json.loads(response.body)

        self.assertEqual(body["providers"], list_provider_capabilities())
        self.assertEqual(
            body["credential_variants"], list_credential_variant_capabilities()
        )
        self.assertEqual(body["operation_vocabulary"], sorted(CREDENTIAL_OPERATIONS))

    async def test_catalog_route_remains_authenticated_and_typed(self):
        route = next(route for route in router.routes if route.path == "/api/providers")

        self.assertTrue(
            any(dependency.call is verify_panel_token for dependency in route.dependant.dependencies)
        )
        self.assertIsNotNone(route.response_model)


if __name__ == "__main__":
    unittest.main()
