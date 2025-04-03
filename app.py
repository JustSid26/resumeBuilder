from flask import Flask, render_template, request
app = Flask(__name__)

about = 'This is a simple portfolio builder in which it will create a portfolio for you based on your inputs. The portfolio is also downloadable as a pdf. Try it, because it is free and convenient.'


@app.route("/")
def index():
    return render_template("index.html", about=about)

@app.route("/portfolio")
def portfolio_maker():
    return render_template("portfolio.html")

@app.route("/login")
def login_page():
    return render_template("login.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='10000', debug=True)