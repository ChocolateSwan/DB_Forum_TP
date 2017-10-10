# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponse
import psycopg2
import psycopg2.extras
import json
import sys
from utils import return_cursor, select_user_id,\
    select_forum_id


def create_forum(request):
    cursor, connection = return_cursor()
    data = json.loads(request.body.decode('utf-8'))
    user = select_user_id(cursor, data['user'])
    if user is None:
        return JsonResponse\
            ({"message": "Can't find user with nickname {}\n".format(data['user'])}, status=404)

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



def details_forum (request, slug):
    cursor, connection = return_cursor()
    req_select_forum = "SELECT posts, threads, title, user_nickname FROM \"Forum\" where slug = '{}';"\
        .format(slug)
    try:
        cursor.execute(req_select_forum)
        forum = cursor.fetchone()
        return JsonResponse({'posts': forum[0],
                             'slug': slug,
                             'threads': forum[1],
                             'title': forum[2],
                             'user': forum[3]}, status=200, )
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

def create_thread (request, slug):
    # cursor, connection = return_cursor()
    # data = json.loads(request.body.decode('utf-8'))
    #
    # user = select_user_id(cursor, data['author'])
    # forum = select_forum_id(cursor, data['slug'])
    # if user is None:
    #     return JsonResponse \
    #         ({"message": "Can't find user with nickname {}\n".format(data['user'])}, status=404)
    # if forum is None:
    #     return JsonResponse \
    #         ({"message": "Can't find forum with slug {}\n".format(slug)}, status=404)
    #
    # req_insert_thread = "INSERT INTO thread (author_id, author_nickname, forum_id, forum_slug, message, slug, title)\
    #     VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}');" \
    #     .format(data['slug'], data['title'], user[0], data['user'], )
    # try:
    #     cursor.execute(req_insert_forum)
    #     connection.commit()
    # except psycopg2.Error as err:

    #
    #
    #
    # sql = "INSERT INTO forum (id, author_name, created ,posts,threads) VALUES ('%s', '%s', '%s', 0, 0);" \
    #       % (data[u'slug'], data[u'title'], data[u'user'],)

    return JsonResponse({1:1},status=201)






