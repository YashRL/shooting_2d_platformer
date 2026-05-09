# Phase 2: Engine Core Refactoring Plan

## Objective
Migrate the `engine/` folder and root-level engine scripts into `src/engine/`. Split files containing multiple classes so that exactly one class resides in one `.py` file.

## Actions to Execute (Do not deviate):

1. **`loader.py` Migration -> `src/engine/core/ResourceManager.py`**
   - Extract the `ResourceManager` class from `engine/loader.py`.
   - Create `src/engine/core/ResourceManager.py` and paste the class. Fix local `pygame` imports.

2. **`physics.py` Migration -> `src/engine/core/PhysicsEntity.py`**
   - Extract the `PhysicsEntity` class from `engine/physics.py`.
   - Create `src/engine/core/PhysicsEntity.py`. Paste the class.

3. **`animation.py` Migration -> `src/engine/graphics/AnimationManager.py`**
   - Extract `AnimationManager` from `engine/animation.py`.
   - Create `src/engine/graphics/AnimationManager.py`. Paste the class.

4. **`parallax.py` Migration -> `src/engine/graphics/ParallaxManager.py`**
   - Extract `ParallaxManager` from `engine/parallax.py`.
   - Create `src/engine/graphics/ParallaxManager.py`. Paste the class.

5. **`ui.py` Migration -> `src/engine/ui/UIManager.py`**
   - Extract `UIManager` from `engine/ui.py`.
   - Create `src/engine/ui/UIManager.py`. Paste the class.

6. **Root `effects.py` Migration -> `src/engine/graphics/EffectManager.py`**
   - Identify classes inside `effects.py` (e.g., `EffectManager`, `Particle`, `Projectile`).
   - Split them:
     - `src/engine/graphics/EffectManager.py`
     - `src/engine/graphics/Particle.py`
     - `src/engine/graphics/Projectile.py`

7. **Root `registry.py` Migration -> `src/engine/core/Registry.py`**
   - Move `registry.py` to `src/engine/core/Registry.py` (or extract its classes if multiple exist).

8. **Cleanup:**
   - Delete the old `engine/` folder at the project root.
   - Delete root `effects.py` and `registry.py`.

## Completion Criteria
The original `engine/` folder is gone. `src/engine/` is fully populated with single-class scripts. Imports are broken at this stage; they will be fixed in Phase 6.