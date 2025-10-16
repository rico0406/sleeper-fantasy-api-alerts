# 🏈 Sleeper Fantasy API Alerts

**Automated Fantasy Football League Insights & Alerts**

This project connects to the [Sleeper Fantasy Football API](https://sleeper.com) to automatically track your league’s results, standings, and player transactions — and deliver alerts directly to **Telegram**.  
It also runs on a **scheduled basis** via **GitHub Actions**, making it fully autonomous once deployed.

---

## 🚀 Features

✅ **Weekly Reports**  
- Automatically fetches league standings and matchup results every Tuesday (12h UTC).

✅ **Daily Alerts**  
- Monitors player adds/drops across the league.  
- Notifies when a highly owned player (>70%) is dropped or placed on waivers.

✅ **Game-Day Alerts** *(coming soon)*  
- Detects key in-game events for players on your roster (e.g., touchdowns, fumbles, interceptions).

✅ **Interactive Telegram Bot**  
- Users can message the bot directly with commands like:
  - `standings` or `classificação` → get current standings.
  - Future commands may include `results`, `waivers`, etc.

✅ **Modular Design**  
- Separate logic for weekly, daily, and live alerts.  
- Reusable and extendable code modules (`league_tools.py`, `alerts.py`, `telegram_bot.py`).

✅ **Automated & Cloud-Ready**  
- Runs autonomously every week through **GitHub Actions**.  
- The interactive bot runs continuously on **Render**, **Railway**, or **Fly.io**.

---

## 🧱 Project Structure
```
sleeper-fantasy-api-alerts/
│
├── alerts.py # Core logic for daily/weekly/live alerts
├── league_tools.py # League and Sleeper API interaction
├── telegram_bot.py # Telegram message sending utilities
├── telegram_interactive.py # Interactive Telegram bot (user commands)
├── main.py # Entry point for automated alerts (GitHub Actions)
│
├── .github/workflows/action_handler.yml # GitHub Actions scheduler
├── Procfile # For Render/Railway deployment
├── requirements.txt
├── .env.example # Environment variable template
└── README.md
```

---

## ⚙️ Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/rico0406/sleeper-fantasy-api-alerts.git
cd sleeper-fantasy-api-alerts

2. Create a virtual environment

python -m venv venv
source venv/Scripts/activate   # Windows
source venv/bin/activate       # macOS/Linux

3. Install dependencies

pip install -r requirements.txt

4. Configure your environment

Copy .env.example to .env and fill in your credentials:

TELEGRAM_BOT_TOKEN=your_telegram_token
SLEEPER_LEAGUE_ID=your_sleeper_league_id
SLEEPER_USER_ID=your_user_id

💬 Run the Telegram Bot Locally

python telegram_interactive.py

You should see:

🤖 Telegram interactive bot is running...

Then, open your bot on Telegram and send a message:

standings

☁️ Deploy on Render / Railway

    Push this project to your GitHub.

    Create a new Worker service on Render

or Railway

    .

    Add environment variables:

        TELEGRAM_BOT_TOKEN

        SLEEPER_LEAGUE_ID

        SLEEPER_USER_ID

    Deploy! The bot will stay online 24/7.

The Procfile handles the process:

worker: python telegram_interactive.py

🧠 Architecture Overview

    Sleeper API Layer (league_tools.py) → fetches live league data.

    Alert Engine (alerts.py) → processes and formats insights.

    Delivery System (telegram_bot.py & GitHub Actions) → sends automated alerts.

    Interactive Layer (telegram_interactive.py) → responds to user messages in real time.

🧰 Technologies Used
Category	Technology
Backend	Python 3.11+
API	Sleeper Fantasy API
Messaging	Telegram Bot API
Automation	GitHub Actions
Deployment	Render / Railway
Environment	python-dotenv
HTTP	requests
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

🌍 GitHub Profile
🏆 License

This project is released under the MIT License

.


---

### 💾 2. Faça o commit e o push do README

No terminal:

```bash
git add README.md
git commit -m "Add detailed README.md for project documentation"
git push origin main