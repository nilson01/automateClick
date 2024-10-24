
# Automation Project

This project automates clicking buttons on the screen for tasks like confirming transactions in MetaMask. It supports two modes of operation:
- **2Clicker**: Automates two buttons (Write and Confirm).
- **5Clicker**: Automates a sequence involving MetaMask interactions (Write, Confirm, MetaMask, Speed Up, and Submit).

## Features
- Automates tasks by locating and clicking buttons on the screen.
- Easily configurable by replacing images in the `source` folder.
- Two modes: `testing` (1 minute) and `production` (1 hour).
- Logging of actions with timestamps and coordinates.

## Setup

### Step 1: Clone the repository
```bash
git clone https://github.com/yourusername/automation_project.git
cd automation_project
```

### Step 2: Set up the environment
```bash
python -m venv env  # or conda create --name automation_env python=3.9
source env/bin/activate  # Windows: .\env\Scripts\activate
```

### Step 3: Install dependencies
```bash
pip install -r requirements.txt
```

## Usage

### 2Clicker
To run the 2Clicker automation script, which automates two steps:
```bash
python clicker/2Clicker.py
```

### 5Clicker
To run the 5Clicker automation script, which automates MetaMask-related steps:
```bash
python clicker/5Clicker.py
```

Choose `testing` or `production` mode when prompted.

## Contributing
Feel free to open issues or submit pull requests. Let's automate things together!
