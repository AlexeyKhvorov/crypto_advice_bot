import datetime
import time

import pymysql
from aiogram import Router, F
from aiogram.enums import ChatAction
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile
import pandas as pd
from fpdf import FPDF
from datetime import datetime
from decimal import Decimal, ROUND_HALF_EVEN
import ccxt

import callback_factory
import config
import functions
import fsm
import keyboards
from bot import bot

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message,
                    state: FSMContext):
    await message.answer(text="Добро пожаловать в <b>crypto_advice_bot</b>! 👋\n\n - По кнопке <b>«Сделать расчет»</b> ✍️ "
             "Вы можете посчитать наиболее выгодные инвестиции в майнинг-оборудование "
             "конкретно для Вас и Ваших условий. \n - По кнопке "
             "<b>«Сколько я уже мог заработать» ❓</b> Вы можете увидеть, сколько могли заработать, сколько могли заработать, начав майнить раньше.\n"
             " - По кнопке <b>«Как купить монеты дешевле рынка» 🛒</b> Вы сможете увидеть одну из стратегий "
             "майнинга крипты, позволяющая покупать любой актив на рынке с большим дисконтом.\n"
             " - Также можно ознакомиться с подробным дашбордом по "
             "майнинг-оборудованию на платформе <b>Yandex DataLens</b> 📊.\n\n"
             "Что Вы хотите сделать?",
        reply_markup=keyboards.main_menu)
    functions.writing_logs(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message.from_user.id, 'start')
    await state.clear()


@router.callback_query(F.data == 'return_to_main_menu')
async def main_menu(callback: CallbackQuery,
                    state: FSMContext):
    await callback.message.answer(
        text="Добро пожаловать в <b>crypto_advice_bot</b>! 👋\n\n - По кнопке <b>«Сделать расчет»</b> ✍️ "
             "Вы можете посчитать наиболее выгодные инвестиции в майнинг-оборудование "
             "конкретно для Вас и Ваших условий. \n - По кнопке "
             "<b>«Сколько я уже мог заработать» ❓</b> Вы можете увидеть, сколько могли заработать, сколько могли заработать, начав майнить раньше.\n"
             " - По кнопке <b>«Как купить монеты дешевле рынка» 🛒</b> Вы сможете увидеть одну из стратегий "
             "майнинга крипты, позволяющая покупать любой актив на рынке с большим дисконтом.\n"
             " - Также можно ознакомиться с подробным дашбордом по "
             "майнинг-оборудованию на платформе <b>Yandex DataLens</b> 📊.\n\n"
             "Что Вы хотите сделать?",
        reply_markup=keyboards.main_menu)
    await state.clear()


@router.callback_query(F.data == 'calculation')
async def calculation(callback: CallbackQuery,
                      state: FSMContext):
    functions.writing_logs(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), callback.from_user.id, 'calculation')
    await callback.message.edit_text(text="Окей, каким бюджетом вы располагаете (в 💲)? \nВведите целое "
                                          "неотрицательное число")
    await callback.answer()
    await state.set_state(fsm.GetUserData.insert_budget)


@router.message(StateFilter(fsm.GetUserData.insert_budget),
                lambda x: x.text.isdigit() and int(x.text) > 0)
async def calculation_budget_success(message: Message,
                                     state: FSMContext):
    await state.update_data(budget=message.text)
    await message.answer(text="Сколько у вас свободных майнинговых мощностей ⚡ \n(в Вт*час)?\nВведите целое "
                                 "неотрицательное число (майнер в среднем потребляет <b>2000 - 3500 Вт*час</b>)")
    await state.set_state(fsm.GetUserData.insert_available_power)


@router.message(StateFilter(fsm.GetUserData.insert_budget))
async def calculation_budget_fail(message: Message,
                                  state: FSMContext):
    await message.answer(text=f'К сожалению, то, что вы ввели, не похоже на целое положительное число 🤔 '
                                 f'Попробуйте еще раз',
                            reply_markup=keyboards.return_to_main_menu)
    await state.clear()


@router.message(StateFilter(fsm.GetUserData.insert_available_power),
                lambda x: x.text.isdigit() and int(x.text) > 0)
async def calculation_available_power_success(message: Message,
                                              state: FSMContext):
    await state.update_data(available_power=message.text)
    await message.answer(
        text="Укажите вашу цену ⚡ электроэнергии (в 💲) - через точку \n(в среднем в РФ цена за ЭЭ <b>0.02 - 0.07</b> $/кВт)")
    await state.set_state(fsm.GetUserData.insert_electro_price)


@router.message(StateFilter(fsm.GetUserData.insert_available_power))
async def calculation_available_power_fail(message: Message,
                                           state: FSMContext):
    await message.answer(text=f'К сожалению, то, что вы ввели, не похоже на целое положительное число 🤔 '
                                 f'Попробуйте еще раз',
                            reply_markup=keyboards.return_to_main_menu)
    await state.clear()


@router.message(StateFilter(fsm.GetUserData.insert_electro_price),
                lambda x: float(x.text) >= 0)
async def calculation_electro_price_success(message: Message,
                                            state: FSMContext):
    try:
        await state.update_data(electro_price=message.text)
        await message.answer(
            text="Хорошо, с вашими условиями разобрались 👌. \nДавайте поговорим о ваших предпочтениях. \nКакую "
                 "из нижеперечисленных целей считаете наиболее важной для себя?",
            reply_markup=keyboards.purpose_choice_menu)
        await state.set_state(fsm.GetUserData.insert_purpose)
    except ValueError:
        await message.answer(
            text=f"То, что вы ввели, не похоже на цену электроэнергии 🤔. Проверьте, что вводите цену "
                 f"электроэнергии через точку и попробуйте еще раз",
            reply_markup=keyboards.return_to_main_menu)


@router.message(StateFilter(fsm.GetUserData.insert_electro_price))
async def calculation_electro_price_fail(message: Message,
                                         state: FSMContext):
    await message.answer(text=f'К сожалению, то, что вы ввели, не похоже на целое положительное число 🤔 '
                                 f'Попробуйте еще раз',
                            reply_markup=keyboards.return_to_main_menu)
    await state.clear()


@router.callback_query(StateFilter(fsm.GetUserData.insert_purpose))
async def less_electricity_pay(callback: CallbackQuery,
                               state: FSMContext):
    await state.update_data(purpose=callback.data)
    await callback.message.edit_text(
        text="Укажите <b>максимальную сумму в месяц</b>, с которой вы готовы расстаться для оплаты "
             "электроэнергии (в 💲)?")
    await callback.answer()
    await state.set_state(fsm.GetUserData.insert_max_electricity_pay)


@router.message(StateFilter(fsm.GetUserData.insert_max_electricity_pay),
                lambda x: x.text.isdigit() and int(x.text) > 0)
async def less_electricity_pay_success(message: Message,
                                       state: FSMContext):
    await state.update_data(max_electricity_pay=message.text)
    await message.answer(text="Супер! С этим тоже разобрались! Может, вы хотели бы майнить какую-то конкретную"
                                 " криптовалюту?",
                            reply_markup=keyboards.coin_choice_menu)
    await state.set_state(fsm.GetUserData.insert_coin)


@router.message(StateFilter(fsm.GetUserData.insert_max_electricity_pay))
async def less_electricity_pay_fail(message: Message,
                                    state: FSMContext):
    await message.answer(text=f'К сожалению, то, что вы ввели, не похоже на целое положительное число 🤔 '
                                 f'Попробуйте еще раз',
                            reply_markup=keyboards.return_to_main_menu)
    await state.clear()


@router.callback_query(StateFilter(fsm.GetUserData.insert_coin), F.data == 'BTC')
async def coin_chosen_btc_380v(callback: CallbackQuery,
                               state: FSMContext):
    await state.update_data(coin=callback.data)
    await callback.message.edit_text(text="Отличный выбор! Уточните, есть ли у вас доступ к трехфазной сети ⚡?",
                                     reply_markup=keyboards.btc_380_menu)
    await callback.answer()
    await state.set_state(fsm.GetUserData.insert_380v_for_btc)


@router.callback_query(StateFilter(fsm.GetUserData.insert_coin), F.data == 'Diversification')
async def coin_chosen_div_380v(callback: CallbackQuery,
                               state: FSMContext):
    await state.update_data(coin=callback.data)
    await callback.message.edit_text(text="Отличный выбор! Уточните, есть ли у вас доступ к трехфазной сети ⚡?",
                                     reply_markup=keyboards.btc_380_menu)
    await state.set_state(fsm.GetUserData.insert_380v_for_btc)


@router.callback_query(StateFilter(fsm.GetUserData.insert_380v_for_btc))
async def coin_chosen_btc_or_div_hydro(callback: CallbackQuery,
                                       state: FSMContext):
    await state.update_data(v380=callback.data)
    await callback.message.edit_text(text="Хорошо, и последний вопрос - есть ли у вас возможность установить асики на "
                                       "водяной системе охлаждения 🌊?",
                                  reply_markup=keyboards.btc_hydro_menu)
    await state.set_state(fsm.GetUserData.insert_hydro_for_btc)


@router.callback_query(StateFilter(fsm.GetUserData.insert_hydro_for_btc))
async def coin_chosen_btc_or_div_final(callback: CallbackQuery,
                                       state: FSMContext):
    await state.update_data(hydro=callback.data)
    await callback.message.edit_text(text="Отлично, кажется, это все, что я хотел узнать. Нажмите кнопку 'Получить "
                                       "результат', и я запущу расчет",
                                  reply_markup=keyboards.get_result_menu)
    await state.set_state(fsm.GetUserData.final_stage)


@router.callback_query(StateFilter(fsm.GetUserData.insert_coin))
async def coin_chosen_final(callback: CallbackQuery,
                            state: FSMContext):
    await state.update_data(coin=callback.data)
    await callback.message.edit_text(text="Отлично, кажется, это все, что я хотел узнать. Нажмите кнопку 'Получить "
                                       "результат', и я запущу расчет",
                                  reply_markup=keyboards.get_result_menu)
    await state.set_state(fsm.GetUserData.final_stage)


