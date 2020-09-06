# coding: utf8
import urllib, time

import common
if common.not_is_local(): raise HTTP(200, T('local ERROR'))

def index(): return dict(message="test")

# проверить как работают команды БИЛЛИНГА
# http://127.0.0.1:8000/polza/cp_cmd/test/function?par1=123&par2=wert
# для проверки отвергнутых команд:
# задать параметр not_mine то незаписываем команду в нашу базу и она должна будет
# на биллинге отвергнута
# http://127.0.0.1:8000/polza/cp_cmd/test/send_many?14qZ3c9WGGBZrftMUhDTnrQMzwafYwNiLt=200RUB&1K3tcPTf2haKz6jBwa9h9kZiY8s6fNdVt4=100RUB&not_mine
#
# проверка отсылки команды и ответа на ее сервиса криптоПай - смотрим в базе что комнда принята сервисом
# http://127.0.0.1:8000/polza/cp_cmd/test/test_cmd_send?par1=12&par2=ww&par3=qwe
# параметр not_mine тут задаст что это не наша команда и она в базе данных нашей не запишется
# а на сервисе КП доложна удалиться из таблицы команд к выполнению от нас
#
# проверка исполнения - должен прийтьи ответ что комнда исполнена и результат в нашу базу записывается
# http://127.0.0.1:8000/polza/cp_cmd/test/test_cmd_resp?hash=... - задать нужный хэш
#
# проверить что сервис отвергнет посылку команды не нашу можно так:
# http://cryptopay.in/shop/api/cmd/test_cmd_send/12/test_cmd_send13?par1=12&par2=ww&par3=qweq&hash=123456
def test():
    url = settings.CP_API_URL
    #url = url + '/cmd/' + request.fuction() + '/' +  settings.CP_SHOP_ID
    fnc = request.args(0)
    url = url + '/cmd/' + fnc + '/' +  settings.CP_SHOP_ID
    vars = request.vars
    cmd_st = None
    if fnc == 'test_cmd_resp':
        # это проба ответа команды
        hash1 = request.vars.get('hash')
        cmd_st = hash1 and db(db.cmds_stack.hash1 == hash1).select().first()
        if not cmd_st:
            raise HTTP(200, 'command with that hash not found')
    else:
        # для уникальности хэш воткнем в параметры время
        while True:
            vars['time'] = time.time()
            hash1 = hash( '%s' % vars )
            rrr = db(db.cmds_stack.hash1 == hash1).select().first()
            if not rrr:
                # хэш уникальный
                break
        # а теперь удалим время из параметров
        vars.pop('time')
        vars['hash'] = hash1
    #print code
        if 'not_mine' not in vars:
            id = db.cmds.insert(name = fnc, hash1 = hash1, pars = vars )
            db.cmds_stack.insert(ref_ = id, hash1 = hash1 )
            # тут же сохраним запись иначе в ответе ее не будет в базе команд
            db.commit()
    pars = urllib.urlencode(vars)
    f = urllib.urlopen(url, pars)
    r = f.read()
    res = { 'url': url, 'status': f.getcode(), 'resp': XML(r) }
    #print res
    if cmd_st:
        res['NOTE']='see table db.cmds!'
    return BEAUTIFY(res)
