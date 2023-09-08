import html
import json
import logging
import os
import sys
import traceback

import telegram
from dotenv import load_dotenv
from googleapiclient.errors import HttpError
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, BotCommand
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    filters, MessageHandler, CallbackContext,
)

from constants import HELP_MESSAGE, NO_ENTRY_EMOJI, PENCIL_EMOJI, EJECT_BUTTON_EMOJI, CARD_INDEX_EMOJI, FOLDER_EMOJI, \
    CHECK_EMOJI, BACK_ARROW_EMOJI, CROSS_MARK_EMOJI, WARNING_EMOJI, GDRIVE_SERVICE_ACCOUNT_FILE
from drive import create_service, GDriveFolderTraverser, upload_file_to_gdrive

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP_MESSAGE, parse_mode=ParseMode.HTML)


async def message_with_file_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != int(os.environ['TG_KNOWN_USER_IDS']):
        logger.info(f'Unknown user with user_id={update.effective_user.id} tried to start an interaction.')
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'{NO_ENTRY_EMOJI} You have no rights to use this bot.\nContact @lqrhy3 for details.'
        )
        return None

    logger.info('The user started an interaction.')
    file_id = update.message.document.file_id
    file = await context.bot.get_file(file_id)
    file_name = update.message.document.file_name
    file_path = os.path.join(os.environ['TEMP_DOWNLOADS_DIR'], file_name)
    await file.download_to_drive(file_path)

    if context.user_data.get('gdrive_service', None) is None:
        logger.info('GDrive utils initialisation.')
        gdrive_service_account_file = GDRIVE_SERVICE_ACCOUNT_FILE
        gdrive_service = create_service(gdrive_service_account_file)
        gdrive_folder_traverser = GDriveFolderTraverser(gdrive_service)
        context.user_data['gdrive_service'] = gdrive_service
        context.user_data['gdrive_folder_traverser'] = gdrive_folder_traverser

    context.user_data['file_path'] = file_path
    context.user_data['file_name'] = file_name

    keyboard = [[
        InlineKeyboardButton(f'{PENCIL_EMOJI} Yes', callback_data='rename_file'),
        InlineKeyboardButton(f'{EJECT_BUTTON_EMOJI} No', callback_data='start_folder_choosing')
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        text='Let\'s <b>upload</b> this file to Google Drive!\nDo you want <b>to rename the file</b> before uploading?',
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )
    return 'configure_uploading'


async def send_message_to_rename_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        text=f'{PENCIL_EMOJI} <b>Enter new file name</b> (without extension):',
        parse_mode=ParseMode.HTML
    )
    return 'configure_uploading'


async def rename_file_and_start_folder_choosing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_file_name = update.message.text
    file_ext = os.path.splitext(context.user_data['file_name'])[-1]
    context.user_data['file_name'] = os.path.join(new_file_name, file_ext)

    gdrive_folder_traverser = context.user_data['gdrive_folder_traverser']
    gdrive_folder_traverser.init_folder_structure()

    reply_markup = _make_folder_choosing_markup(gdrive_folder_traverser)
    current_path = gdrive_folder_traverser.get_current_path()
    await update.message.reply_text(
        text=f"{CARD_INDEX_EMOJI} <b>Choose folder to upload the file.</b>"
             f"\nCurrent path: <code>{current_path}</code>",
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )
    return 'configure_uploading'


async def start_folder_choosing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    gdrive_folder_traverser = context.user_data['gdrive_folder_traverser']
    gdrive_folder_traverser.init_folder_structure()

    reply_markup = _make_folder_choosing_markup(gdrive_folder_traverser)
    current_path = gdrive_folder_traverser.get_current_path()
    await query.edit_message_text(
        text=f"{CARD_INDEX_EMOJI} <b>Choose folder to upload the file.</b>"
             f"\nCurrent path: <code>{current_path}</code>",
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )
    return 'configure_uploading'


async def choose_folder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    gdrive_folder_traverser = context.user_data['gdrive_folder_traverser']
    current_folder_name = query.data.split('|')[1].split()[1]
    if current_folder_name == 'go_back':
        gdrive_folder_traverser.move_back()
    else:
        gdrive_folder_traverser.move_to(current_folder_name)

    reply_markup = _make_folder_choosing_markup(gdrive_folder_traverser)
    current_path = gdrive_folder_traverser.get_current_path()
    await query.edit_message_text(
        text=f"{CARD_INDEX_EMOJI} <b>Choose folder to upload the file.</b>"
             f"\nCurrent path: <code>{current_path}</code>",
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )
    return 'configure_uploading'


