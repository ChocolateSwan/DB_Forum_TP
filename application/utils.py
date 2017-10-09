import psycopg2


def return_cursor():
    try:
        connection = psycopg2.connect("dbname='ForumTP' user='olyasur' password='Arielariel111'")
    except:
        print "Sorry! Unable to connect to the database!"

    cursor = connection.cursor()
    return cursor,connection