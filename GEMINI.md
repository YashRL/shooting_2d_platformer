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
- **`physics.py`**: `PhysicsEntity` provides centralized gravity, collision, and terminal velocity logic. Includes consistent `current_ground` detection for standing/carrying logic.
- **`animation.py`**: `AnimationManager` handles state-based frame cycling, flipping, and red-tinted damage flashes.
- **`effects.py`**: `EffectManager` manages particles (muzzle flashes), screen shake, and projectile life-cycles.
- **`parallax.py`**: `ParallaxManager` handles infinite looping background layers with dynamic scaling, intensity, and vertical offsets.
- **`ui.py`**: `UIManager` handles professional HUD elements, including segmented dynamic health bars and icon-based counters.

### 2. Module Layer (`/modules`)
- **`player/`**: `FoxPlayer` features variable-height jumping, 2-slot weapon inventory, and interaction logic.
- **`enemies/`**: `BaseEnemy` framework with `Insect` (ground patrol/edge detection) and `Bee` (advanced flying AI with guard/chase logic).
- **`weapons/`**: Modular weapon classes (`Pistol`, `SMG`) driven by registry stats.
- **`world/`**: `Tile` and `WorldItem` classes. Includes specialized `ExplodingTile` for the "Danger" category, `ExplosiveBarrel` (bullet-triggered hazard), `ThrowingKnife` (Invisible 5-tile raycast trap, directional), and directional metadata for `Pipes`.

### 3. Editor Layer (`editor.py`)
A professional-grade level creation tool featuring:
- **Level Launcher**: Menu for loading existing levels and a "Create New" screen for custom dimensions.
- **Advanced UI**: Two-column layout with a **Nested Categorization System**.
- **Multi-Layer System**: Supports two distinct grid layers: `world` (solid tiles) and `entities` (props, players, enemies, traps).
- **Directional Placement**: Specialized UI for selecting Trap directions (UP, DOWN, LEFT, RIGHT).
- **Undo Engine**: 50-step history via **Ctrl + Z**.
- **Dynamic Navigation**: Zoom (Ctrl + Scroll) and Panning (Middle Click).

## ✨ Juicy HUD Features
- **Segmented Health Bar**: Stitched from `start`, `middle`, and `end` assets; dynamically clips to reflect current HP.
- **Ammo Icon HUD**: Replaces text with professional bullet icons and clear fractional counts.
- **Visual Feedback**: Entities flash red on damage; screen shake on every shot/explosion.

## 🗝️ Registry Categories & Physics Types
| Category | Type | Description |
|---|---|---|
| **Tiles** | `static` | Colliding environment (Grasses, Concrete). |
| **Traps** | `entity` | Includes `KNIFE` (Invisible, directional raycast trigger). |
| **Barrels** | `entity` | Includes `BARREL` (Bullet-triggered explosive). |
| **Props** | `decor` | Non-colliding background/foreground decorations. |
| **Players** | `entity` | Spawns dynamic modules (e.g., `FoxPlayer`). |
| **Enemies** | `entity` | Spawns AI modules (e.g., `Insect`, `Bee`). |

## 📁 Level Format (Composite CSV + JSON)
Levels are saved as a pair of files:
1. **`.csv`**: Grid data where each cell uses `TILE_ID;ENTITY_ID`.
2. **`.json`**: Metadata including theme and parallax settings.

## 🛠️ Upcoming Roadmap
- [x] **Phase 1: Hazards & Springs**: Implement jumping springs and tile-based physics for Mud and Toxic Water.
- [x] **Phase 2: Traps & Crumbling**: Added `ExplodingTile`, `ExplosiveBarrel`, and `ThrowingKnife` hazards.
- [ ] **Phase 3: Moving Platforms**: Node-based pathing for elevators and mobile platforms.
- [ ] **Phase 4: Advanced Combat & Exploration**: Weapon-wielding AI (Gunners), the **Stranger Merchant**, and functional Pipe Entrances.
- [ ] **Sound System**: Implement `engine/sounds.py` for jump, shoot, and hurt effects.
- [ ] **Animation Expansion**: Add hurt, death, and reload states to all entities.
