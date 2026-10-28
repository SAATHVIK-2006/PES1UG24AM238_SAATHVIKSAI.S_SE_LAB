import pytest
from car_insurance_premium import annual_premium, no_claim_bonus, claim_payout

# --- Tests for annual_premium ---

def test_annual_premium_sedan_no_claims():
    assert annual_premium("sedan", 30, 0, False) == 9600

def test_annual_premium_invalid_car_type():
    with pytest.raises(ValueError, match="unknown car type"):
        annual_premium("truck", 30, 0, False)

def test_annual_premium_driver_too_young():
    with pytest.raises(ValueError, match="driver too young"):
        annual_premium("hatchback", 17, 0, False)

def test_annual_premium_young_driver_suv_claims_anti_theft():
    # age < 25 (+4000), claims > 2 (*2), has_anti_theft (-500)
    # base SUV = 15000 + 4000 = 19000; * 2 = 38000; - 500 = 37500
    assert annual_premium("suv", 22, 3, True) == 37500

def test_annual_premium_senior_driver_hatchback_mid_claims():
    # age >= 60 (+2000), claims = 1 (no discount/increase), no anti-theft
    # base hatchback = 8000 + 2000 = 10000
    assert annual_premium("hatchback", 65, 1, False) == 10000

# --- Tests for no_claim_bonus ---

def test_no_claim_bonus_invalid_years():
    with pytest.raises(ValueError, match="invalid years"):
        no_claim_bonus(-1)

def test_no_claim_bonus_zero():
    assert no_claim_bonus(0) == 0

def test_no_claim_bonus_tier1():
    assert no_claim_bonus(1) == 20
    assert no_claim_bonus(2) == 20

def test_no_claim_bonus_tier3():
    assert no_claim_bonus(3) == 35
    assert no_claim_bonus(4) == 35

def test_no_claim_bonus_tier5():
    assert no_claim_bonus(5) == 50
    assert no_claim_bonus(10) == 50

# --- Tests for claim_payout ---

def test_claim_payout_invalid_amounts():
    with pytest.raises(ValueError, match="invalid amount"):
        claim_payout(-100, 5000, 500, False)
    with pytest.raises(ValueError, match="invalid amount"):
        claim_payout(1000, 5000, -50, False)

def test_claim_payout_total_loss():
    assert claim_payout(10000, 8000, 500, True) == 8000

def test_claim_payout_damage_less_than_deductible():
    assert claim_payout(300, 5000, 500, False) == 0

def test_claim_payout_normal():
    # 5000 damage - 1000 deductible = 4000 payout
    assert claim_payout(5000, 10000, 1000, False) == 4000

def test_claim_payout_capped_at_insured_value():
    # payout = 12000 - 1000 = 11000, but capped at insured_value = 8000
    assert claim_payout(12000, 8000, 1000, False) == 8000