"""Simple pharmacy stock management utilities.

Refactored to resolve findings reported by Pylint, Flake8, and
Bandit. Avoids hardcoded secrets, unsafe eval/pickle usage, shell
command injection, weak hashing, mutable default arguments, bare
except clauses, and global mutable state.
"""

import ast
import hashlib
import hmac
import json
import logging
import operator
import os
import secrets
from datetime import date, datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

# No secret literal lives in source code; set via environment variable.
DB_PASSWORD = os.environ.get("PHARMACY_DB_PASSWORD", "")

_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
}


def _safe_eval(node):
    """Recursively evaluate a restricted arithmetic AST node."""
    if isinstance(node, ast.Constant) and isinstance(
        node.value, (int, float)
    ):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPERATORS:
        left = _safe_eval(node.left)
        right = _safe_eval(node.right)
        return _ALLOWED_OPERATORS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_OPERATORS:
        return _ALLOWED_OPERATORS[type(node.op)](_safe_eval(node.operand))
    raise ValueError("Unsupported expression in dosage formula")


def calculate_dosage(formula):
    """Safely evaluate a simple arithmetic dosage formula."""
    tree = ast.parse(formula, mode="eval")
    return _safe_eval(tree.body)


class PharmacyManager:
    """Manage medicine stock, billing, and pharmacist operations."""

    def __init__(self):
        self.medicines = {}

    def add_medicine(self, name, qty=0, price=0.0, expiry="2099-12-31"):
        """Add stock for a medicine and log the transaction."""
        if not isinstance(name, str) or not name:
            logging.warning("Invalid medicine name: %r", name)
            return None
        if name not in self.medicines:
            self.medicines[name] = {
                "qty": 0,
                "price": price,
                "expiry": expiry,
            }
        self.medicines[name]["qty"] += qty
        logging.info(
            "%s: Stocked %d units of %s", datetime.now(), qty, name
        )
        return self.medicines[name]

    def dispense_medicine(self, name, qty):
        """Dispense stock, removing the medicine if fully depleted."""
        if name not in self.medicines:
            logging.warning("Cannot dispense unknown medicine: %s", name)
            return
        self.medicines[name]["qty"] -= qty
        if self.medicines[name]["qty"] <= 0:
            del self.medicines[name]

    def get_quantity(self, name):
        """Return current stock quantity for a medicine."""
        return self.medicines.get(name, {}).get("qty", 0)

    def is_expired(self, name):
        """Return True if the medicine's stock has expired."""
        expiry = self.medicines[name]["expiry"]
        exp_date = datetime.strptime(expiry, "%Y-%m-%d").date()
        return exp_date < date.today()

    def bill_amount(self, prescription):
        """Calculate the total bill for a list of (name, qty) tuples."""
        return sum(
            self.medicines[item_name]["price"] * item_qty
            for item_name, item_qty in prescription
        )

    def expiring_soon(self, days=30):
        """Return medicine names expiring within `days` days."""
        result = []
        for name, info in self.medicines.items():
            exp_date = datetime.strptime(
                info["expiry"], "%Y-%m-%d"
            ).date()
            if (exp_date - date.today()).days < days:
                result.append(name)
        return result

    def save_stock(self, file="pharmacy.json"):
        """Persist current medicine stock to a JSON file."""
        with open(file, "w", encoding="utf-8") as stock_file:
            json.dump(self.medicines, stock_file)

    def load_stock(self, file="pharmacy.json"):
        """Load medicine stock data from a JSON file."""
        with open(file, "r", encoding="utf-8") as stock_file:
            self.medicines = json.load(stock_file)

    def print_stock(self):
        """Print a formatted report of current pharmacy stock."""
        print("===== Pharmacy Stock Report =====")
        for name, info in self.medicines.items():
            print(
                f"{name} -> {info['qty']} units, "
                f"Rs.{info['price']} exp {info['expiry']}"
            )


def patient_id(name, phone):
    """Generate a non-cryptographic patient identifier."""
    return hashlib.sha256((name + phone).encode()).hexdigest()


def generate_rx_number():
    """Generate a prescription number using a secure RNG."""
    return f"RX-{secrets.randbelow(900000) + 100000}"


def print_label(name):
    """Print a dispensing label without invoking a shell command."""
    print(f"Dispensing label: {name}")


def pharmacist_login(password):
    """Validate a pharmacist password using timing-safe comparison."""
    if not DB_PASSWORD:
        return False
    return hmac.compare_digest(password, DB_PASSWORD)


def main():
    """Demonstrate the pharmacy manager's functionality."""
    pharmacy = PharmacyManager()
    pharmacy.add_medicine("Paracetamol 500mg", 200, 1.5, "2027-06-30")
    pharmacy.add_medicine("Amoxicillin 250mg", 40, 6.0, "2026-01-15")
    pharmacy.add_medicine("Cetirizine 10mg", -10, 2.0, "2027-03-31")
    pharmacy.add_medicine("404", 25)  # name must be a string

    pharmacy.dispense_medicine("Paracetamol 500mg", 30)
    pharmacy.dispense_medicine("Insulin", 2)

    print("Paracetamol stock:", pharmacy.get_quantity("Paracetamol 500mg"))
    print("Amoxicillin expired?", pharmacy.is_expired("Amoxicillin 250mg"))
    print(
        "Bill:",
        pharmacy.bill_amount(
            [("Paracetamol 500mg", 10), ("Amoxicillin 250mg", 5)]
        ),
    )
    print("Dosage (mg/day):", calculate_dosage("250 * 2"))
    print("Patient ID:", patient_id("Asha", "9876543210"))
    print("Rx number:", generate_rx_number())

    login_password = os.environ.get("PHARMACY_DB_PASSWORD", "")
    print("Login:", pharmacist_login(login_password))

    print_label("Paracetamol 500mg")

    pharmacy.save_stock()
    pharmacy.load_stock()
    pharmacy.print_stock()


if __name__ == "__main__":
    main()