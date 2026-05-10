# TheTreeSentinal Engine 2.0 - Comprehensive Architecture Design

## 🏛️ System Philosophy
Engine 2.0 is a **Registry-Driven Object-Oriented Framework**. Every gameplay actor is a standalone module, and the engine acts as an orchestrator that injects dependencies (Assets, Physics, Effects) into these modules at runtime.

---

## 🏗️ Core Engine Package (`src.engine`)

### 📦 `core` - Foundation
| Script | Class | Logic / Pseudo-Code |
| :--- | :--- | :--- |
| `ResourceManager.py` | `ResourceManager` | **Logic:** Loads `registry.json`. Performs **Surgical Tinting** using `pygame.PixelArray` to replace specific greens with 3-shade palettes while protecting browns. Spawns entities by mapping strings to class names via `importlib`. |
| `PhysicsEntity.py` | `PhysicsEntity` | **Logic:** Two-pass collision. `apply_physics` calculates X-move, checks collisions, then calculates Y-move (gravity), then checks collisions. This prevents "corner-snagging". |
| `Registry.py` | `Registry` | **Logic:** Static helper that auto-discovers tiles by scanning `Assets/PNG/Tiles/Tiles/` and generates unique IDs for numeric filenames. |

### 📦 `graphics` - Rendering
| Script | Class | Logic / Pseudo-Code |
| :--- | :--- | :--- |
| `AnimationManager.py`| `AnimationManager`| **Logic:** Frame cycling using a timer. `get_current_frame()` returns a copy of the surface. If `flash_red` is True, it surgically replaces green pixels with red shades for 1 frame. |
| `ParallaxManager.py` | `ParallaxManager` | **Logic:** Holds a list of `ParallaxLayer`. `draw()` iterates through them, applying individual `factor` offsets based on camera position. |
| `ParallaxLayer.py`   | `ParallaxLayer`   | **Logic:** Infinite loop drawing. `x_offset = (cam_x * factor) % width`. Draws the image twice at `(-offset)` and `(width - offset)`. |
| `EffectManager.py`   | `EffectManager`   | **Logic:** Orchestrator for `Particles` and `Projectiles`. `get_shake_offset()` returns random `(x, y)` if `shake_timer > now`. |
| `Particle.py`       | `Particle`       | **Logic:** Simple sprite that moves by a velocity vector and calls `self.kill()` after `lifetime` expires. |
| `Projectile.py`     | `Bullet`, `Rocket`| **Logic:** `Bullet` is linear movement. `Rocket` includes a smokescreen particle emitter in its `update()` and a radial damage scan in its `explode()`. |

### 📦 `ui` - Interface
| Script | Class | Logic / Pseudo-Code |
| :--- | :--- | :--- |
| `UIManager.py`       | `UIManager`       | **Logic:** Segmented bars. Draws a base 'Empty' bar, then draws 'Full' segments onto a temporary surface and blits a clipped portion of that surface to match HP %. |

---

## 🎮 Game Logic Package (`src.game`)

### 📦 `entities` - Actors
| Script | Class | Logic / Pseudo-Code |
| :--- | :--- | :--- |
| `players/FoxPlayer.py` | `FoxPlayer` | **Logic:** Input state machine. `handle_input` maps keys to velocity. Detects "Hazard" tiles by inflating its hit-rect by 8px and scanning the platform group. |
| `enemies/BaseEnemy.py` | `BaseEnemy` | **Logic:** Generic damage handler. Implements `take_damage` which applies a knockback vector: `vel.x = (direction * knockback_force)`. |
| `enemies/RabbitEnemy.py`| `RabbitEnemy`| **Logic:** Personality AI. Randomly switches between 'walk', 'dodge', and 'taunt' states based on a timer and player distance. |
| `enemies/BossRabbit.py` | `BossRabbit` | **Logic:** Tactical AI. Tries to maintain an "ideal distance" (5 tiles) from the player. Flees and triggers `weapon.reload()` when ammo is empty. |
| `enemies/Insect.py`   | `Insect`      | **Logic:** Patrol AI. Performs "Edge Detection" by checking a 2x2 pixel area in front and below its feet. If no collision, it flips direction. |
| `enemies/Bee.py`      | `Bee`         | **Logic:** Flying AI. Uses vector normalization to move toward the player. If it hits a wall, it attempts to "slide" along the axis with the smallest difference. |
| `npcs/Merchant.py`    | `Merchant`    | **Logic:** Static interaction actor. Placeholder for shop logic. |

