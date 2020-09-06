# coding: utf8
import urllib
#import urllib2

#
# обработка ответов по командам на сервис криптоПай
# если у команды еще нет статуса - значит обработка отсылки команды - сменим статус на SND
# если у команды статус = SND - значит команда обработана - надо получить ответ
def cmd_proc(hash1):
    import common
    # это ответ на команду - тут должен быть наш ХЭШ
    cmd_stack_r = db(db.cmds_stack.hash1 == hash1)
    cmd_stack = cmd_stack_r.select().first()
    if not cmd_stack:
        # если нет у нас такой команды с таким хэшем - то выдадим ответ пустой
        raise HTTP(200, '-')

    cmd = db.cmds[ cmd_stack.ref_ ]
    if not cmd.status:
        # если у команды еще нет статуса - значит это ответ
        # что команда на криптоПай принята - сменим статус на SND
        cmd.update_record( status = 'SND')
    elif cmd.status == 'SND':
        # если у команды статус = SND
        # - значит команда уже обработана - надо получить ответ
        url = settings.CP_API_URL + '/cmd_res/%s?cmd=%s' % ( settings.CP_SHOP_ID, cmd.hash1)
        #print url
        try:
            f = urllib.urlopen(url)
            r = f.read()
            #res = { 'url': url, 'status': f.getcode(), 'resp': XML(r) }
            #print f.getcode(), r
        except Exception as e:
            # там ошибка какая-то
            log('%s - %s' % (url, e))
            raise HTTP(501, '%s %s' % (hash1, e))
        if f.getcode() < 500:
            cmd.update_record( status = 'RES', res = r, res_on = request.now)
            cmd_stack_r.delete()

    # выход из обработки
    raise HTTP(444, '%s' % hash1)

###########################################################
# ловим уведомление от cryproPay
# тут досточно только номер заказа указать
# http://127.0.0.1:8000/polza/cp/resp?order=main&bill=12
# http://ipo-polza.ru/cp/resp?bill=378
###########################################################
# еще отвечает на уведомления о поступивших командах - успех - возвращаем КОД = 444 и в теле КОД хэша
def resp():
    bill = request.vars.get('bill')
    cmd_hash = request.vars.get('cmd')
    if cmd_hash :
        cmd_proc( cmd_hash )
        return 'error if here' # - сюда не должно прити - там raise HTTP

    # нельзя тут брать - вдруг кто-то обманул и подставил не тот bill = request.vars.get('bill')
    order = db(db.orders.bill == bill ).select().first()
    mess = bill
    if not order:
        return 'order and fond not mine'
    import cpay_lib
    mess = mess + '<br> info: %s' % cpay_lib.get_info_last(settings, db, order)
    return mess