@router.callback_query(StateFilter(fsm.GetUserData.final_stage))
async def get_result(callback: CallbackQuery,
                     state: FSMContext):
    fsm_result = await state.get_data()
    now = datetime.now()

    db_connection = pymysql.connect(host=config.host, database=config.database,
                                    user=config.user, password=config.password)

    query = ("SELECT name, correct_hash_rate, energy_consumption, price, coin, cool_type, fiat_profitability FROM "
             "asic_general_info_12_view")
    df = pd.read_sql(query, db_connection)
    df['specific_power_for_calculation'] = df.apply(functions.specific_power_for_calculation, axis=1)
    df['coin_risks'] = df.apply(functions.coin_risks, axis=1)
    df['v380'] = df.apply(functions.v380, axis=1)
    df['payback_in_months'] = df['price'] / ((df['fiat_profitability'] * 30 / df['specific_power_for_calculation'] *
                                              df['correct_hash_rate']) - (
                                                     float(fsm_result['electro_price']) * df[
                                                 'energy_consumption'] / 1000 * 720))
    df['monthly_profitability'] = ((df['fiat_profitability'] * 30 / df['specific_power_for_calculation'] *
                                    df['correct_hash_rate']) - (
                                           float(fsm_result['electro_price']) * df['energy_consumption'] / 1000 * 720))
    df['monthly_pay'] = float(fsm_result['electro_price']) * 720 * df['energy_consumption'] / 1000
    filtered_data = df.query("payback_in_months > 0 & monthly_profitability > 0 & monthly_pay >= 0")

    if fsm_result['purpose'] == 'quick_payback':
        df_sorted = filtered_data.sort_values(by='payback_in_months')
    elif fsm_result['purpose'] == 'highly_profit':
        df_sorted = filtered_data.sort_values(by='monthly_profitability', ascending=False)
    else:
        df_sorted = filtered_data.sort_values(by='monthly_pay')

    if fsm_result['coin'] == 'BTC':
        if fsm_result['v380'] == 'btc_380_yes':
            if fsm_result['hydro'] == 'btc_hydro_yes':
                final_filtered_df = df_sorted.query("coin == 'SHA-256 (BTC)'")
            elif fsm_result['hydro'] == 'btc_hydro_no':
                final_filtered_df = df_sorted.query("coin == 'SHA-256 (BTC)' & cool_type == 'Воздушное'")
        elif fsm_result['v380'] == 'btc_380_no':
            final_filtered_df = df_sorted.query("coin == 'SHA-256 (BTC)' & v380 == 0 & cool_type == 'Воздушное'")
    elif fsm_result['coin'] == 'ETC':
        final_filtered_df = df_sorted.query("coin == 'Ethash (ETC)'")
    elif fsm_result['coin'] == 'LTC':
        final_filtered_df = df_sorted.query("coin == 'Scrypt (LTC+DOGE)'")
    elif fsm_result['coin'] == 'DASH':
        final_filtered_df = df_sorted.query("coin == 'X11 (DASH)'")
    elif fsm_result['coin'] == 'KAS':
        final_filtered_df = df_sorted.query("coin == 'KHeavyHash (KAS)'")
    elif fsm_result['coin'] == 'CKB':
        final_filtered_df = df_sorted.query("coin == 'Eaglesong (CKB)'")
    elif fsm_result['coin'] == 'KDA':
        final_filtered_df = df_sorted.query("coin == 'Blake2s (KDA)'")
    elif fsm_result['coin'] == 'ALPH':
        final_filtered_df = df_sorted.query("coin == 'Blake3 (ALPH)'")
    elif fsm_result['coin'] == 'HNS':
        final_filtered_df = df_sorted.query("coin == 'Blake2B+SHA3 (HNS)'")
    elif fsm_result['coin'] == 'ZEC':
        final_filtered_df = df_sorted.query("coin == 'Equihash (ZEC)'")
    elif fsm_result['coin'] == 'Diversification':
        if fsm_result['v380'] == 'btc_380_yes':
            if fsm_result['hydro'] == 'btc_hydro_yes':
                final_filtered_df = df_sorted
            elif fsm_result['hydro'] == 'btc_hydro_no':
                final_filtered_df = df_sorted.query("cool_type == 'Воздушное'")
        elif fsm_result['v380'] == 'btc_380_no':
            final_filtered_df = df_sorted.query("v380 == 0 & cool_type == 'Воздушное'")

    if fsm_result['coin'] == 'Diversification':
        final_filtered_df_safety = final_filtered_df.query("coin_risks == 1")
        final_filtered_df_risk = final_filtered_df.query("coin_risks == 2")
        data_tuple_safety = list(final_filtered_df_safety.to_records(index=False))
        data_tuple_risk = list(final_filtered_df_risk.to_records(index=False))
        summary_list_safety = []
        summary_list_risk = []

        budget_safety = int(fsm_result['budget'])
        available_power_safety = int(fsm_result['available_power'])
        max_electricity_pay_safety = int(fsm_result['max_electricity_pay'])

        if fsm_result['purpose'] == 'quick_payback' or fsm_result['purpose'] == 'highly_profit':
            while budget_safety > 0 and available_power_safety > 0:
                added = False
                for sublist in data_tuple_safety:
                    if budget_safety >= sublist[3] and available_power_safety >= sublist[2]:
                        summary_list_safety.append(sublist)
                        budget_safety -= sublist[3]
                        available_power_safety -= sublist[2]
                        added = True
                        break

                if not added:
                    break
        else:
            while budget_safety > 0 and available_power_safety > 0 and max_electricity_pay_safety > 0:
                added = False
                for sublist in data_tuple_safety:
                    if (budget_safety >= sublist[3] and available_power_safety >= sublist[2] and
                            max_electricity_pay_safety >= sublist[-1]):
                        summary_list_safety.append(sublist)
                        budget_safety -= sublist[3]
                        available_power_safety -= sublist[2]
                        max_electricity_pay_safety -= sublist[-1]
                        added = True
                        break

                if not added:
                    break

        budget_risk = int(fsm_result['budget'])
        available_power_risk = int(fsm_result['available_power'])
        max_electricity_pay_risk = int(fsm_result['max_electricity_pay'])

        if fsm_result['purpose'] == 'quick_payback' or fsm_result['purpose'] == 'highly_profit':
            while budget_risk > 0 and available_power_risk > 0:
                added = False
                for sublist in data_tuple_risk:
                    if budget_risk >= sublist[3] and available_power_risk >= sublist[2]:
                        summary_list_risk.append(sublist)
                        budget_risk -= sublist[3]
                        available_power_risk -= sublist[2]
                        added = True
                        break

                if not added:
                    break
        else:
            while budget_risk > 0 and available_power_risk > 0 and max_electricity_pay_risk > 0:
                added = False
                for sublist in data_tuple_risk:
                    if (budget_risk >= sublist[3] and available_power_risk >= sublist[2] and
                            max_electricity_pay_risk >= sublist[-1]):
                        summary_list_risk.append(sublist)
                        budget_risk -= sublist[3]
                        available_power_risk -= sublist[2]
                        max_electricity_pay_risk -= sublist[-1]
                        added = True
                        break

                if not added:
                    break
        new_summary_list_safety = list(map(tuple, summary_list_safety))
        new_summary_list_risk = list(map(tuple, summary_list_risk))

        if new_summary_list_safety and new_summary_list_risk:
            dohod_safety = 0
            rashod_safety = 0
            summa_oborud_safety = 0

            for elem in new_summary_list_safety:
                dohod_safety += (elem[-2] + elem[-1])
                rashod_safety += elem[-1]
                summa_oborud_safety += elem[3]

            df_new_safety = pd.DataFrame(new_summary_list_safety,
                                         columns=['Наименование', 'Хэшрейт (1 шт.)', 'Потребление, Вт.',
                                                  'Стоимость (в USD)', 'Алгоритм', 'Охлаждение', 'Доход',
                                                  'Кол-во',
                                                  'Риск', '380 В', 'Окупаемость (в мес.)',
                                                  'Прибыль (в USD) в мес.',
                                                  'Расходы (в USD) в мес.'])

            df_final_safety = df_new_safety.groupby(['Наименование', 'Алгоритм'], as_index=False).agg({
                'Кол-во': 'count',
                'Стоимость (в USD)': 'sum',
                'Хэшрейт (1 шт.)': 'mean',
                'Потребление, Вт.': 'sum',
                'Окупаемость (в мес.)': 'mean',
                'Прибыль (в USD) в мес.': 'sum',
                'Расходы (в USD) в мес.': 'sum'
            })

            df_final_safety.loc['Сумма'] = df_final_safety.agg({'Кол-во': 'sum', 'Стоимость (в USD)': 'sum',
                                                                'Потребление, Вт.': 'sum',
                                                                'Прибыль (в USD) в мес.': 'sum',
                                                                'Расходы (в USD) в мес.': 'sum'})
            df_final_safety = df_final_safety.round(decimals=1)

            purpose_dict = {
                'quick_payback': 'Как можно быстрее окупиться',
                'highly_profit': 'Иметь максимально возможный месячный доход',
                'less_electricity_pay': 'Меньше платить за электроэнергию'
            }

            # Создаем PDF документ
            pdf = FPDF(orientation='L', unit='mm', format='A4')
            pdf.add_page()

            # Устанавливаем шрифт и размер текста
            pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
            pdf.set_font('DejaVu', '', 9)

            # Добавляем таблицу в PDF
            pdf.cell(200, 5, txt=f"Отчет на {now.strftime('%d-%m-%Y %H:%M')}", ln=True, align='L')
            pdf.cell(200, 5, txt=f"Бюджет: {int(fsm_result['budget'])} $", ln=True, align='L')
            pdf.cell(200, 5, txt=f"Доступный объем ЭЭ: {int(fsm_result['available_power'])} Вт*час", ln=True,
                     align='L')
            pdf.cell(200, 5, txt=f"Стоимость ЭЭ: {fsm_result['electro_price']} $/кВт", ln=True, align='L')
            pdf.cell(200, 5, txt=f"Предпочитаемая криптовалюта: {fsm_result['coin']}", ln=True, align='L')
            pdf.cell(200, 5, txt=f"Цель: {purpose_dict[fsm_result['purpose']]}", ln=True, align='L')
            pdf.cell(200, 5, txt=f"Стратегия: надежная", ln=True, align='L')
            pdf.ln(10)
            pdf.set_font('DejaVu', '', 7)
            pdf.set_fill_color(200, 220, 255)

            # Добавляем заголовки столбцов
            for col in df_final_safety.columns:
                if col == 'Наименование':
                    pdf.cell(60, 10, str(col), 1, align='L')
                elif col == 'Кол-во':
                    pdf.cell(12, 10, str(col), 1, align='C')
                else:
                    pdf.cell(30, 10, str(col), 1, align='C')
            pdf.ln()

            # Добавляем данные из DataFrame
            for index, row in df_final_safety.iterrows():
                for col in df_final_safety.columns:
                    if col == 'Наименование' and str(row[col]) == 'nan':
                        pdf.cell(60, 10, 'Итого', 1, align='L')
                    elif col == 'Наименование':
                        pdf.cell(60, 10, str(row[col]), 1, align='L')
                    elif str(row[col]) == 'nan' and (
                            col == 'Алгоритм' or col == 'Хэшрейт (1 шт.)' or col == 'Окупаемость (в мес.)'):
                        pdf.cell(30, 10, '-', 1, align='C')
                    elif col == 'Кол-во':
                        pdf.cell(12, 10, str(row[col]), 1, align='C')
                    else:
                        pdf.cell(30, 10, str(row[col]), 1, align='C')
                pdf.ln()

            # Сохраняем PDF файл
            pdf.output(f"files/report_safety_id_{callback.from_user.id}.pdf")

            dohod_risk = 0
            rashod_risk = 0
            summa_oborud_risk = 0

            for elem in new_summary_list_risk:
                dohod_risk += (elem[-2] + elem[-1])
                rashod_risk += elem[-1]
                summa_oborud_risk += elem[3]

            df_new_risk = pd.DataFrame(new_summary_list_risk,
                                       columns=['Наименование', 'Хэшрейт (1 шт.)', 'Потребление, Вт.',
                                                'Стоимость (в USD)', 'Алгоритм', 'Охлаждение', 'Доход',
                                                'Кол-во',
                                                'Риск', '380 В', 'Окупаемость (в мес.)',
                                                'Прибыль (в USD) в мес.',
                                                'Расходы (в USD) в мес.'])

            df_final_risk = df_new_risk.groupby(['Наименование', 'Алгоритм'], as_index=False).agg({
                'Кол-во': 'count',
                'Стоимость (в USD)': 'sum',
                'Хэшрейт (1 шт.)': 'mean',
                'Потребление, Вт.': 'sum',
                'Окупаемость (в мес.)': 'mean',
                'Прибыль (в USD) в мес.': 'sum',
                'Расходы (в USD) в мес.': 'sum'
            })

            df_final_risk.loc['Сумма'] = df_final_risk.agg({'Кол-во': 'sum', 'Стоимость (в USD)': 'sum',
                                                            'Потребление, Вт.': 'sum',
                                                            'Прибыль (в USD) в мес.': 'sum',
                                                            'Расходы (в USD) в мес.': 'sum'})
            df_final_risk = df_final_risk.round(decimals=1)

            # Создаем PDF документ
            pdf = FPDF(orientation='L', unit='mm', format='A4')
            pdf.add_page()

            # Устанавливаем шрифт и размер текста
            pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
            pdf.set_font('DejaVu', '', 9)

            # Добавляем таблицу в PDF
            pdf.cell(200, 5, txt=f"Отчет на {now.strftime('%d-%m-%Y %H:%M')}", ln=True, align='L')
            pdf.cell(200, 5, txt=f"Бюджет: {int(fsm_result['budget'])} $", ln=True, align='L')
            pdf.cell(200, 5, txt=f"Доступный объем ЭЭ: {int(fsm_result['available_power'])} Вт*час", ln=True,
                     align='L')
            pdf.cell(200, 5, txt=f"Стоимость ЭЭ: {fsm_result['electro_price']} $/кВт", ln=True, align='L')
            pdf.cell(200, 5, txt=f"Предпочитаемая криптовалюта: {fsm_result['coin']}", ln=True, align='L')
            pdf.cell(200, 5, txt=f"Цель: {purpose_dict[fsm_result['purpose']]}", ln=True, align='L')
            pdf.cell(200, 5, txt=f"Стратегия: рискованная", ln=True, align='L')
            pdf.ln(10)
            pdf.set_font('DejaVu', '', 7)
            pdf.set_fill_color(200, 220, 255)

            # Добавляем заголовки столбцов
            for col in df_final_risk.columns:
                if col == 'Наименование':
                    pdf.cell(60, 10, str(col), 1, align='L')
                elif col == 'Кол-во':
                    pdf.cell(12, 10, str(col), 1, align='C')
                else:
                    pdf.cell(30, 10, str(col), 1, align='C')
            pdf.ln()

            # Добавляем данные из DataFrame
            for index, row in df_final_risk.iterrows():
                for col in df_final_risk.columns:
                    if col == 'Наименование' and str(row[col]) == 'nan':
                        pdf.cell(60, 10, 'Итого', 1, align='L')
                    elif col == 'Наименование':
                        pdf.cell(60, 10, str(row[col]), 1, align='L')
                    elif str(row[col]) == 'nan' and (
                            col == 'Алгоритм' or col == 'Хэшрейт (1 шт.)' or col == 'Окупаемость (в мес.)'):
                        pdf.cell(30, 10, '-', 1, align='C')
                    elif col == 'Кол-во':
                        pdf.cell(12, 10, str(row[col]), 1, align='C')
                    else:
                        pdf.cell(30, 10, str(row[col]), 1, align='C')
                pdf.ln()

            # Сохраняем PDF файл
            pdf.output(f"files/report_risk_id_{callback.from_user.id}.pdf")
            await callback.message.answer(text='По расчетам и вашим вводным данным удалось составить две стратегии '
                                               'инвестирования в майнинг-оборудование - надежную и рискованную')
            await callback.message.answer(text='Надежная стратегия:')
            await callback.message.bot.send_chat_action(
                chat_id=callback.from_user.id,
                action=ChatAction.UPLOAD_DOCUMENT
            )
            file_path = f"files/report_safety_id_{callback.from_user.id}.pdf"
            await callback.message.reply_document(document=FSInputFile(
                path=file_path,
                filename="Your_report_safety.pdf"
            ))
            await callback.message.answer(text=f"Бюджет проекта - <b>$ {int(fsm_result['budget'])}</b>\n"
                                               f"Ежемесячный доход - <b>$ {int(dohod_safety)}</b>\n"
                                               f"Ежемесячные расходы на ЭЭ в <b>$ {fsm_result['electro_price']}/кВт</b>"
                                               f" - <b>$ {int(rashod_safety)}</b>\n"
                                               f"Ежемесячная прибыль - <b>$ {int(dohod_safety - rashod_safety)}</b>\n"
                                               f"Окупаемость проекта - <b>{round(float(summa_oborud_safety / (dohod_safety - rashod_safety)), 1)} мес.</b>\n")
            await callback.message.answer(text='Рискованная стратегия:')
            await callback.message.bot.send_chat_action(
                chat_id=callback.from_user.id,
                action=ChatAction.UPLOAD_DOCUMENT
            )
            file_path = f"files/report_risk_id_{callback.from_user.id}.pdf"
            await callback.message.reply_document(document=FSInputFile(
                path=file_path,
                filename="Your_report_risk.pdf"
            ))
            await callback.message.answer(text=f"Бюджет проекта - <b>$ {int(fsm_result['budget'])}</b>\n"
                                               f"Ежемесячный доход - <b>$ {int(dohod_risk)}</b>\n"
                                               f"Ежемесячные расходы на ЭЭ в <b>$ {fsm_result['electro_price']}/кВт</b>"
                                               f" - <b>$ {int(rashod_risk)}</b>\n"
                                               f"Ежемесячная прибыль - <b>$ {int(dohod_risk - rashod_risk)}</b>\n"
                                               f"Окупаемость проекта - <b>{round(float(summa_oborud_risk / (dohod_risk - rashod_risk)), 1)} мес.</b>\n")
            functions.writing_logs(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), callback.from_user.id,
                                   'calculation_result')
            await callback.message.answer(
                text='<b>Помните, что это - теоретический расчет, сделанный при текущем курсе '
                     'криптовалют, а также при текущей сложности сети. \nХалвинги криптовалют '
                     'также '
                     'не учитаны при расчетах.</b>')
            await callback.message.answer(
                text='С более полной информацией об оборудовании вы можете ознакомиться в моем '
                     'регулярно обновляющемся дашборде: '
                     '<u>https://datalens.yandex/kth6k05xlg9c8</u>',
                reply_markup=keyboards.return_to_main_menu)
        elif new_summary_list_safety and not new_summary_list_risk:
            dohod = 0
            rashod = 0
            summa_oborud = 0

            for elem in new_summary_list_safety:
                dohod += (elem[-2] + elem[-1])
                rashod += elem[-1]
                summa_oborud += elem[3]

            df_new = pd.DataFrame(new_summary_list_safety,
                                  columns=['Наименование', 'Хэшрейт (1 шт.)', 'Потребление, Вт.',
                                           'Стоимость (в USD)', 'Алгоритм', 'Охлаждение', 'Доход',
                                           'Кол-во',
                                           'Риск', '380 В', 'Окупаемость (в мес.)',
                                           'Прибыль (в USD) в мес.',
                                           'Расходы (в USD) в мес.'])

            df_final = df_new.groupby(['Наименование', 'Алгоритм'], as_index=False).agg({
                'Кол-во': 'count',
                'Стоимость (в USD)': 'sum',
                'Хэшрейт (1 шт.)': 'mean',
                'Потребление, Вт.': 'sum',
                'Окупаемость (в мес.)': 'mean',
                'Прибыль (в USD) в мес.': 'sum',
                'Расходы (в USD) в мес.': 'sum'
            })

            df_final.loc['Сумма'] = df_final.agg({'Кол-во': 'sum', 'Стоимость (в USD)': 'sum',
                                                  'Потребление, Вт.': 'sum',
                                                  'Прибыль (в USD) в мес.': 'sum',
                                                  'Расходы (в USD) в мес.': 'sum'})
            df_final = df_final.round(decimals=1)

            purpose_dict = {
                'quick_payback': 'Как можно быстрее окупиться',
                'highly_profit': 'Иметь максимально возможный месячный доход',
                'less_electricity_pay': 'Меньше платить за электроэнергию'
            }

            # Создаем PDF документ
            pdf = FPDF(orientation='L', unit='mm', format='A4')
            pdf.add_page()

            # Устанавливаем шрифт и размер текста
            pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
            pdf.set_font('DejaVu', '', 9)

            # Добавляем таблицу в PDF
            pdf.cell(200, 5, txt=f"Отчет на {now.strftime('%d-%m-%Y %H:%M')}", ln=True, align='L')
            pdf.cell(200, 5, txt=f"Бюджет: {int(fsm_result['budget'])} $", ln=True, align='L')
            pdf.cell(200, 5, txt=f"Доступный объем ЭЭ: {int(fsm_result['available_power'])} Вт*час", ln=True,
                     align='L')
            pdf.cell(200, 5, txt=f"Стоимость ЭЭ: {fsm_result['electro_price']} $/кВт", ln=True, align='L')
            pdf.cell(200, 5, txt=f"Предпочитаемая криптовалюта: {fsm_result['coin']}", ln=True, align='L')
            pdf.cell(200, 5, txt=f"Цель: {purpose_dict[fsm_result['purpose']]}", ln=True, align='L')
            pdf.cell(200, 5, txt=f"Стратегия: надежная", ln=True, align='L')
            pdf.ln(10)
            pdf.set_font('DejaVu', '', 7)
            pdf.set_fill_color(200, 220, 255)

            # Добавляем заголовки столбцов
            for col in df_final.columns:
                if col == 'Наименование':
                    pdf.cell(60, 10, str(col), 1, align='L')
                elif col == 'Кол-во':
                    pdf.cell(12, 10, str(col), 1, align='C')
                else:
                    pdf.cell(30, 10, str(col), 1, align='C')
            pdf.ln()

            # Добавляем данные из DataFrame
            for index, row in df_final.iterrows():
                for col in df_final.columns:
                    if col == 'Наименование' and str(row[col]) == 'nan':
                        pdf.cell(60, 10, 'Итого', 1, align='L')
                    elif col == 'Наименование':
                        pdf.cell(60, 10, str(row[col]), 1, align='L')
                    elif str(row[col]) == 'nan' and (
                            col == 'Алгоритм' or col == 'Хэшрейт (1 шт.)' or col == 'Окупаемость (в мес.)'):
                        pdf.cell(30, 10, '-', 1, align='C')
                    elif col == 'Кол-во':
                        pdf.cell(12, 10, str(row[col]), 1, align='C')
                    else:
                        pdf.cell(30, 10, str(row[col]), 1, align='C')
                pdf.ln()

            # Сохраняем PDF файл
            pdf.output(f"files/report_safety_id_{callback.from_user.id}.pdf")
            await callback.message.answer(text='По расчетам и вашим вводным данным удалось составить только '
                                               'надежную стратегию инвестирования в майнинг-оборудование:')
            await callback.message.bot.send_chat_action(
                chat_id=callback.from_user.id,
                action=ChatAction.UPLOAD_DOCUMENT
            )
            file_path = f"files/report_safety_id_{callback.from_user.id}.pdf"
            await callback.message.reply_document(document=FSInputFile(
                path=file_path,
                filename="Your_report.pdf"
            ))

            await callback.message.answer(text=f"Бюджет проекта - <b>$ {int(fsm_result['budget'])}</b>\n"
                                               f"Ежемесячный доход - <b>$ {int(dohod)}</b>\n"
                                               f"Ежемесячные расходы на ЭЭ в <b>$ {fsm_result['electro_price']}/кВт</b>"
                                               f" - <b>$ {int(rashod)}</b>\n"
                                               f"Ежемесячная прибыль - <b>$ {int(dohod - rashod)}</b>\n"
                                               f"Окупаемость проекта - <b>{round(float(summa_oborud / (dohod - rashod)), 1)} мес.</b>\n")
            functions.writing_logs(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), callback.from_user.id,
                                   'calculation_result')
            await callback.message.answer(text='Помните, что это - теоретический расчет, сделанный при текущем курсе '
                                               'криптовалют, а также при текущей сложности сети. Халвинги криптовалют '
                                               'также '
                                               'не учитаны при расчетах.')
            await callback.message.answer(
                text='С более полной информацией об оборудовании вы можете ознакомиться в моем '
                     'регулярно обновляющемся дашборде: '
                     '<u>https://datalens.yandex/kth6k05xlg9c8</u>',
                reply_markup=keyboards.return_to_main_menu)
        elif new_summary_list_risk and not new_summary_list_safety:
            dohod = 0
            rashod = 0
            summa_oborud = 0

            for elem in new_summary_list_risk:
                dohod += (elem[-2] + elem[-1])
                rashod += elem[-1]
                summa_oborud += elem[3]

            df_new = pd.DataFrame(new_summary_list_risk,
                                  columns=['Наименование', 'Хэшрейт (1 шт.)', 'Потребление, Вт.',
                                           'Стоимость (в USD)', 'Алгоритм', 'Охлаждение', 'Доход',
                                           'Кол-во',
                                           'Риск', '380 В', 'Окупаемость (в мес.)',
                                           'Прибыль (в USD) в мес.',
                                           'Расходы (в USD) в мес.'])

            df_final = df_new.groupby(['Наименование', 'Алгоритм'], as_index=False).agg({
                'Кол-во': 'count',
                'Стоимость (в USD)': 'sum',
                'Хэшрейт (1 шт.)': 'mean',
                'Потребление, Вт.': 'sum',
                'Окупаемость (в мес.)': 'mean',
                'Прибыль (в USD) в мес.': 'sum',
                'Расходы (в USD) в мес.': 'sum'
            })

            df_final.loc['Сумма'] = df_final.agg({'Кол-во': 'sum', 'Стоимость (в USD)': 'sum',
                                                  'Потребление, Вт.': 'sum',
                                                  'Прибыль (в USD) в мес.': 'sum',
                                                  'Расходы (в USD) в мес.': 'sum'})
            df_final = df_final.round(decimals=1)

            purpose_dict = {
                'quick_payback': 'Как можно быстрее окупиться',
                'highly_profit': 'Иметь максимально возможный месячный доход',
                'less_electricity_pay': 'Меньше платить за электроэнергию'
            }

            # Создаем PDF документ
            pdf = FPDF(orientation='L', unit='mm', format='A4')
            pdf.add_page()

            # Устанавливаем шрифт и размер текста
            pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
            pdf.set_font('DejaVu', '', 9)

            # Добавляем таблицу в PDF
            pdf.cell(200, 5, txt=f"Отчет на {now.strftime('%d-%m-%Y %H:%M')}", ln=True, align='L')
            pdf.cell(200, 5, txt=f"Бюджет: {int(fsm_result['budget'])} $", ln=True, align='L')
            pdf.cell(200, 5, txt=f"Доступный объем ЭЭ: {int(fsm_result['available_power'])} Вт*час", ln=True,
                     align='L')
            pdf.cell(200, 5, txt=f"Стоимость ЭЭ: {fsm_result['electro_price']} $/кВт", ln=True, align='L')
            pdf.cell(200, 5, txt=f"Предпочитаемая криптовалюта: {fsm_result['coin']}", ln=True, align='L')
            pdf.cell(200, 5, txt=f"Цель: {purpose_dict[fsm_result['purpose']]}", ln=True, align='L')
            pdf.cell(200, 5, txt=f"Стратегия: рискованная", ln=True, align='L')
            pdf.ln(10)
            pdf.set_font('DejaVu', '', 7)
            pdf.set_fill_color(200, 220, 255)

            # Добавляем заголовки столбцов
            for col in df_final.columns:
                if col == 'Наименование':
                    pdf.cell(60, 10, str(col), 1, align='L')
                elif col == 'Кол-во':
                    pdf.cell(12, 10, str(col), 1, align='C')
                else:
                    pdf.cell(30, 10, str(col), 1, align='C')
            pdf.ln()

            # Добавляем данные из DataFrame
            for index, row in df_final.iterrows():
                for col in df_final.columns:
                    if col == 'Наименование' and str(row[col]) == 'nan':
                        pdf.cell(60, 10, 'Итого', 1, align='L')
                    elif col == 'Наименование':
                        pdf.cell(60, 10, str(row[col]), 1, align='L')
                    elif str(row[col]) == 'nan' and (
                            col == 'Алгоритм' or col == 'Хэшрейт (1 шт.)' or col == 'Окупаемость (в мес.)'):
                        pdf.cell(30, 10, '-', 1, align='C')
                    elif col == 'Кол-во':
                        pdf.cell(12, 10, str(row[col]), 1, align='C')
                    else:
                        pdf.cell(30, 10, str(row[col]), 1, align='C')
                pdf.ln()

            # Сохраняем PDF файл
            pdf.output(f"files/report_risk_id_{callback.from_user.id}.pdf")
            await callback.message.answer(text='По расчетам и вашим вводным данным удалось составить только '
                                               'рискованную стратегию инвестирования в майнинг-оборудование:')
            await callback.message.bot.send_chat_action(
                chat_id=callback.from_user.id,
                action=ChatAction.UPLOAD_DOCUMENT
            )
            file_path = f"files/report_risk_id_{callback.from_user.id}.pdf"
            await callback.message.reply_document(document=FSInputFile(
                path=file_path,
                filename="Your_report.pdf"
            ))

            await callback.message.answer(text=f"Бюджет проекта - <b>$ {int(fsm_result['budget'])}</b>\n"
                                               f"Ежемесячный доход - <b>$ {int(dohod)}</b>\n"
                                               f"Ежемесячные расходы на ЭЭ в <b>$ {fsm_result['electro_price']}/кВт</b>"
                                               f" - <b>$ {int(rashod)}</b>\n"
                                               f"Ежемесячная прибыль - <b>$ {int(dohod - rashod)}</b>\n"
                                               f"Окупаемость проекта - <b>{round(float(summa_oborud / (dohod - rashod)), 1)} мес.</b>\n")
            functions.writing_logs(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), callback.from_user.id,
                                   'calculation_result')
            await callback.message.answer(text='Помните, что это - теоретический расчет, сделанный при текущем курсе '
                                               'криптовалют, а также при текущей сложности сети. Халвинги криптовалют '
                                               'также '
                                               'не учитаны при расчетах.')
            await callback.message.answer(
                text='С более полной информацией об оборудовании вы можете ознакомиться в моем '
                     'регулярно обновляющемся дашборде: '
                     '<u>https://datalens.yandex/kth6k05xlg9c8</u>',
                reply_markup=keyboards.return_to_main_menu)
        else:
            await callback.message.answer(text='К сожалению, опираясь на расчеты и ваши вводные, не нашлось доступного '
                                               'для вас оборудования. Пожалуйста, попробуйте изменить параметры поиска '
                                               'оборудования и заново запустите расчет',
                                          reply_markup=keyboards.return_to_main_menu)

    # для обычного алгоритма
    else:
        data_tuple = list(final_filtered_df.to_records(index=False))
        summary_list = []

        budget = int(fsm_result['budget'])
        available_power = int(fsm_result['available_power'])
        max_electricity_pay = int(fsm_result['max_electricity_pay'])

        if fsm_result['purpose'] == 'quick_payback' or fsm_result['purpose'] == 'highly_profit':
            while budget > 0 and available_power > 0:
                added = False
                for sublist in data_tuple:
                    if budget >= sublist[3] and available_power >= sublist[2]:
                        summary_list.append(sublist)
                        budget -= sublist[3]
                        available_power -= sublist[2]
                        added = True
                        break

                if not added:
                    break
        else:
            while budget > 0 and available_power > 0 and max_electricity_pay > 0:
                added = False
                for sublist in data_tuple:
                    if budget >= sublist[3] and available_power >= sublist[2] and max_electricity_pay >= sublist[-1]:
                        summary_list.append(sublist)
                        budget -= sublist[3]
                        available_power -= sublist[2]
                        max_electricity_pay -= sublist[-1]
                        added = True
                        break

                if not added:
                    break

        new_summary_list = list(map(tuple, summary_list))
        if new_summary_list:
            dohod = 0
            rashod = 0
            summa_oborud = 0

            for elem in new_summary_list:
                dohod += (elem[-2] + elem[-1])
                rashod += elem[-1]
                summa_oborud += elem[3]

            df_new = pd.DataFrame(new_summary_list, columns=['Наименование', 'Хэшрейт (1 шт.)', 'Потребление, Вт.',
                                                             'Стоимость (в USD)', 'Алгоритм', 'Охлаждение', 'Доход',
                                                             'Кол-во',
                                                             'Риск', '380 В', 'Окупаемость (в мес.)',
                                                             'Прибыль (в USD) в мес.',
                                                             'Расходы (в USD) в мес.'])

            df_final = df_new.groupby(['Наименование', 'Алгоритм'], as_index=False).agg({
                'Кол-во': 'count',
                'Стоимость (в USD)': 'sum',
                'Хэшрейт (1 шт.)': 'mean',
                'Потребление, Вт.': 'sum',
                'Окупаемость (в мес.)': 'mean',
                'Прибыль (в USD) в мес.': 'sum',
                'Расходы (в USD) в мес.': 'sum'
            })

            df_final.loc['Сумма'] = df_final.agg({'Кол-во': 'sum', 'Стоимость (в USD)': 'sum',
                                                  'Потребление, Вт.': 'sum',
                                                  'Прибыль (в USD) в мес.': 'sum',
                                                  'Расходы (в USD) в мес.': 'sum'})
            df_final = df_final.round(decimals=1)

            purpose_dict = {
                'quick_payback': 'Как можно быстрее окупиться',
                'highly_profit': 'Иметь максимально возможный месячный доход',
                'less_electricity_pay': 'Меньше платить за электроэнергию'
            }

            # Создаем PDF документ
            pdf = FPDF(orientation='L', unit='mm', format='A4')
            pdf.add_page()

            # Устанавливаем шрифт и размер текста
            pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
            pdf.set_font('DejaVu', '', 9)

            # Добавляем таблицу в PDF
            pdf.cell(200, 5, txt=f"Отчет на {now.strftime('%d-%m-%Y %H:%M')}", ln=True, align='L')
            pdf.cell(200, 5, txt=f"Бюджет: {int(fsm_result['budget'])} $", ln=True, align='L')
            pdf.cell(200, 5, txt=f"Доступный объем ЭЭ: {int(fsm_result['available_power'])} Вт*час", ln=True,
                     align='L')
            pdf.cell(200, 5, txt=f"Стоимость ЭЭ: {fsm_result['electro_price']} $/кВт", ln=True, align='L')
            pdf.cell(200, 5, txt=f"Предпочитаемая криптовалюта: {fsm_result['coin']}", ln=True, align='L')
            pdf.cell(200, 5, txt=f"Цель: {purpose_dict[fsm_result['purpose']]}", ln=True, align='L')
            pdf.ln(10)
            pdf.set_font('DejaVu', '', 7)
            pdf.set_fill_color(200, 220, 255)

            # Добавляем заголовки столбцов
            for col in df_final.columns:
                if col == 'Наименование':
                    pdf.cell(60, 10, str(col), 1, align='L')
                elif col == 'Кол-во':
                    pdf.cell(12, 10, str(col), 1, align='C')
                else:
                    pdf.cell(30, 10, str(col), 1, align='C')
            pdf.ln()

            # Добавляем данные из DataFrame
            for index, row in df_final.iterrows():
                for col in df_final.columns:
                    if col == 'Наименование' and str(row[col]) == 'nan':
                        pdf.cell(60, 10, 'Итого', 1, align='L')
                    elif col == 'Наименование':
                        pdf.cell(60, 10, str(row[col]), 1, align='L')
                    elif str(row[col]) == 'nan' and (
                            col == 'Алгоритм' or col == 'Хэшрейт (1 шт.)' or col == 'Окупаемость (в мес.)'):
                        pdf.cell(30, 10, '-', 1, align='C')
                    elif col == 'Кол-во':
                        pdf.cell(12, 10, str(row[col]), 1, align='C')
                    else:
                        pdf.cell(30, 10, str(row[col]), 1, align='C')
                pdf.ln()

            # Сохраняем PDF файл
            pdf.output(f"files/report_id_{callback.from_user.id}.pdf")
            await callback.message.answer(text='Судя по расчетам и вашим вводным, это оборудование подойдет вам больше '
                                               'всего:')
            await callback.message.bot.send_chat_action(
                chat_id=callback.from_user.id,
                action=ChatAction.UPLOAD_DOCUMENT
            )
            file_path = f"files/report_id_{callback.from_user.id}.pdf"
            await callback.message.reply_document(document=FSInputFile(
                path=file_path,
                filename="Your_report.pdf"
            ))

            await callback.message.answer(text=f"Бюджет проекта - <b>$ {int(fsm_result['budget'])}</b>\n"
                                               f"Ежемесячный доход - <b>$ {int(dohod)}</b>\n"
                                               f"Ежемесячные расходы на ЭЭ в <b>$ {fsm_result['electro_price']}/кВт</b>"
                                               f" - <b>$ {int(rashod)}</b>\n"
                                               f"Ежемесячная прибыль - <b>$ {int(dohod - rashod)}</b>\n"
                                               f"Окупаемость проекта - <b>{round(float(summa_oborud / (dohod - rashod)), 1)} мес.</b>\n")
            functions.writing_logs(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), callback.from_user.id,
                                   'calculation_result')
            await callback.message.answer(text='Помните, что это - теоретический расчет, сделанный при текущем курсе '
                                               'криптовалют, а также при текущей сложности сети. Халвинги криптовалют '
                                               'также '
                                               'не учитаны при расчетах.')
            await callback.message.answer(
                text='С более полной информацией об оборудовании вы можете ознакомиться в моем '
                     'регулярно обновляющемся дашборде: '
                     '<u>https://datalens.yandex/kth6k05xlg9c8</u>',
                reply_markup=keyboards.return_to_main_menu)
        else:
            await callback.message.answer(text='К сожалению, опираясь на расчеты и ваши вводные, не нашлось доступного '
                                               'для вас оборудования. Пожалуйста, попробуйте изменить параметры поиска '
                                               'оборудования и заново запустите расчет',
                                          reply_markup=keyboards.return_to_main_menu)
    await state.clear()


