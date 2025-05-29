<<<<<<< HEAD
# Auto Email Responder

An automated Python script that checks for unread emails in your Gmail inbox and sends automatic replies to messages containing urgent keywords.

## Features

- Securely connects to Gmail via IMAP
- Monitors your inbox for unread emails
- Automatically replies to emails containing urgent keywords
- Marks processed emails as read
- Logs all activities for easy monitoring
- Runs on a schedule (every 10 minutes)

## Requirements

- Python 3.6+
- Gmail account with app-specific password
- Internet connection

## Installation

1. Clone or download this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file by copying the example:

```bash
cp .env.example .env
```

4. Edit the `.env` file with your Gmail credentials:

```
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_specific_password
```

**Note:** For security reasons, use an app-specific password instead of your regular Gmail password. You can create one at [Google Account Security](https://myaccount.google.com/security).

## Usage

To start the Auto Email Responder:

```bash
python auto_email_responder.py
```

The script will:

1. Connect to your Gmail account
2. Check for unread emails immediately
3. Start a scheduler to check every 10 minutes
4. Log all activities to the console

To stop the script, press `Ctrl+C` in the terminal.

You can also use the included npm script if you prefer:

```bash
npm start
```

## How It Works

1. The script connects to your Gmail inbox using IMAP
2. It searches for unread emails
3. For each unread email, it extracts:
   - Sender's email address
   - Subject line
   - Email body
4. If the email contains urgent keywords (like "urgent", "help", "asap"), it sends an automatic reply
5. After processing, it marks the email as read
6. Every action is logged to the console

## Configuration

You can customize the urgent keywords by editing the `urgent_keywords` list in the `EmailHandler` class in `email_handler.py`:

```python
self.urgent_keywords = ['urgent', 'help', 'asap', 'emergency', 'important']
```

## Security Considerations

- The script uses app-specific passwords instead of your main Google account password
- Credentials are stored in a local `.env` file, not hardcoded in the scripts
- The `.env` file is included in `.gitignore` to prevent accidental commits

## Troubleshooting

If you encounter issues:

1. Ensure you're using an app-specific password
2. Check that less secure app access is enabled in your Google account
3. Verify your internet connection
4. Look at the logs for specific error messages

## License

This project is licensed under the MIT License - see the LICENSE file for details.
=======
# email-handler
Auto replay emails
>>>>>>> c87f3ab82f161c2b25f3c5a5a17062d3b791cbf2
