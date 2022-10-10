from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home_get():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def home_post():
    # print(request.form)
    val1 = request.form['first']
    val2 = request.form['second']
    val3 = request.form['third']
    val4 = request.form['fourth']
    val5 = request.form['fifth']
    result = float(val1) * float(val2) * float(val3) * float(val4) * float(val5)
    # print(result)
    return render_template('index.html', result= result, first= val1, second= val2, third= val3, fourth= val4, fifth= val5)

app.run(host='0.0.0.0')