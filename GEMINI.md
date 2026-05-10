# TheTreeSentinal Engine 2.0 - Java-Style Architecture update

# Instructions for Coding Agents
1. Use environment "conda activate games".
2. **Strict Package Hierarchy:** All source code lives in `src/`. Utilities live in `tools/`. Tests live in `tests/`.
3. **One Class, One Script:** Every `.py` file must contain exactly **one** class. Filenames must match class names in PascalCase.
4. **Absolute Imports:** Use absolute imports starting from the project root (e.g., `from src.engine.core...`).
5. **JSON Level Format:** Levels are stored as unified `.json` files. Manual `START` entity determines player spawn.
6. **Rendering Standard:** Always draw world and UI elements to `self.world_surface` to support post-processing filters.
7. **Registry Injection:** `ResourceManager.spawn` injects `item_id` and `asset` into all entities. Ensure modules use `self.properties.get('asset')` for sprite loading.

## 🚀 Engine Overview
A high-performance, modular, data-driven 2D platformer engine built on **Pygame-ce**. Engine 2.0 adopts strict OOP principles and a registry-driven architecture.

## ✨ New in 2.0
- **Noir Filter:** Full-screen 3-tone grayscale post-processing (toggleable in Settings).
- **Manual Spawn:** Precise control over player start positions via the `START` entity in the editor.
- **Scrollable Editor UI:** Robust sidebar with categories, sub-categories, and mouse-wheel scrolling.
- **Surgical Tinting:** Advanced palette replacement targeting specific greens while protecting wood/dirt tones.
- **Modular Editor:** Component-based UI with Command Pattern for perfect Undo/Redo.

## 🏗️ Core Architecture (Simplified)
- **`src/engine/`**: Core systems (Resource Management, Physics, Graphics, UI).
- **`src/game/`**: Actors and Interactive World items.
- **`tools/`**: Development utilities including the OOP Level Editor.

## 📁 Essential Files
- `data/registry.json`: Source of Truth for all IDs, modules, and default stats.
- `Architecture.md`: Detailed technical design and API reference.
- `TODO.md`: Roadmap for upcoming features like the Universal Property Inspector.

## 🐛 Known Issues & Debugging
- **Path Sensitivity:** Scripts MUST be run from the project root (`D:\Yash_Code\2D_Game`).
- **Command:** `python src/main.py` or `python tools/LevelEditor.py`.
