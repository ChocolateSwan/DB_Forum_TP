from psycopg2.pool import ThreadedConnectionPool


def init_connection_pool():
    try:
        return ThreadedConnectionPool(2,
                                      10,
                                      'host=127.0.0.1 '
                                      'user=olyasur '
                                      'dbname=ForumTP '
                                      'password=Arielariel111')
    except:
        print "I can't init ThreadedConnectionPool"
        exit(1)





