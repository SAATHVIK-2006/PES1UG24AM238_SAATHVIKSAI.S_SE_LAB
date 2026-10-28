# Static Code Analysis — Issue Report
**File analyzed:** `pharmacy_manager.py`
**Tools used:** Pylint, Bandit, Flake8
**Initial Pylint Score:** 4.83/10
**Target Pylint Score:** ≥ 9.5/10

---

## Summary

| Tool | Total Issues Found | Severity Breakdown |
|---|---|---|
| Bandit | 8 | High: 2, Medium: 2, Low: 4 |
| Flake8 | 21 | Style/PEP8 violations |
| Pylint | 30+ | Score: 4.83/10 |

---

## Detailed Issue Table

| # | Issue | Tool | Type / Code | Severity | Line(s) | Description | Fix Approach |
|---|---|---|---|---|---|---|---|
| 1 | Insecure module import | Bandit | B403 | Low | 3 | `pickle` module can execute arbitrary code during deserialization | Replaced with `json` for save/load operations |
| 2 | Hardcoded password | Bandit | B105 | Low | 11 | `DB_PASSWORD = "pharma@123"` stored as plaintext literal | Loaded from `os.environ.get("PHARMACY_DB_PASSWORD", "")` |
| 3 | Bare except with pass | Bandit | B110 | Low | 26–28 | `try/except: pass` silently swallows all exceptions including `KeyboardInterrupt` | Replaced with explicit `if name not in self.medicines` check |
| 4 | Use of `eval()` | Bandit | B307 | **Medium** | 48 | Arbitrary code execution risk from untrusted formula string | Built safe AST-based arithmetic evaluator (`ast.parse` + restricted operator whitelist) |
| 5 | Weak hash (MD5) | Bandit | B324 | **High** | 51 | MD5 is cryptographically broken, unsuitable for IDs | Switched to `hashlib.sha256` |
| 6 | Insecure RNG | Bandit | B311 | Low | 54 | `random.randint` not suitable for security-sensitive values | Switched to `secrets.randbelow()` |
| 7 | Insecure deserialization | Bandit | B301 | Medium | 64 | `pickle.load()` can execute arbitrary code from untrusted files | Replaced with `json.load()` |
| 8 | Shell injection risk | Bandit | B605 | **High** | 68 | `os.system()` call built from unvalidated string input | Removed shell call; replaced with `print()` |
| 9 | Mutable default argument | Pylint | W0102 (dangerous-default-value) | Bug | 13 | `audit=[]` default list is shared and mutated across all function calls | Removed parameter entirely; replaced with `logging.info()` call |
| 10 | Bare except clause | Pylint / Flake8 | W0702 / E722 | Medium | 27 | Catches all exceptions without specifying type | Replaced with explicit existence check |
| 11 | Use of `global` statement | Pylint | W0603 (global-statement) | Medium | 63 | Mutating module-level global state makes code hard to test/maintain | Refactored into `PharmacyManager` class; `medicines` is now an instance attribute |
| 12 | Resource not using context manager | Pylint | R1732 (consider-using-with) | Medium | 57, 62 | Manual `open()`/`close()` risks file handle leaks on error | Used `with open(...) as f:` pattern |
| 13 | Non-PEP8 function naming | Pylint | C0103 (invalid-name) | Low | All function defs | `addMedicine`, `isExpired`, etc. use camelCase instead of snake_case | Renamed all functions/methods to `snake_case` |
| 14 | Missing module docstring | Pylint | C0114 | Low | 1 | No documentation describing the module's purpose | Added module-level docstring |
| 15 | Missing function docstrings | Pylint | C0116 | Low | All functions | No documentation on any function/method | Added docstrings to every function and method |
| 16 | Unused imports | Flake8 / Pylint | F401 / W0611 | Low | 2, 6 | `sys` never used; `logging` imported but unused in original | Removed `sys`; `logging` now actively used for audit trail |
| 17 | Unnecessary if/else returning bool | Pylint | R1703 / R1705 | Low | 35, 79 | `if x: return True else: return False` pattern is redundant | Simplified to direct boolean expression return |
| 18 | Line too long | Flake8 / Pylint | E501 / C0301 | Low | 19, 87, 98 | Lines exceed 79/100 character limit | Wrapped long lines across multiple lines |
| 19 | Missing blank lines between defs | Flake8 | E302 / E305 | Low | Multiple (13, 22, 30, 33, 40, 46, 50, 53, 56, 61, 67, 70, 78, 84, 89, 108) | PEP8 requires 2 blank lines before/after top-level defs | Added proper blank-line spacing throughout |
| 20 | Old-style string formatting | Pylint | C0209 (consider-using-f-string) | Low | 19 | Used `%`-style string formatting | Converted to f-strings |
| 21 | No type validation on input | Logic (manual finding) | — | Low | `addMedicine(404, 25)` call in `main()` | Passing a non-string name silently creates invalid stock entry | Added `isinstance(name, str)` guard with warning log |

