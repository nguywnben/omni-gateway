"""Static security and interaction contracts for the audit operations console."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.panel.root import serve_control_panel

ROOT = BACKEND_DIR.parent
AUDIT_SCRIPT_PATH = ROOT / "frontend" / "js" / "features" / "audit.js"
AUDIT_STYLE_PATH = ROOT / "frontend" / "css" / "audit.css"


class AuditConsoleContractTests(unittest.TestCase):
    def test_audit_surface_is_reachable_and_semantic(self):
        body = serve_control_panel().body.decode("utf-8")

        for element_id in (
            "auditTab",
            "auditFilterForm",
            "auditEventList",
            "auditEventStatus",
            "auditPreviousPage",
            "auditNextPage",
            "auditDetailDialog",
            "auditRetentionForm",
        ):
            self.assertIn(f'id="{element_id}"', body)
        self.assertIn('data-tab="audit"', body)
        self.assertIn('data-i18n="audit.observability"', body)
        self.assertIn('aria-live="polite"', body)
        self.assertIn('<dialog id="auditDetailDialog"', body)

    def test_audit_client_uses_bounded_server_contracts(self):
        source = AUDIT_SCRIPT_PATH.read_text(encoding="utf-8")

        self.assertIn("fetch(`./api/audit/events?${params.toString()}`", source)
        self.assertIn("eventAbortController", source)
        self.assertIn("eventRequestId", source)
        self.assertIn("fetch('./api/audit/retention')", source)
        self.assertIn("method: 'PUT'", source)
        self.assertIn("./api/audit/export", source)
        self.assertIn("params.set('format', format)", source)
        self.assertIn("page_size", source)
        self.assertIn("cursorStack", source)
        self.assertIn("next_cursor", source)

    def test_audit_client_revalidates_and_renders_untrusted_records_safely(self):
        source = AUDIT_SCRIPT_PATH.read_text(encoding="utf-8")

        for field in (
            "schema_version",
            "event_id",
            "occurred_at",
            "request_id",
            "actor_type",
            "actor_fingerprint",
            "action",
            "target_type",
            "target_fingerprint",
            "outcome",
            "change_codes",
        ):
            self.assertIn(f"'{field}'", source)
        self.assertIn("textContent", source)
        self.assertNotIn("innerHTML", source)
        for forbidden in ("prompt", "api_key", "credential_name", "raw_secret"):
            self.assertNotIn(forbidden, source)

    def test_persisted_filters_exclude_correlating_identifiers(self):
        source = AUDIT_SCRIPT_PATH.read_text(encoding="utf-8")
        persistence_block = source.split("const AUDIT_PERSISTED_FILTERS", 1)[1].split("];", 1)[0]

        for safe_field in ("actor_types", "actions", "target_types", "outcomes", "page_size"):
            self.assertIn(f"'{safe_field}'", persistence_block)
        for transient_field in (
            "request_id",
            "actor_fingerprints",
            "target_fingerprints",
            "occurred_after",
            "occurred_before",
            "cursor",
        ):
            self.assertNotIn(f"'{transient_field}'", persistence_block)

    def test_audit_export_filename_is_allowlisted(self):
        source = AUDIT_SCRIPT_PATH.read_text(encoding="utf-8")
        export_block = source.split("async function exportAuditEvents", 1)[1].split(
            "async function saveAuditRetention", 1
        )[0]

        self.assertIn("omni-audit-", source)
        self.assertIn("URL.createObjectURL", source)
        self.assertIn("URL.revokeObjectURL", source)
        self.assertIn("AUDIT_EXPORT_FILENAME_PATTERN", source)
        self.assertIn("const filters = AuditConsoleState.filters", export_block)
        self.assertNotIn("readAuditFilters()", export_block)

    def test_audit_has_dedicated_responsive_styles(self):
        source = AUDIT_STYLE_PATH.read_text(encoding="utf-8")

        self.assertIn(".audit-layout", source)
        self.assertIn(".audit-event-card", source)
        self.assertIn("@media (max-width: 760px)", source)
        self.assertIn(":focus-visible", source)


if __name__ == "__main__":
    unittest.main()
