# Instructions for Coding Agents
1. Use environment "conda activate games".
2. Constantly update `registry.json` for new assets and stats.
3. Keep this file updated as the "Source of Truth" for the engine's state.
4. This file is Agent-first.

# TheTreeSentinal Engine by Yash - 2D Platformer Framework

## 🚀 Engine Overview
A modular, data-driven 2D platformer engine built on top of **Pygame-ce**. The engine uses a **Registry-Driven Architecture**, allowing for high scalability and separation of concerns.

## 🏗️ Core Architecture
The project is divided into three main layers:

### 1. Engine Layer (`/engine`)
- **`loader.py`**: The `ResourceManager` handles `registry.json`, pre-loads assets, dynamically spawns entity classes via `importlib`, and features auto-discovery for nested asset folders.
- **`physics.py`**: `PhysicsEntity` provides centralized gravity, collision, and terminal velocity logic.
- **`animation.py`**: `AnimationManager` handles state-based frame cycling, flipping, and red-tinted damage flashes.
- **`effects.py`**: `EffectManager` manages particles (muzzle flashes), screen shake, and projectile life-cycles.

### 2. Module Layer (`/modules`)
- **`player/`**: `FoxPlayer` features variable-height jumping, 2-slot weapon inventory, and dynamic UI.
- **`enemies/`**: `BaseEnemy` framework with `Insect` (ground patrol/edge detection) and `Bee` (advanced flying AI with guard/chase logic).
- **`weapons/`**: Modular weapon classes (`Pistol`, `SMG`) driven by registry stats.
- **`world/`**: `Tile` and `WorldItem` classes (supports solid static tiles and non-colliding decor props).

### 3. Editor Layer (`editor.py`)
A professional-grade level creation tool featuring:
- **Level Launcher**: Menu for loading existing levels and a "Create New" screen for custom dimensions.
- **Advanced UI**: Two-column layout with a **Nested Categorization System** (Tiles -> Concrete, Foundation, Green Grass, Purple Grass).
- **Safety Systems**: Safe-Entry System (starts with no item selected) and Mouse Debounce (prevents accidental edits across states).
- **Tool System**: Stamp and Erase modes (Left Click/Right Click).
- **Undo Engine**: 50-step history via **Ctrl + Z**.
- **Dynamic Navigation**: Zoom (Ctrl + Scroll) and Panning (Middle Click).
- **Instant Testing**: "PLAY SCENE" button launches the game with the current level.

## 🗝️ Registry Categories & Physics Types
| Category | Type | Description |
|---|---|---|
| **Tiles** | `static` | Colliding environment (Concrete, Foundation, Grasses). Auto-discovered. |
| **Props** | `decor` | Non-colliding background/foreground decorations. Auto-discovered. |
| **Players** | `entity` | Spawns dynamic modules (e.g., `FoxPlayer` at `START`). |
| **Weapons** | `entity` | Spawns weapon modules (e.g., `P` for Pistol, `CT` for SMG). |
| **Enemies** | `entity` | Spawns AI modules (e.g., `E_I` for Insect, `E_b` for Bee). |

## 🛠️ Upcoming Roadmap
- [ ] **Sound System**: Implement `engine/sounds.py` and integrate existing `.ogg` assets for actions (jump, shoot, hurt).
- [ ] **Level Metadata**: Transition from raw CSV to JSON for levels to store name, theme, and music data.
- [ ] **Animation Expansion**: Add more animation states (hurt, death, reload) to player and enemies.
- [ ] **Parallax Backgrounds**: Add support for layered scrolling backgrounds in the engine.
