from flask import Flask, request, render_template, jsonify
import sqlite3
import hashlib
import sys
from datetime import datetime

application = Flask(__name__)
 # или :memory: чтобы сохранить в RAM

@application.route("/")
def index():
    return """<!DOCTYPE html>
<html lang="en-us">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <title>Unity WebGL Player | Bomberman 2D</title>
    <link rel="shortcut icon" href="TemplateData/favicon.ico">
    <link rel="stylesheet" href="TemplateData/style.css">
  </head>
  <body>
    <div id="unity-container" class="unity-desktop">
      <canvas id="unity-canvas"></canvas>
      <div id="unity-loading-bar">
        <div id="unity-logo"></div>
        <div id="unity-progress-bar-empty">
          <div id="unity-progress-bar-full"></div>
        </div>
      </div>
      <div id="unity-footer">
        <div id="unity-webgl-logo"></div>
        <div id="unity-fullscreen-button"></div>
        <div id="unity-build-title">Bomberman 2D</div>
      </div>
    </div>
    <script>
      var buildUrl = "Build";
      var loaderUrl = buildUrl + "/WebBuild.loader.js";
      var config = {
        dataUrl: buildUrl + "/WebBuild.data",
        frameworkUrl: buildUrl + "/WebBuild.framework.js",
        codeUrl: buildUrl + "/WebBuild.wasm",
        streamingAssetsUrl: "StreamingAssets",
        companyName: "DefaultCompany",
        productName: "Bomberman 2D",
        productVersion: "1.0",
      };

      var container = document.querySelector("#unity-container");
      var canvas = document.querySelector("#unity-canvas");
      var loadingBar = document.querySelector("#unity-loading-bar");
      var progressBarFull = document.querySelector("#unity-progress-bar-full");
      var fullscreenButton = document.querySelector("#unity-fullscreen-button");

      if (/iPhone|iPad|iPod|Android/i.test(navigator.userAgent)) {
        container.className = "unity-mobile";
        config.devicePixelRatio = 1;
      } else {
        canvas.style.width = "960px";
        canvas.style.height = "600px";
      }
      loadingBar.style.display = "block";

      var script = document.createElement("script");
      script.src = loaderUrl;
      script.onload = () => {
        createUnityInstance(canvas, config, (progress) => {
          progressBarFull.style.width = 100 * progress + "%";
        }).then((unityInstance) => {
          loadingBar.style.display = "none";
          fullscreenButton.onclick = () => {
            unityInstance.SetFullscreen(1);
          };
        }).catch((message) => {
          alert(message);
        });
      };
      document.body.appendChild(script);
    </script>
  </body>
</html>
"""

@application.route("/root")
def root():
    conn = sqlite3.connect("db.db")
    cursor = conn.cursor()
    result = cursor.execute("""SELECT * FROM Users""").fetchall()
    return str(result)

@application.route("/reg")
def register():
    if len(list(set(["login", "password"]) & set(list(request.args.keys())))) != 2:
        return jsonify({"Result": "One or more parameter incorrect"})
    if request.args["login"] == "" or request.args["password"] == "":
        return jsonify({"Result": "One of field missed"})

    conn = sqlite3.connect("db.db")
    cursor = conn.cursor()
    username = cursor.execute(f"""SELECT login FROM Users
                                  WHERE login = '{request.args["login"]}'""").fetchall()
    if (len(username) > 0):
        return jsonify({"Result": "Login exist"})
    cursor.execute(f"""INSERT INTO Users (login, nickname, password, money, win, lose) VALUES ('{request.args["login"]}', '{request.args["login"]}', '{hashlib.sha256(str(request.args["password"]).encode()).hexdigest()}', 1500, 0, 0)""")
    conn.commit()
    return jsonify({"Result": "OK", "password": hashlib.sha256(str(request.args["password"]).encode()).hexdigest()})

@application.route("/login")
def login():
    conn = sqlite3.connect("db.db")
    cursor = conn.cursor()
    username = cursor.execute(f"""SELECT * FROM Users
                                  WHERE login = '{request.args["login"]}'""").fetchone()
    if username is None:
        return jsonify({"Result": "User not found"})
    if not hashlib.sha256(str(request.args["password"]).encode()).hexdigest() == username[1]:
        return jsonify({"Result": "User not found"})
    conn.commit()
    return jsonify({"Result": "OK", "password": hashlib.sha256(str(request.args["password"]).encode()).hexdigest()})


@application.route("/get")
def getUserData():
    conn = sqlite3.connect("db.db")
    cursor = conn.cursor()
    user = cursor.execute(f"""SELECT * FROM Users
                                  WHERE login = '{request.args["login"]}'""").fetchone()
    if user is None:
        return jsonify({"Result": "User not found"})
    if not request.args["password"] in user[1]:
        return jsonify({"Result": "User not found"})
    return jsonify({"Result": "OK", "money": user[2], "win": user[3], "lose": user[4], "nickname": user[7]})


