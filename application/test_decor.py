
from contextlib import contextmanager
from psycopg2.pool import ThreadedConnectionPool

try:
    pool = ThreadedConnectionPool(2, 10, 'host=127.0.0.1 user=olyasur dbname=ForumTP password=Arielariel111')
except:
    print "Oops ThreadedConnectionPool!!!"


def cursor_decorator(function_to_decorate):

    def wrapper():
        connection = pool.getconn()
        cur = connection.cursor()
        function_to_decorate()



    return wrapper