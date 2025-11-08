from flask import Flask, render_template, request, redirect, flash
import db

app = Flask(__name__)
app.secret_key = "01102007"  # Necesario para flash (mensajes)

# Página principal - Menú inicial
@app.route("/")
def menu():
    return render_template("home.html")

# Página donde se muestran categorías
@app.route("/categoria/<categoria>")
def categoria(categoria):
    productos = db.obtener_por_categoria(categoria)
    return render_template("categoria.html", categoria=categoria, productos=productos)

# Agregar producto dentro de una categoría
@app.route("/agregar/<categoria>", methods=["GET","POST"])
def agregar(categoria):
    if request.method == "POST":
        nombre = request.form["nombre"]
        cantidad = request.form["cantidad"]

        # Se envían valores vacíos para los campos que ya no usamos
        db.agregar_producto(
            nombre,
            categoria,
            cantidad,
            "",   # ubicacion
            "",   # marca
            None  # fecha_caducidad
        )

        return redirect(f"/categoria/{categoria}")
    
    return render_template("agregar.html", categoria=categoria)


# Listado de recetas
@app.route("/recetas")
def recetas():
    lista = db.obtener_recetas()
    return render_template("recetas.html", recetas=lista)

# Página de una receta específica
@app.route("/receta/<int:id>")
def receta(id):
    receta = db.obtener_receta(id)
    ingredientes = db.obtener_ingredientes_receta(id)
    return render_template("receta.html", receta=receta, ingredientes=ingredientes)

# Preparar receta (DESCONTAR ingredientes)
@app.route("/preparar/<int:id>")
def preparar(id):
    faltantes = db.preparar_receta(id)

    if faltantes:
        flash("No hay suficientes ingredientes: " + ", ".join(faltantes), "error")
        return redirect(f"/receta/{id}")  # Volver a la receta donde se muestra el mensaje

    flash("Receta preparada con éxito ✅", "success")
    return redirect(f"/receta/{id}")

@app.route("/agregar_receta", methods=["GET", "POST"])
def agregar_receta():
    if request.method == "POST":
        nombre = request.form["nombre"]
        ingredientes = request.form.getlist("ingrediente[]")
        cantidades = request.form.getlist("cantidad[]")

        receta_id = db.crear_receta(nombre)

        for ing, cant in zip(ingredientes, cantidades):
            db.agregar_ingrediente_a_receta(receta_id, ing, cant)

        return redirect("/recetas")

    inventario = db.obtener_inventario()
    return render_template("agregar_receta.html", inventario=inventario)


# Página de categorías (inventario general)
@app.route("/categorias")
def categorias():
    inventario = db.obtener_inventario()
    return render_template("index.html", inventario=inventario)

@app.route("/sumar/<nombre>", methods=["POST"])
def sumar(nombre):
    cantidad = int(request.form.get("cantidad", 1))  # ← evita el error KeyError
    db.sumar_producto(nombre, cantidad)
    return redirect(request.referrer)

@app.route("/restar/<nombre>", methods=["POST"])
def restar(nombre):
    db.restar_producto(nombre, 1)
    categoria = request.referrer.split("/")[-1]  # vuelve a la categoría actual
    return redirect(f"/categoria/{categoria}")




if __name__ == "__main__":
    app.run(debug=True)
