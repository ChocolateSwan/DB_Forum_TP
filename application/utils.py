import psycopg2


def return_cursor():
    try:
        connection = psycopg2.connect("dbname='ForumTP' user='olyasur' password='Arielariel111'")
    except:
        print "Sorry! Unable to connect to the database!"

    cursor = connection.cursor()
    return cursor,connection


def select_user_id(cursor, user_nickname):
    req_select_user = " SELECT id FROM \"User\" where nickname = '{}';" \
        .format(user_nickname)
    user = None
    try:
        cursor.execute(req_select_user)
        user = cursor.fetchone()
    except:
        print ("Can't select user")
    return user



def select_forum_id(cursor, forum_slug):
    req_select_forum = " SELECT id FROM \"Forum\" where slug = '{}';" \
        .format(forum_slug)
    forum = None
    try:
        cursor.execute(req_select_forum)
        forum = cursor.fetchone()
    except:
        print ("Can't select forum")
    return forum

def user_make_json(user):
    return { 'about': user[0],
            'email': user[1],
            'fullname': user[2],
            'nickname': user[3]}