@router.callback_query(F.data == 'fomo')
async def fomo_start(callback: CallbackQuery,
                     state: FSMContext):
    functions.writing_logs(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), callback.from_user.id, 'fomo')
    await callback.message.edit_text(text="Добро пожаловать в FOMO-раздел!\nЗдесь вы сможете наглядно увидеть <b>(на "
                                       "реальных данных)</b>, сколько денег вы уже успели потерять, пока вы думаете, "
                                       "стоит ли заходить в майнинг. Расчеты сделаны уже <b>по фактической сложности "
                                       "сети</b>.\nИтак, выберем наш асик. Какой выберете?\n"
                                       "(текстом введите наименование интересующего вас асика \n(<u><i>прим."
                                       " 'S21'</i></u>))")
    await state.set_state(fsm.Fomo.insert_asic_name)


@router.message(StateFilter(fsm.Fomo.insert_asic_name), F.text.len() > 1)
async def fomo_insert_asic(message: Message,
                           state: FSMContext):
    is_asics = await functions.asic_list(message.text)
    if is_asics:
        if len(is_asics) > 15:
            await message.answer(text='Слишком много результатов поиска:(\n'
                                      'Попробуйте ввести название более конкретно',
                                 reply_markup=keyboards.return_to_main_menu)
        else:
            await message.answer(text='Окей, вот, что удалось найти по вашему запросу:',
                                 reply_markup=await keyboards.create_asic_list_keyboard(message.text))
    else:
        await message.answer(text='К сожалению, по вашему запросу не нашлось ни одного результата :(\n'
                                  'Попробуйте ввести название повторно',
                             reply_markup=keyboards.return_to_main_menu)


