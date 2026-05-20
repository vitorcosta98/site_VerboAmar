from site_verbo_amar import app, render_template, lista_projetos

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/area-academica")
def area_academica():
    return render_template("area_academica.html")

@app.route("/cadastro")
def cadastro():
    return render_template("cadastro.html")