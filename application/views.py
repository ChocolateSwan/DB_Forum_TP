# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from contextlib import contextmanager
from django.http import JsonResponse
import psycopg2
import psycopg2.extras
import json
from utils import init_connection_pool


# Get connection pool
pool = init_connection_pool()


@contextmanager
def get_cursor():
    connection = pool.getconn()
    # Make dictionary cursor
    cur = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        yield cur, connection
    finally:
        cur.close()
        pool.putconn(connection)


########################################
# Forum (begin)
########################################

# request: "slug", "title": "Pirate stories", "user"
# response:  "posts", "slug", "threads", "title", "user"
def create_forum(request):
    with get_cursor() as (cursor, connection):
        data = json.loads(request.body.decode('utf-8'))
        req_insert_forum = "WITH t as " \
                           "(INSERT INTO \"Forum\" " \
                           "(slug, title, user_id) " \
                           "VALUES ('{}', '{}', " \
                           "(SELECT id from \"User\" WHERE nickname = '{}')) " \
                           "RETURNING posts, slug, threads, title, user_id )" \
                           "SELECT posts, slug, threads, title, nickname AS \"user\" " \
                           "FROM t  INNER JOIN \"User\" ON t.user_id = \"User\".id;" \
            .format(data['slug'],
                    data['title'],
                    data['user'], )
        try:
            cursor.execute(req_insert_forum)
            connection.commit()
        except psycopg2.Error as err:
            connection.rollback()
            if "user_id" in err.message:
                return JsonResponse({"message": "Can't find user with nickname {}\n"
                                     .format(data['user'])},
                                    status=404, )
            if "forum_slug_unique" in err.message:
                req_select_forum = "SELECT \"Forum\".posts, \"Forum\".slug, " \
                                   "\"Forum\".threads,\"Forum\".title, \"User\".nickname as \"user\" " \
                                   "FROM \"Forum\" " \
                                   "INNER JOIN \"User\" " \
                                   "ON \"Forum\".user_id = \"User\".id " \
                                   "WHERE \"Forum\".slug = '{}';"\
                    .format(data['slug'])
                cursor.execute(req_select_forum)
                return JsonResponse(dict(cursor.fetchone()),
                                    status=409, )
        return JsonResponse(dict(cursor.fetchone()),
                            status=201, )


# request: not parameters
# response: "posts", "slug", "threads", "title", "user"
def details_forum(request, slug):
    with get_cursor() as (cursor, connection):
        req_select_forum = "SELECT \"Forum\".posts, \"Forum\".slug, \"Forum\".threads," \
                           "\"Forum\".title, \"User\".nickname AS \"user\" " \
                           "FROM \"Forum\" " \
                           "INNER JOIN \"User\" " \
                           "ON \"Forum\".user_id = \"User\".id " \
                           "WHERE \"Forum\".slug = '{}';"\
            .format(slug)
        try:
            cursor.execute(req_select_forum)
            return JsonResponse(dict(cursor.fetchone()),
                                status=200, )
        except:
            return JsonResponse({"message": "Can't find forum with slug = {}"
                                .format(slug)},
                                status=404, )


def forum_users(request, slug):
    with get_cursor() as (cursor, connection):
        req_select_forum = "SELECT id from \"Forum\" where slug = '{}'".format(slug)
        try:
            cursor.execute(req_select_forum)
        except psycopg2.Error as err:
            return JsonResponse({"message": "cant' find"}, status=404, )
        forum = cursor.fetchone()

        if forum is None:
            return JsonResponse({"message": "cant' find"}, status=404, )
        req_select_users = '''
                   select DISTINCT about, email, fullname, nickname from "Forum" 
                    inner join thread on "Forum".id = thread.forum_id
                    inner join "User" on thread.author_id = "User".id 
                    where "Forum".slug = '{}' {}
                    
                    
                    UNION 
                    
                    select DISTINCT about, email, fullname, nickname from post
                    inner join "User" on post.author_id = "User".id
                    inner join thread on post.thread_id = thread.id
                    inner join "Forum" on thread.forum_id = "Forum".id 
                    where "Forum".slug = '{}' {}
                    
                    
                    order by nickname {}
                    {}
        '''.format(slug,
                   "and nickname > '{}'".format(request.GET.get('since')) if request.GET.get('since') is not None else " ",
                   slug,
                   "and nickname > '{}'".format(request.GET.get('since')) if request.GET.get('since') is not None else " ",
                   "DESC" if request.GET.get('desc') == "true" else "ASC",
                   "LIMIT {}".format(int(request.GET.get('limit'))) if request.GET.get('limit') is not None else " "

        )
        if request.GET.get('desc') == "true":
            req_select_users = req_select_users.replace('>','<')
        try:
            cursor.execute(req_select_users)
            return JsonResponse(map(lambda x: dict(x), cursor.fetchall()), safe=False, status=200, )
        except:
            print "forum_users ВСЕ ПЛОХО"