@router.message(StateFilter(fsm.Fomo.insert_asic_name))
async def fomo_insert_asic_fail(message: Message,
                                state: FSMContext):
    await message.answer(text='К сожалению, по вашему запросу не нашлось ни одного результата :(\n'
                              'Попробуйте ввести название повторно',
                         reply_markup=keyboards.return_to_main_menu)


@router.callback_query(callback_factory.AsicsList.filter())
async def fomo_choose_date(callback: CallbackQuery,
                           callback_data: callback_factory.AsicsList,
                           state: FSMContext):
    min_date = await functions.min_date_in_db(callback_data.item)
    await state.update_data(asic=callback_data.item)
    await state.update_data(date=min_date[0])
    await callback.message.edit_text(text=f'С какой даты хотите посчитать? 📅\nСамая ранняя доступная дата - '
                                       f'<b>{min_date[0]}</b>',
                                  reply_markup=keyboards.date_choose)


@router.callback_query(F.data == 'manual_date')
async def fomo_insert_manual_date(callback: CallbackQuery,
                                  state: FSMContext):
    await callback.message.edit_text(text='Введите дату в формате ГГГГ-ММ-ДД 📅')
    await state.set_state(fsm.Fomo.insert_date)


@router.message(StateFilter(fsm.Fomo.insert_date), F.text)
async def fomo_insert_manual_date_check(message: Message,
                                        state: FSMContext):
    is_date_correct = await functions.date_check(message.text)
    if is_date_correct:
        await state.update_data(date=message.text)
        data = await state.get_data()
        dates = await functions.all_date_in_db(data['asic'])
        dates_corr = [date[0] for date in dates]
        nearest_date = min(dates_corr, key=lambda x: abs(datetime.strptime(str(x), "%Y-%m-%d")
                                                         - datetime.strptime(data['date'], "%Y-%m-%d")))
        await state.update_data(date=nearest_date)
        await message.answer(text=f"Ближайшая дата к введенной - <b>{nearest_date}</b>\nВыбрать эту дату?",
                             reply_markup=keyboards.manual_date_confirm)
    else:
        await message.answer(text=f"Некорректный формат введенной Вами даты. Попробуйте еще раз",
                             reply_markup=keyboards.return_to_main_menu)


