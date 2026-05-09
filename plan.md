# Master Restructuring & UI Architecture Plan

## Executive Summary
This document serves as the master index for the comprehensive restructuring of the 2D Platformer Engine. The goal is to adopt strict Object-Oriented Programming (OOP) principles, enforce a Java-style "One Class = One Script" rule, transition level data to a unified JSON format, and rebuild the Level Editor UI using modular, component-based best practices.

Because the project is large, the restructuring is split into 6 distinct, highly detailed phases. Each phase has its own dedicated plan file. **All thinking and architectural decisions have been resolved in these documents.** During execution, the goal is pure implementation of these plans.

## Target Directory Architecture
```text
D:\Yash_Code\2D_Game\
├── Assets/                 # Static resources (Images, Audio)
├── data/                   # JSON config/registry
├── levels/                 # JSON level data (Unified format)
├── tools/                  # All utility scripts
│   ├── LevelEditor.py      # New Modular OOP Editor
│   ├── AssetRecolor.py     
│   └── SpriteSplitter.py   
├── tests/                  # All test scripts
├── src/                    # The Java-style root package
│   ├── main.py             # Game entry point
│   ├── engine/             # Core Engine Package
│   │   ├── core/           
│   │   │   ├── ResourceManager.py
│   │   │   └── PhysicsEntity.py
│   │   ├── graphics/       
│   │   │   ├── AnimationManager.py
│   │   │   ├── ParallaxManager.py
│   │   │   └── EffectManager.py
│   │   └── ui/             
│   │       └── UIManager.py
│   ├── game/               # Gameplay Specific Logic
│   │   ├── entities/       
│   │   │   ├── players/    
│   │   │   │   ├── BasePlayer.py
│   │   │   │   └── FoxPlayer.py
│   │   │   ├── enemies/    
│   │   │   │   ├── BaseEnemy.py
│   │   │   │   ├── RabbitEnemy.py
│   │   │   │   ├── BossRabbit.py
│   │   │   │   ├── Insect.py
│   │   │   │   └── Bee.py
│   │   │   └── npcs/       
│   │   │       └── Merchant.py
│   │   ├── weapons/        
│   │   │   ├── BaseWeapon.py
│   │   │   ├── Pistol.py
│   │   │   ├── SMG.py
│   │   │   └── RocketLauncher.py
│   │   └── world/          
│   │       ├── Tile.py
│   │       ├── ExplosiveBarrel.py
│   │       ├── Trampoline.py
│   │       ├── MovingPlatform.py
│   │       └── Trap.py
└── GEMINI.md               # Project rules
```

## Detailed Execution Phases
Read these files in order to execute the restructuring:
1.  **[Phase 1: Scaffolding & Cleanup](plans/phase_1_scaffolding.md)**
2.  **[Phase 2: Engine Core Refactoring](plans/phase_2_engine_refactor.md)**
3.  **[Phase 3: Game Modules Refactoring](plans/phase_3_game_refactor.md)**
4.  **[Phase 4: Level Data Migration to JSON](plans/phase_4_data_migration.md)**
5.  **[Phase 5: Level Editor UI Rebuild](plans/phase_5_editor_ui.md)**
6.  **[Phase 6: Wiring & Final Integration](plans/phase_6_wiring.md)**