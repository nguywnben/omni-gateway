from __future__ import annotations

import dataclasses
import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.coordination import QuotaReconciliationResult
from core.ha_reconciliation import (
    RECONCILIATION_COMPONENTS,
    HaReconciliationCoordinator,
    ReconciliationComponent,
    ReconciliationPage,
    ReconciliationReceipt,
    advance_reconciliation_receipt,
    new_reconciliation_receipt,
    sign_reconciliation_receipt,
    verify_reconciliation_receipt,
    verify_reconciliation_receipt_signature,
)

HEX_A = "a" * 64
HEX_B = "b" * 64
KEY = b"k" * 32


class ReconciliationReceiptTests(unittest.TestCase):
    def receipt(self) -> ReconciliationReceipt:
        return new_reconciliation_receipt(
            deployment_id="gateway-east-01",
            namespace_digest=HEX_A,
            prior_epoch=1,
            target_epoch=2,
            operation_id="reconcile-operation-1",
            manifest_checksum=HEX_B,
            migration_plan_id="dmg_" + ("1" * 32),
            migration_checkpoint_revision=7,
            migration_checkpoint_checksum="c" * 64,
        )

    def test_new_receipt_has_every_component_in_closed_order(self) -> None:
        receipt = self.receipt()

        self.assertEqual(
            tuple(component.component for component in receipt.components),
            RECONCILIATION_COMPONENTS,
        )
        self.assertFalse(receipt.complete)
        self.assertTrue(all(not component.started for component in receipt.components))

    def test_pages_are_bounded_ordered_and_resume_with_a_canonical_digest(self) -> None:
        receipt = self.receipt()
        page = ReconciliationPage(
            ReconciliationComponent.QUOTA,
            input_cursor=None,
            scanned=256,
            complete=False,
            cursor="opaque-next",
            snapshot_digest=HEX_A,
            challenged_operations=1,
        )
        receipt = advance_reconciliation_receipt(receipt, page)
        progress = receipt.components[0]
        self.assertEqual(progress.pages, 1)
        self.assertEqual(progress.scanned, 256)
        self.assertNotEqual(progress.digest, HEX_A)

        with self.assertRaisesRegex(ValueError, "cursor"):
            advance_reconciliation_receipt(
                receipt,
                dataclasses.replace(page, input_cursor="wrong-cursor"),
            )
        with self.assertRaisesRegex(ValueError, "order"):
            advance_reconciliation_receipt(
                receipt,
                ReconciliationPage(
                    ReconciliationComponent.USAGE_LIABILITY,
                    None,
                    0,
                    True,
                    None,
                    HEX_A,
                    1,
                ),
            )

    def test_zero_records_still_requires_a_positive_challenge(self) -> None:
        with self.assertRaisesRegex(ValueError, "challenge"):
            ReconciliationPage(
                ReconciliationComponent.QUOTA,
                input_cursor=None,
                scanned=0,
                complete=True,
                cursor=None,
                snapshot_digest=HEX_A,
                challenged_operations=0,
            )

    def test_usage_component_cannot_advance_while_liability_is_outstanding(self) -> None:
        receipt = advance_reconciliation_receipt(
            self.receipt(),
            ReconciliationPage(
                ReconciliationComponent.QUOTA,
                None,
                0,
                True,
                None,
                HEX_A,
                1,
            ),
        )
        with self.assertRaisesRegex(ValueError, "liability"):
            advance_reconciliation_receipt(
                receipt,
                ReconciliationPage(
                    ReconciliationComponent.USAGE_LIABILITY,
                    None,
                    1,
                    True,
                    None,
                    HEX_A,
                    1,
                    liability_nanos=1,
                ),
            )
        self.assertFalse(receipt.components[1].started)
        with self.assertRaisesRegex(ValueError, "liability"):
            advance_reconciliation_receipt(
                receipt,
                ReconciliationPage(
                    ReconciliationComponent.USAGE_LIABILITY,
                    None,
                    1,
                    True,
                    None,
                    HEX_A,
                    1,
                    active_reservations=1,
                ),
            )

    def test_signature_rejects_tamper_wrong_key_and_incomplete_receipts(self) -> None:
        receipt = self.receipt()
        partial = advance_reconciliation_receipt(
            receipt,
            ReconciliationPage(
                ReconciliationComponent.QUOTA,
                None,
                0,
                True,
                None,
                HEX_A,
                1,
            ),
        )
        signed_partial = sign_reconciliation_receipt(partial, KEY)
        self.assertTrue(verify_reconciliation_receipt_signature(signed_partial, KEY))
        self.assertFalse(verify_reconciliation_receipt(signed_partial, KEY))
        self.assertFalse(
            verify_reconciliation_receipt_signature(
                dataclasses.replace(signed_partial, manifest_checksum="d" * 64),
                KEY,
            )
        )

        for component in RECONCILIATION_COMPONENTS:
            receipt = advance_reconciliation_receipt(
                receipt,
                ReconciliationPage(component, None, 0, True, None, HEX_A, 1),
            )
        signed = sign_reconciliation_receipt(receipt, KEY)
        decoded = ReconciliationReceipt.from_dict(signed.to_dict())

        self.assertTrue(verify_reconciliation_receipt(decoded, KEY))
        self.assertFalse(verify_reconciliation_receipt(decoded, b"z" * 32))
        self.assertFalse(
            verify_reconciliation_receipt(
                dataclasses.replace(decoded, manifest_checksum="d" * 64),
                KEY,
            )
        )
        self.assertFalse(verify_reconciliation_receipt(self.receipt(), KEY))

    def test_unknown_duplicate_missing_and_invalid_component_records_fail_closed(self) -> None:
        receipt = self.receipt()
        raw = receipt.to_dict()
        raw["unknown"] = True
        with self.assertRaises(ValueError):
            ReconciliationReceipt.from_dict(raw)

        raw = self.receipt().to_dict()
        raw["components"] = raw["components"][:-1]
        with self.assertRaises(ValueError):
            ReconciliationReceipt.from_dict(raw)


class ReconciliationCoordinatorTests(unittest.IsolatedAsyncioTestCase):
    async def test_quota_operation_distinguishes_revisited_cursor_pages(self) -> None:
        class QuotaStore:
            def __init__(self) -> None:
                self.operations: list[str] = []

            async def reconcile_quota_state(self, **kwargs):
                self.operations.append(kwargs["operation_id"])
                return QuotaReconciliationResult(0, False, "revisited", HEX_A)

        store = QuotaStore()
        coordinator = HaReconciliationCoordinator(object(), store)
        receipt = ReconciliationReceiptTests().receipt()
        first_page = ReconciliationPage(
            ReconciliationComponent.QUOTA,
            None,
            0,
            False,
            "revisited",
            HEX_A,
            1,
        )
        first_progress = advance_reconciliation_receipt(receipt, first_page)
        await coordinator.next_page(first_progress, limit=256, apply=True)
        await coordinator.next_page(first_progress, limit=256, apply=True)

        second_progress = advance_reconciliation_receipt(
            first_progress,
            dataclasses.replace(first_page, input_cursor="revisited"),
        )
        await coordinator.next_page(second_progress, limit=256, apply=True)

        self.assertEqual(store.operations[0], store.operations[1])
        self.assertNotEqual(store.operations[1], store.operations[2])


if __name__ == "__main__":
    unittest.main()
