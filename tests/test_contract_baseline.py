"""Dependency-free regression checks for the existing MVP and the v1 fixture."""
import json
import unittest
from collections import defaultdict
from pathlib import Path

from demo.fraud_detection_demo import risk_score

ROOT = Path(__file__).resolve().parents[1]


class V1ContractTests(unittest.TestCase):
    def test_fixture_and_existing_python_score_agree(self):
        req = json.loads((ROOT / "contracts/examples/risk-request.json").read_text())
        res = json.loads((ROOT / "contracts/examples/risk-result.json").read_text())
        self.assertEqual(req["eventId"], res["eventId"])
        existing_tx = {
            "customer": req["customerId"],
            "to": req["beneficiaryId"],
            "amount": req["amountTry"],
            "active_call": req["call"]["isActive"],
            "remote_access": req["remoteAccessDetected"],
        }
        beneficiaries = defaultdict(set)
        if not req["isNewBeneficiary"]:
            beneficiaries[req["customerId"]].add(req["beneficiaryId"])
        score, reasons = risk_score(existing_tx, beneficiaries)
        if (req["isNewBeneficiary"] and req["amountTry"] >= 20_000
                and req["muleFanInCount"] >= 4):
            score += 30
        self.assertEqual(score, 80)
        self.assertEqual(score, res["score"])
        self.assertEqual(res["decision"], "HOLD" if score >= 70 else "ALLOW")
        self.assertEqual(len(reasons), 3)

    def test_known_small_transfer_is_allowed(self):
        tx = {"customer": "C001", "to": "B001", "amount": 2500,
              "active_call": False, "remote_access": False}
        score, reasons = risk_score(tx, defaultdict(set, {"C001": {"B001"}}))
        self.assertEqual(score, 0)
        self.assertFalse(reasons)

    def test_all_contract_examples_parse(self):
        for path in (ROOT / "contracts").rglob("*.json"):
            with self.subTest(path=path):
                self.assertIsInstance(json.loads(path.read_text()), dict)


if __name__ == "__main__":
    unittest.main()

