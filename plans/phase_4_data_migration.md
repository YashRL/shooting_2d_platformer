# Phase 4: Level Data Migration Plan

## Objective
Transition the game's level data format from dual `.csv` + `.json` files to a unified, hierarchical `.json` format to support advanced entity properties.

## Actions to Execute (Do not deviate):

1. **Create Migration Script:**
   - Create a temporary script at `tools/migrate_levels.py`.
   - The script must iterate through the `levels/` directory.
   - For every `level_X.csv` and its corresponding `level_X.json`:
     1. Read the CSV grid into a 2D array.
     2. Read the JSON metadata.
     3. Construct a new dictionary structure:
        ```python
        {
            "metadata": {
                "theme": "...",
                "parallax": "..."
            },
            "layers": {
                "background": [], # If applicable
                "main": [ # 2D array of tile IDs
                    [0, 1, 1, 0],
                    [2, 2, 2, 2]
                ],
                "entities": [ # List of specific entities parsed from the CSV
                    {"type": "PLAYER", "x": 5, "y": 10, "properties": {}},
                    {"type": "BOSS_RABBIT", "x": 20, "y": 10, "properties": {"hp": 500}}
                ]
            }
        }
        ```
     4. Save this new structure to `levels/level_X_new.json`.

2. **Execute Migration:**
   - Run `python tools/migrate_levels.py`.
   - Verify the generated `_new.json` files contain accurate map data.

3. **Update `ResourceManager` (Data Loader):**
   - Open `src/engine/core/ResourceManager.py`.
   - Modify the `load_level(level_name)` function.
   - Delete all CSV parsing logic (`csv.reader`).
   - Implement purely JSON parsing logic reading the new structure defined above.
   - Ensure entities are spawned correctly based on the `entities` list instead of scanning a raw CSV grid.

4. **Cleanup:**
   - Delete all `.csv` files from the `levels/` directory.
   - Rename `level_X_new.json` to overwrite the old `.json` files.
   - Delete `tools/migrate_levels.py`.

## Completion Criteria
The game levels are exclusively `.json`. The `ResourceManager` successfully parses the unified JSON format to render the map and spawn entities without crashing.