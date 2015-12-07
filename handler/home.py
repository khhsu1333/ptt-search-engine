#!/usr/bin/env python3
# coding=utf-8
#
# Copyright 2015 Kuo Hsuan Hsu
import logging

from tornado import gen
from utils.preprocess import get_word_vec

from handler.base import BaseHandler


class HomePage(BaseHandler):
    def get(self):
        params = dict(page='home')
        self.render('home.html', **params)

    @gen.coroutine
    def post(self):
        self.redirct('/')


class SearchPage(BaseHandler):
    @gen.coroutine
    def get(self):
        query = self.get_argument('q', default='')

        ranked_result = []
        err = None
        info = None
        if query:
            query_vec, query_len = get_word_vec(query)
            if len(query_vec) == 0:
                info = '請嘗試其他關鍵字'
            else:
                cmd = "SELECT * FROM words WHERE {};".format(' or '.join(['word=%s' for _ in range(0, len(query_vec))]))
                try:
                    cursor = yield self.db.execute(cmd, tuple(query_vec))
                    matched_words = cursor.fetchall()
                    if len(matched_words) == 0:
                        info = '找不到符合此關鍵字的文件'
                    else:
                        articles_vec = dict()
                        for word in matched_words:
                            text = word[0]
                            article_id = str(word[1])
                            count = word[2]

                            if not article_id in articles_vec:
                                articles_vec[article_id] = dict()

                            if not text in articles_vec[article_id] or count > articles_vec[article_id][text]:
                                articles_vec[article_id][text] = count

                        # get article metadata
                        cmd = "SELECT * FROM articles WHERE article_id in ({});".format(','.join(articles_vec.keys()))
                        cursor = yield self.db.execute(cmd)
                        articles = cursor.fetchall()

                        # calculate cosine similarity
                        for article in articles:
                            article_id = str(article[0])
                            title = article[3]
                            url = article[4]
                            cache = article[5]
                            length = article[6]
                            score = article[8]

                            a = articles_vec[article_id]
                            sim = 0
                            for word, count in a.items():
                                sim += query_vec[word] * count

                            sim = sim / (query_len * length)
                            ranked_result.append([url, title, sim, cache.replace('data', '/article'), score])

                        # sort by similarity
                        ranked_result = sorted(ranked_result, key=lambda k: k[2], reverse=True)
                except Exception as error:
                    print(error)
                    err = '伺服器發生錯誤'
        else:
            info = '無搜尋結果'

        result_len = 50 if len(ranked_result) > 50 else len(ranked_result)
        params = dict(page="search", articles=ranked_result[:result_len], query=query, err=err, info=info)
        self.render("search.html", **params)
