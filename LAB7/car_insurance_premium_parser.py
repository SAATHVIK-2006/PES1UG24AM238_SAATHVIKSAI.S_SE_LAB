from datetime import datetime

def normalize_registration(plate):
    """
    Removes spaces and dashes from a registration number and upper-cases it.
    Handles None and non-string inputs defensively.
    """
    if plate is None or not isinstance(plate, str) or not plate.strip():
        raise ValueError("Registration plate cannot be None or empty")
    return plate.strip().upper()

def total_claim_amount(text):
    """
    Calculates total claim amount from a semicolon-separated string.
    Handles None, empty strings, and malformed numbers defensively.
    """
    if text is None or not isinstance(text, str) or not text.strip():
        return 0
    
    total = 0
    for amount in text.split(';'):
        amount = amount.strip()
        if amount:
            if not amount.isdigit() and not (amount.startswith('-') and amount[1:].isdigit()):
                raise ValueError(f"Invalid claim amount: {amount}")
            total += int(amount)
    return total

def driver_age(dob, current_year=2026):
    """
    Calculates driver age based on DD/MM/YYYY format.
    Handles None, empty strings, and invalid date formats defensively.
    """
    if dob is None or not isinstance(dob, str):
        raise ValueError("Date of birth cannot be None")
    
    parts = dob.split('/')
    if len(parts) < 3 or not parts[2].strip().isdigit():
        raise ValueError("Invalid date of birth format")
        
    birth_year = int(parts[2].strip())
    return current_year - birth_year

if __name__ == "__main__":
    # Interactive test run
    print("==== Running normalize_registration ====")
    try:
        reg = input("Enter a registration number (e.g. ka 01 ab 1234): ")
        print(f"Normalized registration: {normalize_registration(reg)}")
    except Exception as e:
        print(f"Handled error: {e}")

    print("\n==== Running total_claim_amount ====")
    try:
        claims = input("Enter past claim amounts separated by ; (e.g. 12000;4500;800): ")
        print(f"Total claimed: {total_claim_amount(claims)}")
    except Exception as e:
        print(f"Handled error: {e}")

    print("\n==== Running driver_age ====")
    try:
        dob_input = input("Enter the driver's date of birth as DD/MM/YYYY (e.g. 14/08/1999): ")
        print(f"Driver age in 2026: {driver_age(dob_input)}")
    except Exception as e:
        print(f"Handled error: {e}")