@router.message(StateFilter(fsm.Fomo.insert_date))
async def fomo_insert_manual_date_check(message: Message,
                                        state: FSMContext):
    await message.answer(text=f"То, что вы ввели, не похоже на текст 🤔. Попробуйте еще раз",
                         reply_markup=keyboards.return_to_main_menu)


@router.callback_query(F.data.in_(['early_date', 'manual_date_confirm_button']))
async def fomo_insert_electricity_price(callback: CallbackQuery,
                                        state: FSMContext):
    await callback.message.edit_text(
        text='Укажите вашу цену ⚡ электроэнергии (в 💲) - через точку \n(в среднем в РФ цена за ЭЭ <b>0.02 - 0.07</b> $/кВт)')
    await state.set_state(fsm.Fomo.insert_electricity)


@router.message(StateFilter(fsm.Fomo.insert_electricity),
                lambda x: float(x.text) >= 0)
async def fomo_summary_confirm(message: Message,
                               state: FSMContext):
    try:
        await state.update_data(electricity_price=message.text)
        data = await state.get_data()
        asic = await functions.asic_list_accuracy(data['asic'])
        await message.answer(text=f"Итак, кажется, что это все, что нужно. Давайте сверимся и запустим расчет:\n"
                                  f"Наименование: <b>{asic[0][0]}</b>\n"
                                  f"Энергопотребление: <b>{int(asic[0][2])} Вт</b>\n"
                                  f"Алгоритм: <b>{asic[0][3]}</b>\n"
                                  f"Считаем с даты: <b>{data['date']}</b>\n"
                                  f"Стоимость электроэнергии: <b>{data['electricity_price']} $/кВт</b>",
                             reply_markup=keyboards.calculation_start)
        await state.set_state(fsm.Fomo.get_result)
    except ValueError:
        await message.answer(text=f"То, что вы ввели, не похоже на цену электроэнергии. Проверьте, что вводите цену "
                                  f"электроэнергии через точку и попробуйте еще раз",
                             reply_markup=keyboards.return_to_main_menu)


@router.message(StateFilter(fsm.Fomo.insert_electricity))
async def fomo_summary_confirm_fail(message: Message):
    await message.answer(text=f"То, что вы ввели, не похоже на цену электроэнергии 🤔. Попробуйте еще раз",
                         reply_markup=keyboards.return_to_main_menu)


