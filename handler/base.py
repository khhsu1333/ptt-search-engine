#!/usr/bin/env python3
# coding=utf-8
#
# Copyright 2015 Kuo Hsuan Hsu
import tornado.web


class BaseHandler(tornado.web.RequestHandler):
    def __init__(self, *a, **kw):
        tornado.web.RequestHandler.__init__(self, *a, **kw)
        self.jinja2 = self.settings.get('jinja2')

    def get_user_locale(self):
        user_locale = self.get_cookie('user_locale')
        if user_locale:
            return tornado.locale.get(user_locale)
        return None

    @property
    def db(self):
        return self.application.db

    @property
    def static_path(self):
        return self.application.settings['static_path']

    # Override this function for authentication
    def get_current_user(self):
        user_id = self.get_secure_cookie('user')
        if not user_id:
            return None
        #return self.user_model.get_user_by_uid(int(user_id))

    def render(self, template_name, **params):
        html = self.render_string(template_name, **params)
        self.write(html)

    def render_string(self, template_name, **params):
        params["static_url"] = self.static_url
        params["xsrf_form_html"] = self.xsrf_form_html
        params["current_user"] = self.current_user
        params["request"] = self.request
        params["_"] = self.locale.translate

        template = self.jinja2.get_template(template_name)
        return template.render(**params)

    def render_from_string(self, template_string, **params):
        template = self.jinja2.from_string(template_string)
        return template.render(**params)