### 📦 `weapons` - Combat
| Script | Class | Logic / Pseudo-Code |
| :--- | :--- | :--- |
| `BaseWeapon.py`       | `BaseWeapon`     | **Logic:** Timer-based reload. `update()` checks `now - reload_start > reload_speed`. `can_shoot()` checks `ammo > 0` and `fire_rate` cooldown. |
| `Pistol.py`, `SMG.py`| ...              | **Logic:** Data overrides for `BaseWeapon`. SMG uses `shoot_type = 'auto'`. |
| `RocketLauncher.py`   | `RocketLauncher` | **Logic:** Overrides `shoot_type` to 'rocket', triggering the `EffectManager.spawn_rocket` logic. |

### 📦 `world` - Environment
| Script | Class | Logic / Pseudo-Code |
| :--- | :--- | :--- |
| `Tile.py`             | `Tile`           | **Logic:** Static collider. Stores `damage` values for poison floor logic. |
| `ExplodingTile.py`    | `ExplodingTile`  | **Logic:** Proximity trigger. If `player.current_ground == self`, start growth animation. Uses `math.sin` for a red pulsing alpha overlay before `kill()`. |
| `MovingPlatform.py`   | `MovingPlatform` | **Logic:** Waypoint logic. Moves toward `nodes[idx]`. When `dist < speed`, snaps to node and increments `idx`. |
| `Trampoline.py`       | `Trampoline`     | **Logic:** Bounce logic. If `player.vel.y > 0` and `colliderect`, sets `player.vel.y = jump_boost`. |
| `ThrowingKnife.py`    | `ThrowingKnife`  | **Logic:** Invisible Raycast. Has a long `ray_rect`. If player enters `ray_rect`, `triggered = True` and the knife begins moving in its fixed direction. |

---

## 🛠️ Editor Suite (`tools`)

### 📦 `LevelEditor.py` - Orchestrator
**Logic:** State machine (`MENU`, `EDITING`, `SETTINGS`). Dispatches events to UI Panels first; if unhandled, dispatches to `handle_click` for world editing. 

### 📦 `editor` package
| Script | Class | Logic / Pseudo-Code |
| :--- | :--- | :--- |
| `Camera.py`          | `EditorCamera`   | **Logic:** Coordinate mapping. `screen_to_world = (mouse_pos - offset) / zoom`. Essential for placing tiles correctly while zoomed. |
| `CommandStack.py`    | `CommandStack`   | **Logic:** Undo/Redo. Stores `Command` objects. `undo()` calls `command.undo()` and moves it to a redo list. |
| `UIComponents.py`    | `Button`, `Panel`| **Logic:** Event consumption. `handle_event` returns `True` if the mouse is within the component's rect, preventing clicks from "bleeding through" to the world. |

---

## 📁 Data Schemas

### Level JSON Structure
```python
{
    "metadata": { "theme": "nature_1", "parallax_intensity": 1.1, "parallax_y_offset": 50 },
    "layers": {
        "main": [ ["TILE_ID", "TILE_ID[layer:front]"], ... ], # 2D Grid
        "entities": [ { "type": "BOSS_R", "x": 500, "y": 200, "properties": { "hp": 500 } } ]
    }
}
```

### Registry JSON Structure
```python
{
    "items": {
        "ID": {
            "category": "Enemies",
            "type": "entity",
            "module": "src.game.entities.enemies.Bee",
            "class": "Bee",
            "asset": "path/to/img.png"
        }
    }
}
```
