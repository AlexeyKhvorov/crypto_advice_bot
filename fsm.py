from aiogram.fsm.state import State, StatesGroup


class GetUserData(StatesGroup):
    insert_budget = State()
    insert_available_power = State()
    insert_electro_price = State()
    insert_max_electricity_pay = State()
    insert_purpose = State()
    insert_coin = State()
    insert_380v_for_btc = State()
    insert_hydro_for_btc = State()
    final_stage = State()


class Fomo(StatesGroup):
    insert_asic_name = State()
    insert_date = State()
    insert_electricity = State()
    get_result = State()


class CheapCoins(StatesGroup):
    insert_asic_name = State()
    insert_electricity = State()
    get_result = State()


class Feedback(StatesGroup):
    insert_feedback = State()

