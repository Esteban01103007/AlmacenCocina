import mysql.connector
import os

def conectar():
    return mysql.connector.connect(
        host=os.getenv("MYSQLHOST", "mysql.railway.internal"),
        port=os.getenv("MYSQLPORT", 3306),
        user=os.getenv("MYSQLUSER", "root"),
        password=os.getenv("MYSQLPASSWORD", "RHbIiAuamfVfclUqMipxsGAGkudfQiIY"),
        database=os.getenv("MYSQLDATABASE", "railway")
    )

def obtener_por_categoria(categoria):
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM inventario WHERE categoria = %s", (categoria,))
    datos = cursor.fetchall()
    conexion.close()
    return datos

def obtener_inventario():
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT nombre, cantidad FROM inventario")
    datos = cursor.fetchall()
    conexion.close()
    return datos

def agregar_producto(nombre, categoria, cantidad, ubicacion="Sin definir", marca="", fecha=""):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        INSERT INTO inventario (nombre, categoria, cantidad, ubicacion, marca, fecha_caducidad)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (nombre, categoria, cantidad, ubicacion, marca, fecha))
    conexion.commit()
    conexion.close()

def obtener_recetas():
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT id, nombre FROM recetas ORDER BY id DESC")
    datos = cursor.fetchall()
    conexion.close()
    return datos

def obtener_receta(id):
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM recetas WHERE id=%s", (id,))
    datos = cursor.fetchone()
    conexion.close()
    return datos

def obtener_ingredientes_receta(id):
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM recetas_ingredientes WHERE receta_id=%s", (id,))
    datos = cursor.fetchall()
    conexion.close()
    return datos

def preparar_receta(id):
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("SELECT ingrediente, cantidad_necesaria FROM recetas_ingredientes WHERE receta_id=%s", (id,))
    ingredientes = cursor.fetchall()
    faltantes = []

    for ing in ingredientes:
        cursor.execute("SELECT cantidad FROM inventario WHERE nombre=%s", (ing["ingrediente"],))
        stock = cursor.fetchone()

        if not stock or int(stock["cantidad"]) < int(ing["cantidad_necesaria"]):
            faltantes.append(f"{ing['ingrediente']} (falta {ing['cantidad_necesaria']})")

    if faltantes:
        conexion.close()
        return faltantes

    for ing in ingredientes:
        cursor.execute("""
            UPDATE inventario
            SET cantidad = cantidad - %s
            WHERE nombre = %s
        """, (ing["cantidad_necesaria"], ing["ingrediente"]))

    conexion.commit()
    conexion.close()
    return None
