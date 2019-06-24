import socket
import urllib.parse

import _thread

from utils import log
# 需要加前缀 import utils
# 错的
# import utils.log
# utils.log()

from routes import error
from routes import route_dict


# 定义一个 class 用于保存请求的数据
class Request(object):
    def __init__(self, r):
        self.raw_data = r
        # 只能 split 一次，因为 body 中可能有换行
        # 把 body 放入 request 中
        header, self.body = r.split('\r\n\r\n', 1)
        h = header.split('\r\n')
        parts = h[0].split()
        self.path = parts[1]
        # 设置 request 的 method
        self.method = parts[0]

        self.path, self.query = parsed_path(self.path)
        log('path 和 query', self.path, self.query)

    def form(self):
        body = urllib.parse.unquote_plus(self.body)
        log('form', self.body)
        log('form', body)
        args = body.split('&')
        f = {}
        log('args', args)
        for arg in args:
            k, v = arg.split('=')
            f[k] = v
        log('form() 字典', f)
        return f


def parsed_path(path):
    """
    输入: /min?message=hello&author=min
    返回
    (/min, {
        'message': 'hello',
        'author': 'min',
    })
    """
    index = path.find('?')
    if index == -1:
        return path, {}
    else:
        p = path[:index]
        query_string = path[index + 1:]
        args = query_string.split('&')
        query = {}
        for arg in args:
            k, v = arg.split('=')
            query[k] = v
        return p, query


def request_from_connection(connection):
    request = b''
    buffer_size = 1024
    while True:
        r = connection.recv(buffer_size)
        request += r
        # 取到的数据长度不够 buffer_size 的时候，说明数据已经取完了。
        if len(r) < buffer_size:
            request = request.decode()
            log('request\n {}'.format(request))
            return request


def response_for_request(request):
    """
    根据 path 调用相应的处理函数
    没有处理的 path 会返回 404
    """

    r = route_dict()
    response = r.get(request.path, error)
    # return response()
    # return route_index(request)
    return response(request)


def process_connection(connection):
    with connection:
        r = request_from_connection(connection)
        # 因为 chrome 会发送空请求导致 split 得到空 list
        # 所以这里判断一下防止程序崩溃
        if len(r) > 0:
            request = Request(r)
            # 用 response_for_path 函数来得到 path 对应的响应内容
            response = response_for_request(request)
            # 把响应发送给客户端
            connection.sendall(response)
        else:
            connection.sendall(b'')
            log('接收到了一个空请求')


def run(host, port):
    """
    启动服务器
    """
    # 初始化 socket 套路
    # 使用 with 可以保证程序中断的时候正确关闭 socket 释放占用的端口
    log('开始运行于', 'http://{}:{}'.format(host, port))
    with socket.socket() as s:
        s.bind((host, port))
        # 无限循环来处理请求
        # 监听 接受 读取请求数据 解码成字符串
        s.listen()
        while True:
            connection, address = s.accept()
            log('ip <{}>\n'.format(address))
            _thread.start_new_thread(process_connection, (connection,))
            # with connection:
            #     r = request_from_connection(connection)
            #     # 因为 chrome 会发送空请求导致 split 得到空 list
            #     # 所以这里判断一下防止程序崩溃
            #     if len(r) > 0:
            #         request = Request(r)
            #         # 用 response_for_path 函数来得到 path 对应的响应内容
            #         response = response_for_request(request)
            #         # 把响应发送给客户端
            #         connection.sendall(response)
            #     else:
            #         connection.sendall(b'')
            #         log('接收到了一个空请求')


if __name__ == '__main__':
    # 生成配置并且运行程序
    # http://localhost:3000/
    config = dict(
        host='localhost',
        port=3000,
    )
    run(**config)
