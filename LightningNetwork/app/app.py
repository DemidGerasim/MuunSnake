from flask import Flask, render_template
app = Flask(__name__)
application = app

@app.route('/')
def index():
    return render_template ('index.html')

@app.route('/posts')
def posts():
    return render_template ('posts.html')

@app.route('/plagiat')
def plagiat():
    return render_template ('plagiat.html')