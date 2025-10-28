# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based game automation bot for Lineage that uses computer vision (OpenCV, YOLO) to detect targets and PyAutoGUI to perform automated actions. The bot captures game window screenshots, detects objects using trained models, and automates character movement and combat.

## Project Structure

```
lineage-bot/
├── src/
│   ├── core/                       # Reusable core components
│   │   ├── window_capture.py       # Win32 API window screenshot capture
│   │   ├── vision.py, vision_v2.py # Detection rectangle to click point conversion
│   │   ├── detection/              # Object detection modules
│   │   │   ├── yolo.py            # YOLO v1 detection (threaded)
│   │   │   ├── yolo_v2.py         # YOLO v2 with enhanced result parsing
│   │   │   └── cascade.py         # Cascade classifier detection (legacy)
│   │   └── utils/
│   │       └── bot_utils.py       # Target sorting and positioning utilities
│   │
│   ├── bots/                       # Bot implementations organized by area
│   │   ├── chi2/                   # Chi2 cave bot
│   │   │   ├── bot.py             # Chi2Bot class with state machine
│   │   │   ├── mage.py            # Chi2 mage variant
│   │   │   └── runner.py          # Main entry point
│   │   ├── la3/                    # LA3 area bot
│   │   ├── sea3/                   # Sea3 area bot
│   │   └── dragon6/                # Dragon6 area bot
│   │
│   └── login/                      # Login automation
│       └── auto_login.py
│
├── models/                         # All trained models
│   ├── yolo/                       # YOLO .pt model files
│   └── cascade/                    # Cascade classifier XML files
│
├── scripts/                        # Clean entry point scripts
│   ├── run_chi2.py
│   ├── run_la3.py
│   └── ...
│
├── tools/                          # Development and training tools
│   ├── capture.py                  # Screenshot capture utility
│   ├── train/                      # Model testing scripts
│   └── legacy/tutorial/            # Learning examples (archived)
│
└── bin/                            # Batch scripts (Windows)
```

## Environment Setup

1. Create Python virtual environment:
   ```bash
   python -m venv .venv
   ```

2. Activate virtual environment:
   - Windows: `.\.venv\Scripts\activate`
   - macOS/Linux: `source .venv/bin/activate`

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running Bots

### Using Batch Scripts (Windows)

The project includes Windows batch scripts in `bin/` that handle environment setup and bot execution:

- `bin/chi2.bat` - Runs Chi2 cave bot (requires `LIN_BOT_PATH` environment variable)
- `bin/la3.bat` - Runs LA3 bot
- `bin/sea3.bat` - Runs Sea3 bot
- `bin/dragon6.bat` - Runs Dragon6 bot

Each batch script:
1. Checks for `LIN_BOT_PATH` environment variable
2. Creates virtual environment if it doesn't exist
3. Installs dependencies
4. Runs the corresponding bot script from `scripts/`

### Direct Python Execution

```bash
# Run from project root
python scripts/run_chi2.py
python scripts/run_la3.py
python scripts/run_sea3.py
python scripts/run_dragon6.py
python scripts/run_login.py
```

## Architecture

### Core Components

1. **Window Capture** (`src/core/window_capture.py`):
   - Captures game window screenshots using Win32 API in a threaded loop
   - Handles window border/titlebar offsets (8px border, 30px titlebar)
   - Provides coordinate translation between screenshot and screen positions via `get_screen_position()`

2. **Detection Systems** (`src/core/detection/`):
   - **`yolo.py`**: YOLO-based object detection with `plot_bboxes()` returning `[x, y, w, h, name]`
   - **`yolo_v2.py`**: Enhanced YOLO with `plot_result()` returning `[x, y, x2, y2, name, conf]`
   - **`cascade.py`**: Cascade classifier-based detection (older approach, less accurate)
   - All detection modules run in separate threads for real-time processing

3. **Vision** (`src/core/vision.py`, `vision_v2.py`):
   - Converts detection rectangles to click points (center of bounding boxes)
   - `get_click_points()`: Returns list of (x, y) tuples for clicking
   - `draw_rectangles()`: Visualization for debugging

4. **Bot State Machine** (`src/bots/*/bot.py`):
   - States: INITIALIZING, SEARCHING, MOVING, MINING, BACKTRACKING
   - Target prioritization by pythagorean distance from character (always at screen center)
   - Skill timing (F7, F9 keys) with configurable delays
   - Ignore list to prevent re-attacking same positions
   - Movement logic (F5 key) when no targets detected or timeout reached

