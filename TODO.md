# TheTreeSentinal Engine 2.0 - Roadmap & TODO

## 🎯 High Priority: Universal Property Inspector
The goal is to allow the Level Editor to modify the stats of **any** spawned entity (Enemies, Bosses, Platforms, Traps) individually.

### 1. Editor Components (Missing)
- [ ] **`PropertyInspector` Class:** A new UI component in `tools/editor/` that dynamically generates input fields based on the selected entity's type.
- [ ] **Selection Logic:** Implement `handle_selection` in `LevelEditor.py` to find the entity at mouse coordinates when using the **SELECT** tool.
- [ ] **Dynamic UI Binding:** The inspector must read the `properties` dict from the entity in `level_data` and write back to it when the user types.

### 2. Engine Improvements
- [ ] **Stat Serialization:** Ensure all entities (like `Insect.py` or `MovingPlatform.py`) prioritize the `properties` dict passed in their `__init__` over hardcoded defaults.
- [ ] **Visual Selection:** Highlight the selected entity in the editor with a distinct colored border or bounding box.

## 🛠️ Important Classes for Implementation
- **`tools/LevelEditor.py`**: Must manage the `selected_entity` state and toggle the visibility of the Property Inspector.
- **`tools/editor/UIComponents.py`**: Needs specialized `NumericInput` or improved `InputBox` to handle stat changes cleanly.
- **`src/engine/core/ResourceManager.py`**: The `spawn()` method is already set up to pass `**kwargs` as properties—ensure this is strictly followed by all game modules.
- **`src/game/entities/enemies/BaseEnemy.py`**: The foundation for all enemy stats. Ensure it handles custom HP/Speed flawlessly.

## 🎨 Visuals & Juice
- [ ] **Particle Editor:** A tool to test particle effects in real-time.
- [ ] **Sound System:** Implementation of `src/engine/core/SoundManager.py`.
- [ ] **Screen Transitions:** Fade-in/out between the Menu and the Game.

## 🐛 Bug Tracking
- [ ] **Layer Overlap:** Verify that [layer:front] tiles correctly block projectiles if they are meant to be solid.
- [ ] **Input Focus:** Ensure typing in an `InputBox` doesn't trigger game shortcuts (like Ctrl+Z).
