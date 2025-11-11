# 🏈 Sleeper Fantasy API Alerts

**Automated Fantasy Football League Insights & Alerts**

This project connects to the [Sleeper Fantasy Football API](https://sleeper.com) to automatically track your league’s results, standings, and player transactions — and deliver alerts directly to **Telegram**.  
It also runs on a **scheduled basis** via **GitHub Actions**, making it fully autonomous once deployed.

---

## 🚀 Features

✅ **Weekly Reports**  
- Automatically fetches league standings and matchup results every Tuesday (12h UTC).  
- Uses `weekly_alerts()` to build structured Telegram messages.

✅ **Daily Alerts**  
- Detects players dropped or moved to waivers.  
- Sends an alert when a **highly owned player (>70%)** is dropped.

✅ **Live Score Change Alerts** 🟢 *(new!)*  
- Monitors your fantasy team’s **live points** during matchups.  
- Sends a Telegram alert when your team scores **more than 5 new points**.  
- Identifies which **starter players** contributed to the increase.  
- Powered by:
  - `get_user_matchup()` → identifies your team’s matchup  
  - `get_user_starters_points()` → collects individual starter stats  
  - `live_score_change_alert()` → triggers score-based alerts  
  - 
✅ **Interactive Telegram Bot**  
- Users can message the bot directly with commands like:
  - `standings` or `classificação` → get current standings.
  - Future commands may include `results`, `waivers`, etc.

✅ **Modular Design**  
- Separate logic for weekly, daily, and live alerts.  
- Reusable and extendable code modules (`league_tools.py`, `alerts.py`, `telegram_bot.py`).

✅ **Fully Modular Design**  
- Separated logic per function and concern:
  - `league_tools.py` → data retrieval and transformations  
  - `alerts.py` → alert creation and formatting  
  - `telegram_bot.py` → message delivery  
  - `main.py` → entry point for automated runs  

---

## 🧱 Project Structure
```
sleeper-fantasy-api-alerts/
│
├── alerts.py # Daily, weekly, and live scoring alerts
├── league_tools.py # League data utilities (matchups, standings, points)
├── players_tools.py # Player data lookups and ownership ratios
├── telegram_bot.py # Sends messages to Telegram
├── telegram_interactive.py # Interactive bot for user commands
├── main.py # GitHub Actions entry point
│
├── .github/workflows/action_handler.yml # Automated scheduling
├── Procfile # For Render/Railway deployment
├── requirements.txt
├── .env.example
└── README.md
```

---

## ⚙️ Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/rico0406/sleeper-fantasy-api-alerts.git
cd sleeper-fantasy-api-alerts
```
2. Create a virtual environment

```bash
python -m venv venv
source venv/Scripts/activate   # Windows
source venv/bin/activate       # macOS/Linux
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Configure your environment

Copy .env.example to .env and fill in your credentials:

```bash
TELEGRAM_BOT_TOKEN=your_telegram_token
SLEEPER_LEAGUE_ID=your_sleeper_league_id
SLEEPER_USER_ID=your_user_id
```

💬 Run the Telegram Bot Locally

```bash
python telegram_interactive.py
```

You should see:

🤖 Telegram interactive bot is running...

Then, open your bot on Telegram and send a message:

standings

☁️ Deploy on Render / Railway

Push this project to your GitHub. Create a new Worker service 
on Render or Railway

Add environment variables:

    TELEGRAM_BOT_TOKEN

    SLEEPER_LEAGUE_ID

    SLEEPER_USER_ID

Deploy! The bot will stay online 24/7.

The Procfile handles the process:

worker: python telegram_interactive.py

🧠 Architecture Overview

| Layer                                             | Description                                 |
| ------------------------------------------------- | ------------------------------------------- |
| **Sleeper API Layer** (`league_tools.py`)         | Retrieves league, roster, and matchup data  |
| **Player Layer** (`players_tools.py`)             | Fetches player stats, names, and ownership  |
| **Alert Engine** (`alerts.py`)                    | Builds weekly, daily, and live score alerts |
| **Delivery System** (`telegram_bot.py`)           | Sends messages to Telegram                  |
| **Automation** (`main.py` + GitHub Actions)       | Runs alerts on schedule                     |
| **Interactive Layer** (`telegram_interactive.py`) | Responds to live user commands              |

🧰 Technologies Used
| Category    | Technology          |
| ----------- | ------------------- |
| Backend     | Python 3.11+        |
| API         | Sleeper Fantasy API |
| Messaging   | Telegram Bot API    |
| Automation  | GitHub Actions      |
| Deployment  | Render / Railway    |
| Environment | python-dotenv       |
| HTTP        | requests            |

🤖 GitHub Actions Automation

This project runs automatically every week via a scheduled GitHub Action.

.github/workflows/action_handler.yml

on:
  schedule:
    - cron: "0 12 * * 2"  # Every Tuesday at 12:00 UTC
jobs:
  weekly_alerts:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run weekly alerts
        run: python main.py

👨‍💻 Author

Ricardo Oliveira
Python Developer / Master in Industrial Automation Engineering
Building automation tools, data workflows, and intelligent backend systems.