@router.callback_query(F.data == 'calculation_start', StateFilter(fsm.Fomo.get_result))
async def fomo_calculation_start(callback: CallbackQuery,
                                 state: FSMContext):
    data = await state.get_data()
    asic = await functions.asic_list_accuracy(data['asic'])
    if asic:
        if asic[0][3] == 'Scrypt (LTC+DOGE)':
            query = f"SELECT * FROM mining_profitability_bot_view WHERE name = '{asic[0][0]}' AND date >= '{data['date']}'"
            db = pymysql.connect(host=config.host, database=config.database,
                                 user=config.user, password=config.password)
            try:
                df = pd.read_sql(query, db)
                df_ltc = df.loc[(df['currency'] == 'LTC')]
                df_doge = df.loc[(df['currency'] == 'DOGE')]
                max_date_tuple = await functions.max_date_in_currency_exchange()
                max_date = max_date_tuple[0]
                currency_ltc_tuple = await functions.get_last_crypto_course_ltc(max_date)
                currency_doge_tuple = await functions.get_last_crypto_course_doge(max_date)
                currency_ltc = currency_ltc_tuple[0].quantize(Decimal('0.00'), rounding=ROUND_HALF_EVEN)
                currency_doge = currency_doge_tuple[0].quantize(Decimal('0.00'), rounding=ROUND_HALF_EVEN)
                crypto_sum_ltc = Decimal(df_ltc['crypto_sum'].sum()).quantize(Decimal('0.00'), rounding=ROUND_HALF_EVEN)
                crypto_sum_doge = Decimal(df_doge['crypto_sum'].sum()).quantize(Decimal('0.00'),
                                                                                rounding=ROUND_HALF_EVEN)
                days_of_work = df_ltc['num_of_days'].sum()
                electricity_pay = days_of_work * asic[0][2] * 24 * float(data['electricity_price']) / 1000
                fiat_sum_ltc = (crypto_sum_ltc * currency_ltc).quantize(Decimal('0.00'), rounding=ROUND_HALF_EVEN)
                fiat_sum_doge = (crypto_sum_doge * currency_doge).quantize(Decimal('0.00'), rounding=ROUND_HALF_EVEN)
                start_price = df_ltc.loc[(df_ltc['date'] == data['date'])]['price'].values[0]
                start_fiat_profit_one_day = df_ltc.loc[(df_ltc['date'] == data['date'])]['fiat_sum_one_day'].values[0]
                current_price = df_ltc.loc[(df_ltc['date'] == max(df_ltc['date']))]['price'].values[0]
                last_date_in_list = max(df_ltc['date'])
                delta_price = start_price - current_price
                start_payback = round((start_price / (
                        start_fiat_profit_one_day - (asic[0][2] * 24 * float(data['electricity_price']) / 1000)) / 30),
                                      1)
                current_percent_payback = ((fiat_sum_ltc + fiat_sum_doge) - Decimal(electricity_pay)).quantize(
                    Decimal('0.00'),
                    rounding=ROUND_HALF_EVEN) / Decimal(
                    start_price) * 100
                days_of_mining = (datetime.now().date() - data['date']).days
                await callback.message.answer(text=f"Асик: <b>{asic[0][0]}</b>\n"
                                                   f"Алгоритм: <b>{asic[0][3]}</b>\n\n"
                                                   f"За период с <b>{data['date']}</b> по сегодняшний день вам бы уже удалось намайнить: \n"
                                                   f"<b>{crypto_sum_ltc} LTC - ${fiat_sum_ltc.quantize(Decimal('0.00'), rounding=ROUND_HALF_EVEN)} (текущий курс - {currency_ltc} USDT</b>),\n"
                                                   f"<b>{crypto_sum_doge} DOGE - ${fiat_sum_doge.quantize(Decimal('0.00'), rounding=ROUND_HALF_EVEN)} (текущий курс - {currency_doge} USDT).</b>\n"
                                                   f"Оплата за электроэнергию составила бы <b>${int(electricity_pay)}</b>. \nИтого - прибыль <b>${((fiat_sum_ltc + fiat_sum_doge) - Decimal(electricity_pay)).quantize(Decimal('0.00'), rounding=ROUND_HALF_EVEN)}</b>\n\n"
                                                   f"Также стоит упомянуть и стоимость оборудования. \n"
                                                   f"Стоимость асика <b>{data['date']} - ${int(start_price)}</b>\n"
                                                   f"Стоимость асика <b>{last_date_in_list} - ${int(current_price)}</b>\n"
                                                   f"За этот период цена {asic[0][0]} "
                                                   f"<b>{'увеличилась' if int(delta_price) < 0 else 'уменьшилась'} на ${int(delta_price) if delta_price > 0 else -int(delta_price)} "
                                                   f"({round(delta_price / start_price * 100, 1) if delta_price > 0 else - round(delta_price / start_price * 100, 1)} %)</b>\n\n"
                                                   f"Теперь перейдем к окупаемости. На момент покупки <b>{data['date']}</b> {asic[0][0]} "
                                                   f"«на бумаге» окупался за <b>{start_payback} мес.</b>\n"
                                                   f"Сейчас же, спустя <b>{round(days_of_mining / 30, 1)} мес.</b> после покупки асик окупился бы на"
                                                   f" <b>{current_percent_payback.quantize(Decimal('0.00'), rounding=ROUND_HALF_EVEN)} процентов!</b>")
                if current_percent_payback >= 100:
                    await callback.message.answer(
                        text=f"То есть, <b>{asic[0][0]} окупился бы за {(days_of_mining / (current_percent_payback / 100) / 30).quantize(Decimal('0.0'), rounding=ROUND_HALF_EVEN)} мес.</b> и сейчас работал бы в плюс!")
                else:
                    await callback.message.answer(
                        text=f"Расчетная окупаемость по текущему курсу 💹 составит <b>{(days_of_mining / (current_percent_payback / 100) / 30).quantize(Decimal('0.0'), rounding=ROUND_HALF_EVEN)} мес.</b>")
                functions.writing_logs(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), callback.from_user.id,
                                       'fomo_result')
                await callback.message.answer(
                    text="Также не следует забывать, что <b>сложность майнинга ⛏️ стремительно растет</b> по"
                         " всем популярным алгоритам, и <b>то количество крипты, которое вы могли бы "
                         "намайнить сегодня будет больше, чем завтра (в большинстве случаев).</b> "
                         "Но решать, конечно же, вам!\n\n"
                         "Рекомендую также ознакомиться <b>с дашбордом в BI-системе Yandex Datalens 📊</b> - "
                         "там вы сможете сравнить различное оборудование между собой по окупаемости, "
                         "доходности и многим другим показателям! Вот ссылка: "
                         "<u>https://datalens.yandex/kth6k05xlg9c8</u>\n\n"
                         "Дашборд регулярно обновляется и дополняется. Также просьба оставлять ваши "
                         "пожелания, идеи и замечания по боту и дашборду по кнопке <b>«Оставить "
                         "комментарий 💬»</b>.",
                    reply_markup=keyboards.fomo_end)


            finally:
                # Закрываем соединение
                db.close()
        else:
            query = f"SELECT * FROM mining_profitability_bot_view WHERE name = '{asic[0][0]}' AND date >= '{data['date']}'"
            db = pymysql.connect(host=config.host, database=config.database,
                                 user=config.user, password=config.password)
            try:
                df = pd.read_sql(query, db)
                currency = df['currency'].unique().tolist()[0]
                max_date_tuple = await functions.max_date_in_currency_exchange()
                max_date = max_date_tuple[0]
                currency_value_tuple = await functions.get_last_crypto_course(currency, max_date)
                currency_value = currency_value_tuple[0].quantize(Decimal('0.00'), rounding=ROUND_HALF_EVEN)
                if asic[0][3] == 'SHA-256 (BTC)':
                    crypto_sum = Decimal(df['crypto_sum'].sum()).quantize(Decimal('0.0000'), rounding=ROUND_HALF_EVEN)
                else:
                    crypto_sum = Decimal(df['crypto_sum'].sum()).quantize(Decimal('0.00'), rounding=ROUND_HALF_EVEN)
                days_of_work = df['num_of_days'].sum()
                electricity_pay = days_of_work * asic[0][2] * 24 * float(data['electricity_price']) / 1000
                fiat_sum = (crypto_sum * currency_value).quantize(Decimal('0.00'), rounding=ROUND_HALF_EVEN)
                start_price = df.loc[(df['date'] == data['date'])]['price'].values[0]
                start_fiat_profit_one_day = df.loc[(df['date'] == data['date'])]['fiat_sum_one_day'].values[0]
                current_price = df.loc[(df['date'] == max(df['date']))]['price'].values[0]
                last_date_in_list = max(df['date'])
                delta_price = start_price - current_price
                start_payback = round((start_price / (
                        start_fiat_profit_one_day - (asic[0][2] * 24 * float(data['electricity_price']) / 1000)) / 30),
                                      1)
                current_percent_payback = (fiat_sum - Decimal(electricity_pay)).quantize(Decimal('0.00'),
                                                                                         rounding=ROUND_HALF_EVEN) / Decimal(
                    start_price) * 100
                days_of_mining = (datetime.now().date() - data['date']).days
                await callback.message.answer(text=f"Асик: <b>{asic[0][0]}</b>\n"
                                                   f"Алгоритм: <b>{asic[0][3]}</b>\n\n"
                                                   f"За период с <b>{data['date']}</b> по сегодняшний день вам бы уже удалось намайнить: \n<b>{crypto_sum} {currency}</b>, "
                                                   f"что в долларовом эквиваленте по актуальному курсу <b>{currency_value} USDT</b> составляет <b>${fiat_sum.quantize(Decimal('0.00'), rounding=ROUND_HALF_EVEN)}</b>.\n"
                                                   f"Оплата за электроэнергию составила бы <b>${int(electricity_pay)}</b>. \nИтого - прибыль <b>${(fiat_sum - Decimal(electricity_pay)).quantize(Decimal('0.00'), rounding=ROUND_HALF_EVEN)}</b>\n\n"
                                                   f"Также стоит упомянуть и стоимость оборудования. \n"
                                                   f"Стоимость асика <b>{data['date']} - ${int(start_price)}</b>\n"
                                                   f"Стоимость асика <b>{last_date_in_list} - ${int(current_price)}</b>\n"
                                                   f"За этот период цена {asic[0][0]} "
                                                   f"<b>{'увеличилась' if int(delta_price) < 0 else 'уменьшилась'} на ${int(delta_price) if delta_price > 0 else -int(delta_price)} "
                                                   f"({round(delta_price / start_price * 100, 1) if delta_price > 0 else - round(delta_price / start_price * 100, 1)} %)</b>\n\n"
                                                   f"Теперь перейдем к окупаемости. На момент покупки <b>{data['date']}</b> {asic[0][0]} "
                                                   f"«на бумаге» окупался за <b>{start_payback} мес.</b>\n"
                                                   f"Сейчас же, спустя <b>{round(days_of_mining / 30, 1)} мес.</b> после покупки асик окупился бы на"
                                                   f" <b>{current_percent_payback.quantize(Decimal('0.00'), rounding=ROUND_HALF_EVEN)} процентов!</b>")
                if current_percent_payback >= 100:
                    await callback.message.answer(
                        text=f"То есть, <b>{asic[0][0]} окупился бы за {(days_of_mining / (current_percent_payback / 100) / 30).quantize(Decimal('0.0'), rounding=ROUND_HALF_EVEN)} мес.</b> и сейчас работал бы в плюс!")
                else:
                    await callback.message.answer(
                        text=f"Расчетная окупаемость по текущему курсу составит <b>{(days_of_mining / (current_percent_payback / 100) / 30).quantize(Decimal('0.0'), rounding=ROUND_HALF_EVEN)} мес.</b>")
                functions.writing_logs(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), callback.from_user.id,
                                       'fomo_result')
                await callback.message.answer(
                    text="Также не следует забывать, что <b>сложность майнинга ⛏️ стремительно растет</b> по"
                         " всем популярным алгоритам, и <b>то количество крипты, которое вы могли бы "
                         "намайнить сегодня будет больше, чем завтра (в большинстве случаев).</b> "
                         "Но решать, конечно же, вам!\n\n"
                         "Рекомендую также ознакомиться <b>с дашбордом в BI-системе Yandex Datalens 📊</b> - "
                         "там вы сможете сравнить различное оборудование между собой по окупаемости, "
                         "доходности и многим другим показателям! Вот ссылка: "
                         "<u>https://datalens.yandex/kth6k05xlg9c8</u>\n\n"
                         "Дашборд регулярно обновляется и дополняется. Также просьба оставлять ваши "
                         "пожелания, идеи и замечания по боту и дашборду по кнопке <b>«Оставить "
                         "комментарий 💬»</b>.",
                    reply_markup=keyboards.fomo_end)


            finally:
                # Закрываем соединение
                db.close()
    else:
        await callback.message.answer(text='Что-то пошло не так. Попробуйте еще раз',
                                      reply_markup=keyboards.return_to_main_menu)

    await state.clear()


