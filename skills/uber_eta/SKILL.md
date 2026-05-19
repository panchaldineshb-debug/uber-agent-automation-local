## Purpose
Fetch ride ETAs and price ranges from Uber without booking.

## Inputs
- `pickup`: address string e.g. "855 Grove Ave, Edison, NJ 08820"
- `dropoff`: address string e.g. "39 Henry St, Edison, NJ 08820"

## Outputs
`list[dict]` — each dict has keys: `type` (str), `eta_minutes` (int), `price_range` (str).
Returns `[]` on error or no results.

## Dependencies
- `playwright` (via scripts/uber_eta.py)
- `config/uber_state.json` — used if present for authenticated session

## Public API
```python
from skills.uber_eta.handler import UberETASkill

skill = UberETASkill()
results = skill.get_eta(pickup="855 Grove Ave, Edison NJ", dropoff="39 Henry St, Edison NJ")
```