def _make_folder_choosing_markup(gdrive_folder_traverser):
    folders = gdrive_folder_traverser.get_current_children()
    folders = [' '.join((FOLDER_EMOJI, folder)) for folder in folders]

    keyboard = [
        [InlineKeyboardButton(folder, callback_data=f'choose_folder|{folder}')]
        for folder in folders
    ]

    keyboard.append(
        [InlineKeyboardButton(' '.join((CHECK_EMOJI, 'Upload here!')), callback_data='end_folder_choosing')]
    )
    if not gdrive_folder_traverser.is_in_root():
        keyboard[-1].insert(
            0, InlineKeyboardButton(
                ' '.join((BACK_ARROW_EMOJI, 'Go back')),
                callback_data=f'choose_folder|{FOLDER_EMOJI} go_back'
            )
        )

    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


async def end_folder_choosing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[
        InlineKeyboardButton(f'{CROSS_MARK_EMOJI} No, cancel uploading!', callback_data='cancel_uploading'),
        InlineKeyboardButton(f'{CHECK_EMOJI} Yes, upload it!', callback_data='upload_file')
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    file_name = context.user_data['file_name']
    gdrive_folder_traverser = context.user_data['gdrive_folder_traverser']
    current_path = gdrive_folder_traverser.get_current_path()
    await query.edit_message_text(
        text=f'{WARNING_EMOJI} Do you want to upload <code>{file_name}</code> file '
             f'to <code>{current_path}</code> folder?',
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )
    return 'finish_uploading'


async def upload_file_and_finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    gdrive_service = context.user_data['gdrive_service']
    gdrive_folder_traverser = context.user_data['gdrive_folder_traverser']
    folder_id = gdrive_folder_traverser.get_current_folder_id()
    file_path = context.user_data['file_path']
    file_name = context.user_data['file_name']

    upload_path = gdrive_folder_traverser.get_current_path()
    try:
        upload_file_to_gdrive(
            service=gdrive_service,
            local_path=file_path,
            upload_folder_id=folder_id,
            upload_file_name=file_name
        )
    except HttpError:
        message = f'{CROSS_MARK_EMOJI} GDrive service was not able to upload your file to the drive.'
    else:
        message = f'{CHECK_EMOJI} File was successfully uploaded to the drive.\n' \
                  f'{PENCIL_EMOJI} File name: <code>{file_name}</code>\n' \
                  f'{FOLDER_EMOJI} File folder: <code>{upload_path}</code>'
    finally:
        logging.info('File uploaded. The interaction finished.')
        os.remove(file_path)

        await query.edit_message_text(
            text=message,
            parse_mode=ParseMode.HTML
        )
        return ConversationHandler.END


async def cancel_uploading_and_finish(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    logging.info('The interaction finished.')
    await query.edit_message_text(text="Uploading was cancelled.")
    return ConversationHandler.END


async def post_init(application: Application):
    await application.bot.set_my_commands([
        BotCommand('/help', 'Show help message'),
    ])


async def error_handle(update: Update, context: CallbackContext) -> None:
    logger.error(msg='Exception while handling an update:', exc_info=context.error)

    try:
        tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
        tb_string = "".join(tb_list)
        update_str = update.to_dict() if isinstance(update, Update) else str(update)
        message = (
            f'An exception was raised while handling an update\n'
            f'<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}'
            '</pre>\n\n'
            f'<pre>{html.escape(tb_string)}</pre>'
        )

        for message_chunk in split_text_into_chunks(message, 4096):
            try:
                await context.bot.send_message(update.effective_chat.id, message_chunk, parse_mode=ParseMode.HTML)
            except telegram.error.BadRequest:
                await context.bot.send_message(update.effective_chat.id, message_chunk)
    except:
        await context.bot.send_message(update.effective_chat.id, 'Some error in error handler')


def split_text_into_chunks(text, chunk_size):
    for i in range(0, len(text), chunk_size):
        yield text[i:i + chunk_size]


def main(tg_bot_token: str):
    application = Application.builder().token(tg_bot_token).post_init(post_init).build()

    start_interaction = MessageHandler(filters.Document.ALL, message_with_file_received)

    conversation_handler = ConversationHandler(
        entry_points=[start_interaction],
        states={
            'configure_uploading': [
                CallbackQueryHandler(send_message_to_rename_file, pattern='^rename_file'),
                MessageHandler(filters.TEXT, rename_file_and_start_folder_choosing),
                CallbackQueryHandler(start_folder_choosing, pattern='^start_folder_choosing'),
                CallbackQueryHandler(choose_folder, pattern='^choose_folder'),
                CallbackQueryHandler(end_folder_choosing, pattern='^end_folder_choosing'),
            ],
            'finish_uploading': [
                CallbackQueryHandler(upload_file_and_finish, pattern='^upload_file'),
                CallbackQueryHandler(cancel_uploading_and_finish, pattern='^cancel_uploading')
            ],
        },
        fallbacks=[start_interaction],
    )
    application.add_handler(conversation_handler)

    help_handler = CommandHandler('help', help_command)
    application.add_handler(help_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    load_dotenv()
    TG_BOT_TOKEN = os.environ['TG_BOT_TOKEN']

    main(tg_bot_token=TG_BOT_TOKEN)
