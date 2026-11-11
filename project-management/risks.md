# Risks and Mitigation

| Risk | Mitigation |
|---|---|
| pygame incompatible with newer Python versions (3.14) — no
  precompiled wheel available, compilation fails without system
  libraries (SDL2, freetype) | Pinned the dev environment to
  Python 3.12/3.13 in the Makefile; documented the cause so the
  team doesn't hit it again |
| Mazegenerator package must be used as-is (per subject rules) | Installed via the provided .whl into a vendor/ folder rather
  than copying source files |
| Audio initialization can fail on machines without a sound
  device (e.g. some WSL setups) | Wrapped pygame.mixer calls in
  try/except; the game runs silently instead of crashing |
| Config file could be missing, malformed, or contain invalid
  values | Added validation/clamping for every config field, with
  safe defaults and no raw traceback on failure |
| Merge between two branches introduced a silent bug (a function
  body was lost) | Caught via manual testing after merging;
  highlighted the importance of running the game after every
  merge, not just checking it compiles |
| One contributor unavailable for ~5 weeks mid-project | The
  other contributor maintained momentum solo; work was
  rebalanced and re-synced once both were back, with a full
  review pass across the whole codebase |
