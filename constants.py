GDRIVE_SERVICE_ACCOUNT_FILE = '/code/gdrive-credentials.json'

FOLDER_EMOJI = '\U0001F4C2'
CHECK_EMOJI = '\u2705'
BACK_ARROW_EMOJI = '\U0001F519'
PENCIL_EMOJI = '\u270F\uFE0F'
EJECT_BUTTON_EMOJI = '\u23CF\uFE0F'
ROBOT_FACE_EMOJI = '\U0001F916'
SPARKLES_EMOJI = '\u2728'
CARD_INDEX_EMOJI = '\U0001F5C2'
WARNING_EMOJI = '\u26A0'
CROSS_MARK_EMOJI = '\u274C'
NO_ENTRY_EMOJI = '\u26D4'

HELP_MESSAGE = f"""This bot {ROBOT_FACE_EMOJI} is designed to easily <b>upload</b> single file <b>documents to Google Drive </b>.

Just <b>send a file to start interaction</b> with the bot. {SPARKLES_EMOJI}
The bot then will:
    1. {PENCIL_EMOJI} Ask for a file name to assign to the file (optional).
    2. {FOLDER_EMOJI} Offer to choose a folder to upload the file.
    3. {CHECK_EMOJI} Upload the file and inform about uploading status.
"""
