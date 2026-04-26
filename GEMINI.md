# Gemini Engine - 2D Platformer Framework

## 🚀 Engine Overview
A modular, data-driven 2D platformer engine built on top of **Pygame-ce**. The engine uses a **Registry-Driven Architecture**, allowing for high scalability and separation of concerns.

## 🏗️ Core Architecture
The project is divided into three main layers:

### 1. Engine Layer (`/engine`)
- **`loader.py`**: The `ResourceManager` handles `registry.json`, pre-loads assets, and dynamically spawns entity classes.
- **`physics.py`**: `PhysicsEntity` provides centralized gravity, collision, and terminal velocity logic.
- **`animation.py`**: `AnimationManager` handles state-based frame cycling, flipping, and juicy effects like red-tinted damage flashes.
- **`effects.py`**: `EffectManager` manages particles (muzzle flashes), screen shake, and projectile life-cycles.

### 2. Module Layer (`/modules`)
Every game object is a self-contained module:
- **`player/`**: `FoxPlayer` handles complex input, variable-height jumping, and a 2-slot weapon inventory.
- **`enemies/`**: `BaseEnemy` framework with `Insect` (ground patrol) and `Bee` (advanced flying AI/guarding).
- **`weapons/`**: Modular weapon classes (`Pistol`, `SMG`) defined by stats in the registry.
- **`world/`**: Tile and Prop logic.

### 3. Data Layer (`/data` & `/levels`)
- **`registry.json`**: The "Master Brain." Defines item types, asset paths, Python class mappings, and combat stats.
- **Scene Files**: CSV-based grid data representing world layouts.

## 🗝️ Registry Identifiers (JSON/CSV)
| ID | Type | Description |
|---|---|---|
| **1-234** | Static | Environmental tiles (Stone, Grass, etc.) |
| **START** | Entity | Player character spawn point |
| **P / CT** | Weapon | Pistol and Chicago Typewriter (SMG) |
| **E_I / E_b** | Enemy | Insect (Ground) and Bee (Flying AI) |

## 🎮 Current Controls
- **W**: Jump (Dynamic height based on hold duration)
- **A / D**: Horizontal Movement
- **Spacebar / Left Click**: Shoot Weapon
- **R**: Manual Reload
- **E**: Interact / Pick up World Items
- **1 / 2**: Switch Weapon Slots

## ✨ Juicy Combat Features
- **Variable Jump**: Hold W for higher jumps; quick tap for hops.
- **Impact Feedback**: Entities flash red on damage and experience resistance-based knockback.
- **Screen Juice**: Screen shake and muzzle particles on every shot.
- **Reload UI**: Circular progress bar appears near the weapon during reloads.

## 🛠️ Upcoming Roadmap
- [ ] **Sound System**: Implement `engine/sounds.py` to utilize existing `.ogg` assets.
- [ ] **Prop System**: Add a "Decor" category for non-colliding world props (bushes, clouds).
- [ ] **Level Metadata**: Transition from raw CSV to JSON for levels to store metadata (name, theme, music).
- [ ] **Editor UI**: Add in-editor grid resizing and level naming.
