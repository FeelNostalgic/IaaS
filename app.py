from flask import Flask, render_template, request, redirect

from Backend.errorEnums import UserLoginError, UserCreationError, S3UploadError
from Backend.userController import UserController
from Backend.usersFunctionality import UsersFunctionality

app = Flask(__name__)
user_controller = UserController()
users_functionality = UsersFunctionality()

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template("index.html")

@app.route('/profile', methods=['GET', 'POST'])
def login():
    if(request.method == 'POST'):
        username = request.form['username']
        password = request.form['password']
        response = user_controller.login_user(username, password)
        if response ==  UserLoginError.NONE:
            messages_received = user_controller.get_user_messages()
            return render_template("messages.html", messages = messages_received)

@app.route('/logout', methods=['GET', 'POST'])
def messages():
    if(request.method == 'GET'):
        user_controller.logout_user()
        return redirect("/")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if (request.method == 'GET'):
        return render_template("signup.html")
    if(request.method == 'POST'):
        username = request.form['username']
        password = request.form['password']
        full_name = request.form['full_name']
        response = user_controller.register_user(username, password, full_name)
        if response == UserCreationError.NONE:
            return render_template("index.html")

@app.route('/sendMessage', methods=['GET', 'POST'])
def sendMessage():
    if(request.method == 'GET'):
        users = UsersFunctionality.get_all_users()
        return render_template("sendMessage.html", users = users)
    if(request.method == 'POST'):
        username = request.form['username']
        message = request.form['message']
        #response = users_functionality.send_message_to_registered_user(username, message)
        response = users_functionality.send_large_message_to_registered_user(username, message)
        if response == S3UploadError.NONE:
            return redirect("/sendMessage")

    return render_template("sendMessage.html")

if __name__ == '__main__':
    app.run()
