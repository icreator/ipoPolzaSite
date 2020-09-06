# -*- coding: utf-8 -*-

routes_in = (
    # очень много запросов идут на эту иконку почемуто. ответ сервера 400(код ошибки) 50(миллисек?)
    (r'/favicon.ico', r'/polza2/static/images/favicon.png'),
    (r'/favicon.png', r'/polza2/static/images/favicon.png'),
    (r'/robots.txt', r'/polza2/static/robots.txt'),
    (r'/', r'/polza2/default/index/'),
    (r'/index/$anything', r'/polza2/default/index/$anything'),
    (r'/index', r'/polza2/default/index'),
    (r'/polza2/index', r'/polza2/default/index'),
    (r'/polza2', r'/polza2/default/index'),
    (r'/$anything', r'/polza2/$anything'),
    )

routes_out = [
    #(x, y) for (y, x) in routes_in
    (r'/polza2/static/images/favicon.png', r'/favicon.ico'),
    (r'/polza2/static/images/favicon.png', r'/favicon.png'),
    (r'/polza2/static/robots.txt', r'/robots.txt'),
    (r'/polza2/$anything', r'/$anything')
    ]
#routes_out.insert(0, )
#routes_out.insert(0, (r'/polza2', r'/'))