@router.callback_query(F.data == 'feedback')
async def feedback(callback: CallbackQuery,
                   state: FSMContext):
    functions.writing_logs(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), callback.from_user.id, 'feedback')
    await callback.message.answer(f"Пожалуйста, введите ваши сообщение 💬 (можно скринами, текстом, стикерами). \n"
                                  f"Если хотите получить ответ на сообщение - оставьте также свой <b>@username</b>")
    await state.set_state(fsm.Feedback.insert_feedback)


@router.message(StateFilter(fsm.Feedback.insert_feedback))
async def feedback_success(message: Message,
                           state: FSMContext):
    await bot.forward_message(chat_id=config.FEEDBACK_CHAT_ID, from_chat_id=message.chat.id,
                              message_id=message.message_id)
    await message.answer(text='Отлично! Ваше сообщение принято! Спасибо!',
                         reply_markup=keyboards.return_to_main_menu)
    await state.clear()


@router.callback_query(F.data == 'cheap_coins')
async def cheap_start(callback: CallbackQuery,
                      state: FSMContext):
    functions.writing_logs(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), callback.from_user.id, 'cheap_coins')
    await callback.message.edit_text(text="Хотите ли вы купить монеты дешевле, чем они стоят на рынке? 🤔\n"
                                       "Благодаря майнингу у вас есть такая возможность! \nДавайте сделаем небольшой "
                                       "расчет, и вы сами в этом убедитесь! 🛒\n"
                                       "Итак, выберем наш майнер. Какой выберете?\n"
                                       "<i><u>(текстом введите наименование интересующего Вас асика (прим."
                                       " 'S21'))</u></i>")
    await state.set_state(fsm.CheapCoins.insert_asic_name)


@router.message(StateFilter(fsm.CheapCoins.insert_asic_name), F.text.len() > 1)
async def cheap_insert_asic(message: Message,
                            state: FSMContext):
    is_asics = await functions.asic_list(message.text)
    if is_asics:
        if len(is_asics) > 15:
            await message.answer(text='Слишком много результатов поиска:(\n'
                                      'Попробуйте ввести название более конкретно',
                                 reply_markup=keyboards.return_to_main_menu)
        else:
            await message.answer(text='Окей, вот, что удалось найти по вашему запросу:',
                                 reply_markup=await keyboards.create_cheap_asic_list_keyboard(message.text))
    else:
        await message.answer(text='К сожалению, по вашему запросу не нашлось ни одного результата :(\n'
                                  'Попробуйте ввести название повторно',
                             reply_markup=keyboards.return_to_main_menu)


@router.message(StateFilter(fsm.CheapCoins.insert_asic_name))
async def cheap_insert_asic_fail(message: Message,
                                 state: FSMContext):
    await message.answer(text='К сожалению, по вашему запросу не нашлось ни одного результата :(\n'
                              'Попробуйте ввести название повторно',
                         reply_markup=keyboards.return_to_main_menu)


@router.callback_query(callback_factory.CheapAsicsList.filter(), StateFilter(fsm.CheapCoins.insert_asic_name))
async def cheap_insert_electro(callback: CallbackQuery,
                               callback_data: callback_factory.CheapAsicsList,
                               state: FSMContext):
    await state.update_data(asic=callback_data.item)
    await callback.message.edit_text(
        text='Укажите вашу цену ⚡ электроэнергии (в 💲) - через точку \n(в среднем в РФ цена за ЭЭ <b>0.02 - 0.07</b> $/кВт)')
    await state.set_state(fsm.CheapCoins.insert_electricity)


@router.message(StateFilter(fsm.CheapCoins.insert_electricity),
                lambda x: float(x.text) >= 0)
async def cheap_summary_confirm(message: Message,
                                state: FSMContext):
    try:
        await state.update_data(electricity_price=message.text)
        data = await state.get_data()
        asic = await functions.asic_list_accuracy(data['asic'])
        await message.answer(text=f"Кажется, что это все, что нужно. Давайте сверимся и запустим расчет:\n"
                                  f"Наименование: <b>{asic[0][0]}</b>\n"
                                  f"Энергопотребление: <b>{int(asic[0][2])} Вт</b>\n"
                                  f"Алгоритм: <b>{asic[0][3]}</b>\n"
                                  f"Стоимость электроэнергии: <b>{data['electricity_price']} $/кВт</b>",
                             reply_markup=keyboards.calculation_start)
        await state.set_state(fsm.CheapCoins.get_result)
    except ValueError:
        await message.answer(text=f"То, что вы ввели, не похоже на цену электроэнергии 🤔. Проверьте, что вводите цену "
                                  f"электроэнергии через точку и попробуйте еще раз",
                             reply_markup=keyboards.return_to_main_menu)


@router.message(StateFilter(fsm.CheapCoins.insert_electricity))
async def cheap_summary_confirm_fail(message: Message):
    await message.answer(text=f"То, что вы ввели, не похоже на цену электроэнергии 🤔. Попробуйте еще раз",
                         reply_markup=keyboards.return_to_main_menu)