5. **Runner Scripts** (`src/bots/*/runner.py`):
   - Main entry points wrapping bot execution in `main()` function
   - Initialize WindowCapture, YoloDetection, Vision, and Bot instances
   - Coordinate threaded execution: capture → detection → bot action loop
   - Handle keyboard controls (q=quit, p=pause, c=continue) when DEBUG=True

6. **Utilities** (`src/core/utils/bot_utils.py`):
   - `targets_ordered_by_distance()`: Filters and sorts targets by distance with inner/outer radius constraints
   - `find_next_target()`: Finds non-ignored target from sorted list
   - `get_screen_position()`: Translates screenshot coordinates to screen coordinates
   - `is_duplicated_target()`: Checks if target position already attacked

### Bot Behavior Configuration

Each bot class defines tunable constants:
- `INNER_IGNORE_RADIUS` / `OUTER_IGNORE_RADIUS`: Target detection range (typically 0-500 pixels)
- `SKILL_F7_DELAY`, `SKILL_F9_DELAY`: Cooldown timers for skills (seconds)
- `SKILL_MOVE_DELAY`: Time before triggering movement (typically 20-30s)
- `DETECTION_WAITING_THRESHOLD`: Timeout before moving when no targets found (5-8s)
- `ATTACK_INTERVAL`: Duration of attack action (1-1.5s)
- `ENABLE_F7`, `ENABLE_F9`, `ENABLE_MOVING`: Feature flags to enable/disable specific behaviors

### Threading Model

All major components run in separate threads with Lock-based synchronization:
- **WindowCapture**: Continuously captures screenshots at max rate
- **YoloDetection**: Continuously processes frames for object detection
- **Bot**: Runs state machine logic and controls PyAutoGUI actions
- Thread-safe updates via `Lock.acquire()` / `Lock.release()` pattern

### Model Management

Models are stored in `models/` directory at project root:
- **YOLO models** (`models/yolo/`): `.pt` files for different areas (chi2.pt, la3-v3.pt, stairs2.pt, etc.)
- **Cascade models** (`models/cascade/`): XML files for cascade classifiers (legacy)

Runner scripts reference models with relative paths from project root: `'models/yolo/chi2.pt'`

## Development Workflow

### Adding a New Bot Variant

1. Create new bot directory: `src/bots/new_area/`
2. Copy existing bot class (e.g., from `chi2/bot.py`)
3. Adjust tunable constants for area-specific behavior
4. Create `runner.py` with proper imports
5. Train YOLO model for new area and place in `models/yolo/`
6. Add entry script in `scripts/run_new_area.py`
7. Create batch script in `bin/new_area.bat`

### Training New Detection Models

1. Collect screenshots using `tools/capture.py`
2. Train YOLO model using external tools (Ultralytics, Roboflow, etc.)
3. Place trained `.pt` file in `models/yolo/`
4. Test with `tools/train/test_yolo_img.py`
5. Adjust confidence threshold in bot runner (conf parameter)

### Debugging

- Set `DEBUG = True` in runner script to enable OpenCV visualization
- Use keyboard controls: **q** (quit), **p** (pause), **c** (continue)
- Check console output for state transitions and target detection logs
- Monitor ignore list growth to debug target deduplication

## Key Implementation Details

- **Character position**: Always assumed to be at screen center (`window_w/2, window_h/2`)
- **Coordinate systems**: Code distinguishes between screenshot coordinates (relative to captured image) and screen coordinates (absolute). Use `get_screen_position()` for translation.
- **Target deduplication**: Bots maintain `ignore_positions` list with summed coordinates `(x + y + distance)` to avoid re-clicking. Cleared on F5 press.
- **Movement reset**: Pressing F5 clears ignore list and resets detection timers (`last_detect_time`, `last_move_time`, `last_search_time`)
- **Import structure**: All imports use absolute paths from project root (e.g., `from src.core.detection.yolo import YoloDetection`)
- **pywin32 dependency**: Required for Win32 API window capture. Only works on Windows.

## Legacy Code

- **Original lin_bot/ directory**: Preserved for reference but deprecated
- **Tutorial examples**: Moved to `tools/legacy/tutorial/` (learning progression from basic template matching to full bot)
- **train-model/ directory**: Preserved but scripts moved to `tools/train/`
