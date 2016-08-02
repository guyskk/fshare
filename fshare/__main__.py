import re
import click
import subprocess
from os import listdir, makedirs, remove
from os.path import isfile, join, exists, abspath
from flask import Flask, Blueprint, request, current_app
from flask_restaction import Api, abort
from werkzeug.utils import secure_filename
from werkzeug import SharedDataMiddleware

LAN_IP = re.compile(r"inet\D*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})")


def create_app(server_address, shared_folder):
    app = Flask(__name__)
    if not exists(shared_folder):
        makedirs(shared_folder)
    app.add_url_rule('/shared/<filename>', 'shared', build_only=True)
    app.wsgi_app = SharedDataMiddleware(
        app.wsgi_app, {'/shared': shared_folder})
    bp_api = Blueprint("api", __name__)
    api = Api(bp_api)
    api.meta["$url_prefix"] = "/api"
    api.add_resource(Shared, server_address, shared_folder)
    app.register_blueprint(bp_api, url_prefix="/api")

    @app.route("/")
    def index():
        return app.send_static_file("index.html")

    return app


def get_lan_ip():
    """获取局域网IP"""
    ipbytes = subprocess.check_output(["ifconfig"])
    iplist = LAN_IP.findall(ipbytes.decode("utf-8"))
    ip_10 = ip_172 = ip_192 = None
    for ip in iplist:
        start, __, __, __ = ip.split('.')
        if start == "10":
            ip_10 = ip
        elif start == "172":
            ip_172 = ip
        elif start == "192":
            ip_192 = ip
    ip = ip_192 or ip_172 or ip_10
    return ip


class Shared:

    def __init__(self, server_address, shared_folder):
        self.server_address = server_address
        self.shared_folder = shared_folder

    def get_server_address(self):
        """
        获取服务器地址

        $output:
            url?url: 服务器地址
        """
        if self.server_address is None:
            abort(500, "Can't get LAN IP")
        else:
            return {"url": self.server_address}

    def post(self):
        """
        上传文件

        $output:
            - received files
            - name?str: filename
              saved?bool: the file saved or not
        $error:
            400.NoFile: 未收到文件
        """
        files = list(request.files.values())
        if not files:
            abort(400, "NoFile", "未收到文件")
        result = []
        for f in files:
            filename = secure_filename(f.filename)
            try:
                f.save(join(self.shared_folder, filename))
                result.append({"name": filename, "saved": True})
            except Exception as ex:
                current_app.logger.exception(ex)
                result.append({"name": filename, "saved": False})
        return result

    def get_list(self):
        """
        获取文件列表

        $output:
            - str&desc="filename"
        """
        files = [f for f in listdir(self.shared_folder)
                 if isfile(join(self.shared_folder, f))]
        return files

    def delete(self, name):
        """
        删除一个文件

        $input:
            name?str: filename
        $output:
            message?str: message
        """
        f = join(self.shared_folder, name)
        if isfile(f):
            remove(f)
            return {"message": "删除成功"}
        else:
            return {"message": "文件已删除"}


@click.command()
@click.option('--port', "-p", default=8080, help='server port')
@click.option('--shared', "-s", default='./shared', help='shared folder')
def main(port, shared):
    shared = abspath(shared)
    click.echo(" * Shared folder: %s" % shared)
    ip = get_lan_ip()
    if ip is None:
        click.echo(" * Can't get LAN IP")
        server_address = None
    else:
        click.echo(" * LAN IP: %s" % ip)
        server_address = "http://%s:%s" % (ip, port)
    app = create_app(server_address, shared)
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
