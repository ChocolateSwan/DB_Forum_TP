# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from contextlib import contextmanager
from psycopg2.pool import ThreadedConnectionPool

from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponse
import psycopg2
import psycopg2.extras
import json
import sys
from utils import return_cursor, select_user_id,\
    select_forum_id, user_make_json

#=========================================
try:
    pool = ThreadedConnectionPool(2, 10, 'host=127.0.0.1 user=olyasur dbname=ForumTP password=Arielariel111')
except:
    print "Oops ThreadedConnectionPool"

@contextmanager
def get_cursor():
    print ("open")
    connection = pool.getconn()
    cur = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        yield cur, connection
        # con.commit()
    finally:
        print ("close")
        cur.close()
        pool.putconn(connection)

#=========================================


########################################
# Forum
########################################
def create_forum(request):
    with get_cursor() as (cursor, connection):
        data = json.loads(request.body.decode('utf-8'))
        req_insert_forum = "INSERT INTO \"Forum\" (slug, title, user_id) VALUES ('{}', '{}',\
                (SELECT id from \"User\" where nickname = '{}'));" \
            .format(data['slug'], data['title'], data['user'], )
        try:
            cursor.execute(req_insert_forum)
            connection.commit()
        except psycopg2.Error as err:
            connection.rollback()
            if "user_id" in err.message:
                return JsonResponse\
                    ({"message": "Can't find user with nickname {}\n".format(data['user'])}, status=404)
            if "forum_slug_unique" in err.message:
                req_select_forum = "SELECT \"Forum\".posts, \"Forum\".slug, \"Forum\".threads,\"Forum\".title, \"User\".nickname as \"user\" \
                    FROM \"Forum\" INNER JOIN \"User\" ON \"Forum\".user_id = \"User\".id where \"Forum\".slug = '{}';"\
                    .format(data['slug'])
                cursor.execute(req_select_forum)
                return JsonResponse(dict(cursor.fetchone()),status=409)
            print ("Cant't insert forum")
        return JsonResponse( {'posts': 0, 'slug': data['slug'], 'threads': 0,
                              'title': data['title'], 'user': data['user']}, status=201, )


def details_forum(request, slug):
    with get_cursor() as (cursor, connection):
        req_select_forum = "SELECT \"Forum\".posts, \"Forum\".slug, \"Forum\".threads,\"Forum\".title, \"User\".nickname as \"user\" \
        FROM \"Forum\" INNER JOIN \"User\" ON \"Forum\".user_id = \"User\".id where \"Forum\".slug = '{}';"\
            .format(slug)
        try:
            cursor.execute(req_select_forum)
            return JsonResponse(dict(cursor.fetchone()), status=200, )
        except:
            return JsonResponse({"message": "Can't find forum with slug = {}".\
                                format(slug)}, status=404, )


#
# {
#   "author": "j.sparrow",
#   "created": "2017-01-01T00:00:00.000Z",
#   "message": "An urgent need to reveal the hiding place of Davy Jones. Who is willing to help in this matter?",
#   "title": "Davy Jones cache"
# }

def create_thread(request, slug):
    cursor, connection = return_cursor()
    data = json.loads(request.body.decode('utf-8'))
    user = select_user_id(cursor, data['author'])
    forum = select_forum_id(cursor, slug)
    if user is None:
        return JsonResponse \
            ({"message": "Can't find user with nickname {}\n".format(data['user'])}, status=404)
    if forum is None:
        return JsonResponse \
            ({"message": "Can't find forum with slug {}\n".format(slug)}, status=404)
    # Проверили юзера и наличие форума
    req_insert_thread = "INSERT INTO thread (author_id, forum_id, forum_slug, message, slug, title)\
        VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}');" \
        .format(data['slug'], data['title'], user[0], data['user'], )
    # try:
    #     cursor.execute(req_insert_forum)
    #     connection.commit()
    # except psycopg2.Error as err:
    #     pass



    #
    # sql = "INSERT INTO forum (id, author_name, created ,posts,threads) VALUES ('%s', '%s', '%s', 0, 0);" \
    #       % (data[u'slug'], data[u'title'], data[u'user'],)

    return JsonResponse({1:1},status=201)




########################################
# User
########################################
def create_user(request, nickname):
    with get_cursor() as (cursor, connection):
        data = json.loads(request.body.decode('utf-8'))
        req_insert_user = "INSERT INTO \"User\" (about, email, fullname, nickname) VALUES ('{}', '{}', '{}', '{}');" \
            .format(data['about'], data['email'], data['fullname'], nickname)
        try:
            cursor.execute(req_insert_user)
            connection.commit()
        except psycopg2.Error as err:
            connection.rollback()
            if "unique" in err.message:
                req_select_user = " SELECT about, email, fullname, nickname FROM \"User\" where email = '{}' or nickname = '{}';"\
                    .format(data['email'],nickname)
                cursor.execute(req_select_user)
                users = cursor.fetchall()
            return JsonResponse(map(lambda x: dict(x), users), safe=False, status=409)
        return JsonResponse( {'about': data['about'], 'email': data['email'],'fullname': data['fullname'],
                              'nickname': nickname}, status=201, )


def profile_user(request, nickname):
    with get_cursor() as (cursor, connection):
        if request.method == "GET":
            req_select_username = "SELECT about, email, fullname, nickname FROM \"User\" where nickname = '{}';"\
                .format(nickname)
            try:
                cursor.execute(req_select_username)
                # user = cursor.fetchone()
                return JsonResponse(dict(cursor.fetchone()), status=200)
            except:
                return JsonResponse({"message": "Can't user with nickname = {}".\
                                    format(nickname)}, status=404, )
        else:
            data = json.loads(request.body.decode('utf-8'))
            req_select_username = "SELECT id FROM \"User\" where nickname = '{}';" \
                .format(nickname)
            try:
                cursor.execute(req_select_username)
                user = cursor.fetchone()
                if user is None:
                    return JsonResponse({"message": "Can't user with nickname = {}". \
                                        format(nickname)}, status=404, )

                else:
                    req_update_user = "UPDATE \"User\" SET about = '{}', email = '{}', fullname = '{}' where id = '{}'; "\
                    .format(data['about'], data['email'], data['fullname'], user['id'])
                    try:
                        cursor.execute(req_update_user)
                        connection.commit()
                    except psycopg2.Error as err:
                        connection.rollback()
                        if "unique" in err.message:
                            return JsonResponse({"message": "Conflict"}, status=409, )
                    return JsonResponse({'about': data['about'], 'email': data['email'], 'fullname': data['fullname'],
                                         'nickname': nickname}, status=200, )
            except:
                print "oooooooooopppps"

########################################
# User
########################################