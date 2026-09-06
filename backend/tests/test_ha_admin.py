from __future__ import annotations

import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.ha_activation import verify_ha_activation_record
from ha_admin import _parser


class HaAdminTests(unittest.TestCase):
    def test_mutations_are_dry_run_by_default(self) -> None:
        arguments = _parser().parse_args(["drain"])
        self.assertFalse(arguments.apply)

    def test_epoch_mutations_accept_explicit_operation_id(self) -> None:
        arguments = _parser().parse_args(
            ["advance-epoch", "--apply", "--operation-id", "epoch-op-00000001"]
        )
        self.assertTrue(arguments.apply)
        self.assertEqual(arguments.operation_id, "epoch-op-00000001")

    def test_reconciliation_page_size_is_closed_and_bounded(self) -> None:
        arguments = _parser().parse_args(["reconcile", "--page-size", "17"])
        self.assertEqual(arguments.page_size, 17)
        with self.assertRaises(SystemExit):
            _parser().parse_args(["reconcile", "--quota-page-size", "257"])

    def test_activation_allowlist_is_closed_before_w419(self) -> None:
        self.assertFalse(verify_ha_activation_record("act_" + ("a" * 32)))


if __name__ == "__main__":
    unittest.main()
