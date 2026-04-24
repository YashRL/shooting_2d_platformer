# 2D Platformer Project - Gemini memory

## 🚀 Project Overview
A 2D side-scrolling platformer built with **Pygame-ce** using modular Python scripts.

## 🛠️ Tech Stack & Environment
- **Engine**: Pygame-ce (Community Edition)
- **Environment**: Conda env named `games` (Python 3.10)
- **Assets**: Custom Kenney-style sprites (18x18 scaled to 36x36)

## 📁 File Structure
- `main.py`: The core game loop, camera, and player controller.
- `level_editor.py`: Visual tool to design levels and save to CSV.
- `enemies.py`: Registry and logic for ground and flying AI.
- `effects.py`: Particle manager and screen juice (shake, muzzle flash).
- `levels/`: Folder containing `.csv` level data.

## 🗝️ Custom Map Identifiers (CSV Codes)
| Code | Item | Description |
|---|---|---|
| **1-234** | Tiles | Environment tiles (numbered X.png) |
| **P** | Pistol | Old 6-shooter, decent damage, manual fire |
| **CT** | Chicago Typewriter | Automatic SMG, fast fire rate, 30 ammo |
| **E_I** | Insect | Ground enemy, slow patrol, edge detection |
| **E_b** | Bee | Advanced flying AI, 10-tile chase radius, obstacle avoidance |

## 🎮 Controls
- **W**: Jump / Double Jump
- **A / D**: Move Left / Right
- **Spacebar**: Shoot Weapon
- **E**: Pick up Item
- **R**: Reload Weapon
- **1 / 2**: Switch Weapon Slots

## ✨ Juicy Features
- **Smooth Camera**: Centers on player and clamps to map edges.
- **Combat Juice**: Screen shake on fire, muzzle flash particles, red hit flashes.
- **Physics**: 0.8 Gravity, scalable resistance-based knockback for enemies.
- **UI**: Circular reload progress bar near player, HP/Ammo HUD.

## 📌 Development Notes
- All tiles were renamed from `tile_0000.png` to `1.png` for direct numeric access.
- Enemies have a `resistance` stat that affects how far they are pushed back by bullets.