########################################
# Forum (end)
########################################

########################################
# Thread (begin)
########################################


# request: "author", "created", "message", "title"
# response: "author", "created", "forum", "id", "message", "slug", "title", "votes"
def create_thread(request, slug):
    with get_cursor() as (cursor, connection):
        data = json.loads(request.body.decode('utf-8'))
        req_insert_thread = "WITH t AS " \
                            "(INSERT INTO thread (author_id, created, forum_id, message, slug, title)" \
                            " VALUES ((SELECT id FROM \"User\" WHERE nickname = '{}'), '{}', " \
                            "(SELECT id FROM \"Forum\" WHERE slug = '{}'),'{}', {},'{}') " \
                            "RETURNING author_id, created, forum_id,id, message, slug, title, votes)" \
                            "SELECT nickname AS \"author\", created, f.slug AS \"forum\",t.id, " \
                            "message, t.slug, t.title, t.votes " \
                            "FROM t  " \
                            "INNER JOIN \"User\" ON t.author_id = \"User\".id " \
                            "INNER JOIN \"Forum\" f ON t.forum_id = f.id " \
            .format(data['author'],
                    "now()" if data.get('created') is None else data.get('created'),
                    slug,
                    data['message'],
                    "NULL" if data.get('slug') is None else "'"+data.get('slug')+"'",
                    data['title'])
        try:
            cursor.execute(req_insert_thread)
            connection.commit()
        except psycopg2.Error as err:
            connection.rollback()
            if "author_id" in err.message or "forum_id" in err.message:
                return JsonResponse({"message": "Foreign key error"},
                                    status=404)
            if "unique" in err.message:
                req_select_thread = "SELECT u.nickname as \"author\", t.created, f.slug as \"forum\", t.id,t.message,t.slug, t.title, t.votes \
                    FROM thread t  \
                    INNER JOIN \"User\" u ON t.author_id = u.id  \
                    INNER JOIN \"Forum\" f ON t.forum_id = f.id " \
                    "WHERE t.slug = '{}'" \
                    .format(data['slug'])
                cursor.execute(req_select_thread)
                return JsonResponse(dict(cursor.fetchone()),
                                    status=409)
        thread = dict(cursor.fetchone())
        try:
            cursor.execute("BEGIN; UPDATE \"Forum\" SET threads = threads + 1 " \
                              "WHERE slug = '{}' ; COMMIT;".format(thread['forum']))
            return JsonResponse(thread, status=201, )
        except BaseException as err:
            print err.message



