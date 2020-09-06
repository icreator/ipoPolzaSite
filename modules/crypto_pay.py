#!/usr/bin/env python
# coding: utf8
#from gluon import *
from gluon import URL
from gluon.tools import fetch
from gluon.contrib import simplejson as json

### This is module for a billing crypto-currency by cryptoPay.in service
### Это модуль для работы с криптовалютами через сервис cryptoPay.in

######################################################
### author Ermolaev Dmitry icreator@mail.ru (icreator)
######################################################
#
# constants - константы
#
# Your shop_id in cryptoPay.in service or crypto-address
# ваш номер магазина на сервисе или адрес крипто кошелька
CP_SHOP_ID = '12'

CP_URL_CHECK = 'http://cryptoPay.in/shop/api_bill/check.json/'
CP_URL_SHOW = 'http://cryptoPay.in/shop/bill/show/'
CP_URL_API = 'shop', 'api'
CP_URL_MAKE = 'shop', 'api_bill', 'make.json'
CP_URL_PARS = dict(host='cryptoPay.in', scheme='http')

# set a common parameters for all bills
# задаем общие параметры, передающиеся для всех создаваемых счетов
CP_URL_VARS = {
    # start notify my shop only from "HARD" status of the bill
    # посылать уведомления только при появлении статуса HARD и выше
    'note_on': 'HARD',
    # not convert incomed crypto-currencies to fiat money
    # не конвертировать поступившую крриптовалюту
    'not_convert': 1,
    # currency for calculate cost - RUB EUR USD
    # валютта счета в которой задана цена счета
    'curr': 'RUB',
    # 'vol': 1000, # default volume if price = 0
    # 'public':1, # if you want make public bills
    # 'email': settings.email_adm,
    }
######################################################

''' define of table with orders
описание таблицы заказов в базе данных для хранения информации

db.define_table('orders_tab',
    Field('cod', length=10, unique=True, comment=T('Произвольный номер заказа') ),
    Field('price', 'decimal(12,6)', default = 0.01, comment=T('Цена заказа')),
    Field('curr', length=3, writable=False),
    Field('cpay_bill_id', length=24,  writable=False), ## хранит номер счета и секретный ключ
    Field('cp_pars', 'json', comment='дополнительные параметры для данного заказа'),
    Field('payed', 'boolean',  writable=False),
    )
'''

# make url
# order_id - may be empty
# создает ссылку, номер заказа может быть пустой
def make_bill_url(db, order_record, pars_in={}):

    # copy common parameters into url_vars
    # копируем - чтобы не поменять значения в константе
    url_vars = CP_URL_VARS.copy()

    ### update parameters
    
    if order_record.cod:
        url_vars[ 'order'] = order_record.cod
    else:
        ### if [order] is empty - it will be generate in cryptoPay bill
        ### если номер заказа пуст - он будет автоматически сгенерирован на сервисе
        pass

    if order_record.price:
        url_vars[ 'price'] = order_record.price
    else:
        ### if [price] is empty - it will be setted to 0 in cryptoPay bill
        ### если цена не задана то счет будет с нулевой ценой
        pass

    if order_record.curr:
        url_vars[ 'curr'] = order_record.curr
    else:
        ### if [curr] is empty - it will be setted to BTC in cryptoPay bill
        ### если валюта счета не задана то она установится в BTC на сервисе
        pass

    # if other pars is exist for this ORDER then update url_vars
    if order_record.cp_pars:
        url_vars.update(order_record.cp_pars)

    # other input pars update
    # добавим дополнительные параметры
    url_vars.update(pars_in)

    # generate URL for example - http://shop/api_bill/make.json/10?[url_vars]
    # создадим ссылку для команды make
    return URL(CP_URL_MAKE, args=[CP_SHOP_ID], vars=url_vars, **CP_URL_PARS)

#
# make new bill on cryptoPay.in
# создать новый счет
#
def make_bill(db, order_record, pars_in={}):
    
    if order_record.cpay_bill_id:
        # bill already maked
        # счет уже создан
        cpay_bill_id = order_record.cpay_bill_id
    else:
        # make URL for "make bill" command
        # создать ссылку
        url = make_bill_url(db, order_record, pars_in)
        #print url

        # open url for make the bill
        # открыть ссылку
        ###  insread of:
        ###      import urllib
        ###      page = urllib.urlopen('http://www.web2py.com').read()
        ### - use fetch function - than correct open Google GAE`s pages
        resp = fetch(url)
        # print resp
        # >> resp = 2341.fg3Wdr1

        try:
            # split bill_id and secret_key
            # разделим результат по точке
            tab = resp.split('.')
            bill_id = tab[0]
            bill_id = int(bill_id)
            if len(tab)>1:
                secret_key = tab[1]
            cpay_bill_id = resp
        except:
            # something wrong
            # ошибка
            return 'ERROR: %s' % resp
    
        #print 'update order_rec with', resp
        # save response as [bill_id].[secret_key] in order record
        # сохраним ответ как номер счета и секретный ключ 
        order_record.update_record( cpay_bill_id = cpay_bill_id )
        db.commit()

    ### redirect clients to http://cryptoPay.in/shop/bill/show/[cpay_bill_id]
    ### перенаправим клиента на созданный счет
    redirect(CP_URL_SHOW + cpay_bill_id)

    
#
# check status of payments when receive a note from cryptoPay.in
# проверка статуса оплаты - когда сайт принял уведомление от сервиса
# mess - for debug purposes
#
def on_note(db, pars):
    # take order cod from pars of note
    #
    order_cod = pars['order']
    
    # find order record for that cod
    # поиск по номеру заказа
    order_record = db(db.orders_tab.cod == order_cod).select().first()
    
    if not order_record:
        # if not found - ignore note
        #
        return 'ERROR: not mine'

    # make url for "check" command
    #
    url = CP_URL_CHECK + order_record.cpay_bill_id
    
    # send "check" command and receive response
    #
    resp = fetch(url)
    
    # decode response as JSON
    #
    resp = json.loads( resp )
    #print resp
    
    # examinate this response
    #
    mess = ''
    if resp['price'] == order_record.price and resp['order'] == order_record.cod and resp['curr'] == order_record.curr:
        # parameters of the bill is true
        # параметры ответа корректные
        mess += ' parameters of the bill is true<br>'
        if resp['payed'] == order_record.price:
            # bill is payed, check status!
            # счет полностью оплачен, проверим статус оплаты
            mess += ' bill is payed, check status...<br>'
            if resp['status'] in ['HARD', 'CLOSED']:
                # status OK, update my order
                # статус подходящий, учтем оплату заказа
                order_record.update_record( payed = True )
                db.commit()
                mess += ' PAYED! status:%s<br>' % resp['status']
                return mess
    mess += ' NOT PAYED, response: %s' % resp
    return mess
