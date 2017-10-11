from contextlib import contextmanager
from psycopg2.pool import ThreadedConnectionPool

try:
    pool = ThreadedConnectionPool(2, 10, 'host=127.0.0.1 user=olyasur dbname=ForumTP password=Arielariel111')
except:
    print "Oops ThreadedConnectionPool!!!"


# Get Cursor
@contextmanager
def get_cursor():
    connection = pool.getconn()
    cur = connection.cursor()
    try:
        yield cur, connection
        # con.commit()
    finally:
        cur.close()
        pool.putconn(connection)


with get_cursor() as (cur,con):
    print (con)
    print "heey"
    cur.execute("SELECT about, email, fullname, nickname FROM \"User\" where nickname = \'j.sparrow\';")
    # con.commit()
    r = cur.fetchall()
    print r
