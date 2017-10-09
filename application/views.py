# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponse
import psycopg2
import psycopg2.extras
import json
import sys
from utils import return_cursor


def create_forum(request):
    cursor, connection = return_cursor()
    body_unicode = request.body.decode('utf-8')
    data = json.loads(body_unicode)
    print data
    req_select_user =" SELECT id FROM \"User\" where nickname = '{}';"\
        .format(data['user'])
    user = None
    try:
        cursor.execute(req_select_user)
        user = cursor.fetchone()
    except:
        print ("Can't select user")
    if user is None:
        return JsonResponse\
            ({"message": "Can't find user with nickname {}\n".format(data['user'])}, status=404)
    print(user)
    req_insert_forum = "INSERT INTO \"Forum\" (slug, title, user_id, user_nickname) VALUES ('{}', '{}', '{}', '{}');"\
        .format(data['slug'],data['title'], user[0],data['user'],)
    try:
        cursor.execute(req_insert_forum)
        connection.commit()
    except psycopg2.Error as err:
        connection.rollback()
        if "forum_slug_unique" in err.message:
            forum = None
            req_select_forum = " SELECT posts, threads, title, user FROM \"Forum\" where slug = '{}';"\
                .format(data['slug'])
            try:
                cursor.execute(req_select_forum)
                forum = cursor.fetchone()

            except psycopg2.Error as err :
                print err.message
                print ("Can't select forum")
            return JsonResponse({"posts": forum[0],
                                 "slug": data['slug'],
                                 "threads": forum[1],
                                 "title": forum[2],
                                 "user": forum[3]},status=409)
        print ("Cant't insert forum")

    return JsonResponse( {'posts': 0,
                          'slug': data['slug'],
                          'threads': 0,
                          'title': data['title'],
                          'user': data['user']},status=201, )



    #
    #     sql = "INSERT INTO forum (slug, title, user_name) VALUES ('%s', '%s', '%s', 0, 0);"\
    #     % (data[u'slug'],data[u'title'], data[u'user'],)
    #
    #     try:
    #         cur.execute(sql)
    #         conn.commit()
    #     except psycopg2.Error as err:
    #         if err.pgcode == "25P02":
    #             return JsonResponse({1:2},status=409)
    #
    #         print "I can't insert"
    #     sql = "SELECT posts,slug,threads,title,user_name FROM forum where slug = '%s';"\
    #     %(data[u'slug'])
    #
    #     try:
    #         cur.execute(sql)
    #     except:
    #         print "I can't select"
    #     row = cur.fetchone()
    # return JsonResponse( {'posts': row[0],
    #                       'slug':row[1],
    #                       'threads': row[2],
    #                       'title': row[3],
    #                       'user': row[4]},status=201, )

    return JsonResponse({1:1}, status=201)


def detailsForum (request, slug):
    pass
    # cursor, connection = returnCursor()
    # sql = "SELECT posts,slug,threads,title,user_name FROM forum where slug = '%s';" \
    #       % (slug)
    #
    #
    # try:
    #     cur.execute(sql)
    #     row = cur.fetchone()
    #     return JsonResponse({'posts': row[0],
    #                          'slug': row[1],
    #                          'threads': row[2],
    #                          'title': row[3],
    #                          'user': row[4]}, status=200, )
    # except:
    #     return JsonResponse({"message": "Can't find forum with slug = %s"%(slug)}, status=201, )


def createThread (request, slug):
    pass
#     cur, conn = returnCursor()
#     data = json.loads(request.body)
#     sql = "INSERT INTO forum (id, author_name, created ,posts,threads) VALUES ('%s', '%s', '%s', 0, 0);" \
#           % (data[u'slug'], data[u'title'], data[u'user'],)
#
#     return JsonResponse({1:1},status=201)