@router.callback_query(F.data == 'calculation_start', StateFilter(fsm.CheapCoins.get_result))
async def cheap_calculation_start(callback: CallbackQuery,
                                  state: FSMContext):
    data = await state.get_data()
    asic = await functions.asic_list_accuracy(data['asic'])
    if asic:
        if asic[0][3] == 'Scrypt (LTC+DOGE)':
            query = f"SELECT * FROM mining_profitability_bot_view_last_date WHERE name = '{asic[0][0]}'"
            db = pymysql.connect(host=config.host, database=config.database,
                                 user=config.user, password=config.password)
            try:
                await callback.message.bot.send_chat_action(
                    chat_id=callback.from_user.id,
                    action=ChatAction.TYPING)
                df = pd.read_sql(query, db)
                df = df.head(1)
                await callback.message.bot.send_chat_action(
                    chat_id=callback.from_user.id,
                    action=ChatAction.TYPING)
                if not df.empty:
                    self_cost_1_usdt = ((df['energy_consumption'] / 1000 * 24 * float(data['electricity_price'])) /
                                        (df['fiat_profitability'] / df['specific_power_for_calculation'] * df[
                                            'correct_hash_rate'])).values[0]
                    exchange = ccxt.binance()
                    tickers = ['BTC', 'ETH', 'SOL', 'TON', 'BNB', 'APT', 'SUI', 'ARB', 'OP']
                    tickers_full = ['Bitcoin', 'Ethereum', 'Solana', 'Toncoin', 'Binance Coin', 'Aptos', 'Sui',
                                    'Arbitrum', 'Optimism']
                    tickers_value = []
                    for ticker in tickers:
                        tickers_value.append(exchange.fetch_ticker(f'{ticker}/USDT')['last'])
                    tickers_cheap_value = [round(ticker_value * self_cost_1_usdt, 2) for ticker_value in tickers_value]
                    currency_result = list(zip(tickers, tickers_full, tickers_value, tickers_cheap_value))
                    currency_string = '\n'.join([
                        f"<b>{ticket[0]}</b> ({ticket[1]}) - ваша цена <b>${ticket[3]}</b> (по рынку ${ticket[2]})"
                        for ticket in currency_result])
                    await callback.message.bot.send_chat_action(
                        chat_id=callback.from_user.id,
                        action=ChatAction.TYPING)
                    await callback.message.answer(
                        text=f"Перед тем, как показать результат, необходимо убедиться, что все "
                             f"одинаково хорошо понимают эту стратегию. \nПриведу следующий "
                             f"пример:")
                    await callback.message.answer(
                        text=f"За месяц работы ваш майнер добыл криптовалюты на <b>$500</b>, затратив "
                             f"при этом электроэнергии  на ⚡ <b>$100</b>. \nПотратив на производство всего "
                             f"$100, вы за $500 продаете вашу криптовалюту на биржах и "
                             f"покупаете ту криптовалюту, которую готовы держать в долгосрок, "
                             f"потратив всего $100. \nИными словами, себестоимость одного "
                             f"добытого криптодоллара для вас составила $0.2, и абсолютно любую "
                             f"крипту вы можете приобрести в <b>5 (!!!) раз</b> дешевле "
                             f"рыночной цены. \nА теперь к вашему примеру:")
                    await callback.message.bot.send_chat_action(
                        chat_id=callback.from_user.id,
                        action=ChatAction.TYPING)
                    time.sleep(5)
                    await callback.message.bot.send_chat_action(
                        chat_id=callback.from_user.id,
                        action=ChatAction.TYPING)
                    await callback.message.answer(text=f"Майнер: <b>{asic[0][0]}</b>\n"
                                                       f"Алгоритм: <b>{asic[0][3]}</b>\n"
                                                       f"Цена за 1 кВт: <b>${data['electricity_price']}</b>\n\n"
                                                       f"Себестоимость добычи 1 USDT для {asic[0][0]} - "
                                                       f"<b>${round(self_cost_1_usdt, 2)}</b>, и вот ваш актуальный курс "
                                                       f"некоторых криптовалют:\n\n"
                                                       f"{currency_string}")
                    await callback.message.bot.send_chat_action(
                        chat_id=callback.from_user.id,
                        action=ChatAction.TYPING)
                    time.sleep(10)
                    await callback.message.bot.send_chat_action(
                        chat_id=callback.from_user.id,
                        action=ChatAction.TYPING)
                    if self_cost_1_usdt > 1:
                        await callback.message.answer(
                            text=f"Сожалеем, но такая конфигурация не является окупаемой на текущий момент :(")
                        functions.writing_logs(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), callback.from_user.id,
                                               'cheap_coins_result')
                    else:
                        await callback.message.answer(
                            text=f"P.S. Следует понимать, что данная стратегия работает <b>исключительно до того момента</b>, "
                                 f"пока вы продаете ваш намайненный {asic[0][3].split('(')[1].split(')')[0]}"
                                 f" и на деньги с продажи покупаете крипту.\nИ второй момент, который важно понимать.\n"
                                 f"<b>Больше устройств -> больше плата за электроэнергию -> больше дешевых монет для продажи</b>.\nЕсли в вашем арсенале имеется одно устройство мощностью 100 Ватт и вы платите за электричество, скажем,"
                                 f"$5 в месяц, то нетрудно догадаться, какое количество крипты вам удастся купить "
                                 f"(<u>спойлер: очень маленькое</u>).\n"
                                 f"Поэтому предлагаю добавить еще совсем немного математики, чтобы вы поняли порядок чисел:")
                        await callback.message.bot.send_chat_action(
                            chat_id=callback.from_user.id,
                            action=ChatAction.TYPING)
                        time.sleep(3)
                        await callback.message.bot.send_chat_action(
                            chat_id=callback.from_user.id,
                            action=ChatAction.TYPING)
                        await callback.message.answer(
                            text=f"Для того, чтобы в месяц этим способом покупать крипты, например, на $1000 "
                                 f"<b>(для вас это ${round(1000 * round(self_cost_1_usdt, 2), 0)})</b> вам необходимо купить асиков {asic[0][0]}"
                                 f" на сумму ${round(((1000 * round(self_cost_1_usdt, 2) / (float(data['electricity_price']) * df['energy_consumption'] * 720 / 1000)) * df['price']).values[0], 0)}.\n"
                                 f"<b>Это порядка {round((1000 * round(self_cost_1_usdt, 2) / (float(data['electricity_price']) * df['energy_consumption'] * 720 / 1000)).values[0], 1)} асиков</b>.")
                        await callback.message.bot.send_chat_action(
                            chat_id=callback.from_user.id,
                            action=ChatAction.TYPING)
                        time.sleep(3)
                    await callback.message.bot.send_chat_action(
                        chat_id=callback.from_user.id,
                        action=ChatAction.TYPING)
                    time.sleep(3)
                    await callback.message.bot.send_chat_action(
                        chat_id=callback.from_user.id,
                        action=ChatAction.TYPING)
                    await callback.message.answer(
                        text="P.P.S. Также не следует забывать, что <b>сложность майнинга ⛏️ стремительно растет</b> по"
                             " всем популярным алгоритам, и <b>то количество крипты, которое вы могли бы "
                             "намайнить сегодня будет больше, чем завтра (в большинстве случаев).</b> "
                             "Но решать, конечно же, вам!\n\n"
                             "Рекомендую также ознакомиться <b>с дашбордом в BI-системе Yandex Datalens</b> - "
                             "там вы сможете сравнить различное оборудование между собой по окупаемости, "
                             "доходности и многим другим показателям! Вот ссылка: "
                             "<u>https://datalens.yandex/kth6k05xlg9c8</u>\n\n"
                             "Дашборд регулярно обновляется и дополняется. Также просьба оставлять ваши "
                             "пожелания, идеи и замечания по боту и дашборду по кнопке <b>«Оставить "
                             "комментарий»</b>.",
                        reply_markup=keyboards.fomo_end)
                    functions.writing_logs(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), callback.from_user.id,
                                           'cheap_coins_result')
                else:
                    await callback.message.answer(
                        text="К сожалению, на данный момент этот майнер не находится в продаже :(\n"
                             "Попробуйте, пожалуйста, выбрать другое оборудование",
                        reply_markup=keyboards.return_to_main_menu)


            finally:
                # Закрываем соединение
                db.close()
        else:
            query = f"SELECT * FROM mining_profitability_bot_view_last_date WHERE name = '{asic[0][0]}'"
            db = pymysql.connect(host=config.host, database=config.database,
                                 user=config.user, password=config.password)
            try:
                await callback.message.bot.send_chat_action(
                    chat_id=callback.from_user.id,
                    action=ChatAction.TYPING)
                df = pd.read_sql(query, db)
                await callback.message.bot.send_chat_action(
                    chat_id=callback.from_user.id,
                    action=ChatAction.TYPING)
                if not df.empty:
                    self_cost_1_usdt = ((df['energy_consumption'] / 1000 * 24 * float(data['electricity_price'])) /
                                        (df['fiat_profitability'] / df['specific_power_for_calculation'] * df[
                                            'correct_hash_rate'])).values[0]
                    exchange = ccxt.binance()
                    tickers = ['BTC', 'ETH', 'SOL', 'TON', 'BNB', 'APT', 'SUI', 'ARB', 'OP']
                    tickers_full = ['Bitcoin', 'Ethereum', 'Solana', 'Toncoin', 'Binance Coin', 'Aptos', 'Sui',
                                    'Arbitrum',
                                    'Optimism']
                    tickers_value = []
                    for ticker in tickers:
                        tickers_value.append(exchange.fetch_ticker(f'{ticker}/USDT')['last'])
                    tickers_cheap_value = [round(ticker_value * self_cost_1_usdt, 2) for ticker_value in tickers_value]
                    currency_result = list(zip(tickers, tickers_full, tickers_value, tickers_cheap_value))
                    currency_string = '\n'.join([
                        f"<b>{ticket[0]}</b> ({ticket[1]}) - Ваша цена <b>${ticket[3]}</b> (по рынку ${ticket[2]})"
                        for ticket in currency_result])
                    await callback.message.bot.send_chat_action(
                        chat_id=callback.from_user.id,
                        action=ChatAction.TYPING)
                    await callback.message.answer(
                        text=f"Перед тем, как показать результат, необходимо убедиться, что все "
                             f"одинаково хорошо понимают эту стратегию. \nПриведу следующий "
                             f"пример:")
                    await callback.message.answer(
                        text=f"За месяц работы ваш майнер добыл криптовалюты на <b>$500</b>, затратив "
                             f"при этом электроэнергии  на ⚡ <b>$100</b>. \nПотратив на производство всего "
                             f"$100, вы за $500 продаете вашу криптовалюту на биржах и "
                             f"покупаете ту криптовалюту, которую готовы держать в долгосрок, "
                             f"потратив всего $100. \nИными словами, себестоимость одного "
                             f"добытого криптодоллара для вас составила $0.2, и абсолютно любую "
                             f"крипту вы можете приобрести в <b>5 (!!!) раз</b> дешевле "
                             f"рыночной цены. \nА теперь к вашему примеру:")
                    await callback.message.bot.send_chat_action(
                        chat_id=callback.from_user.id,
                        action=ChatAction.TYPING)
                    time.sleep(5)
                    await callback.message.bot.send_chat_action(
                        chat_id=callback.from_user.id,
                        action=ChatAction.TYPING)
                    await callback.message.answer(text=f"Майнер: <b>{asic[0][0]}</b>\n"
                                                       f"Алгоритм: <b>{asic[0][3]}</b>\n"
                                                       f"Цена за 1 кВт: <b>${data['electricity_price']}</b>\n\n"
                                                       f"Себестоимость добычи 1 USDT для {asic[0][0]} - "
                                                       f"<b>${round(self_cost_1_usdt, 2)}</b>, и вот ваш актуальный курс "
                                                       f"некоторых криптовалют:\n\n"
                                                       f"{currency_string}")
                    await callback.message.bot.send_chat_action(
                        chat_id=callback.from_user.id,
                        action=ChatAction.TYPING)
                    time.sleep(10)
                    await callback.message.bot.send_chat_action(
                        chat_id=callback.from_user.id,
                        action=ChatAction.TYPING)
                    if self_cost_1_usdt > 1:
                        await callback.message.answer(
                            text=f"Сожалеем, но такая конфигурация не является окупаемой на текущий момент :(")
                        functions.writing_logs(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), callback.from_user.id,
                                               'cheap_coins_result')
                    else:
                        await callback.message.answer(
                            text=f"P.S. Следует понимать, что данная стратегия работает <b>исключительно до того момента</b>, "
                                 f"пока вы продаете ваш намайненный {asic[0][3].split('(')[1].split(')')[0]}"
                                 f" и на деньги с продажи покупаете крипту.\nИ второй момент, который важно понимать.\n"
                                 f"<b>Больше устройств -> больше плата за электроэнергию -> больше дешевых монет для продажи</b>.\n"
                                 f"Если в вашем арсенале имеется одно устройство мощностью 100 Ватт и вы платите за электричество, скажем, "
                                 f"$5 в месяц, то нетрудно догадаться, какое количество крипты вам удастся купить "
                                 f"(<u>спойлер: очень маленькое</u>).\n"
                                 f"Поэтому предлагаю добавить еще совсем немного математики, чтобы вы поняли порядок "
                                 f"чисел:")
                        time.sleep(3)
                        await callback.message.answer(
                            text=f"Для того, чтобы в месяц этим способом покупать крипты, например, на $1000 "
                                 f"<b>(для вас это ${round(1000 * round(self_cost_1_usdt, 2), 0)})</b> вам необходимо купить асиков {asic[0][0]}"
                                 f" на сумму ${round(((1000 * round(self_cost_1_usdt, 2) / (float(data['electricity_price']) * df['energy_consumption'] * 720 / 1000)) * df['price']).values[0], 0)}.\n"
                                 f"<b>Это порядка {round((1000 * round(self_cost_1_usdt, 2) / (float(data['electricity_price']) * df['energy_consumption'] * 720 / 1000)).values[0], 1)} асиков</b>.")
                        time.sleep(3)
                    await callback.message.bot.send_chat_action(
                        chat_id=callback.from_user.id,
                        action=ChatAction.TYPING)
                    await callback.message.answer(
                        text="P.P.S. Также не следует забывать, что <b>сложность майнинга ⛏️ стремительно растет</b> по"
                             " всем популярным алгоритам, и <b>то количество крипты, которое вы могли бы "
                             "намайнить сегодня будет больше, чем завтра (в большинстве случаев).</b> "
                             "Но решать, конечно же, вам!\n\n"
                             "Рекомендую также ознакомиться <b>с дашбордом в BI-системе Yandex Datalens</b> - "
                             "там вы сможете сравнить различное оборудование между собой по окупаемости, "
                             "доходности и многим другим показателям! Вот ссылка: "
                             "<u>https://datalens.yandex/kth6k05xlg9c8</u>\n\n"
                             "Дашборд регулярно обновляется и дополняется. Также просьба оставлять ваши "
                             "пожелания, идеи и замечания по боту и дашборду по кнопке <b>«Оставить "
                             "комментарий»</b>.",
                        reply_markup=keyboards.fomo_end)
                    functions.writing_logs(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), callback.from_user.id,
                                           'cheap_coins_result')
                else:
                    await callback.message.answer(
                        text="К сожалению, на данный момент этот майнер не находится в продаже :(\n"
                             "Попробуйте, пожалуйста, выбрать другое оборудование",
                        reply_markup=keyboards.return_to_main_menu)


            finally:
                # Закрываем соединение
                db.close()
    else:
        await callback.message.answer(text='Что-то пошло не так. Попробуйте еще раз',
                                      reply_markup=keyboards.return_to_main_menu)

    await state.clear()
