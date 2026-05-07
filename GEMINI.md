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
- **`loader.py`**: The `ResourceManager` handles `registry.json`, pre-loads assets, and dynamically spawns entities. Features **Instance Property Parsing** (converting editor strings like "250" to ints) and a **High-Fidelity Surgical Tinting System**. It performs 3-shade palette replacement on raw unscaled assets before scaling, ensuring perfect pixel matching for target greens while strictly protecting wood/dirt colors (#c47c71, #47324b, #dea989).
- **`animation.py`**: `AnimationManager` handles state-based frame cycling, flipping, and **Surgical Red-Tinted damage flashes** that only affect green pixels.
- **`physics.py`**: `PhysicsEntity` provides centralized gravity, collision, and terminal velocity logic. Includes consistent `current_ground` detection for standing/carrying logic.
- **`effects.py`**: `EffectManager` manages particles, screen shake, and projectiles. Now includes a **Projectile Ownership System** (owner tracking) to differentiate between player and enemy bullets, enabling multi-directional combat.
- **`parallax.py`**: `ParallaxManager` handles infinite looping background layers with dynamic scaling, intensity, and vertical offsets.
- **`ui.py`**: `UIManager` handles professional HUD elements, including segmented dynamic health bars and icon-based counters.

### 2. Module Layer (`/modules`)
- **`player/`**: `FoxPlayer` features variable-height jumping, weapon inventory, and ownership-aware shooting.
- **`enemies/`**: 
    - `BaseEnemy`: Framework for AI and damage handling.
    - `RabbitEnemy`: erratic "Prankster" AI with dodging, taunting, and personality states.
    - `BossRabbit`: Extends `RabbitEnemy` with **Tactical Weapon AI**. Relentless aggression while armed; transitions to "Fear/Panic" dash while reloading.
- **`weapons/`**: Modular weapon classes driven by registry stats.
- **`world/`**: `Tile` and `WorldItem` classes. Includes specialized `ExplodingTile` for the "Danger" category, `ExplosiveBarrel` (bullet-triggered hazard), `ThrowingKnife` (Invisible 5-tile raycast trap, directional), and directional metadata for `Pipes`.

### 3. Editor Layer (`editor.py`)
A professional-grade level creation tool featuring:
- **BOSS Category**: Dedicated category for elite enemies with a **Property Sidebar** for customizing `hp`, `speed`, and `weapon` per instance.
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
| **Weapons** | `entity` | Pickable items (`P`, `CT`, `RL`). |

## 📁 Level Format (Composite CSV + JSON)
Levels are saved as a pair of files:
1. **`.csv`**: Grid data where each cell uses `TILE_ID;ENTITY_ID`.
2. **`.json`**: Metadata including theme and parallax settings.

## 🛠️ Upcoming Roadmap
- [x] **Phase 1-4**: Hazards, Moving Platforms, and RPG mechanics implemented.
- [x] **Phase 5: Bosses & Tactical AI**: Implemented Boss Rabbit with weapon-wielding AI, projectile ownership, and editor customization.
- [ ] **Phase 6: Exploration & NPCs**: Implement the **Stranger Merchant** and functional Pipe Entrances.
- [ ] **Ambient System**: Implement `engine/ambient.py` for leaves, dust, and wind effects.
- [ ] **Sound System**: Implement `engine/sounds.py` for project-wide SFX.
- [ ] **Animation Expansion**: Add hurt, death, and reload states to all entities.

## 🐛 Known Bugs
- **Platform Selection Dependency**: In the Level Editor (`editor.py`), new platforms (e.g., `MOVING_PLATFORM_2`) reportedly cannot be used independently. Users must select the original `MOVING_PLATFORM` first before the new one functions correctly.
    - **Findings so far**: 
        - Hardcoded checks for `MOVING_PLATFORM` have been replaced with generic `category == "Platforms"` logic.
        - Node placement state is reset on item selection.
        - Registry includes `width_tiles` for correct multi-tile scaling.
        - The bug persists despite no obvious hardcoded links, suggesting a subtle state initialization issue in the editor's selection or UI update loop.