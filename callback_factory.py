from aiogram.filters.callback_data import CallbackData


class AsicsList(CallbackData, prefix='asics'):
    item: str


class CheapAsicsList(CallbackData, prefix='asic'):
    item: str

