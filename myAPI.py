from flask import jsonify,Flask,request,session
import MyDatabase
import time
import json
from tornado.ioloop import IOLoop
from tornado.web import Application
from tornado.websocket import WebSocketHandler  
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer

class WebsocketBase(WebSocketHandler):
	# """继承WebSocketHandler基类，重写所需实例方法"""
    def on_message(self, message):
        """接收消息"""

    def data_received(self, chunk):
        """接收消息"""
        print (chunk)

    def open(self):
        """新的websocket连接后被调动"""
        print ('new_connect', self)

    def on_close(self):
        """websocket连接关闭后被调用"""
        print ('lost_connect', self)

    def check_origin(self, origin):
        """重写同源检查 解决跨域问题"""
        return True

ws_clients = []

class RealData(WebsocketBase):
    """实时数据"""
    def on_message(self, chunk):
  		# """args 是请求参数"""
  		# TODO 实际的业务操作,只需在此处写自己的业务逻辑即可。
        self.write_message('啦啦啦')		# 向客户端返回数据，如果是字典、列表这些数据类型，需要json.dumps()  
        print (chunk)
        print (self)
        ws_clients.append(self)


class WebSocketApplication(Application):
    def __init__(self):
        handlers = [
            (r'/real_data', RealData),        # websocket路由
        ]
        Application.__init__(self, handlers)



app = Flask(__name__)
WEBSOCKET_DICT = {}  
@app.route('/api/assign3/get_chatrooms', methods=['GET'])
def get_chatrooms():
        mydb = MyDatabase.MyDatabase()

        query = "SELECT * FROM chatrooms"
        mydb.cursor.execute(query)

        chatroom_list = mydb.cursor.fetchall()

        return jsonify(status="OK",data=chatroom_list)

@app.route('/api/assign3/get_messages', methods=['GET'])
def get_messages():
        mydb = MyDatabase.MyDatabase()
        message_list = []

        chatroom_id = request.args.get("chatroom_id", 0, type=int)
        page = request.args.get("page", 1, type=int)

        query = "SELECT chatroom_id,user_id,name,message,message_time FROM messages WHERE chatroom_id = %s ORDER BY  id desc"
        params = (chatroom_id)
        mydb.cursor.execute(query,params)

        count = 0
        total_page = 1
        count_msg = 0
        while 1:
                message = mydb.cursor.fetchone()
                if message is None :
                        break
                else :
                        message_list.append(message)
                count+=1

                if count > 10*total_page:
                        total_page = total_page + 1
                if count > 10:
                        count_msg = count - (total_page-1)*10
                else:
                        count_msg+=1

        chat_message = []
        if page == total_page:
                for j in range(count_msg):
                        chat_message.append(message_list[(page-1)*10+j])
        elif page < total_page:
                for i in range(10):
                                chat_message.append(message_list[(page-1)*10+i])
        databean = { "current_page": page, "totals_pages": total_page, "messages": chat_message}
        return jsonify(status="OK",data=databean)

@app.route('/api/assign3/send_message', methods=['POST'])
def send_message():
        mydb = MyDatabase.MyDatabase()
        msg = request.form.get("message")
        name = request.form.get("name")
        chatroom_id = request.form.get("chatroom_id")
        user_id = request.form.get("user_id")
        # WEBSOCKET_DICT[user_id] = ws
        if msg == None or chatroom_id == None or chatroom_id == '' or not chatroom_id.isdigit() or name == None or user_id == None :
                return jsonify(status="ERROR", message="missing parameters")
        else :
                insert_query = "INSERT INTO messages (chatroom_id,user_id,name,message,message_time) VALUES (%s,%s,%s,%s,%s)"

                params = (chatroom_id,user_id,name,msg,time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()+8*3600)))
                mydb.cursor.execute(insert_query,params)
                mydb.db.commit()
        #       for conn in WEBSOCKET_DICT.values():
        #               conn.send(json.dumps({'data':'new message'}))

                for cli in ws_clients:
                        cli.write_message(msg)
                return jsonify(status="OK" )
 
    
def run():
    websocketApp = WebSocketApplication()
    container = WSGIContainer(app)
    websocketApp.listen(port=8002, address='0.0.0.0')
    http_server = HTTPServer(container)
    http_server.listen(8001)
    IOLoop.current().start() 
if __name__ == '__main__':
        run()
        
        #http_server = WSGIServer(('0.0.0.0', 8002), app, handler_class=WebSocketHandler)
        #http_server.serve_forever()