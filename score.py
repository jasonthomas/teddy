import MySQLdb


class Score:
    def __init__(self, host, user, passwd, db):
        self.db = db
        self.host = host
        self.passwd = passwd
        self.user = user

    def query_mysql(self, query):
        db = MySQLdb.connect(host=self.host, user=self.user,
                             passwd=self.passwd, db=self.db)
        cur = db.cursor()
        try:
            cur.execute(query)
            db.commit()
            if int(cur.rowcount) == 1:
                return cur.fetchone()[0]
            else:
                return cur.fetchall()
        except:
            db.rollback()

    def create_user(self, user):
        find_user = """SELECT user from score where user = '%s'""" % user

        if not self.query_mysql(find_user):
            sql = """INSERT INTO score (user) VALUES ('%s')""" % user
            self.query_mysql(sql)

    def increment(self, user):
        self.create_user(user)
        sql = """UPDATE score SET count = count + 1 WHERE user = '%s'""" % user
        self.query_mysql(sql)

    def decrement(self, user):
        self.create_user(user)
        sql = """UPDATE score SET count = count - 1 WHERE user = '%s'""" % user
        self.query_mysql(sql)

    def get_score(self, user):
        self.create_user(user)
        sql = """SELECT count from score where user = '%s'""" % user
        return self.query_mysql(sql)
