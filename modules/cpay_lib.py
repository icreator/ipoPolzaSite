#!/usr/bin/env python
# coding: utf8
from gluon import *
T = current.T
import urllib, urllib2, json

import common, fonds
#print current

# закатаем транзакцию в базу
# тут учетный счет - по типу фонда - возвратный и невозвратный
def trans_insert(settings, db, good, order, tx):
    # {u'status': u'HARD', u'vout': 0, u'rate_order_id': None, u'amo_out': 4.81655508, u'created_on': u'2014-05-29 13:58:44', u'txid': u'4467ae3dd2bc939393796f8aa7ef451e9d4dbbfb39eced0085e23e133362b9ff', u'amount': 0.01262016, u'amo_ret': 0.0}
    amo = tx['amount'] - tx['amo_ret']
    # надо по адресам найти пользователя нашего
    member_id = None
    for addr in tx['addrs']:
        #print addr
        xacc = db(db.memb_x_accs.addr == addr).select().first()
        if xacc:
            member_id = xacc.member_id
            break
    if not member_id:
        # нет пайщика - закатаем
        member_id = settings.UNKNOWN_MEMBER_ID
    #  с какого счета-реквизита-адреса получены и на какой ушли
    membr = db.members[ member_id ]
    fond = db.fonds[ order.fond_id ]
    info = T('оплата крипто-имуществом через cryptoPay.in')
    txid = '%s-%03d' % (tx['txid'], tx['vout'])
    from_fond = main_trans = None
    created_on = tx['created_on']
    storage_id = None # по имени имуществва понятно какое хранилиище
    fonds.make_trans(db, settings, membr, storage_id, good, amo, tx['amo_out'],
                 fond, txid, info, from_fond, main_trans, created_on)
    #print order
    db.order_txids.insert( order_id = order.id, txid = tx['txid'])


def get_info_last(settings, db, order):

    pars = { 'get_addrs':1 }
    uu = 'http://cryptopay.in/shop/api_bill/info.json'
    if order.bill:
        # если номер счета уже мы знаем то по нему делаем запросы
        uu = uu + '/%s' % order.bill
    else:
        # если номер счета еще не получали то по нашему заказу делаем запрос
        uu = uu + '/%s' % settings.CP_SHOP_ID
        pars['order'] = order.name

    last_dt = '%s' % (order.last_dt or '') # обязательно пустую строчку вместо None
    if last_dt:
        pars['from'] = order.last_dt
    pars = urllib.urlencode(pars)
    rq = urllib2.Request(uu, pars)
    #print uu, 'pars:', pars
    res_ = '%s?%s<br>' % (uu, pars)
    #rq.add_header('Authorization', 'Bearer ' + token)
    try:
        f = urllib2.urlopen(rq)
        #html = f.read()
        r = json.load(f)
    except Exception as e:
        print 'xml ', rq, e
        common.log(db, 'xml %s', e)
        return
    #print r
    if r['shop'] != int(settings.CP_SHOP_ID):
        common.log(db, 'shop not mine')
        return 'shop not mine'
    if not order.bill:
        # если номер счета еще не известне - запомним
        order.update_record( bill = r['bill'])

    res_ = res_ + '<br>%s<br>' % r
    amo = order.amo_hard
    amo_new = r['HARD'] + r['TRUE']
    #print amo, '->', amo_new
    # все транзакции выцепим
    res_ = res_ + '<br>INSERT:<br>'

    for (curr_ab, tab) in r[u'payments'].iteritems():
        good = db(db.goods.ab == curr_ab).select().first()
        if not good:
            mess = 'crypto-currency [%s] not found - for CP_RESPONSE' % curr_ab
            res_ = res_ + '<br>%s<br>' % mess
            common.log_err(db,mess)
        for tx in tab:
            # {u'status': u'HARD', u'vout': 0, u'rate_order_id': None, u'amo_out': 4.81655508, u'created_on': u'2014-05-29 13:58:44', u'txid': u'4467ae3dd2bc939393796f8aa7ef451e9d4dbbfb39eced0085e23e133362b9ff', u'amount': 0.01262016, u'amo_ret': 0.0}
            if tx['status'] not in [u'HARD', u'TRUE']: continue
            # тут время создания транхакции может быть раннее но она не подтверждена
            # а быстрая - позже создана и подтверждена уже
            # поэтому не по времени создания а по времени подтверждения
            tx_dt = tx['status_dt']
            last_dt = last_dt or tx_dt
            if last_dt < tx_dt:
                last_dt = tx_dt
            #print last_dt
            # если для такого  счета уже такая транзакция обрабатывалась то пропустим
            rrr = db((db.order_txids.txid == tx['txid'])
                     & (db.order_txids.order_id == order.id)).select().first()
            if rrr:
                #print 'order_txids.txid',rrr
                # такая транзакция уже обработана
                continue
            #print 'INSERT:', tx
            trans_insert(settings, db, good, order, tx)
            res_ = res_ + '<br>%s<br>' % tx
    order.update_record( amo_hard = amo_new, last_dt = last_dt)
    return res_
