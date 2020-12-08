from flask import Flask, request, render_template, jsonify
import sqlite3
import hashlib

app = Flask(__name__)
 # или :memory: чтобы сохранить в RAM


@app.route("/reg")
def register():
    if len(list(set(["Login", "Password"]) & set(list(request.headers.keys())))) != 2:
        return jsonify({"Result": "One or more parameter incorrect"})
    if request.headers["login"] == "" or request.headers["password"] == "":
        return jsonify({"Result": "One of field missed"})

    conn = sqlite3.connect("db.db")
    cursor = conn.cursor()
    username = cursor.execute(f"""SELECT login FROM Users
                                  WHERE login = '{request.headers["login"]}'""").fetchall()
    if (len(username) > 0):
        return jsonify({"Result": "Login exist"})
    cursor.execute(f"""INSERT INTO Users (login, nickname, password, money, win, lose) VALUES ('{request.headers["login"]}', '{request.headers["login"]}', '{hashlib.sha256(str(request.headers["password"]).encode()).hexdigest()}', 1500, 0, 0)""")
    conn.commit()
    return jsonify({"Result": "OK"});

@app.route("/login")
def login():
    conn = sqlite3.connect("db.db")
    cursor = conn.cursor()
    username = cursor.execute(f"""SELECT * FROM Users
                                  WHERE login = '{request.headers["login"]}'""").fetchone()
    if username is None:
        return jsonify({"Result": "User not found"})
    if not request.headers["password"] in username[1]:
        return jsonify({"Result": "User not found"})
    return jsonify({"Result": "OK"})


    cursor.execute(f"""INSERT INTO Users (login, nickname, password, money, win, lose) VALUES ('{request.headers["login"]}', '{request.headers["login"]}', '{request.headers["password"]}', 1500, 0, 0)""")
    conn.commit()
    return jsonify({"Result": "OK"});


@app.route("/get")
def getUserData():
    conn = sqlite3.connect("db.db")
    cursor = conn.cursor()
    user = cursor.execute(f"""SELECT * FROM Users
                                  WHERE login = '{request.headers["login"]}'""").fetchone()
    if user is None:
        return jsonify({"Result": "User not found"})
    if not request.headers["password"] in user[1]:
        return jsonify({"Result": "User not found"})
    print('reiojhqwefiuew')
    return jsonify({"Result": "OK", "money": user[2], "win": user[3], "lose": user[4], "nickname": user[7]})


@app.route("/change_nickname")
def change_nickname():
    conn = sqlite3.connect("db.db")
    cursor = conn.cursor()
    if len(list(set(["Login", "Password", "Nickname"]) & set(list(request.headers.keys())))) != 3:
        return jsonify({"Result": "One or more parameter incorrect"})
    if request.headers["login"] == "" or request.headers["password"] == "" or request.headers["nickname"] == "":
        return jsonify({"Result": "One or more param missed"})
    user = cursor.execute(f"""SELECT * FROM Users
                                      WHERE login = '{request.headers["login"]}'""").fetchone()
    if user is None:
        return jsonify({"Result": "User not found"})
    if not request.headers["password"] in user[1]:
        return jsonify({"Result": "User not found"})

    if user[2] <= 50:
        return jsonify({"Result": "You have not enough money"})
    cursor.execute(f"""UPDATE Users SET nickname = '{request.headers['nickname']}'
                                  WHERE login = '{request.headers["login"]}'""")
    conn.commit()
    return jsonify({"Result": "OK"})

@app.route("/change_password")
def change_password():
    conn = sqlite3.connect("db.db")
    cursor = conn.cursor()
    if len(list(set(["Login", "Password", "New-Password"]) & set(list(request.headers.keys())))) != 3:
        return jsonify({"Result": "One or more parameter incorrect"})
    if request.headers["login"] == "" or request.headers["password"] == "" or request.headers["new_password"] == "":
        return jsonify({"Result": "One or more param missed"})
    user = cursor.execute(f"""SELECT * FROM Users
                                      WHERE login = '{request.headers["login"]}'""").fetchone()
    if user is None:
        return jsonify({"Result": "User not found"})
    if not request.headers["password"] in user[1]:
        return jsonify({"Result": "User not found"})
    cursor.execute(f"""UPDATE Users SET password = '{request.headers['new_password']}'
                                  WHERE login = '{request.headers["login"]}'""")
    conn.commit()
    return jsonify({"Result": "OK"})


