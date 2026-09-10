"""Production dashboard state, request-budget, and bounded-list contracts."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.panel.usage_routes import get_usage_stats, get_usage_stats_page

ROOT = BACKEND_DIR.parent
DASHBOARD_FRAGMENT = ROOT / "frontend/fragments/pages/dashboard.html"
DASHBOARD_SCRIPT = ROOT / "frontend/js/features/dashboard.js"
DASHBOARD_STYLES = ROOT / "frontend/css/observability.css"


class ProductionDashboardContractTests(unittest.TestCase):
    def _source(self, path: Path) -> str:
        self.assertTrue(path.is_file(), f"Missing dashboard asset: {path}")
        return path.read_text(encoding="utf-8")

    def _run_state_contract(self, assertions: str) -> None:
        node = shutil.which("node")
        if node is None:
            self.skipTest("Node.js is required for the dashboard state contract.")
        harness = f"""
const fs = require('fs');
const vm = require('vm');
const source = fs.readFileSync({json.dumps(str(DASHBOARD_SCRIPT))}, 'utf8');
vm.runInThisContext(source + `\n;globalThis.__dashboardState = deriveDashboardState; globalThis.__renderDashboardTimeline = renderTimelineChart;`);
const derive = globalThis.__dashboardState;
function assert(condition, message) {{ if (!condition) throw new Error(message); }}
{assertions}
"""
        result = subprocess.run(
            [node, "-e", harness],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)

    def test_state_fixtures_identify_one_clear_next_action(self):
        self._run_state_contract(
            """
const fixtures = [
    [{ total_files: 0, active_files: 0, total_calls: 0 }, { status: 'no_data' }, 'first_time', 'providers'],
    [{ total_files: 2, active_files: 0, total_calls: 8 }, { status: 'no_data' }, 'no_provider', 'pool'],
    [{ total_files: 2, active_files: 2, total_calls: 40 }, { status: 'healthy' }, 'healthy', 'activity'],
    [{ total_files: 2, active_files: 2, total_calls: 100, failed_calls: 9 }, { status: 'healthy' }, 'healthy', 'activity'],
    [{ total_files: 2, active_files: 1, total_calls: 40 }, { status: 'critical' }, 'degraded', 'activity'],
];
for (const [aggregate, health, expectedState, expectedTab] of fixtures) {
    const result = derive(aggregate, health);
    assert(result.state === expectedState, `${expectedState}: received ${result.state}`);
    assert(result.actionTab === expectedTab, `${expectedState}: received ${result.actionTab}`);
    assert(result.titleKey && result.descriptionKey && result.actionKey, `${expectedState}: incomplete guidance`);
}
"""
        )

    def test_primary_dashboard_surfaces_match_the_production_information_order(self):
        fragment = self._source(DASHBOARD_FRAGMENT)

        for element_id in (
            "dashboardReadiness",
            "dashboardReadinessTitle",
            "dashboardReadinessAction",
            "dashboardQuickActions",
            "totalCostUsd",
            "dashboardP95Latency",
            "recentActivityList",
        ):
            self.assertIn(f'id="{element_id}"', fragment)
        self.assertNotIn('data-i18n="slo.kicker"', fragment)
        self.assertNotIn("Service objectives", fragment)
        self.assertRegex(fragment, r"<details[^>]+class=\"[^\"]*slo-export-status")
        self.assertLess(
            fragment.index('id="dashboardReadiness"'), fragment.index('id="dashboardStats"')
        )
        self.assertLess(
            fragment.index('id="providerHealthCard"'), fragment.index('id="operationalHealthCard"')
        )

    def test_dashboard_load_has_a_fixed_request_budget_and_bounded_lists(self):
        source = self._source(DASHBOARD_SCRIPT)

        self.assertEqual(len(re.findall(r"\bfetch\(", source)), 4)
        self.assertIn("./api/usage/stats/page?", source)
        self.assertIn("page_size=100", source)
        self.assertIn("./api/traces?page_size=5", source)
        self.assertIn("routes.slice(0, 10)", source)
        self.assertIn("traces.slice(0, DASHBOARD_RECENT_ACTIVITY_PAGE_SIZE)", source)

    def test_dashboard_header_collapses_at_the_tablet_breakpoint(self):
        styles = self._source(DASHBOARD_STYLES)

        self.assertRegex(
            styles,
            r"(?s)@media \(max-width: 960px\).*?#dashboardTab \.page-header\s*\{\s*display: grid;",
        )

    def test_empty_timeline_reports_zero_peak_requests(self):
        self._run_state_contract(
            """
const wrapper = { innerHTML: '' };
const maxInfo = { textContent: '' };
globalThis.document = { getElementById: (id) => id === 'timelineBarsWrapper' ? wrapper : maxInfo };
globalThis.t = (_key, values = {}) => String(values.count ?? '');
globalThis.escapeHtml = (value) => String(value);
globalThis.getActiveLocale = () => 'en-US';
globalThis.__renderDashboardTimeline([{ requests: 0, successful_requests: 0, failed_requests: 0, tokens: 0 }]);
assert(maxInfo.textContent === '0', `zero traffic peak: received ${maxInfo.textContent}`);
"""
        )


class BoundedUsageDashboardApiTests(unittest.IsolatedAsyncioTestCase):
    async def test_usage_stats_returns_only_the_requested_bounded_page(self):
        rows = {
            "low.json": {"calls": 1},
            "high.json": {"calls": 9},
            "middle.json": {"calls": 4},
        }
        with patch(
            "core.panel.usage_routes.get_stats_for_period",
            new=AsyncMock(return_value=rows),
        ):
            response = await get_usage_stats_page(period="1d", page_size=2, token="panel")
            legacy = await get_usage_stats(period="1d", token="panel")

        self.assertEqual(legacy["data"], rows)

        self.assertEqual(list(response["data"]), ["high.json", "middle.json"])
        self.assertEqual(response["page_size"], 2)
        self.assertEqual(response["total_items"], 3)
        self.assertTrue(response["has_more"])


if __name__ == "__main__":
    unittest.main()
