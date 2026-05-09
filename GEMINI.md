# TheTreeSentinal Engine 2.0 - Java-Style Architecture update

# Instructions for Coding Agents
1. Use environment "conda activate games".
2. Constantly update `registry.json` for new assets and stats.
3. Keep this file updated as the "Source of Truth" for the engine's state.
4. This file is Agent-first.
5. Everything must be in structure and every thing will be Class like Java

# Instructions for Coding Agents
1. Use environment "conda activate games".
2. **Strict Package Hierarchy:** All source code lives in `src/`. Utilities live in `tools/`. Tests live in `tests/`.
3. **One Class, One Script:** Every `.py` file must contain exactly **one** class. Filenames must match class names in PascalCase (e.g., `FoxPlayer.py`).
4. **Absolute Imports:** Use absolute imports starting from the project root (e.g., `from src.engine.core.ResourceManager import ResourceManager`).
5. **JSON Level Format:** Levels are stored as unified `.json` files in the `levels/` directory. No more CSVs.
6. Constantly update `data/registry.json` for new assets and stats.
7. This file is the "Source of Truth" for the engine's state.

## 🚀 Engine Overview
A high-performance, modular, data-driven 2D platformer engine built on **Pygame-ce**. Engine 2.0 adopts strict Object-Oriented Programming (OOP) principles and a package-based structure inspired by Java and industry-standard software engineering.

## 🏗️ Core Architecture (Version 2.0)

### 1. Engine Layer (`src/engine/`)
- **`core/ResourceManager.py`**: Centralized asset loading, entity spawning, and high-fidelity surgical tinting. Supports instance property parsing (e.g., `ID[prop:val]`).
- **`core/PhysicsEntity.py`**: Centralized gravity, collision, and platform-carrying logic.
- **`graphics/AnimationManager.py`**: State-based frame cycling with support for surgical damage flashes.
- **`graphics/ParallaxManager.py`**: Manages infinite looping background layers.
- **`graphics/EffectManager.py`**: Handles particles, screen shake, and projectiles with ownership tracking.
- **`ui/UIManager.py`**: Handles segmented dynamic health bars and HUD elements.

### 2. Game Layer (`src/game/`)
- **`entities/players/`**: Contains `FoxPlayer.py` and other player modules.
- **`entities/enemies/`**: Categorized AI modules (e.g., `BaseEnemy`, `RabbitEnemy`, `BossRabbit`, `Bee`).
- **`weapons/`**: Modular weapon logic (e.g., `Pistol`, `SMG`, `RocketLauncher`).
- **`world/`**: Interactive elements like `Tile`, `ExplodingTile`, `MovingPlatform`, and `Trampoline`.

### 3. Editor Layer (`tools/`)
- **`LevelEditor.py`**: A modular, OOP-based level creation tool.
- **`editor/`**: Package containing editor core components:
    - `Camera.py`: Panning and zoom logic.
    - `CommandStack.py`: Command pattern implementation for robust Undo/Redo.
    - `UIComponents.py`: Reusable UI primitives (Buttons, Panels, InputBoxes).

## 📁 Level Data Format (Unified JSON)
Engine 2.0 uses a hierarchical JSON format for all levels.
```json
{
    "metadata": { "theme": "nature_1", "parallax_intensity": 1.0 },
    "layers": {
        "main": [["TILE_ID", "-1"], ...],
        "entities": [
            { "type": "ENEMY_ID", "x": 100, "y": 200, "properties": { "hp": 50 } }
        ]
    }
}
```

## ✨ New in 2.0
- **Startup Menu:** Professional new/load level flow in the editor.
- **Surgical Tinting:** Advanced palette replacement targeting specific greens while protecting wood/dirt tones.
- **Modular UI:** A fully custom, class-based UI system for tools and HUD.
- **Enhanced Physics:** Improved sub-pixel precision and platform adherence.

## 🐛 Known Issues & Debugging
- **Path Sensitivity:** Scripts MUST be run from the project root (`D:\Yash_Code\2D_Game`) to resolve absolute imports and relative data paths.
- **Command:** `python src/main.py` or `python tools/LevelEditor.py`.
