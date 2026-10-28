BASE_PREMIUM = {"hatchback": 8000, "sedan": 12000, "suv": 15000}


def annual_premium(car_type, driver_age, claims_last_3_years, has_anti_theft):
    if car_type not in BASE_PREMIUM:
        raise ValueError("unknown car type")
    if driver_age < 18:
        raise ValueError("driver too young")
    premium = BASE_PREMIUM[car_type]
    if driver_age < 25:
        premium += 4000
    elif driver_age >= 60:
        premium += 2000
    if claims_last_3_years == 0:
        premium -= premium // 5
    elif claims_last_3_years > 2:
        premium = premium * 2
    if has_anti_theft:
        premium -= 500
    return premium


def no_claim_bonus(claim_free_years):
    if claim_free_years < 0:
        raise ValueError("invalid years")
    if claim_free_years >= 5:
        return 50
    elif claim_free_years >= 3:
        return 35
    elif claim_free_years >= 1:
        return 20
    return 0


def claim_payout(damage_cost, insured_value, deductible, is_total_loss):
    if damage_cost < 0 or deductible < 0:
        raise ValueError("invalid amount")
    if is_total_loss:
        return insured_value
    if damage_cost <= deductible:
        return 0
    payout = damage_cost - deductible
    if payout > insured_value:
        return insured_value
    return payout