# request: no parameters
# response: "author", "created", "forum", "id", "message", "slug", "title", "votes"
def thread_details(request, slug_or_id):
    with get_cursor() as (cursor, connection):
        # Проверяем наличие Thread
        id_thread = None
        if slug_or_id.isdigit():
            cursor.execute("SELECT id from thread WHERE id = {}".format(slug_or_id))
            id_thread = cursor.fetchone()
            if id_thread is None:
                return JsonResponse({"message": "No thread"}, status=404, )
            else:
                id_thread = id_thread['id']
            id_thread = slug_or_id
        else:
            cursor.execute("SELECT id from thread WHERE slug = '{}'".format(slug_or_id))
            id_thread = cursor.fetchone()
            if id_thread is None:
                return JsonResponse({"message": "No thread"}, status=404, )
            else:
                id_thread = id_thread['id']
        #Get request
        if request.method == "GET":
            req_select_thread =" SELECT u.nickname AS \"author\", thread.created, " \
                              "f.slug AS \"forum\", thread.id," \
                              "thread.message,thread.slug, thread.title, thread.votes \
                                FROM thread  \
                                INNER JOIN \"User\" u ON thread.author_id = u.id  \
                                INNER JOIN \"Forum\" f ON thread.forum_id = f.id " \
                              "WHERE  thread.id = {};".format(id_thread)
            cursor.execute(req_select_thread)
            tr = cursor.fetchone()
            if tr is None:
                return JsonResponse({"message": "No thread"}, status=404, )
            return JsonResponse(dict(tr),
                                status=200, )
        # POST method
        else:
            гг
            data = json.loads(request.body.decode('utf-8'))
            # Generate UPDATE thread
            req_select_thread = " SELECT u.nickname AS \"author\", thread.created, " \
                                "f.slug AS \"forum\", thread.id," \
                                "thread.message,thread.slug, thread.title, thread.votes \
                                 FROM thread  \
                                 INNER JOIN \"User\" u ON thread.author_id = u.id  \
                                 INNER JOIN \"Forum\" f ON thread.forum_id = f.id " \
                                "WHERE  thread.id = {};".format(id_thread)
            if data.get('message') == None:
                cursor.execute(req_select_thread)
                return JsonResponse(dict(cursor.fetchone()), status=200, )

            req_update_thread = "UPDATE thread SET "
            for key in data:
                req_update_thread += key + " = '" + str(data[key]) + "', "
            req_update_thread = req_update_thread[:req_update_thread.rfind(',')]
            req_update_thread += " where id = " + str(id_thread)
            print req_update_thread
            try:

                cursor.execute(req_update_thread)
                connection.commit()

                cursor.execute(req_select_thread)
                tr = cursor.fetchone()
                return JsonResponse(dict(tr), status=200, )
            except psycopg2.Error as err:
                print err.message
                return JsonResponse({"message": "Error"}, status=404,)







def threads_forum(request, slug):
    with get_cursor() as (cursor, connection):
        req_select_forum = "SELECT id from \"Forum\" where slug = '{}'".format(slug)
        try:
            cursor.execute(req_select_forum)
            connection.commit()
        except psycopg2.Error as err:
            return JsonResponse({"message": "cant' find"}, status=404, )
        forum = cursor.fetchone()
        if forum is None:
            return JsonResponse({"message": "cant' find"}, status=404, )
        req_select_threads ="SELECT nickname as \"author\", created, f.slug as \"forum\",t.id, message, t.slug, t.title, t.votes  \
        FROM thread t INNER JOIN \"User\" u ON t.author_id = u.id INNER JOIN \"Forum\" f ON t.forum_id = f.id WHERE f.slug = '{}'"\
        .format(slug)
        if request.GET.get('since') is not None:
            req_select_threads += " AND t.created" + \
            (' <= ' if request.GET.get('desc') == 'true' else ' >= ') +\
            " '{}' ".format(request.GET['since'])
        req_select_threads += ' ORDER BY t.created '
        if request.GET.get('desc') is not None and request.GET.get('desc') == 'true':
            req_select_threads += 'DESC'
        if request.GET.get('limit') is not None:
            req_select_threads += " LIMIT {} ".format(int(request.GET['limit']))
        req_select_threads += ';'


        try:
            cursor.execute(req_select_threads)
            connection.commit()
        except psycopg2.Error as err:
            return JsonResponse({"message": "cant' find"}, status=404, )
        return JsonResponse(map(lambda x: dict(x), cursor.fetchall()), safe = False, status=200, )



def thread_posts(request,slug_or_id):
    with get_cursor() as (cursor, connection):
        pass




########################################
# Thread (end)
########################################

########################################
# User (begin)
########################################


# Response: "about", "email" , "fullname"
# Request: "about", "email", "fullname", "nickname"
def create_user(request, nickname):
    with get_cursor() as (cursor, connection):
        data = json.loads(request.body.decode('utf-8'))
        req_insert_user = "INSERT INTO \"User\" " \
                          "(about, email, fullname, nickname) " \
                          "VALUES ('{}', '{}', '{}', '{}');"\
            .format(data['about'],
                    data['email'],
                    data['fullname'],
                    nickname)
        try:
            cursor.execute(req_insert_user)
            connection.commit()
        except psycopg2.Error as err:
            connection.rollback()
            if "unique" in err.message:
                req_select_user = "SELECT about, email, fullname, nickname " \
                                  "FROM \"User\" " \
                                  "where email = '{}' or nickname = '{}';"\
                    .format(data['email'],
                            nickname)
                cursor.execute(req_select_user)
                users = cursor.fetchall()
            return JsonResponse(map(lambda x: dict(x), users),
                                safe=False,
                                status=409)
        # TODO write RETURNING in req_insert_user
        return JsonResponse({'about': data['about'],
                             'email': data['email'],
                             'fullname': data['fullname'],
                             'nickname': nickname}, status=201, )


