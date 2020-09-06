#!/usr/bin/env python
# coding: utf8
from gluon import current
from gluon.storage import Storage

from decimal import Decimal

import common, rates

# запомним курс обмена вещи пайщика на вещь учета фонда
def update_goods_rates(db, tr): #tr, good_out_id = None):
    if tr.amo != tr.amo_out:
        # запомним курс обмена
        good_out_id = tr.good_out_id or db.fonds[tr.fond_id].good_id
        rate = tr.amo_out/tr.amo
        rec = db( (db.good_rates.ref1 == tr.good_id )
                 & (db.good_rates.ref2 == good_out_id )
                 & (db.good_rates.on_create == tr.on_create )
                 ).select().first()
        if rec:
            rec.update_record( buy = rate, sell = rate )
        else:
            db.good_rates.insert(ref1 = tr.good_id, ref2 = good_out_id,
                  buy = rate, sell = rate, on_create = tr.on_create)


def resum_memb(db, member, fond, trans, amo, amo_out):
    if fond.stats: return

    if fond.good_id:
        # если у фонда задана еденица учета то и у пайщика вещи в нее перекувырнем
        # найдем вещь для этой единицы с курсом = 1
        memb_good_id = fond.good_id
        amo_memb_good = amo_out
    else:
        memb_good_id = trans.good_id
        amo_memb_good = amo


    # пересчитаем фонды члена
    memb_good = db((db.memb_goods.good_id == memb_good_id)
                     & (db.memb_goods.memb_id == trans.memb_id)).select().first()
    if not memb_good:
        #print 'memb_good_id', memb_good_id, 'trans.memb_id',trans.memb_id
        db.memb_goods.insert(good_id = memb_good_id, memb_id = trans.memb_id, amo = amo_memb_good )
    else:
        memb_good.update_record( amo = memb_good.amo + amo_memb_good )

    if fond.unret:
        # пай не в возвращаемый - его отдельно считаем везде
        member.update_record ( bal_u = member.bal_u + amo_out )
    else:
        member.update_record ( bal = member.bal + amo_out )

    amo_memb_calc = amo_memb_good
    # учтем коэфф фондов для расччетного баланса
    koef = fond.koef
    if koef == 0:
        # за этот фонд не неасчитываем
        return
    elif koef != 1:
        # увеличим начисление пайщику по коэфф
        amo_memb_calc = amo_memb_calc * koef
    member.update_record ( bal_c = member.bal_c + amo_memb_calc )


# расчет для фонда, его вещей и программы
def resum_fond(db, fond, trans, amo, amo_out):
    # теперь баланс фонда изменим
    fond.update_record( bal = fond.bal + amo_out )
    fond_good = db((db.fond_goods.fond_id==fond.id)
        & (db.fond_goods.good_id==trans.good_id)).select().first()
    if fond_good: fond_good.update_record( amo = fond_good.amo + amo, amo_out = fond_good.amo_out + amo_out )
    else: db.fond_goods.insert(fond_id=fond.id, good_id=trans.good_id, amo = amo, amo_out = amo_out )

    # баланс программы - с учетом возвращаемое нет
    prog = db.progs[fond.prog_id]
    if fond.unret:
        # пай не в возвращаемый - его отдельно считаем везде
        prog.update_record ( bal_u = prog.bal_u + amo_out )
    else:
        prog.update_record ( bal = prog.bal + amo_out )

def make_inv_bonus(db, memb_inv, good, amo,
           p_to_fond, p_from_fond, trans, lvl_div, lvl):
    amo_out = settings = txid = info = storage_id = None
    # если это ассоциаттивный то уполовиним подарок
    bonus = memb_inv.minor and amo * Decimal(0.5) or amo
    #print 'make_inv_bonus', bonus, lvl
    make_trans(db, settings, memb_inv, storage_id, good, bonus, amo_out,
           p_to_fond, txid, info, p_from_fond,
           # эта транзакция появилась по расчету от этой:
           trans)
    lvl -= 1
    if lvl > 0:
        # продолжим рекурсию
        amo = amo / Decimal(lvl_div)
        memb_inv = db.members[ memb_inv.inv_id ]
        if memb_inv:
            # если есть у него свой главный партнер
            make_inv_bonus(db, memb_inv, good, amo,
                   p_to_fond, p_from_fond, trans, lvl_div, lvl)
    return

