# Minecraft Coordinates Manager (Tkinter GUI)

This is a small Python program I made to keep track of Minecraft coordinates.  
It lets you create profiles for different worlds (like SMP servers, singleplayer worlds, etc.), save locations with names, and optionally store the world seed. Everything is stored in a `cords-data.json` file so it stays saved between runs.

The goal of this tool is just to make it easier to keep track of places without writing them down or losing them.

---

## Features

### Profiles
- Create as many profiles as you want (SMP, Hardcore, Testing World, etc.)
- Each profile can have:
  - A world seed (optional)
  - A list of saved coordinates

### Coordinate Saving
- Add coordinates with a custom name  
- Coordinates are saved as X, Y, Z values
- You can load, remove, or re-add updated coordinates
- Copy the selected coordinate to clipboard
- Print coordinates to the terminal for quick access

### Data Handling
- Automatically saves everything into `cords-data.json`
- Supports exporting your data to a JSON file
- Supports importing JSON files back into the app

### GUI
- Built with Tkinter
- Works on Linux, Windows, and macOS
- Simple interface with a profile list on the left and coordinates on the right

---

## Installing Tkinter (Linux Mint / Ubuntu)

If Tkinter isn’t installed, open a terminal and run:

```bash
sudo apt update
sudo apt install python3-tk
```

You can test it with:

```bash
python3 -m tkinter
```

If a little Tk window opens, you’re good to go.

---

## How to Run

Clone the repo:

```bash
git clone https://github.com/ToastyPixel/minecraft-coords-manager.git
cd Minecraft-Coordinates-Manager
```

Then run the program:

```bash
python3 minecraft_coords_manager.py
```

---

## Data File

All of your profiles and coordinates are stored here:

```
cords-data.json
```

Example format:

```json
{
  "My SMP": {
    "seed": "123456789",
    "coords": [
      { "name": "Spawn", "x": 0, "y": 64, "z": 0 },
      { "name": "Cool Cave", "x": -3237, "y": 40, "z": 1820 }
    ]
  }
}
```

---

## Folder Layout

```
Minecraft-Coordinates-Manager/
│
├── minecraft_coords_manager.py
├── cords-data.json   (generated automatically)
└── README.md
```

---