# request: "about", "email", "fullname"
# response: "about", "email": "captaina@blackpearl.sea", "fullname", "nickname"
def profile_user(request, nickname):
    with get_cursor() as (cursor, connection):
        if request.method == "GET":
            req_select_username = "SELECT about, email, fullname, nickname " \
                                  "FROM \"User\" " \
                                  "WHERE nickname = '{}';"\
                .format(nickname)
            try:
                cursor.execute(req_select_username)
                return JsonResponse(dict(cursor.fetchone()),
                                    status=200, )
            except:
                return JsonResponse({"message":  "Can't user with nickname = {}".
                                    format(nickname)},
                                    status=404, )
        # Method POST
        else:
            data = json.loads(request.body.decode('utf-8'))
            req_select_username = "SELECT id " \
                                  "FROM \"User\" " \
                                  "WHERE nickname = '{}';" \
                .format(nickname)
            try:
                cursor.execute(req_select_username)
                user = cursor.fetchone()
                if user is None:
                    return JsonResponse({"message": "Can't user with nickname = {}". \
                                        format(nickname)},
                                        status=404, )
                else:
                    # Generate UPDATE User
                    req_update_user = "UPDATE \"User\" SET "
                    for key in data:
                        req_update_user += key+" = '" + str(data[key])+"', "
                    req_update_user = req_update_user[:req_update_user.rfind(',')]
                    req_update_user += " where id = " + str(user['id'])
                    try:
                        cursor.execute(req_update_user)
                        connection.commit()
                    except psycopg2.Error as err:
                        connection.rollback()
                        if "unique" in err.message:
                            return JsonResponse({"message": "Conflict"},
                                                status=409, )
                    req_select_user = " SELECT about, email, fullname, nickname " \
                                      "FROM \"User\" " \
                                      "WHERE nickname = '{}';".\
                        format(nickname)
                    cursor.execute(req_select_user)
                    return JsonResponse(dict(cursor.fetchone()),
                                        status=200, )
            except:
                print "It is FAIL"


########################################
# User (end)
########################################


# [
#   {
#     "author": "j.sparrow",
#     "message": "We should be afraid of the Kraken.",
#     "parent": 0
#   }
# ]

########################################
# Post
########################################
def create_post(request, slug_or_id):
    # TODO slug_or_id into one query
    with get_cursor() as (cursor, connection):
        data = json.loads(request.body)
        id_thread = None
        if slug_or_id.isdigit():
            id_thread = slug_or_id
        else:
            print slug_or_id
            cursor.execute("SELECT id from thread WHERE slug = '{}'".format(slug_or_id))
            id_thread = cursor.fetchone()
            if id_thread is None:
                return JsonResponse({"message": "No thread"}, status=404, )
            else:
                id_thread = id_thread['id']
        print id_thread
        req_insert_posts = "WITH t as (INSERT INTO post (author_id, created, message,parent,thread_id) VALUES "
        for post in list(data):
            req_insert_posts += " ((SELECT id FROM \"User\" WHERE nickname = '{}'), now(), '{}',{},{}),"\
                .format(post['author'],
                        post['message'],
                        0 if post.get('parent') is None else int(post.get('parent')),
                        id_thread)

        req_insert_posts = req_insert_posts[:req_insert_posts.rfind(',')]
        req_insert_posts += " RETURNING id, author_id, created,isedited, message,parent,thread_id)"
        req_insert_posts += "select t.id, u.nickname as \"author\", t.created,f.slug as \"forum\", t.isedited, t.message, t.parent,thread_id\
                             as \"thread\" from t  INNER JOIN \"User\" u ON t.author_id = u.id inner join thread on thread.id = t.thread_id inner join \"Forum\" f on thread.forum_id = f.id;"

        try:
            cursor.execute(req_insert_posts)

            result = map(lambda x: dict(x), cursor.fetchall())
            cursor.execute("BEGIN; UPDATE \"Forum\" SET posts = posts + {} " \
                              "WHERE slug = '{}' ; COMMIT;".format( len(result),result[0]['forum']))
            # user = cursor.fetchone()
            return JsonResponse(result, safe=False, status=201)
        except psycopg2.Error as err:
            print "99999999999999999999999"
            if "author_id" in err.message:
                return JsonResponse({"message": "no author"}, status=404)
            if "thread" in err.message:
                return JsonResponse({"message": "no thread"}, status=404)

            print err.message
            pass
        return JsonResponse({1:1}, status=200)



