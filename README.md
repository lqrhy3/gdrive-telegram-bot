<div align="center">

# Telegram Bot for Google Drive
</div>
<p align="center">
<a href="https://t.me/gdrive_documents_bot?start=source=github" alt="Run Telegram Bot shield"><img src="https://img.shields.io/badge/RUN-Telegram%20Bot-blue?logo=data:image/svg+xml;base64,PHN2ZyBpZD0iTGl2ZWxsb18xIiBkYXRhLW5hbWU9IkxpdmVsbG8gMSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiB4bWxuczp4bGluaz0iaHR0cDovL3d3dy53My5vcmcvMTk5OS94bGluayIgdmlld0JveD0iMCAwIDI0MCAyNDAiPjxkZWZzPjxsaW5lYXJHcmFkaWVudCBpZD0ibGluZWFyLWdyYWRpZW50IiB4MT0iMTIwIiB5MT0iMjQwIiB4Mj0iMTIwIiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+PHN0b3Agb2Zmc2V0PSIwIiBzdG9wLWNvbG9yPSIjMWQ5M2QyIi8+PHN0b3Agb2Zmc2V0PSIxIiBzdG9wLWNvbG9yPSIjMzhiMGUzIi8+PC9saW5lYXJHcmFkaWVudD48L2RlZnM+PHRpdGxlPlRlbGVncmFtX2xvZ288L3RpdGxlPjxjaXJjbGUgY3g9IjEyMCIgY3k9IjEyMCIgcj0iMTIwIiBmaWxsPSJ1cmwoI2xpbmVhci1ncmFkaWVudCkiLz48cGF0aCBkPSJNODEuMjI5LDEyOC43NzJsMTQuMjM3LDM5LjQwNnMxLjc4LDMuNjg3LDMuNjg2LDMuNjg3LDMwLjI1NS0yOS40OTIsMzAuMjU1LTI5LjQ5MmwzMS41MjUtNjAuODlMODEuNzM3LDExOC42WiIgZmlsbD0iI2M4ZGFlYSIvPjxwYXRoIGQ9Ik0xMDAuMTA2LDEzOC44NzhsLTIuNzMzLDI5LjA0NnMtMS4xNDQsOC45LDcuNzU0LDAsMTcuNDE1LTE1Ljc2MywxNy40MTUtMTUuNzYzIiBmaWxsPSIjYTljNmQ4Ii8+PHBhdGggZD0iTTgxLjQ4NiwxMzAuMTc4LDUyLjIsMTIwLjYzNnMtMy41LTEuNDItMi4zNzMtNC42NGMuMjMyLS42NjQuNy0xLjIyOSwyLjEtMi4yLDYuNDg5LTQuNTIzLDEyMC4xMDYtNDUuMzYsMTIwLjEwNi00NS4zNnMzLjIwOC0xLjA4MSw1LjEtLjM2MmEyLjc2NiwyLjc2NiwwLDAsMSwxLjg4NSwyLjA1NSw5LjM1Nyw5LjM1NywwLDAsMSwuMjU0LDIuNTg1Yy0uMDA5Ljc1Mi0uMSwxLjQ0OS0uMTY5LDIuNTQyLS42OTIsMTEuMTY1LTIxLjQsOTQuNDkzLTIxLjQsOTQuNDkzcy0xLjIzOSw0Ljg3Ni01LjY3OCw1LjA0M0E4LjEzLDguMTMsMCwwLDEsMTQ2LjEsMTcyLjVjLTguNzExLTcuNDkzLTM4LjgxOS0yNy43MjctNDUuNDcyLTMyLjE3N2ExLjI3LDEuMjcsMCwwLDEtLjU0Ni0uOWMtLjA5My0uNDY5LjQxNy0xLjA1LjQxNy0xLjA1czUyLjQyNi00Ni42LDUzLjgyMS01MS40OTJjLjEwOC0uMzc5LS4zLS41NjYtLjg0OC0uNC0zLjQ4MiwxLjI4MS02My44NDQsMzkuNC03MC41MDYsNDMuNjA3QTMuMjEsMy4yMSwwLDAsMSw4MS40ODYsMTMwLjE3OFoiIGZpbGw9IiNmZmYiLz48L3N2Zz4=" width="230"/></a>
</p>

## Description

This is a simple telegram bot for Google Drive. The bot was designed for personal use. Its purpose is to ease document 
accounting. The bot can browse folders on the drive and upload a file to it.

The bot was created with `python-telegram-bot` and `google-api-python-client` APIs.
<p align="center">
  <img src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExdDh6eDh1eHlveXhpZnozMmMzNmJpMjlvdDFxZTR2eDM3OXZra2RxeiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/FlHB8yZOQvGt3pIb5K/giphy.gif" />
</p>

## Setup
1. Create a service account at Google Cloud Platform, download its key and grant permissions to the service account at 
your Google Drive.
2. Get your Telegram bot token from [@BotFather](https://t.me/BotFather).
3. Get your Telegram id [@userinfobot](https://t.me/userinfobot).
4. Add to the `.env` file bot token and your Telegram id.
    ```dotenv
    TG_BOT_TOKEN=bot_token
    TG_KNOWN_USER_IDS=your_telegram_id
    ```
5. Build and run docker mounting the GCP service account key file.
```shell
docker build -t gdrive_telegram_bot .
docker run --env-file .env -v $(PATH_TO_GCP_KEY_FILE):/code/gdrive-credentials.json gdrive_telegram_bot
```

