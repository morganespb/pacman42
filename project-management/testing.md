# Acceptance Testing

Testing was done manually, in-game, after each feature was
implemented. No automated test suite was written (not required by
the subject), but every mechanic below was verified by playing
through it directly:

- Player movement, wall collision, smooth interpolation
- Ghost collision (life loss, invincibility during cheat mode)
- Pacgum / super pacgum collection and scoring
- Ghost edible state, fleeing behavior, being eaten, respawn with
  temporary immunity
- Ghost staggered activation and BFS pursuit with randomness
- Level timer, level restart on timeout
- Game over / game won flow, highscore entry and persistence
- Config validation with deliberately broken/missing config files
- Cheat mode (speed, invincibility, level skip) toggling on and off
- `make lint-strict` and `mypy --strict` passing with zero errors
- Interrupt handling (Ctrl+C, missing config file, missing sound
  files) exits cleanly without a raw traceback