def post_details(request, id):
    print request.GET.get('related')
    with get_cursor() as (cursor, connection):
        if request.method == "GET":
            req_select_post = '''
                        select  u.nickname as "author", p.created, f.slug as "forum", p.id, p.isedited as "isEdited", p.message, p.parent, p.thread_id as "thread"
            from post p
            inner join "User" u on u.id = p.author_id
            inner join thread t on p.thread_id = t.id
            inner join "Forum" f on f.id = t.forum_id
            where p.id = {}
                        '''.format(id)
            cursor.execute(req_select_post)
            post = (cursor.fetchone())
            if post is None:
                return JsonResponse({"message": "no post"}, status=404)
            result = {"post":dict(post)}
            if request.GET.get('related') is not None:
                if "user" in request.GET.get('related'):
                    req_select_user = '''
                    SELECT about, email, fullname, nickname
                    FROM "User" 
                    where nickname = '{}';
                    '''.format(post['author'])
                    cursor.execute(req_select_user)
                    user = cursor.fetchone()
                    result['author'] = dict(user)
                if "thread" in  request.GET.get('related'):
                    req_select_thread = '''SELECT nickname as "author", created, f.slug as "forum",t.id, message, t.slug, t.title, t.votes  
                            FROM thread t 
                            INNER JOIN "User" u ON t.author_id = u.id 
                            INNER JOIN "Forum" f ON t.forum_id = f.id WHERE t.id = {}
                    '''.format(post['thread'])
                    cursor.execute(req_select_thread)
                    thread = cursor.fetchone()
                    result['thread'] = dict(thread)
                if "forum" in request.GET.get('related'):
                    req_select_thread = '''
                    SELECT  "Forum".posts,  "Forum".slug,  "Forum".threads,
                        "Forum".title,  "User".nickname AS  "user"
                        FROM  "Forum"
                        INNER JOIN  "User"
                        ON  "Forum".user_id =  "User".id
                        WHERE  "Forum".slug = '{}';
                    '''.format(post['forum'])
                    cursor.execute(req_select_thread)
                    forum = cursor.fetchone()
                    result['forum'] = dict(forum)
            return JsonResponse(result, status=200, )
        else:
            data = json.loads(request.body.decode('utf-8'))
            req_select_post = '''
                         select  u.nickname as "author", p.created, f.slug as "forum", p.id, p.isedited as "isEdited", p.message, p.parent, p.thread_id as "thread"
            from post p
            inner join "User" u on u.id = p.author_id
            inner join thread t on p.thread_id = t.id
            inner join "Forum" f on f.id = t.forum_id
            where p.id = {}
            '''.format(id)
            cursor.execute(req_select_post)
            post = cursor.fetchone()
            if post is None:
                return JsonResponse({"message":"post not found"}, status=404, )
            if data.get('message') is None or post['message'] == data['message']:
                return JsonResponse(dict(post), status=200, )
            req_update_post = '''
            BEGIN;
            UPDATE post SET message = '{}', isedited = true
            WHERE id = {};
            COMMIT;
             select  u.nickname as "author", p.created, f.slug as "forum", p.id, p.isedited as "isEdited", p.message, p.parent, p.thread_id as "thread"
            from post p
            inner join "User" u on u.id = p.author_id
            inner join thread t on p.thread_id = t.id
            inner join "Forum" f on f.id = t.forum_id
            where p.id = {}
            '''.format(data['message'], id,id)
            cursor.execute(req_update_post)
            post = dict(cursor.fetchone())

            return JsonResponse(post, status=200, )










########################################
# Post (end)
########################################


########################################
# Service Information (begin)
########################################

# request: no parameters
# response: "forum", "post", "thread", "user"
def clear_service(request):
    with get_cursor() as (cursor, connection):
        req_delete_all = "DELETE FROM Vote; \
                          DELETE FROM post;\
                          DELETE FROM thread; \
                          DELETE FROM \"Forum\"; \
                          DELETE FROM \"User\""
        try:
            cursor.execute(req_delete_all)
            return JsonResponse({},
                                status=200)
        except :
            print ("I cant delete all information from db")