# тут расчеты всех суммирующих величин при появлении транзакции
# negotiate - если надо наоборот транзакцию вычесть
def resum(db, trans, negotiate=None):
    log_ = False
    if not trans: return

    #print trans
    amo = trans.amo
    # учтем курс обмена данного имущества
    amo_out = trans.amo_out # поидее криптопай его сам выдает в каждой транзакции - его и берем там


    if negotiate:
        # удалим вляиние этой транзакции - для пересчетов
        amo = -amo
        amo_out = -(amo_out or 0)


    good = db.goods[trans.good_id]
    fond = db.fonds[ trans.fond_id ]


    # теперь тоже самое для фонда откуда снялось
    # тут надо учеть если фонд для учета то не менять вещи у пайщика
    from_fond = db.fonds[ trans.from_fond_id ]
    if from_fond.stats:
        # значит извне приход-расход
        # если в общество вошло что-то то кол-во поменяем
        good.update_record(amo = good.amo + amo, amo_out = good.amo_out + amo_out)
        if log_:
            print 'good.update_record(amo = good.amo + amo, amo_out = good.amo_out + amo_out)'

    if from_fond.id != fond.id:
        resum_fond(db, fond, trans, amo, amo_out)
        resum_fond(db, from_fond, trans, -amo, -amo_out)
        if log_:
            print 'resum_fond'

    # если член один и тот же и фонд один (или не вычисляемый) то только у него сделать изменение
    memb = db.members[ trans.memb_id ]
    resum_memb(db, memb, fond, trans, amo, amo_out)

    # теперь все расчетные транзакции создадим
    for calc in db(db.fond_calcs.fond_id == fond.id).select():
        if log_:
            print 'fond_calc:', calc
        # найдена авто-расчетная запись
        if calc.self_:
            pass
        else:
            # это расчет для партнеров
            if memb.inv_id:
                inviter = db.members[memb.inv_id]
                #print inviter
                if calc.perc:
                    # берем процент от выхода
                    amo_bonus = amo * calc.perc * Decimal(0.01)
                    if calc.vol and calc.vol < amo_bonus:
                        # Проверяем на максимальное значение
                        amo_bonus = calc.vol
                else:
                    amo_bonus = calc.vol
                ### amo_out - обнулим чтобы посчиталось по еденице фонда выхода
                amo_out = settings = info = storage_id = None
                amo = amo_bonus
                memb_inv = inviter
                p_from_fond = db.fonds[calc.from_fond_id]
                p_to_fond = db.fonds[calc.to_fond_id]
                #txid = trans.txid
                #print trans
                make_inv_bonus(db, memb_inv, good, amo, p_to_fond, p_from_fond,
                           # эта транзакция появилась по расчету от этой:
                           trans, calc.lvl_div, calc.lvl_max)
    return True

