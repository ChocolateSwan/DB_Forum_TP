import psycopg2
import psycopg2.extras


def select_str (**kwargs):
    sql_str = "SELECT "
    for field in kwargs['fields']:
        sql_str += field + ","

    sql_str += " FROM " + kwargs['table']
    if kwargs.get('where_fields') is not None:
        sql_str += " WHERE "
        for field in kwargs['where_fields']:
            sql_str += field + " "

    print sql_str
    return sql_str




# 0-if has errors, 1 - result
def selest_query(cursor, **kwargs):
    try:
        cursor.execute(select_str(table=kwargs['table'], fields=kwargs['fields']))
        if kwargs.get('where_fields') is not None:
            return [0, cursor.fetchone()]
        else:
            return [0,cursor.fetchall()]
    except psycopg2.Error as err:
        return [1, err]


try:
    connection = psycopg2.connect("dbname='ForumTP' user='olyasur' password='Arielariel111'")
except:
    print "Sorry! Unable to connect to the database!"

cursor = connection.cursor()
print (selest_query(cursor, table="\'User\'", fields = ['id', 'nickname']))