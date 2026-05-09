# Phase 5: Level Editor UI Rebuild Plan

## Objective
Completely rebuild `tools/LevelEditor.py` using a modular, OOP, component-based UI architecture, replacing the old imperative drawing logic. Implement a Command Pattern for Undo/Redo.

## Architecture Blueprint

Inside `tools/LevelEditor.py` (or a dedicated `tools/editor/` package if preferred during execution, but default to one file if small enough, or multiple files in `tools/editor_ui/`):

1. **`EditorCamera` Class:**
   - Manages `scroll_x` and `scroll_y`.
   - Handles Middle-Click panning and scrolling.

2. **`CommandStack` Class (Undo/Redo System):**
   - Maintains a `list` of executed commands and a pointer index.
   - **`Command` Interface:** Has `execute()` and `undo()` methods.
   - **`PlaceTileCommand(x, y, layer, old_id, new_id)`**: Reverts a specific tile change.
   - **`PlaceEntityCommand(entity_data)`**: Removes/Adds an entity from the JSON entity list.

3. **UI Components (Classes):**
   - **`Button(Rect, text, callback)`**: Handles hover states, clicks, and rendering.
   - **`SidebarPanel`**: Renders the background panel, handles scrolling if too many items.
   - **`PropertyInspector`**: A specialized panel that appears when an entity (like BOSS) is selected. It renders input boxes for dynamic properties (e.g., `hp`, `speed`).

4. **`LevelEditor` Main Class:**
   - The State Machine for the editor.
   - Instantiates `EditorCamera`, `CommandStack`, and UI Components.
   - **`update()`**: Dispatches events to UI components first. If UI doesn't consume the click, dispatches to the canvas grid.
   - **`draw()`**: Draws the map (using `Camera` offset), then draws the Grid overlay, then calls `draw()` on all UI components.

5. **Saving / Loading Integration:**
   - Ensure the Editor writes to the new unified JSON format created in Phase 4.

## Actions to Execute (Do not deviate):
1. Rename old editor to `tools/old_level_editor.py` (done in Phase 1).
2. Create fresh `tools/LevelEditor.py`.
3. Implement `EditorCamera`.
4. Implement UI primitives (`Button`, `Panel`).
5. Implement `CommandStack` and Commands.
6. Implement main `LevelEditor` loop.
7. Wire up loading/saving the unified JSON format.

## Completion Criteria
Running `python tools/LevelEditor.py` launches a robust editor. You can place tiles, undo placements with `Ctrl+Z` perfectly, edit boss properties, and save the map as a single unified JSON file.