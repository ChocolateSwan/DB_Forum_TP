import psycopg2
import psycopg2.extras
import psycopg2.extensions

from psycopg2 import pool
from psycopg2.pool import ThreadedConnectionPool
from time import time

from psycopg2 import sql


conn = psycopg2.connect("dbname='ForumTP' user='olyasur' password='Arielariel111'")
dict_cur = conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
dict_cur.execute("INSERT INTO \"User\" (nickname, email,fullname) VALUES(%s, %s,%s)",("test2", "test2","test2"))

dict_cur.execute("SELECT * FROM \"User\" where nickname = \'test2\'")
rec = dict_cur.fetchone()
print (rec.nickname)
print rec.about


print psycopg2.__version__

#pool = psycopg2.pool.ThreadedConnectionPool(5, 10, 'host=127.0.0.1 user=test dbname=test password=test')
# tr = ThreadedConnectionPool(5, 10, 'host=127.0.0.1 user=olyasur dbname=ForumTP password=Arielariel111')
# pool = psycopg2.pool.PersistentConnectionPool(5, 10, 'host=127.0.0.1 user=test dbname=test password=test')


class TimeProfiler():
    _started = []
    labels = {}

    def start(self, label):
        self._started.append(label)
        self.labels[label] = time()

    def stop(self, label):
        if self.labels.has_key(label):
            if label in self._started: self._started.remove(label)
            self.labels[label] = '%.10f' % (time() - self.labels[label])
        else:
            self.labels[label] = 0

    def get_list(self):
        labels = {}
        for key in self.labels.keys():
            if key not in self._started: labels[key] = self.labels[key]
        return labels


T = TimeProfiler()
T.stop('create pool')
try:

    pool = ThreadedConnectionPool(2, 10, 'host=127.0.0.1 user=olyasur dbname=ForumTP password=Arielariel111')
except:
    print "oops"

print T.get_list()

T.start('connect 1')
c = pool.getconn()
T.stop('connect 1')

print T.get_list()


T.start('connect 2')
c = pool.getconn()
T.stop('connect 2')

print T.get_list()

c = pool.putconn

try:
    T.start('connect 3')
    c = pool.getconn()
except:
    print "lol"
c = pool.getconn()
T.stop('connect 3')

print T.get_list()

print T.get_list()

query = sql.SQL("select {0} from {1}").format(sql.SQL(', ').join([sql.Identifier('foo'), sql.Identifier('bar')]),sql.Identifier('table'))

print(query.as_string(conn))

qq = sql.SQL("select nickname from {} where {} = %d %s").format(sql.Identifier('User'), sql.Identifier('id'),).as_string(conn)%(1,"or id = 4")
print(qq)
cursor = conn.cursor()
cursor.execute(qq)
res = cursor.fetchall()
print (res)


# cursor_factory=psycopg2.extras.DictCursor