
import unittest
from unittest.mock import MagicMock
from fraud_service import CircuitBreaker


class TestFraudService(unittest.TestCase):

    def test_circuit_breaker_success(self):
        breaker = CircuitBreaker()
        result = breaker.call(lambda: "Success")
        self.assertEqual(result, "Success")

    def test_circuit_breaker_failure(self):
        breaker = CircuitBreaker(threshold=3)

        for _ in range(3):
            with self.assertRaises(ValueError):
                breaker.call(lambda: (_ for _ in ()).throw(ValueError("DB error")))

        with self.assertRaises(RuntimeError):
            breaker.call(lambda: "Should not execute")

    def test_circuit_breaker_recovers(self):
        breaker = CircuitBreaker()
        self.assertEqual(breaker.call(lambda: 100), 100)


if __name__ == "__main__":
    unittest.main(verbosity=2)
