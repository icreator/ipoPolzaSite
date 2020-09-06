#!/usr/bin/env python
# coding: utf8
import datetime

#from gluon import *
from gluon.cache import lazy_cache
from gluon import current


RATES_TIME = 360 # в сек жизни курса с биржи

'''
# используем кэш на неск минут
### @lazy_cache('get_7p_rate', vars=True, time_expire=300, cache_model='ram')
### НЕТ так нельзя потому что для других параметров значение будет тоже - что приведет к ошибке
def get_7p_rate1(db, db7p, good1, curr2):
    unit0 = db(good1.unit_id == db.units.id).select().first()
    #print curr2,'unit', unit,
    if unit0 and unit0.ab == curr2:
        from gluon.storage import Storage
        return Storage(bp1=1.0, sp1=1.0)
    dt_ = datetime.datetime.now() - datetime.timedelta(0, RATES_TIME)
    curr7p_1 = db7p(db7p.currs.abbrev == unit0.ab).select().first()
    curr7p_2 = db7p(db7p.currs.abbrev == curr2).select().first()
    if not curr7p_1 or not curr7p_2: return
    pair = db7p((db7p.exchg_pairs.curr1_id == curr7p_1.id)
        & (db7p.exchg_pairs.curr2_id == curr7p_2.id)
        & (db7p.exchg_pairs.on_update > dt_)
        ).select().first()
    if pair:
        # а теперь запомним курс в архиве
        u2 = db(db.units.ab == curr2).select().first()
        good2 = u2 and db(db.good0s.unit_id == u2.id).select().first()
        if good2:
            db.good_rates.insert( good1_id=good1.id, good2_id=good2.id, sell=pair.sp1, buy=pair.bp1)
    return pair
def get_7p_rate(db, db7p, good1, curr2):
    # кэш берем по нашему юниту_ид и абрев. валюты учета
    return current.cache.ram('7p_rate %s%s' % (good1.unit_id, curr2),
              lambda: get_7p_rate1(db, db7p, good1, curr2), time_expire=10)


def get_income(db, db7p, good1, curr2):
    pair = get_7p_rate(db, db7p, good1, curr2)
    if not pair: return
    rate = pair.bp1
    return rate

def get_outcome(db, db7p, good1, curr2):
    pair = get_7p_rate(db, db7p, good1, curr2)
    if not pair: return
    rate = pair.sp1
    return rate
'''

# взять курс на какую-то дату
# tab выбрать - units - goods
def get_income_on_dt(db, tab, ref1, ref2, dt):
    dt_a = datetime.timedelta(0, RATES_TIME * 5)
    dt1 = dt - dt_a
    dt2 = dt + dt_a
    rates = db((db[tab].on_create > dt1)
            & (db[tab].on_create < dt2)).select()
    if not rates:
        return
    rate = None
    for r in rates:
        if r.ref1 == ref1 and r.ref2 == ref2:
            rate = r
            break
    if rate:
        rate = rate.buy
    else:
        # иначе ищем обратный курс
        for r in rates:
            if r.ref1 == ref2 and r.ref2 == ref1:
                rate = r
                break
        if rate: rate = 1/r.sell
    return rate
