# X Bot - Bash Shell Tips

A Twitter/X bot that posts useful bash shell tips every second day (every other day).

## Features

- Posts a random bash tip every 2 days
- Tracks posted tips to avoid repetition
- 70+ useful bash shell tips included
- Easy to schedule with cron

## Setup

### 1. Get X API Credentials

1. Go to [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. Create a new app or use an existing one
3. Generate your API keys and tokens with **Read and Write** permissions
4. You'll need:
   - API Key (Consumer Key)
   - API Secret (Consumer Secret)
   - Access Token
   - Access Token Secret
   - Bearer Token

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```bash
X_API_KEY=your_api_key_here
X_API_SECRET=your_api_secret_here
X_ACCESS_TOKEN=your_access_token_here
X_ACCESS_TOKEN_SECRET=your_access_token_secret_here
X_BEARER_TOKEN=your_bearer_token_here
```

### 4. Load Environment Variables

You can either:

**Option A: Use python-dotenv (recommended for development)**

Modify `main.py` to add this at the top:
```python
from dotenv import load_dotenv
load_dotenv()
```

**Option B: Export manually**

```bash
export $(cat .env | xargs)
```

**Option C: Add to your shell profile**

Add the exports to `~/.bashrc` or `~/.zshrc`

## Usage

### Run Manually

```bash
python main.py
```

### Schedule with Cron

To run the bot automatically, add it to your crontab:

```bash
crontab -e
```

Add this line to run daily at 10 AM (the bot will post only every 2nd day):

```bash
0 10 * * * cd /home/aimonkied/x_bot && /usr/bin/python3 main.py >> bot.log 2>&1
```

Or run it twice daily to have more flexibility:

```bash
0 10,22 * * * cd /home/aimonkied/x_bot && /usr/bin/python3 main.py >> bot.log 2>&1
```

### Using systemd timer (Alternative)

Create a service file `/etc/systemd/system/bash-tip-bot.service`:

```ini
[Unit]
Description=Bash Tip Bot
After=network.target

[Service]
Type=oneshot
User=aimonkied
WorkingDirectory=/home/aimonkied/x_bot
EnvironmentFile=/home/aimonkied/x_bot/.env
ExecStart=/usr/bin/python3 /home/aimonkied/x_bot/main.py

[Install]
WantedBy=multi-user.target
```

Create a timer file `/etc/systemd/system/bash-tip-bot.timer`:

```ini
[Unit]
Description=Run Bash Tip Bot Daily

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
```

Enable and start:

```bash
sudo systemctl enable bash-tip-bot.timer
sudo systemctl start bash-tip-bot.timer
```

## Files

- `main.py` - Main bot script
- `tips.txt` - Tweet content (edit this to change what gets posted!)
- `requirements.txt` - Python dependencies
- `.env` - Your API credentials (create from .env.example)
- `bot_state.json` - Auto-generated state file (tracks posting history)

## How It Works

1. The bot checks `bot_state.json` to see when it last posted
2. If 2 or more days have passed, it selects a random unused tip
3. Posts the tip to X/Twitter
4. Updates the state file with the current date and used tip
5. Once all tips are used, it resets and starts over

## Adding More Tips

Simply edit [tips.txt](tips.txt) and add one tip per line. The bot will automatically load them!

## Troubleshooting

- **API Error**: Make sure your X app has Read and Write permissions
- **Missing credentials**: Double-check all 5 environment variables are set
- **Not posting**: Check that 2 days have passed since the last post in `bot_state.json`

## License

MIT