---

## Fixes by Priority

### High Severity (fixed first)
- [x] MD5 weak hashing (B324) → SHA-256
- [x] `os.system()` shell injection (B605) → removed shell call

### Medium Severity
- [x] `eval()` arbitrary code execution (B307) → AST-based safe evaluator
- [x] `pickle.load()` insecure deserialization (B301) → JSON
- [x] Bare except (W0702/E722) → explicit check
- [x] `global` statement (W0603) → class-based refactor
- [x] Resource leaks (R1732) → `with` statements

### Low Severity
- [x] Hardcoded password (B105) → environment variable
- [x] Insecure RNG (B311) → `secrets` module
- [x] `pickle` import (B403) → removed
- [x] Try/except/pass (B110) → explicit logic
- [x] Mutable default argument (W0102) → removed parameter
- [x] All naming convention issues (C0103) → snake_case
- [x] All missing docstrings (C0114/C0116) → added
- [x] Unused imports (F401/W0611) → cleaned up
- [x] Line length violations (E501/C0301) → wrapped
- [x] Blank line spacing (E302/E305) → fixed
- [x] Old-style formatting (C0209) → f-strings
- [x] Redundant if/else (R1703/R1705) → simplified

---

## Results

| Metric | Before | After |
|---|---|---|
| Bandit issues | 8 | 0 |
| Flake8 issues | 21 | 0 |
| Pylint score | 4.83/10 | 9.9/10 |

---

## Reflection Questions

**1. What was the most severe issue found, and why?**
The `os.system()` call (B605, High severity) was the most severe — it concatenates unvalidated input directly into a shell command, creating a command injection vulnerability. Combined with the MD5 usage (B324, also High), these were the two issues with the most direct, real-world exploitability.

**2. How did the three tools complement each other?**
Bandit focused exclusively on *security* (eval, pickle, hardcoded secrets, weak hashing, shell injection) — issues Pylint and Flake8 don't check for. Pylint focused on *code quality and design* (mutable defaults, global state, naming, missing docs). Flake8 focused purely on *PEP8 style* (spacing, line length, unused imports). There was some overlap — both Pylint and Flake8 flagged the bare `except:` — but each tool caught unique categories of problems the others missed.

**3. What was the hardest issue to fix?**
Replacing `eval()` safely was the hardest — simply removing it would have broken the dosage calculation feature, so a restricted AST-based evaluator had to be built that only permits basic arithmetic operations.

**4. How does static analysis improve long-term maintainability?**
It catches structural and security problems early, before code review or production deployment. Refactoring away from global state and mutable defaults into a `PharmacyManager` class made the code more testable and eliminated a class of bugs where state could unexpectedly leak between function calls. Consistent style (via Flake8/Pylint) also makes the codebase easier to read and maintain across a team.
