DEVELOP = True
#DEVELOP = False

from gluon.storage import Storage
settings = Storage()

settings.migrate = True
settings.email_adm = 'adm@ipo-polza.ru'
settings.inn = '7722843161'
settings.name = 'ИПО "Польза"'
settings.ogrn = '1147746520866'
settings.y_name = 'Инновационное потребительское общество "Польза"'
settings.title = None #T('Польза для каждого') #'Проводи жизнь с "Пользой"!'
settings.subtitle = None # 'Свободные платежи с пользой для себя и близких...'
settings.author = 'ИПО "Польза"'
settings.author_email = 'adm@ipo-polza.ru'
settings.keywords = 'криптовалюта, биткоин, лайткоин, обмен, биллинг, мерчант, заработать'
settings.description = 'Общество для работы с крипто-имуществом'
settings.layout_theme = 'Default'
settings.database_uri = 'sqlite://storage.sqlite'
settings.security_key = 'a77ae3c7-e85c-42ef-8369-204aa1b03a96'
settings.email_server = 'localhost'
settings.email_sender = 'adm@ipo-polza.ru'
settings.email_login = ''
settings.login_method = 'local'
settings.login_config = ''
settings.plugins = []

settings.CP_IP = '12.12.12.12'
settings.CP_SHOP_ID = '12'
#settings.CP_URL = 'http://cryptoPay.in/shop/bill/show/'
settings.CP_API_BILL_URL = 'http://cryptoPay.in/shop/api_bill/'
settings.CP_API_CMD_URL = 'http://cryptoPay.in/shop/api_cmd/'
settings.CP_URL_BILL_STATS = 'http://cryptoPay.in/shop/api_bill/info/'

settings.CP_URL_MAKE = 'shop', 'api_bill/make.json', settings.CP_SHOP_ID
settings.CP_URL_SHOW = 'http://cryptoPay.in/shop/bill/show/'
# все наши счета публичные
settings.CP_URL_VARS = {
    'public':1, # все сета открытые публике
    'keep': 1, # все поступления оставлять на сервисе до команды
    'note_on': 'HARD', # зачислять при статуче ХАРД
    'not_convert':1, # по умолчанию не конвертировать - если не указано локально другое значение
    'curr':'RUB', # по умолчанию валюта счета - РУБЛЬ
    'vol':1000, # значение по умолчанию в счете
    'email':settings.email_adm, # наша почта
    }
settings.CP_URL_PARS = dict(host='cryptoPay.in', scheme='http')
## vars = settings.CP_URL_VARS.copy()
## vars['order'] = fond.cod
## url = URL(*settings.CP_URL_PATH, vars=vars, **settings.CP_URL_PARS)

settings.UNKNOWN_MEMBER_ID = 7
settings.MAIN_UNIT = 'RUB' # для пересчетов в главную еденицу учета

## ID фондов для учета и расчетов
# фонд поощрений за приглажения по партнерсой программе
settings.PARTNERS_FOND_INV_ID = 9
settings.FOND_CALC_INV = 10
settings.FOND_CALC_RET = 11
settings.FOND_CALC_UNRET = 12
settings.FOND_NEDELIM = 13
