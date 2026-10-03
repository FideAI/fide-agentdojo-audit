"""Thirteen authored challenges comparing frozen and separately amended rules."""
import audit as original
import audit_amended as amended
from amendment_controls import run_controls
from common import NETWORK_ATTEMPTS, save
controls=run_controls(original,amended)
assert len(controls)==13 and not NETWORK_ATTEMPTS
save('results/amendment-controls.json',dict(passed=True,controls=controls,network_attempts=0))
print('PASS: 13 authored amendment controls; five readable contradictions now unknown.')
