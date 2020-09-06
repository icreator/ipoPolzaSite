#!/usr/bin/env python
# coding: utf8
from gluon import *

# взять юнит для вычисляемого поощрения если этот фонд исчисляет начисления
def get_bonus_good(db, good, fond_calc, f_s):
    good_s = good or f_s.good_id and db.goods[f_s.good_id]
    if not good_s:
        f_fr = db.fonds[fond_calc.from_fond_id]
        good_s = f_fr.good_id and db.goods[f_fr.good_id]
    return good_s
# взять юнит для вычисляемого поощрения если этот фонд получает начисления
def get_bonus_good_to(db, good, fond_calc, f_s):
    good_s = f_s.good_id and db.goods[f_s.good_id] or good
    if not good_s:
        f_fr = db.fonds[fond_calc.from_fond_id]
        good_s = f_fr.good_id and db.goods[f_fr.good_id]
    return good_s

def make_fonds_CP_url(pars):
    uu = URL( 'shop', 'bill', 'show', args=[settings.CP_SHOP_ID],
          vars={ 'note_on': 'HARD', 'not_convert':1, 'curr':'RUB', 'vol':1000, 'email':settings.email_adm},
          host='cryptoPay.in', scheme='http')
    return '%s&order=' % settings.CP_URL_ORDER_PARS

def log_err(db, mess):
    db.rollback()
    db.logs.insert( ccc = current.request.controller, fff = current.request.function, messages123456 = '%s' % mess)
    db.commit()
    err_err()
def log(db, mess):
    db.logs.insert( ccc = current.request.controller, fff = current.request.function, messages123456 = '%s' % mess)

def membr_fio(r):
    if r.y_name:
        fio = r.y_name + ' %s' % r.inn
    else:
        dt = r.b_date and r.b_date.__format__('%m-%d') or ''
        fio = (r.l_name or '?') + ' ' + (r.f_name or '') + ' ' + (r.m_name or '') + ' %s' % dt
    return fio
def membr_uri(r):
    return A(membr_fio(r), _href=URL('transs','index/members/view/members', args=[r.id]))

### vvv=True - включает секртную сессию и выдает страницу ошибки
def not_is_local(): ##vvv=None):
    http_host = current.request.env.http_host.split(':')[0]
    remote_addr = current.request.env.remote_addr
    try:
        hosts = (http_host, socket.gethostname(),
                 socket.gethostbyname(http_host),
                 '::1', '127.0.0.1', '::ffff:127.0.0.1')
    except:
        hosts = (http_host, )

    #if vvv and (request.env.http_x_forwarded_for or request.is_https):
    #    session.secure()

    if (remote_addr not in hosts) and (remote_addr != "127.0.0.1"):
        #and request.function != 'manage':
        #if vvv: raise HTTP(200, T('ERROR'))
        return True

from gluon.tools import Mail
# шлем рассылку в скрытых копиях
# тут можно страницу HTML создать по шабллону (add_shop_mail.html) и записи
def send_email_to_descr(to_addrs, subj, mess=None, context=None, templ=None, response = None, settings = None):
    mail = Mail()
    mail.settings.server = 'smtp.sendgrid.net'
    mail.settings.sender = settings.email_sender # 'adm@ipo-polza.ru'
    mail.settings.login = 'azure_90ebc94457b0e6a1c4c920993753f5a6@azure.com:7xirv1rc'
    if not mess and context and templ:
        context['render_mail'] = True
        mess = response.render(templ, context)
    #print mess
    #to_addrs = ['kentrt@yandex.ru','icreator@mail.ru']
    print 'SEND EMAIL TO', to_addrs, '\n',subj
    mail.send(to=to_addrs,
           # видимые копии:
           #cc=len(to_addrs)>1 and to_addrs[1:] or None, - они в спам закатываются (
           # скрытые копии - их в спам записывабт почтовики обычно:
           #bcc=len(to_addrs)>1 and to_addrs[1:] or None,
           subject=subj,
           message=mess)