########
# ОБМЕН между фондами скорее всего придется сделатиьт через - ввод-вывод из фонда с from_fond = счет учета
# тоесть по умолчанию - но тогда будет лишняя запись добавляться
# а обмен между членами...
#
###############
# учетные фонды всегда по умолчанию ставим а кол-во:
## + при внесении в общество
## - при выдаче из общества
#################
# если задан пайшик у котрого берем то кол-во вещей в обществе не меняем
##############
# создать транзакцию
#  с какого счета-реквизита-адреса получены и на какой ушли
# тут на входе должен быть txid+vout: = %s-%03d
####### main_trans=None - если трназакция вычисляемая то гланая транзакция из-за которой вычисления сделаны
## amo_out = None -значит считаем по нпшему курсу по вещам в принимающем фонде
## а если уже задано значит это уже конвертация с cryptoPay.in дана
def make_trans(db, settings, membr, storage_id, good, amo, amo_out, fond, txid, info, from_fond = None, main_trans=None, on_create = None):
    if not from_fond:
        # если не задан фонд откуда то берем по умолчанию учетные счета
        from_fond = db.fonds[fond.unret and settings.FOND_CALC_UNRET or settings.FOND_CALC_RET]

    if main_trans:
        # если это вычисляемая то и дату от главной берем
        on_create = main_trans.on_create
    else: on_create = on_create or current.request.now
    #print '\n',on_create

    good_out_id = None
    if not amo_out and amo !=0: # тут не равно нулю так как АМО с минусом бывает!
        ## amo_out = None -значит считаем по нпшему курсу по вещам в принимающем фонде
        ## а если уже задано значит это уже конвертация с cryptoPay.in дана
        good_out_id = fond.good_id
        if not good_out_id:
            # фонд без заданной единицы - без конвертации значит
            amo_out = amo
        else:
            good_out_id = db.goods[fond.good_id].id
            if good_out_id == good.id:
                # или единицы фонда и входа совпали
                amo_out = amo
            else:
                # тут надо посчитать курс
                # курс криптоПай не выдал
                # если ее нет то все хранится в том имуществе в котром пришли транзакции
                # иначе все транзакции пайщика конвертируются в валюту фонда
                # не забыть НА ДАТУ транзакции курс взять
                rate = rates.get_income_on_dt(db, 'good_rates', good.id, good_out_id, on_create )
                print on_create, rate
                if not rate:
                    #db.rollback()
                    common.log(db, 'rates not found for trans %s: %s -> %s' % (on_create, good.name, good_out_id))
                    #db.commit()
                    #err()
                    amo_out = None
                else:
                    # пересчитаем тепеь для общих цифирь сумму в рублях
                    amo_out = amo * Decimal( rate )
                    #print amo,'x', rate, ' ->', amo_out

    print 'amo, amo_out', amo, amo_out
    pars = dict(storage_id = storage_id,
         from_fond_id = from_fond.id, fond_id = fond.id,
         good_id = good.id,
         memb_id = membr.id,
         amo = amo, amo_out = amo_out,
         txid = txid, info = info, on_create = on_create
         )
    if main_trans:
        # если это вычисляемая
        id = db.trans_calc.insert(ref_ = main_trans.id, **pars)
        trans = db.trans_calc[id]
    else:
        # это главная транзакция
        id = db.trans.insert(**pars)
        pars['good_out_id'] = good_out_id
        update_goods_rates(db, Storage(**pars))
        trans = db.trans[id]
    ## тут у нас 2 разных таблицы на выходе
    ## - поэому возвращаем запись а не ИД
    resum(db, trans)
    return trans

# удаляет все транзакции и их суммы что пришли с криптоПай - чтобы потом заново их учесть
# заново пересчитать все приходы крипты по данному счету-заказу
# тоесть обнулить все сумы по этому фонду и с криптоПай все закачать
def recalc_x_order(db, cod, fond=None):
    fond = fond or db(db.fonds.cod == cod).select().first()
    if not fond:
        return 'error - fond not found'

    negotiate = True
    order = db(db.orders.fond_id == fond.id).select().first()
    if order:
        # по всем транзакция от крито-Пай для этого зазка-фонда
        for o_tx in db(order.id == db.order_txids.order_id).select():
            txid = o_tx.txid
            #print txid
            tab = db(db.trans.txid.like(txid + '%')).select()
            for tr in tab:
                # по всем входм для данной транзакции
                print '...',tr.txid
                resum(db, tr, negotiate)
            # теперь их удалим
            for tr in tab:
                del db.trans[tr.id]

        del db.orders[order.id]
    return
# удаляет все транзакции и их суммы что пришли с криптоПай - чтобы потом заново их учесть
def recalc_x_orders(db):
    for f in db(db.fonds).select():
        recalc_x_order(db, f.cod, f)

def clear_ALL(db):
    return 'хера вам - нельзя юзать а то все потрет'
    for r in db(db.members).select():
        r.update_record(bal=0, bal_u=0, bal_c=0)
    for r in db(db.progs).select():
        r.update_record(bal=0, bal_u=0)
    for r in db(db.fonds).select():
        r.update_record(bal=0)
    for r in db(db.goods).select():
        r.update_record(amo=0, amo_out=0)
    db.trans.truncate()
    db.orders.truncate()
    db.memb_goods.truncate()
    db.fond_goods.truncate()

# не удаляет транзакции основные - просто пересчет всего
def resum_ALL(db):
    for r in db(db.members).select():
        r.update_record(bal=0, bal_u=0, bal_c=0)
    for r in db(db.progs).select():
        r.update_record(bal=0, bal_u=0)
    for r in db(db.fonds).select():
        r.update_record(bal=0)
    for r in db(db.goods).select():
        r.update_record(amo=0, amo_out=0)
    ####
    #### оставим все5 транзакции и ордера от криптопай
    db.memb_goods.truncate()
    db.fond_goods.truncate()
    db.fond_memb_goods.truncate()
    # удалим все расчетные транзакции
    #db(db.trans.calced==True).delete()
    db.trans_calc.truncate()

    # а теперь пересчет по оставшимся транзакциям
    for tr in db(db.trans).select():
        update_goods_rates(db, Storage(tr))
        resum(db, tr)
