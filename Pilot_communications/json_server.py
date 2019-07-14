import json
import requests
import tornado.web
import tornado.httpserver
import tornado.ioloop

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        with open('pilot.json') as pilotcs:
            self.write(json.load(pilotcs))
def make_app():
    return tornado.web.Application([(r"/", MainHandler),])
    
if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
