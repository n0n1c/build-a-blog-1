#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import os
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)



class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class Post(db.Model):
    title = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

class MainPage(Handler):
    def get(self):
        posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC LIMIT 5")
        self.render("front.html", posts = posts)


class ViewPostHandler(Handler):
    def get(self, id):

        post = Post.get_by_id(int(id))
        if post:
            t = jinja_env.get_template("post.html")
            response = t.render(post=post)
        else:
            error = "there is no post with id %s" % id
            t = jinja_env.get_template("404.html")
            response = t.render(error=error)

        self.response.out.write(response)

class NewBlog(Handler):
    def get(self):
        self.render("newpost.html")

    def post(self):
        title = self.request.get("title")
        content = self.request.get("content")

        if title and content:
            post = Post(title = title, content = content)
            post.put()

            id = post.key().id()
            self.redirect('/blog/%s' % id)
        else:
            error = "We need both title and content!"
            self.render("newpost.html", title=title, content=content, error=error)



app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/blog', MainPage),
    ('/blog/newpost', NewBlog),
    (webapp2.Route('/blog/<id:\d+>', ViewPostHandler))
], debug=True)
