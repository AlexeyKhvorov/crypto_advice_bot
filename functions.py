from datetime import datetime

import pymysql
import os
import shutil
import config


def specific_power_for_calculation(data):
    if data['coin'] == 'SHA-256 (BTC)':
        return 100
    elif data['coin'] == 'Ethash (ETC)':
        return 100
    elif data['coin'] == 'Scrypt (LTC+DOGE)':
        return 100
    elif data['coin'] == 'X11 (DASH)':
        return 100
    elif data['coin'] == 'KHeavyHash (KAS)':
        return 0.0001
    elif data['coin'] == 'Eaglesong (CKB)':
        return 0.001
    elif data['coin'] == 'Blake2s (KDA)':
        return 100
    elif data['coin'] == 'Blake3 (ALPH)':
        return 100
    elif data['coin'] == 'Blake2B+SHA3 (HNS)':
        return 1
    elif data['coin'] == 'Equihash (ZEC)':
        return 100


def coin_risks(data):
    if data['coin'] == 'SHA-256 (BTC)':
        return 1
    elif data['coin'] == 'Ethash (ETC)':
        return 1
    elif data['coin'] == 'Scrypt (LTC+DOGE)':
        return 1
    elif data['coin'] == 'X11 (DASH)':
        return 1
    elif data['coin'] == 'KHeavyHash (KAS)':
        return 2
    elif data['coin'] == 'Eaglesong (CKB)':
        return 2
    elif data['coin'] == 'Blake2s (KDA)':
        return 2
    elif data['coin'] == 'Blake3 (ALPH)':
        return 2
    elif data['coin'] == 'Blake2B+SHA3 (HNS)':
        return 2
    elif data['coin'] == 'Equihash (ZEC)':
        return 1


def v380(data):
    if data['coin'] == 'SHA-256 (BTC)' and (data['cool_type'] == 'Водяное' or 'T21'.lower() in data['name'].lower()):
        return 1
    else:
        return 0


async def asic_list(asic):
    db = pymysql.connect(host=config.host, database=config.database,
                         user=config.user, password=config.password)
    try:
        with db.cursor() as cursor:
            sql = "SELECT * FROM miner_list_view WHERE REPLACE (LOWER (name), ' ', '') LIKE REPLACE (LOWER (%s), ' ', '')"
            cursor.execute(sql, ('%' + asic + '%',))
            result = cursor.fetchall()
            return result

    finally:
        # Закрываем соединение
        db.close()


async def asic_list_accuracy(asic):
    db = pymysql.connect(host=config.host, database=config.database,
                         user=config.user, password=config.password)
    try:
        with db.cursor() as cursor:
            sql = "SELECT * FROM miner_list_view WHERE name = %s"
            cursor.execute(sql, (asic,))
            result = cursor.fetchall()
            return result

    finally:
        # Закрываем соединение
        db.close()


async def min_date_in_db(asic):
    db = pymysql.connect(host=config.host, database=config.database,
                         user=config.user, password=config.password)
    try:
        with db.cursor() as cursor:
            sql = "SELECT MIN(date) FROM asic_general_info_47_view WHERE name = %s"
            cursor.execute(sql, (asic,))
            result = cursor.fetchone()
            return result

    finally:
        # Закрываем соединение
        db.close()


async def all_date_in_db(asic):
    db = pymysql.connect(host=config.host, database=config.database,
                         user=config.user, password=config.password)
    try:
        with db.cursor() as cursor:
            sql = "SELECT date FROM asic_general_info_47_view WHERE name = %s"
            cursor.execute(sql, (asic,))
            result = cursor.fetchall()
            return result

    finally:
        # Закрываем соединение
        db.close()


async def date_check(date):
    try:
        datetime.strptime(date, '%Y-%m-%d')
        return True
    except ValueError:
        return False


async def get_last_crypto_course(currency, date):
    db = pymysql.connect(host=config.host, database=config.database,
                         user=config.user, password=config.password)
    try:
        with db.cursor() as cursor:
            sql = "SELECT value FROM currency_exchange WHERE currency = %s AND date = %s"
            cursor.execute(sql, (currency, date))
            result = cursor.fetchone()
            return result

    finally:
        # Закрываем соединение
        db.close()


async def get_last_crypto_course_ltc(date):
    db = pymysql.connect(host=config.host, database=config.database,
                         user=config.user, password=config.password)
    try:
        with db.cursor() as cursor:
            sql = "SELECT value FROM currency_exchange WHERE currency = 'LTC' AND date = %s"
            cursor.execute(sql, (date,))
            result = cursor.fetchone()
            return result

    finally:
        # Закрываем соединение
        db.close()


async def get_last_crypto_course_doge(date):
    db = pymysql.connect(host=config.host, database=config.database,
                         user=config.user, password=config.password)
    try:
        with db.cursor() as cursor:
            sql = "SELECT value FROM currency_exchange WHERE currency = 'DOGE' AND date = %s"
            cursor.execute(sql, (date,))
            result = cursor.fetchone()
            return result

    finally:
        # Закрываем соединение
        db.close()


async def max_date_in_currency_exchange():
    db = pymysql.connect(host=config.host, database=config.database,
                         user=config.user, password=config.password)
    try:
        with db.cursor() as cursor:
            sql = "SELECT MAX(date) FROM currency_exchange"
            cursor.execute(sql)
            result = cursor.fetchone()
            return result

    finally:
        # Закрываем соединение
        db.close()


def cleaning_files():
    # Папка, которую нужно очистить
    folder_path = os.path.join(os.getcwd(), 'files')

    # Проверяем, существует ли папка
    if os.path.exists(folder_path):
        # Удаляем все файлы и подпапки в папке
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)  # Удаляем файл
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # Удаляем папку
            except Exception as e:
                print(f'Не удалось удалить {file_path}. Причина: {e}')
    else:
        print(f'Папка {folder_path} не найдена.')
