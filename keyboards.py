from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

import callback_factory
import functions

# Кнопки главного меню
calculation = InlineKeyboardButton(text='Сделать расчет майнинг-оборудования', callback_data='calculation')
fomo = InlineKeyboardButton(text='Сколько я мог заработать', callback_data='fomo')
cheap_coins = InlineKeyboardButton(text='Как купить монеты дешевле рынка?', callback_data='cheap_coins')
dashboard = InlineKeyboardButton(text='Перейти в подробный дашборд', url='https://datalens.yandex/kth6k05xlg9c8')
feedback_button = InlineKeyboardButton(text='Оставить комментарий', callback_data='feedback')
return_to_main_menu_button = InlineKeyboardButton(text='Вернуться в главное меню', callback_data='return_to_main_menu')

# Кнопки целей пользователя
quick_payback = InlineKeyboardButton(text='Как можно быстрее окупиться', callback_data='quick_payback')
highly_profit = InlineKeyboardButton(text='Иметь максимально возможный месячный доход', callback_data='highly_profit')
less_electricity_pay = InlineKeyboardButton(text='Меньше платить за электроэнергию',
                                            callback_data='less_electricity_pay')

# Кнопки добываемых монет
BTC = InlineKeyboardButton(text='Bitcoin', callback_data='BTC')
ETC = InlineKeyboardButton(text='Ethereum Classic', callback_data='ETC')
LTC = InlineKeyboardButton(text='Litecoin + Dogecoin', callback_data='LTC')
KAS = InlineKeyboardButton(text='Kaspa', callback_data='KAS')
DASH = InlineKeyboardButton(text='Dash', callback_data='DASH')
ZEC = InlineKeyboardButton(text='ZCash', callback_data='ZEC')
CKB = InlineKeyboardButton(text='Nervos Network', callback_data='CKB')
KDA = InlineKeyboardButton(text='Kadena', callback_data='KDA')
HNS = InlineKeyboardButton(text='Handshake', callback_data='HNS')
ALPH = InlineKeyboardButton(text='Alephium', callback_data='ALPH')
Diversification = InlineKeyboardButton(text='Хочу диверсифицировать риски и майнить несколько монет',
                                       callback_data='Diversification')

# Кнопки 380 В да или нет для биткоина
btc_380_yes = InlineKeyboardButton(text='Да', callback_data='btc_380_yes')
btc_380_no = InlineKeyboardButton(text='Нет', callback_data='btc_380_no')

# Кнопки для гидроасиков да или нет для биткоина
btc_hydro_yes = InlineKeyboardButton(text='Да', callback_data='btc_hydro_yes')
btc_hydro_no = InlineKeyboardButton(text='Нет', callback_data='btc_hydro_no')

# Кнопка получить результат
get_result = InlineKeyboardButton(text='Получить результат', callback_data='get_result')

# Инициализация списка кнопок
main_menu_buttons = [[calculation], [fomo], [cheap_coins], [dashboard], [feedback_button]]
purpose_choice_buttons = [[quick_payback], [highly_profit], [less_electricity_pay]]
coin_choice_buttons = [[BTC], [ETC], [LTC], [KAS], [DASH], [ZEC], [CKB], [KDA], [HNS], [ALPH], [Diversification]]
return_to_main_menu_buttons = [[return_to_main_menu_button]]
btc_380_buttons = [[btc_380_yes], [btc_380_no]]
btc_hydro_buttons = [[btc_hydro_yes], [btc_hydro_no]]
get_result_buttons = [[get_result]]

# Создание объектов клавиатур
main_menu = InlineKeyboardMarkup(inline_keyboard=main_menu_buttons)
purpose_choice_menu = InlineKeyboardMarkup(inline_keyboard=purpose_choice_buttons)
coin_choice_menu = InlineKeyboardMarkup(inline_keyboard=coin_choice_buttons)
return_to_main_menu = InlineKeyboardMarkup(inline_keyboard=return_to_main_menu_buttons)
btc_380_menu = InlineKeyboardMarkup(inline_keyboard=btc_380_buttons)
btc_hydro_menu = InlineKeyboardMarkup(inline_keyboard=btc_hydro_buttons)
get_result_menu = InlineKeyboardMarkup(inline_keyboard=get_result_buttons)


# Создание клавиатуры со списком асиков
async def create_asic_list_keyboard(asic):
    builder = InlineKeyboardBuilder()
    asics = await functions.asic_list(asic)
    for asic in asics:
        builder.row(InlineKeyboardButton(
            text=f'{asic[0]}, {int(asic[2])} Вт, {asic[3]}',
            callback_data=callback_factory.AsicsList(
                item=asic[0]).pack()
        ))
    builder.row(return_to_main_menu_button)
    return builder.as_markup()


async def create_cheap_asic_list_keyboard(asic):
    builder = InlineKeyboardBuilder()
    asics = await functions.asic_list(asic)
    for asic in asics:
        builder.row(InlineKeyboardButton(
            text=f'{asic[0]}, {int(asic[2])} Вт, {asic[3]}',
            callback_data=callback_factory.CheapAsicsList(
                item=asic[0]).pack()
        ))
    builder.row(return_to_main_menu_button)
    return builder.as_markup()

# Кнопки FOMO
early_date = InlineKeyboardButton(text='Считать с самой ранней даты', callback_data='early_date')
manual_date = InlineKeyboardButton(text='Ввести дату вручную', callback_data='manual_date')
manual_date_confirm_button = InlineKeyboardButton(text='Да, выбираем эту дату', callback_data='manual_date_confirm_button')
calculation_start_button = InlineKeyboardButton(text='Да, все верно, запускаем расчет!', callback_data='calculation_start')

# Инициализация клавиатур FOMO
date_choose_buttons = [[early_date], [manual_date], [return_to_main_menu_button]]
manual_date_confirm_buttons = [[manual_date_confirm_button], [return_to_main_menu_button]]
calculation_start_buttons = [[calculation_start_button], [return_to_main_menu_button]]
fomo_end_buttons = [[feedback_button], [return_to_main_menu_button]]

# Создание объектов клавиатур FOMO
date_choose = InlineKeyboardMarkup(inline_keyboard=date_choose_buttons)
manual_date_confirm = InlineKeyboardMarkup(inline_keyboard=manual_date_confirm_buttons)
calculation_start = InlineKeyboardMarkup(inline_keyboard=calculation_start_buttons)
fomo_end = InlineKeyboardMarkup(inline_keyboard=fomo_end_buttons)

