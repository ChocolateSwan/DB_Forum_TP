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
        req_insert_forum = "WITH t as (INSERT INTO \"Forum\" (slug, title, user_id) VALUES ('{}', '{}', (SELECT id from \"User\" where nickname = '{}')) RETURNING posts, slug, threads, title, user_id )\
select posts, slug, threads, title, nickname as \"user\" from t  INNER JOIN \"User\" ON t.user_id = \"User\".id;" \
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
        return JsonResponse( dict(cursor.fetchone()), status=201, )


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

########################################
# Forum
########################################

#
# {
#   "author": "j.sparrow",
#   "created": "2017-01-01T00:00:00.000Z",
#   "message": "An urgent need to reveal the hiding place of Davy Jones. Who is willing to help in this matter?",
#   "title": "Davy Jones cache"
# }


def create_thread(request, slug):
    with get_cursor() as (cursor, connection):
        data = json.loads(request.body.decode('utf-8'))
        req_insert_thread = "with t as ( INSERT INTO thread (author_id, created, forum_id, message, slug, title) \
            VALUES ((SELECT id from \"User\" where nickname = '{}'), '{}', \
                  (SELECT id from \"Forum\" where slug = '{}'),'{}', {},'{}')        \
                  RETURNING author_id, created, forum_id,id, message, slug, title, votes\
                  )\
                  SELECT nickname as \"author\", created, f.slug as \"forum\",t.id, message, t.slug, t.title, t.votes\
                   from t  \
                   INNER JOIN \"User\" ON t.author_id = \"User\".id \
                      INNER JOIN \"Forum\" f ON t.forum_id = f.id " \
            .format(data['author'],
                    "now()" if data.get('created') is None else data.get('created'),
                    slug, data['message'],
                    "NULL" if data.get('slug') is None else "'"+data.get('slug')+"'",
                    data['title'])
        try:
            cursor.execute(req_insert_thread)
            connection.commit()
        except psycopg2.Error as err:
            connection.rollback()
            if "author_id" in err.message or "forum_id" in err.message:
                return JsonResponse \
                    ({"message": "Foreign key error"}, status=404)
            if "thread_slug_unique" in err.message: #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                req_select_forum = "SELECT u.nickname as \"author\", t.created, f.id as \"forum\", t.id,t.message,t.slug, t.title, t.votes \
                    FROM thread t WHERE t.slug = '{}' \
                    INNER JOIN \"User\" u ON t.author_id = u.id  \
                    INNER JOIN \"Forum\" f ON t.forum_id = f.id;" \
                    .format(data['slug'])
                cursor.execute(req_select_forum)
                return JsonResponse(dict(cursor.fetchone()), status=409)
                return JsonResponse({1:1}, status=409)
        return JsonResponse(dict(cursor.fetchone()), status=201, )






def threads_forum(request, slug):
    with get_cursor() as (cursor, connection):
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
            print req_select_threads
            cursor.execute(req_select_threads)
            connection.commit()
        except psycopg2.Error as err:
            print err.message
            return JsonResponse({"message": "cant' find"}, status=404, )
        return JsonResponse(map(lambda x: dict(x), cursor.fetchall()), safe = False, status=200, )













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
                    req_update_user = "UPDATE \"User\" SET "
                    for key in data:
                        print key
                        req_update_user += key+" = '" + str(data[key])+"', "
                    req_update_user = req_update_user[:req_update_user.rfind(',')]
                    req_update_user += " where id = " + str(user['id'])
                    try:
                        cursor.execute(req_update_user)
                        connection.commit()
                    except psycopg2.Error as err:
                        connection.rollback()
                        if "unique" in err.message:
                            return JsonResponse({"message": "Conflict"}, status=409, )

                    req_select_user = " SELECT about, email, fullname, nickname FROM \"User\" where nickname = '{}';".format(nickname)
                    cursor.execute(req_select_user)
                    return JsonResponse(dict(cursor.fetchone()), status=200, )
            except:
                print "ooooooooooops"

########################################
# User
########################################