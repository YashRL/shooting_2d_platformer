# Phase 3: Game Modules Refactoring Plan

## Objective
Migrate the `modules/` directory into `src/game/`. Ensure strict one-class-per-file isolation for players, enemies, weapons, and world items.

## Actions to Execute (Do not deviate):

1. **Players (`modules/player/`)**
   - Move `fox.py` contents to `src/game/entities/players/FoxPlayer.py` (assuming class is `FoxPlayer`). Extract any base classes (e.g., `BasePlayer`) into `src/game/entities/players/BasePlayer.py`.

2. **Enemies (`modules/enemies/` and root `enemies.py`)**
   - Move `base_enemy.py` -> `src/game/entities/enemies/BaseEnemy.py`.
   - Move `rabbit.py` -> `src/game/entities/enemies/RabbitEnemy.py`.
   - Move `boss_rabbit.py` -> `src/game/entities/enemies/BossRabbit.py`.
   - Move `insect.py` -> `src/game/entities/enemies/Insect.py`.
   - Move `bee.py` -> `src/game/entities/enemies/Bee.py`.
   - Ensure the root-level `enemies.py` file is dismantled. If it contains a factory or registry (e.g., `EnemyFactory`), create `src/game/entities/enemies/EnemyFactory.py` and move the logic there. Delete root `enemies.py`.

3. **NPCs (`modules/characters/`)**
   - Move `merchant.py` -> `src/game/entities/npcs/Merchant.py`.

4. **Weapons (`modules/weapons/`)**
   - Move `base_weapon.py` -> `src/game/weapons/BaseWeapon.py`.
   - Move `pistol.py` -> `src/game/weapons/Pistol.py`.
   - Move `smg.py` -> `src/game/weapons/SMG.py`.
   - Move `rocket_launcher.py` -> `src/game/weapons/RocketLauncher.py`.

5. **World (`modules/world/`)**
   - Open `modules/world/tile.py`. If it contains `Tile` and `ExplodingTile`, split them into `src/game/world/Tile.py` and `src/game/world/ExplodingTile.py`.
   - Move `barrel.py` -> `src/game/world/ExplosiveBarrel.py` (rename file to match class).
   - Move `moving_platform.py` -> `src/game/world/MovingPlatform.py`.
   - Move `trampoline.py` -> `src/game/world/Trampoline.py`.
   - Move `trap.py` -> `src/game/world/Trap.py`. Extract `ThrowingKnife` if it's in here into `src/game/world/ThrowingKnife.py`.

6. **Cleanup:**
   - Delete the old `modules/` folder.

## Completion Criteria
The old `modules/` folder is gone. `src/game/` is fully populated. Every file contains exactly one class and is named via PascalCase matching the class name.