# Phase 6: Wiring & Final Integration Plan

## Objective
Repair all broken imports across the newly structured `src/` directory, update the main game loop, and verify the entire engine runs flawlessly.

## Actions to Execute (Do not deviate):

1. **Global Import Search & Replace:**
   - Go through every file in `src/engine/` and fix imports.
     - E.g., `from engine.physics import PhysicsEntity` -> `from src.engine.core.PhysicsEntity import PhysicsEntity`
   - Go through every file in `src/game/` and fix imports.
     - E.g., `from modules.enemies.base_enemy import BaseEnemy` -> `from src.game.entities.enemies.BaseEnemy import BaseEnemy`
   - Pay special attention to the `ResourceManager` which dynamically spawns classes; ensure its string-to-class mappings point to the new `src.game.*` namespaces.

2. **Main Loop Refactor (`src/main.py`):**
   - Update imports in `src/main.py`.
   - Ensure `main.py` properly instantiates the isolated managers (e.g., `ResourceManager`, `UIManager`, `AnimationManager`).
   - Verify the state machine or main `while True` loop is clean and calls the appropriate update/draw methods on the packages.

3. **Tool Wiring:**
   - Update `tools/analyze_fox.py` and other utility scripts to import from `src.` instead of old paths.

4. **Testing & QA:**
   - Run `python src/main.py`.
   - Walk through level 0.
   - Verify parallax backgrounds load.
   - Verify player movement, jumping, and collision.
   - Verify enemy AI (Rabbit, Boss).
   - Verify weapon firing and particle effects.
   - Verify health UI and Ammo UI update correctly.

## Completion Criteria
The game launches without a single `ModuleNotFoundError`. Gameplay is 100% identical to the pre-refactor state. The console is clean of errors. The restructuring is officially complete.