# request: no parameters
# response: "forum", "post", "thread", "user"
def status_service(request):
    with get_cursor() as (cursor, connection):
        req_get_statistic = "SELECT " \
                            "(SELECT count(id) FROM \"Forum\") AS \"forum\"," \
                            "(SELECT count (id) FROM post) AS \"post\"," \
                            "(SELECT count(id) FROM thread) AS thread," \
                            "(SELECT count(id) FROM \"User\") AS \"user\";"

        try:
            cursor.execute(req_get_statistic)

            return JsonResponse(dict(cursor.fetchone()),
                                status=200)
        except:
            print ("I cant get statistics")


########################################
# Service Information (end)
########################################


########################################
# Vote (begin)
########################################

# request: "nickname", "voice"
# response: "author", "created", "forum", "id", "message", "slug", "title", "votes"
def create_vote(request, slug_or_id):
    with get_cursor() as (cursor, connection):
        data = json.loads(request.body.decode('utf-8'))
        # Проверяем наличие Thread
        id_thread = None
        if slug_or_id.isdigit():
            id_thread = slug_or_id
        else:
            cursor.execute("SELECT id from thread WHERE slug = '{}'".format(slug_or_id))
            id_thread = cursor.fetchone()['id']
            if id_thread is None:
                return JsonResponse({"message": "No thread"}, status=404, )
        # Проверяем наличие этого голоса
        req_select_vote = "SELECT id from vote WHERE thread_id = {} AND " \
                          "user_id = (SELECT id FROM \"User\" WHERE nickname = '{}') AND " \
                          "vote = {}".format(id_thread, data['nickname'], data['voice'])
        cursor.execute(req_select_vote)
        vote = cursor.fetchone()

        if vote is not None:
            cursor.execute(" SELECT u.nickname AS \"author\", thread.created, " \
                          "f.slug AS \"forum\", thread.id," \
                          "thread.message,thread.slug, thread.title, thread.votes \
                            FROM thread  \
                            INNER JOIN \"User\" u ON thread.author_id = u.id  \
                            INNER JOIN \"Forum\" f ON thread.forum_id = f.id " \
                          "WHERE  thread.id = {};".format(id_thread))
            tr = cursor.fetchone()
            return JsonResponse(dict(tr),
                                status=200, )

        # Insert
        req_insert_vote = "BEGIN; " \
                          "INSERT INTO vote (user_id, thread_id, vote) " \
                          "VALUES ((SELECT id FROM \"User\" WHERE nickname = '{}'), " \
                          "{},{}); " \
                          "UPDATE thread SET votes = votes + 1 " \
                          "WHERE id = {}; " \
                          "COMMIT;" \
                          "SELECT u.nickname AS \"author\", thread.created, " \
                          "f.slug AS \"forum\", thread.id," \
                          "thread.message,thread.slug, thread.title, thread.votes \
                            FROM thread  \
                            INNER JOIN \"User\" u ON thread.author_id = u.id  \
                            INNER JOIN \"Forum\" f ON thread.forum_id = f.id " \
                          "WHERE  thread.id = {};"\
            .format(data['nickname'], id_thread, data['voice'], id_thread ,id_thread)
        try:
            cursor.execute(req_insert_vote)
            # cursor.commit()
            return JsonResponse(dict(cursor.fetchone()),
                                status=200, )
        except psycopg2.Error as err:
            connection.rollback()
            print err.message
            if "unique" in err.message:
                req_update_vote = "BEGIN;" \
                                  "UPDATE vote SET vote = {} " \
                          "WHERE thread_id = {} and user_id = " \
                          "(SELECT id FROM \"User\" WHERE nickname = '{}') ;" \
                                  "UPDATE thread SET votes = votes + 2*{} WHERE id = {};" \
                                  "COMMIT;" \
                                  "SELECT u.nickname AS \"author\", thread.created, " \
                          "f.slug AS \"forum\", thread.id," \
                          "thread.message,thread.slug, thread.title, thread.votes \
                            FROM thread  \
                            INNER JOIN \"User\" u ON thread.author_id = u.id  \
                            INNER JOIN \"Forum\" f ON thread.forum_id = f.id " \
                          "WHERE  thread.id = {};" \
                    .format(data['voice'], id_thread,data['nickname'], data['voice'], id_thread, id_thread)
                cursor.execute(req_update_vote)
                return  JsonResponse(dict(cursor.fetchone()),
                                     status = 200, )
            return JsonResponse({},
                                status=404, )




########################################
# Vote (end)
########################################

