"""Management provider catalog contract tests."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.panel.providers.catalog import (
    get_provider_capability_matrix,
    get_provider_catalog,
    router,
)
from core.provider_registry import (
    CREDENTIAL_OPERATIONS,
    INFERENCE_PROTOCOLS,
    LEGACY_CREDENTIAL_OPERATIONS,
    list_credential_variant_capabilities,
    list_legacy_credential_variant_capabilities,
    list_provider_capabilities,
)
from core.utils import verify_panel_token


class ProviderCatalogRouteTests(unittest.IsolatedAsyncioTestCase):
    async def test_legacy_catalog_remains_unchanged(self):
        response = await get_provider_catalog(token="session")
        body = json.loads(response.body)

        self.assertEqual(body["providers"], list_provider_capabilities())
        self.assertEqual(body["credential_variants"], list_legacy_credential_variant_capabilities())
        self.assertEqual(body["operation_vocabulary"], sorted(LEGACY_CREDENTIAL_OPERATIONS))

        self.assertNotIn("schema_version", body)
        self.assertNotIn("inference_protocol_vocabulary", body)

    async def test_capability_matrix_is_versioned_and_complete(self):
        response = await get_provider_capability_matrix(token="session")
        body = json.loads(response.body)

        self.assertEqual(body["credential_variants"], list_credential_variant_capabilities())
        self.assertEqual(body["operation_vocabulary"], sorted(CREDENTIAL_OPERATIONS))
        self.assertEqual(body["inference_protocol_vocabulary"], sorted(INFERENCE_PROTOCOLS))
        self.assertEqual(body["schema_version"], 2)

    async def test_catalog_route_remains_authenticated_and_typed(self):
        for path in ("/api/providers", "/api/providers/capabilities"):
            route = next(route for route in router.routes if route.path == path)

            self.assertTrue(
                any(
                    dependency.call is verify_panel_token
                    for dependency in route.dependant.dependencies
                )
            )
            self.assertIsNotNone(route.response_model)


if __name__ == "__main__":
    unittest.main()
