# Pixoo 64 Snake Game

<img src="https://github.com/user-attachments/assets/fcca8438-1d1e-4122-b038-c3ecb5fd2978" width="49%"></img><img src="https://github.com/user-attachments/assets/084c4020-9a61-4954-9927-a7b24fad0c00" width="49%"></img>

Pixoo Snake is a classic snake game designed for the Divoom Pixoo device. It features real-time rendering, adjustable difficulty, and a graphical user interface built using Tkinter.

## Features
- Play Snake on a Divoom Pixoo device
- Adjustable difficulty levels: Easy, Medium, Hard, and Insane
- Graphical preview using Tkinter
- Pause, resume, and stop the game anytime
- Grid toggle for better visualization
- Smooth gameplay with responsive controls

## Requirements
- Python 3.x
- Divoom Pixoo device
- Dependencies:
  - `Pillow`
  - `tkinter`
  - [`pixoo` (Custom module for handling Pixoo communication)](https://github.com/SomethingWithComputers/pixoo)

## Installation
1. Clone this repository:
   ```bash
   git clone https://github.com/itsmikethetech/Pixoo-64-Snake.git
   cd Pixoo-64-Snake
   ```
2. Install dependencies:
   ```bash
   pip install Pillow tkinter pixoo
   ```
3. Run the script:
   ```bash
   python Snake.py
   ```

## How to Play
1. Ensure your Divoom Pixoo is connected to the same network.
2. Enter the Pixoo's IP address in the GUI (default is `192.168.1.215`).
3. Click "Connect" to establish a connection.
4. Choose a difficulty level.
5. Click "Start Game" to begin.
6. Control the snake using arrow keys:
   - `Up`: Move up
   - `Down`: Move down
   - `Left`: Move left
   - `Right`: Move right
7. Avoid colliding with yourself; eat food to grow longer.
8. Pause, resume, or stop the game using the GUI buttons.

## Troubleshooting
- **Pixoo not connecting?** Ensure it is powered on and reachable at the entered IP.
- **Game not displaying on Pixoo?** Check network connectivity and try restarting both the game and Pixoo.
- **Snake unresponsive?** Make sure the game is running and focused before using arrow keys.
