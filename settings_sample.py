IDENTITY = {
    'teddy': {
        'nickname': 'teddy',
        'realname': 'teddy',
        'username': 'teddy',
        'nickserv_pw': None
    },
}

NETWORKS = {
    'yourircserver': {
        'host': 'irc.example.com',
        'port': 6697,
        'ssl': True,
        'identity': IDENTITY['teddy'],
        'autojoin': (
            ('#channel1', 'key1'),
            ('#channel2', 'key2'),
	)
    }
}

MYSQL_USER = 'teddy'
MYSQL_HOST = 'localhost'
MYSQL_PASSWORD = 'somepass'
MYSQL_DB = 'somedb'
WOOT_KEY = 'somekey'
REDIS_HOST = ''
