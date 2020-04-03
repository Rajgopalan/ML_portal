
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return 'hello, world!'

@app.route('/countme/<input_str>')
def count_me(input_str):
    return input_str

if __name__ == '__main__':
  app.run()
