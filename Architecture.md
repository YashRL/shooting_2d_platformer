# TheTreeSentinal Engine 2.0 - Technical Architecture & API Reference

## 🏗️ Architectural Paradigm
TheTreeSentinal Engine 2.0 is built using a **Modular Registry-Driven Architecture**. It enforces strict Java-style packaging and a "One Class, One Script" philosophy. 

- **State Management:** Driven by unified JSON level files.
- **Dependency Injection:** Done via the `ResourceManager`, which handles asset loading and dynamic entity instantiation.
- **Physics:** Centralized in a base `PhysicsEntity` class using `pygame.Vector2` for sub-pixel precision.
- **Rendering Pipeline:** Uses a `world_surface` for post-processing before blitting to the main screen.

---

## 📂 Package Index

### 1. `src.engine` (Core Systems)
| Class | Location | Description |
| :--- | :--- | :--- |
| **`ResourceManager`** | `core/ResourceManager.py` | Handles asset loading and dynamic entity instantiation. Injects `item_id`, `asset`, and `category` into all spawned entities. |
| **`PhysicsEntity`** | `core/PhysicsEntity.py` | Base class for movement and two-pass collision detection. |
| **`AnimationManager`** | `graphics/AnimationManager.py` | State-based frame cycling with support for surgical damage flashes. |
| **`ParallaxManager`** | `graphics/ParallaxManager.py` | Manages infinite looping background layers. |
| **`EffectManager`** | `graphics/EffectManager.py` | Orchestrator for particles, screen shake, and projectiles. |
| **`UIManager`** | `ui/UIManager.py` | Handles HUD rendering: segmented health bars and ammo counters. |

### 2. `src.game` (Gameplay Logic)
| Sub-Package | Key Classes | Description |
| :--- | :--- | :--- |
| **`entities.players`** | `FoxPlayer` | Main player controller. Respects manual `START` position from level data. |
| **`entities.enemies`** | `BaseEnemy`, `RabbitEnemy`, `Bee` | AI actors using state-machine personalities. |
| **`weapons`** | `BaseWeapon`, `Pistol`, `SMG` | Modular weapon logic. Stats and sprites are registry-injected. |
| **`world`** | `Tile`, `ExplodingTile`, `WorldItem` | Interactive environment items. `WorldItem` wraps standalone weapons. |

### 3. `tools.editor` (Development Suite)
| Class | Location | Description |
| :--- | :--- | :--- |
| **`LevelEditor`** | `LevelEditor.py` | State machine (Menu, Editing, Settings). Supports **Manual Player Placement** and **Noir Filters**. |
| **`EditorCamera`** | `editor/Camera.py` | Panning and zoom logic with screen-to-world coordinate mapping. |
| **`CommandStack`** | `editor/CommandStack.py` | Undo/Redo implementation via the Command Pattern. |
| **`UIComponents`** | `editor/UIComponents.py` | OOP GUI Library (Panel, Button, InputBox). |

---

## 🧬 Core Logic Snippets

### Post-Processing Filter (Noir Theme)
The engine supports full-screen filters. The `world_surface` is rendered first, then a transformation is applied.

```python
# From src/main.py
# 1. Draw all game elements to a dedicated surface
self.world_surface.fill((0, 0, 0))
self.draw_world(self.world_surface) 
self.ui_manager.draw(self.world_surface)

# 2. Apply filter if active in metadata
final_view = self.world_surface
if self.metadata.get("filters", {}).get("noir"):
    final_view = pygame.transform.grayscale(self.world_surface)

# 3. Blit result to screen
self.screen.blit(final_view, (0, 0))
```

### Manual Player Placement (Singleton START)
The editor ensures only one player spawn exists by enforcing a singleton pattern for the `START` entity type.

```python
# From tools/LevelEditor.py
if self.selected_tile == "START":
    # Remove any existing START entity before placing the new one
    self.level_data["layers"]["entities"] = [e for e in self.level_data["layers"]["entities"] if e["type"] != "START"]
```

---

## 🛠️ Editor Features

- **Scrollable Item Grid:** The sidebar supports vertical scrolling via `MOUSEWHEEL` and uses `screen.set_clip()` for clean rendering.
- **Settings Panel:** Dedicated screen for configuring themes, parallax intensity, and full-screen filters.
- **Entity Previews:** The editor renders the actual sprite for all placed entities (Enemies, Weapons, Start points) instead of placeholders.

---

## 📁 Data Formats

### Level JSON (`levels/*.json`)
```json
{
    "metadata": { 
        "theme": "nature_1", 
        "parallax_intensity": 1.0,
        "filters": { "noir": true }
    },
    "layers": {
        "main": [ ["Concrete_tile", "-1"], ... ],
        "entities": [ 
            { "type": "START", "x": 100, "y": 200, "properties": {} },
            { "type": "Pistol", "x": 300, "y": 200, "properties": {} }
        ]
    }
}
```
