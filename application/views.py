# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponse
import psycopg2
import psycopg2.extras
import json
import sys
from utils import *

# Create your views here.
def returnCursor ():
    conn = 1
    try:
        conn = psycopg2.connect("dbname='ForumTP' user='olyasur' password='Arielariel111'")
    except:
        print "I am unable to connect to the database."

    cur = conn.cursor()
    return cur,conn


# body_unicode = request.body.decode('utf-8')
# body = json.loads(body_unicode)
# content = body['content']


def createForum(request):
    sqlQuery = ""
    conn = 1
    cur,conn = returnCursor()

    if request.method == "POST":
        data = json.loads(request.body)
        sql = "INSERT INTO forum (slug, title, user_name ,posts,threads) VALUES ('%s', '%s', '%s', 0, 0);"\
        % (data[u'slug'],data[u'title'], data[u'user'],)

        try:
            cur.execute(sql)
            conn.commit()
        except psycopg2.Error as err:
            if err.pgcode == "25P02":
                return JsonResponse({1:2},status=409)

            print "I can't insert"
        sql = "SELECT posts,slug,threads,title,user_name FROM forum where slug = '%s';"\
        %(data[u'slug'])

        try:
            cur.execute(sql)
        except:
            print "I can't select"
        row = cur.fetchone()
    return JsonResponse( {'posts': row[0],
                          'slug':row[1],
                          'threads': row[2],
                          'title': row[3],
                          'user': row[4]},status=201, )


def detailsForum (request, slug):
    cur, conn = returnCursor()
    sql = "SELECT posts,slug,threads,title,user_name FROM forum where slug = '%s';" \
          % (slug)


    try:
        cur.execute(sql)
        row = cur.fetchone()
        return JsonResponse({'posts': row[0],
                             'slug': row[1],
                             'threads': row[2],
                             'title': row[3],
                             'user': row[4]}, status=200, )
    except:
        return JsonResponse({"message": "Can't find forum with slug = %s"%(slug)}, status=201, )


def createThread (request, slug):
    cur, conn = returnCursor()
    data = json.loads(request.body)
    sql = "INSERT INTO forum (id, author_name, created ,posts,threads) VALUES ('%s', '%s', '%s', 0, 0);" \
          % (data[u'slug'], data[u'title'], data[u'user'],)

    return JsonResponse({1:1},status=201)






