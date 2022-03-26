from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
import config

user_keyboard = [['/roll', '/wok', '/soup', '/skip']]
start_markup = ReplyKeyboardMarkup(user_keyboard, one_time_keyboard=False)


def start(update, context):
    update.message.reply_text('Приветствую вас! Как я могу к вам обращаться?')

    return 1


def first_response(update, context):
    locality = update.message.text
    update.message.reply_text("{locality}, Что вы предпочитаете заказать?".format(**locals()))
    return 2


def second_response(update, context):
    weather = update.message.text
    update.message.reply_text("Прекрасный выбор! Мы можем вам предложить...")
    return ConversationHandler.END


def skip(update, context):
    update.message.reply_text("----")
    return 2


def stop(update, context):
    update.message.reply_text("Жаль... Всего доброго!")
    return ConversationHandler.END


def main():
    updater = Updater(config.TOKEN, use_context=True)
    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            1: [CommandHandler('skip', skip), MessageHandler(Filters.text, first_response)],
            2: [MessageHandler(Filters.text, second_response)]
        },
        fallbacks=[CommandHandler('stop', stop)]
    )
    dp.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()