@app.route("/change_money")
def changeMoney():
    if len(list(set(["Target-Login", "Login", "Password", "Money"]) & set(list(request.headers.keys())))) != 4:
        return jsonify({"Result": "One or more parameters incorrect"})
    conn = sqlite3.connect("db.db")
    cursor = conn.cursor()
    user = cursor.execute(f"""SELECT * FROM Users
                                      WHERE login = '{request.headers["login"]}'""").fetchone()
    print(user)
    if user is None:
        return jsonify({"Result": "User not found"})
    if not request.headers["password"] in user[1]:
        return jsonify({"Result": "User not found"})
    if user[6] is None:
        return jsonify({"Result": "Could not access"})
    user = cursor.execute(f"""SELECT * FROM Users
                                          WHERE login = '{request.headers["target_login"]}'""").fetchone()
    if user is None:
        return jsonify({"Result": "Target user not found"})
    if user[2] + int(request.headers["money"]) < 0:
        return jsonify({"Result": "You have not enough money"})
    cursor.execute(f"""UPDATE Users SET money = {user[2] + int(request.headers["money"])}
                              WHERE login = '{request.headers["target_login"]}'""")
    conn.commit()
    return jsonify({"Result": "OK", "money": str(user[2] + int(request.headers["money"]))})

@app.route("/change_lose")
def changeLose():
    if len(list(set(["Target-Login", "Login", "Password"]) & set(list(request.headers.keys())))) != 3:
        return jsonify({"Result": "One or more parameters incorrect"})
    conn = sqlite3.connect("db.db")
    cursor = conn.cursor()
    user = cursor.execute(f"""SELECT * FROM Users
                                      WHERE login = '{request.headers["login"]}'""").fetchone()
    print(user)
    if user is None:
        return jsonify({"Result": "User not found"})
    if not request.headers["password"] in user[1]:
        return jsonify({"Result": "User not found"})
    if user[6] is None:
        return jsonify({"Result": "Could not access"})
    user = cursor.execute(f"""SELECT * FROM Users
                                          WHERE login = '{request.headers["target_login"]}'""").fetchone()
    if user is None:
        return jsonify({"Result": "Target user not found"})
    cursor.execute(f"""UPDATE Users SET lose = {user[4] + 1}
                              WHERE login = '{request.headers["target_login"]}'""")
    conn.commit()
    return jsonify({"Result": "OK", "lose": str(user[4] + 1)})

@app.route("/change_win")
def changeWin():
    if len(list(set(["Target-Login", "Login", "Password"]) & set(list(request.headers.keys())))) != 3:
        return jsonify({"Result": "One or more parameters incorrect"})
    conn = sqlite3.connect("db.db")
    cursor = conn.cursor()
    user = cursor.execute(f"""SELECT * FROM Users
                                      WHERE login = '{request.headers["login"]}'""").fetchone()
    print(user)
    if user is None:
        return jsonify({"Result": "User not found"})
    if not request.headers["password"] in user[1]:
        return jsonify({"Result": "User not found"})
    if user[6] is None:
        return jsonify({"Result": "Could not access"})
    user = cursor.execute(f"""SELECT * FROM Users
                                          WHERE login = '{request.headers["target_login"]}'""").fetchone()
    if user is None:
        return jsonify({"Result": "Target user not found"})
    cursor.execute(f"""UPDATE Users SET win = {user[3] + 1}
                              WHERE login = '{request.headers["target_login"]}'""")
    conn.commit()
    return jsonify({"Result": "OK", "win": str(user[3] + 1)})



if __name__ == '__main__':
    app.run("127.0.0.1")
