import logging
from telegram import ReplyKeyboardRemove, Update, CallbackQuery
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)
from dataclasses import dataclass
from datetime import datetime, timedelta

import lib.keyboards as kb
import lib.utils as ut
from lib.backend import Backend
from lib.db.tables import get_engine

menu_names = ut.get_menu_names()

class Client:

    @dataclass()
    class States:
        MAIN_MENU: int
        SITUATION: int
        MIND: int
        EMOTION: int
        BODY: int
        REPLACEMENT: int


    def __init__(self, token: str, engine):
        self.backend = Backend(engine)
        self.application = Application.builder().token(token).build()
        self.states = self.get_states()

    def get_states(self):
        states = self.States(*range(6))
        return states

    async def main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        text = "Hello at emotion bot. Please chose the option below"
        markup = kb.get_start_keyboard()

        await update.message.reply_text(
            text,
            reply_markup=markup
        )
        return self.states.MAIN_MENU

    async def show_last_emotions(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user_id = update.message.from_user.id
        resp = self.backend.get_last_n_situations(user_id, 10)
        markdown = kb.get_start_keyboard()

        if resp.status:
            text = "something was wrong"
            await update.message.reply_text(
                text
                ,reply_markup=markdown
            )
            return self.states.MAIN_MENU

        elif not resp.answer:
            text = "there are no emotions yet"
            await update.message.reply_text(
                text,
                reply_markup=markdown
            )
            return self.states.MAIN_MENU

        text = "\n\n".join([str(emotion) for emotion in resp.answer])
        await update.message.reply_text(
            text,
            reply_markup=markdown
        )

        return self.states.MAIN_MENU
        
    async def proceed_add_case(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        text = "describe the situation"
        await update.message.reply_text(
            text
        )
        return self.states.SITUATION

    async def proceed_situation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        situation = update.message.text
        context.user_data['situation'] = situation

        text = "describe your minds"
        await update.message.reply_text(
            text
        )
        return self.states.MIND

    async def proceed_mind(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        mind = update.message.text
        context.user_data['mind'] = mind

        text = "describe your emotions"
        await update.message.reply_text(
            text
        )
        return self.states.EMOTION

    async def proceed_emotion(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        emotion = update.message.text
        context.user_data['emotion'] = emotion

        text = "describe your body feelings"
        
        await update.message.reply_text(
            text
        )

        return self.states.BODY

    async def proceed_body(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        body = update.message.text
        context.user_data['body'] = body

        text = "write a replacement"
        
        await update.message.reply_text(
            text
        )

        return self.states.REPLACEMENT

    async def done(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        return ConversationHandler.END

    async def proceed_replacemnet(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user_id = update.message.from_user.id
        replacement = update.message.text
        situation = context.user_data['situation']
        mind = context.user_data['mind']
        emotion = context.user_data['emotion']
        body = context.user_data['body']
        create_time = datetime.now()

        response = self.backend.add_situation(
            telegram_id=user_id,
            situation=situation,
            mind=mind,
            emotion=emotion,
            body=body,
            replacement=replacement,
            create_time=create_time
        )

        markdown = kb.get_start_keyboard()

        if response.status:
            text = "emotion was not added"
            await update.message.reply_text(
                text,
                reply_markup=markdown
            )
            return self.states.MAIN_MENU

        text = "your emotion was added"
        
        await update.message.reply_text(
            text,
            reply_markup=markdown
        )

        return self.states.MAIN_MENU

    def build_conversation_handler(self):
        conv_handler = ConversationHandler(
            allow_reentry=True,
            entry_points=[
                    CommandHandler("start", self.main_menu),
            ],
            states={
                self.states.MAIN_MENU: [
                    MessageHandler(filters.Regex(ut.name_to_reg(menu_names.add_emotion)), self.proceed_add_case),
                    MessageHandler(filters.Regex(ut.name_to_reg(menu_names.show_last_emotions)),
                        self.show_last_emotions),
                    MessageHandler(filters.TEXT, self.main_menu)
                    
                ],
                self.states.SITUATION: [
                    MessageHandler(filters.TEXT, self.proceed_situation)
                ],
                self.states.MIND: [
                    MessageHandler(filters.TEXT, self.proceed_mind)
                ],
                self.states.EMOTION: [
                    MessageHandler(filters.TEXT, self.proceed_emotion)
                ],
                self.states.BODY: [
                    MessageHandler(filters.TEXT, self.proceed_body)
                ],
                self.states.REPLACEMENT: [
                    MessageHandler(filters.TEXT, self.proceed_replacemnet)
                ],
            },
            fallbacks=[MessageHandler(filters.Regex("^Done$"), self.done)],
        )

        return conv_handler

    def build_application(self):
        conv_handler = self.build_conversation_handler()
        self.application.add_handler(conv_handler)
        self.application.run_polling(drop_pending_updates=True)
