# Clash of Clans Automation Bot

A Python automation bot for **Clash of Clans** that performs resource farming, attacks, wall upgrades, obstacle removal, and account management using image recognition, OCR, and human-like mouse movement.

> **Disclaimer**
>
> This project is intended for educational purposes and computer vision/automation research. Using automation in Clash of Clans may violate Supercell's Terms of Service and could result in account penalties.

---

## Features

### ⚔️ Automated Attacking
- Searches for multiplayer matches automatically
- Evaluates available loot using OCR
- Skips low-value bases
- Deploys troops using recorded human mouse movements
- Detects battle completion
- Automatically returns home

### 💰 Smart Loot Detection
- Reads Gold and Elixir using EasyOCR
- Attacks only when loot exceeds a configurable threshold
- Continues searching until a profitable base is found

### 🧠 Human-Like Behavior
- Human cursor movement
- Random click offsets
- Randomized delays
- Random village movements
- Random breaks
- Random zooming and dragging
- Replay system using recorded real mouse movements

### ⚡ Lightning Spell Automation
- Detects Air Defenses
- Determines spell count based on Air Defense level
- Casts Lightning Spells automatically

### 🏰 Automatic Wall Upgrades
When storages become full the bot can:

- Upgrade walls automatically
- Detect whether Gold or Elixir should be used
- Upgrade multiple walls at once
- Handle edge cases when only one wall remains

### 🌳 Base Cleanup
Optionally removes:

- Trees
- Bushes
- Logs
- Decorations
- Gem Boxes
- Other removable obstacles

### 👥 Multi-Account Farming
Supports farming multiple Clash of Clans accounts.

Features include:
- Automatic account switching
- Farm until storages are full
- Continue with the next account
- Supports multiple configured accounts

### 🎯 OCR Resource Detection
Uses EasyOCR to read:

- Gold
- Elixir

allowing intelligent attack decisions.

---

# Technologies Used

- Python 3
- PyAutoGUI
- EasyOCR
- Pillow
- NumPy
- HumanCursor
- pynput
- keyboard
- mouse
- pyscreeze

---

# Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/yourrepository.git
cd yourrepository
```

Install dependencies:

```bash
pip install pyautogui
pip install easyocr
pip install pillow
pip install numpy
pip install keyboard
pip install mouse
pip install humancursor
pip install pynput
pip install pyscreeze
```

---

# Required Files

The project expects the following folders:

```
pics/
json/
coords.py
```

### pics/

Contains screenshots used for image recognition such as:

- Attack buttons
- Air Defenses
- Upgrade buttons
- Builder icons
- Clan interface
- Obstacles
- Resource collectors
- Wall upgrade buttons

---

### json/

Contains recorded human deployment paths:

```
recordings.json
```

These recordings are replayed with slight randomization for realistic troop deployment.

---

# Configuration

At startup the script asks:

```
Farm resources on other accounts?
```

You can add account names or skip.

Then:

```
Stop program when storages are full?
```

Finally:

```
Clean the base?
```

This determines whether obstacle removal runs before farming.

---

# Project Structure

```
project/
│
├── pics/
├── json/
│   └── recordings.json
├── coords.py
├── main.py
└── README.md
```

---

# How It Works

1. Collect Star Bonus (if available)
2. Check if storages are full
3. Upgrade walls (optional)
4. Perform random human-like village actions
5. Search for a multiplayer match
6. Read loot using OCR
7. Skip low-value bases
8. Deploy troops using recorded human input
9. Monitor battle
10. Return home
11. Repeat

---

# Human Simulation

To reduce repetitive behavior the bot includes:

- Random pauses
- Random cursor offsets
- Human cursor paths
- Random village exploration
- Random scrolling
- Random zooming
- Random dragging
- Random idle time
- Real recorded deployment replays

---

# Notes

The bot depends heavily on image recognition.

If Supercell changes the game UI, screenshots inside the `pics` folder may need to be updated.

Screen resolution, scaling, and UI layout should remain consistent for best performance.

---

# License

This project is provided for educational purposes only.

Use at your own risk.
