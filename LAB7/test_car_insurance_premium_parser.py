from hypothesis import given, strategies as st
from car_insurance_premium_parser import normalize_registration, total_claim_amount, driver_age

@given(st.text() | st.none())
def test_normalize_registration_no_crash(s):
    try:
        normalize_registration(s)
    except ValueError:
        # Expected validation error for bad input; safe handling
        pass
    except Exception as e:
        assert False, f"normalize_registration crashed with unexpected exception: {e}"

@given(st.text() | st.none())
def test_total_claim_amount_no_crash(s):
    try:
        total_claim_amount(s)
    except ValueError:
        pass
    except Exception as e:
        assert False, f"total_claim_amount crashed with unexpected exception: {e}"

@given(st.text() | st.none())
def test_driver_age_no_crash(s):
    try:
        driver_age(s)
    except ValueError:
        pass
    except Exception as e:
        assert False, f"driver_age crashed with unexpected exception: {e}"