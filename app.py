import re
import sh
from os import listdir, makedirs, remove
from os.path import isfile, join, exists
from flask import Flask, Blueprint, request
from flask_restaction import Api, abort
from werkzeug.utils import secure_filename
from werkzeug import SharedDataMiddleware


LAN_IP = re.compile(r"inet (\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})")
SHARED_FOLDER = "./shared"
PORT = 5000

app = Flask(__name__)
bp_api = Blueprint("api", __name__)
api = Api(bp_api)
api.meta["$url_prefix"] = "/api"

if not exists(SHARED_FOLDER):
    makedirs(SHARED_FOLDER)

app.add_url_rule('/shared/<filename>', 'shared', build_only=True)
app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {'/shared':  SHARED_FOLDER})


def get_lan_ip():
    """获取局域网IP"""
    iplist = LAN_IP.findall(str(sh.ifconfig()))
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
    if ip is None:
        raise ValueError("Can't get LAN IP")
    return ip


class Shared:

    def get_server_address(self):
        """
        获取服务器地址

        $output:
            url?url: 服务器地址
        """
        try:
            ip = get_lan_ip()
        except ValueError as ex:
            abort(500, str(ex))

        return {"url": "http://%s:%s" % (ip, PORT)}

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
                f.save(join(SHARED_FOLDER, filename))
                result.append({"name": filename, "saved": True})
            except Exception as ex:
                app.logger.exception(ex)
                result.append({"name": filename, "saved": False})
        return result

    def get_list(self):
        """
        获取文件列表

        $output:
            - str&desc="filename"
        """
        files = [f for f in listdir(SHARED_FOLDER)
                 if isfile(join(SHARED_FOLDER, f))]
        return files

    def delete(self, name):
        """
        删除一个文件

        $input:
            name?str: filename
        $output:
            message?str: message
        """
        f = join(SHARED_FOLDER, name)
        if isfile(f):
            remove(f)
            return {"message": "删除成功"}
        else:
            return {"message": "文件已删除"}

api.add_resource(Shared)
app.register_blueprint(bp_api, url_prefix="/api")


@app.route("/")
def index():
    return app.send_static_file("index.html")

app.run(host="0.0.0.0", port=PORT, debug=True)
