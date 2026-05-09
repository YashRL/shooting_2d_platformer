# Phase 1: Scaffolding & Cleanup Plan

## Objective
Establish the new directory structure, move utility scripts into `tools/`, tests into `tests/`, and initialize the basic Java-style package structure using `__init__.py` files.

## Actions to Execute (Do not deviate):
1. **Create Directories:**
   - Create `tools/` at the project root.
   - Create `tests/` at the project root.
   - Create `src/` at the project root.
   - Inside `src/`, create `engine/core/`, `engine/graphics/`, `engine/ui/`.
   - Inside `src/`, create `game/entities/players/`, `game/entities/enemies/`, `game/entities/npcs/`.
   - Inside `src/`, create `game/weapons/`, `game/world/`.

2. **Initialize Packages (Add `__init__.py`):**
   - Add empty `__init__.py` files to EVERY directory created in step 1 under `src/` (including `src/` itself).

3. **Move Utilities:**
   - Move `editor.py` to `tools/LevelEditor.py` (Will be rewritten in Phase 5).
   - Move `level_editor.py` to `tools/old_level_editor.py` (Keep for reference).
   - Move `recolor_assets.py` to `tools/AssetRecolor.py`.
   - Move `split_spritesheet.py` to `tools/SpriteSplitter.py`.
   - Move `analyze_fox.py` to `tools/analyze_fox.py`.
   - Move `process_merchant.py` to `tools/process_merchant.py`.

4. **Move Tests:**
   - Move `test_loader_tint.py` to `tests/`.
   - Move `test_scaling.py` to `tests/`.
   - Move `test_tint.py` to `tests/`.

5. **Move Main:**
   - Move `main.py` to `src/main.py`.

## Completion Criteria
All root-level stray Python scripts (except setup files if any) are categorized into `src/`, `tools/`, or `tests/`. The `src/` folder contains a fully initialized package tree.