@application.route("/change_nickname")
def change_nickname():
    conn = sqlite3.connect("db.db")
    cursor = conn.cursor()
    if len(list(set(["login", "password", "nickname"]) & set(list(request.args.keys())))) != 3:
        return jsonify({"Result": "One or more parameter incorrect"})
    if request.args["login"] == "" or request.args["password"] == "" or request.args["nickname"] == "":
        return jsonify({"Result": "One or more param missed"})
    user = cursor.execute(f"""SELECT * FROM Users
                                      WHERE login = '{request.args["login"]}'""").fetchone()
    if user is None:
        return jsonify({"Result": "User not found"})
    if not request.args["password"] in user[1]:
        return jsonify({"Result": "User not found"})

    if user[2] <= 50:
        return jsonify({"Result": "You have not enough money"})
    cursor.execute(f"""UPDATE Users SET nickname = '{request.args['nickname']}'
                                  WHERE login = '{request.args["login"]}'""")
    conn.commit()
    return jsonify({"Result": "OK"})

@application.route("/change_password")
def change_password():
    conn = sqlite3.connect("db.db")
    cursor = conn.cursor()
    if len(list(set(["login", "password", "new_password"]) & set(list(request.args.keys())))) != 3:
        return jsonify({"Result": "One or more parameter incorrect"})
    if request.args["login"] == "" or request.args["password"] == "" or request.args["new_password"] == "":
        return jsonify({"Result": "One or more param missed"})
    user = cursor.execute(f"""SELECT * FROM Users
                                      WHERE login = '{request.args["login"]}'""").fetchone()
    if user is None:
        return jsonify({"Result": "User not found"})
    if not request.args["password"] in user[1]:
        return jsonify({"Result": "User not found"})
    cursor.execute(f"""UPDATE Users SET password = '{hashlib.sha256(str(request.args["new_password"]).encode()).hexdigest()}'
                                  WHERE login = '{request.args["login"]}'""")
    conn.commit()
    return jsonify({"Result": "OK", "new_password": hashlib.sha256(str(request.args["new_password"]).encode()).hexdigest()})


@application.route("/change_money")
def changeMoney():
    if len(list(set(["target_login", "login", "password", "money"]) & set(list(request.args.keys())))) != 4:
        return jsonify({"Result": "One or more parameters incorrect"})
    conn = sqlite3.connect("db.db")
    cursor = conn.cursor()
    user = cursor.execute(f"""SELECT * FROM Users
                                      WHERE login = '{request.args["login"]}'""").fetchone()
    print(user)
    if user is None:
        return jsonify({"Result": "User not found"})
    if not request.args["password"] in user[1]:
        return jsonify({"Result": "User not found"})
    if user[6] is None:
        return jsonify({"Result": "Could not access"})
    user = cursor.execute(f"""SELECT * FROM Users
                                          WHERE login = '{request.args["target_login"]}'""").fetchone()
    if user is None:
        return jsonify({"Result": "Target user not found"})
    if user[2] + int(request.args["money"]) < 0:
        return jsonify({"Result": "You have not enough money"})
    cursor.execute(f"""UPDATE Users SET money = {user[2] + int(request.args["money"])}
                              WHERE login = '{request.args["target_login"]}'""")
    conn.commit()
    return jsonify({"Result": "OK", "money": str(user[2] + int(request.args["money"]))})

@application.route("/change_lose")
def changeLose():
    if len(list(set(["target_login", "login", "password"]) & set(list(request.args.keys())))) != 3:
        return jsonify({"Result": "One or more parameters incorrect"})
    conn = sqlite3.connect("db.db")
    cursor = conn.cursor()
    user = cursor.execute(f"""SELECT * FROM Users
                                      WHERE login = '{request.args["login"]}'""").fetchone()
    print(user)
    if user is None:
        return jsonify({"Result": "User not found"})
    if not request.args["password"] in user[1]:
        return jsonify({"Result": "User not found"})
    if user[6] is None:
        return jsonify({"Result": "Could not access"})
    user = cursor.execute(f"""SELECT * FROM Users
                                          WHERE login = '{request.args["target_login"]}'""").fetchone()
    if user is None:
        return jsonify({"Result": "Target user not found"})
    cursor.execute(f"""UPDATE Users SET lose = {user[4] + 1}
                              WHERE login = '{request.args["target_login"]}'""")
    conn.commit()
    return jsonify({"Result": "OK", "lose": str(user[4] + 1)})

@application.route("/change_win")
def changeWin():
    if len(list(set(["target_login", "login", "password"]) & set(list(request.args.keys())))) != 3:
        return jsonify({"Result": "One or more parameters incorrect"})
    conn = sqlite3.connect("db.db")
    cursor = conn.cursor()
    user = cursor.execute(f"""SELECT * FROM Users
                                      WHERE login = '{request.args["login"]}'""").fetchone()
    print(user)
    if user is None:
        return jsonify({"Result": "User not found"})
    if not request.args["password"] in user[1]:
        return jsonify({"Result": "User not found"})
    if user[6] is None:
        return jsonify({"Result": "Could not access"})
    user = cursor.execute(f"""SELECT * FROM Users
                                          WHERE login = '{request.args["target_login"]}'""").fetchone()
    if user is None:
        return jsonify({"Result": "Target user not found"})
    cursor.execute(f"""UPDATE Users SET win = {user[3] + 1}
                              WHERE login = '{request.args["target_login"]}'""")
    conn.commit()
    return jsonify({"Result": "OK", "win": str(user[3] + 1)})



if __name__ == '__main__':
    application.run("0.0.0.0")
