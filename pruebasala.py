import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import mysql.connector
from tkcalendar import DateEntry
from datetime import date, datetime, time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from openpyxl import Workbook
from tkinter import filedialog


# Conexion con MySQL
def conectar():
    try:
        conexion = mysql.connector.connect(
            user='root',
            password='root',
            host='localhost',
            database='usuarioscoppel',
            port='3306'
        )
        return conexion
    except mysql.connector.Error as err:
        messagebox.showerror(
            "Error", f"Error al conectar a la base de datos: {err}")
        return None


# Inicio de sesión
def ventana_pantalla_sesion():
    global pantalla_sesion
    pantalla_sesion = tk.Tk()
    pantalla_sesion.title("Reservación de Sala de Juntas")
    pantalla_sesion.geometry("1440x960")
    pantalla_sesion.resizable(False, False)

    # Icono Coppel
    pantalla_sesion.iconbitmap("coppel_logo.ico")

    # Logo de Coppel
    logo = tk.PhotoImage(file="coppel_logo.png")
    logo_label = tk.Label(pantalla_sesion, image=logo)
    logo_label.pack(pady=20)

    # Título de la aplicación
    titulo_label = tk.Label(
        pantalla_sesion, text="RESERVACIÓN DE SALA DE JUNTAS", font=("Arial", 16))
    titulo_label.pack(pady=20)

    # Campo de entrada para el correo
    correo_label = tk.Label(
        pantalla_sesion, text="CORREO", font=("Arial", 12))
    correo_label.pack(pady=5)
    global correo_entry
    correo_entry = tk.Entry(pantalla_sesion, width=40, font=("Arial", 12))
    correo_entry.pack(pady=5)

    # Campo de entrada para la contraseña
    contrasena_label = tk.Label(
        pantalla_sesion, text="CONTRASEÑA", font=("Arial", 12))
    contrasena_label.pack(pady=5)
    global contrasena_entry
    contrasena_entry = tk.Entry(
        pantalla_sesion, show="*", width=40, font=("Arial", 12))
    contrasena_entry.pack(pady=5)

    # Botón de iniciar sesión
    iniciar_button = ttk.Button(
        pantalla_sesion, text="INICIAR", command=buscar)
    iniciar_button.pack(pady=20)

    # Ejecutar la ventana
    pantalla_sesion.mainloop()


# Buscar el usuario
def buscar():
    conexion = conectar()
    if conexion:
        cursor = conexion.cursor()
        sql = "SELECT * FROM usuarioscoppel.logincoppel WHERE correo=%s AND password=%s"
        cursor.execute(sql, (correo_entry.get(), contrasena_entry.get()))
        registro = cursor.fetchone()
        if registro:
            global idusuario
            idusuario = registro[0]  # Aquí obtenemos el idusuario
            messagebox.showinfo('Información', 'Iniciaste sesión')

            # Limpiar los campos de correo y contraseña después de iniciar sesión
            correo_entry.delete(0, tk.END)
            contrasena_entry.delete(0, tk.END)

            # Pasamos el nombre y el correo
            abrir_pantalla_principal(registro[1], registro[3])
        else:
            messagebox.showinfo('Error', 'Correo y contraseña incorrectos')
        conexion.close()
    else:
        messagebox.showerror(
            "Error", "No se pudo establecer la conexión con la base de datos.")


def abrir_pantalla_principal(nombre, correo):
    global pantalla_principal
    pantalla_sesion.withdraw()  # Ocultar la ventana de inicio de sesión

    # Crear la nueva ventana
    pantalla_principal = tk.Toplevel()
    pantalla_principal.title("Bienvenido")
    pantalla_principal.geometry("1440x960")
    pantalla_principal.resizable(False, False)

    # Logo
    logo = tk.PhotoImage(file="coppel_logo.png")
    logo_label = tk.Label(pantalla_principal, image=logo)
    logo_label.pack(pady=20)
    logo_label.image = logo  # Guardar la referencia de la imagen para que no se borre

    # Icono Coppel
    pantalla_principal.iconbitmap("coppel_logo.ico")

    # Texto de bienvenida
    bienvenido_label = tk.Label(
        pantalla_principal, text=f"BIENVENIDO {nombre.upper()}", font=("Arial", 16))
    bienvenido_label.pack(pady=20)

    # Botón de Reservar Sala
    reservar_button = ttk.Button(
        pantalla_principal, text="RESERVAR SALA", width=30, command=abrir_ventana_reserva)
    reservar_button.pack(pady=20)

    # Botón de Ver Mis Reservas
    ver_reservas_button = ttk.Button(
        pantalla_principal, text="VER MIS RESERVACIONES", width=30, command=ver_mis_reservaciones)
    ver_reservas_button.pack(pady=10)

    # Condición para mostrar el botón "Informe de salas" solo si el correo es 'joel@gmail.com'
    if correo == "joel@gmail.com":
        informe_salas_button = ttk.Button(
            pantalla_principal, text="INFORME DE SALAS", width=30, command=informe_salas)
        informe_salas_button.pack(pady=10)

    # Botón cerrar sesión
    cerrar_sesion_button = ttk.Button(pantalla_principal, text="Cerrar Sesión", width=30, command=lambda: [
                                      pantalla_principal.destroy(), pantalla_sesion.deiconify()])
    cerrar_sesion_button.pack(pady=10)


# Función para generar el informe de salas
def informe_salas():
    pantalla_principal.withdraw()
    # Crear la nueva ventana para el informe
    ventana_informe = tk.Toplevel()
    ventana_informe.title("Informe de Salas")
    ventana_informe.geometry("1440x960")
    ventana_informe.resizable(False, False)

    # Icono Coppel
    ventana_informe.iconbitmap("coppel_logo.ico")

    # Etiqueta para fecha de inicio
    tk.Label(ventana_informe, text="Fecha de Inicio:",
             font=("Arial", 12)).pack(pady=10)
    fecha_inicio_entry = DateEntry(ventana_informe, date_pattern='yyyy-mm-dd')
    fecha_inicio_entry.pack(pady=5)

    # Etiqueta para fecha final
    tk.Label(ventana_informe, text="Fecha Final:",
             font=("Arial", 12)).pack(pady=10)
    fecha_final_entry = DateEntry(ventana_informe, date_pattern='yyyy-mm-dd')
    fecha_final_entry.pack(pady=5)

    # Botón para generar el informe
    generar_button = ttk.Button(ventana_informe, text="Generar", command=lambda: generar_informe(
        fecha_inicio_entry.get(), fecha_final_entry.get(), ventana_informe))
    generar_button.pack(pady=20)

    # Botón "Atrás" para regresar a la pantalla principal
    boton_atras = ttk.Button(ventana_informe, text="Atrás", command=lambda: [
        ventana_informe.destroy(), pantalla_principal.deiconify()])
    boton_atras.pack(pady=10)


# Función para generar el informe basado en las fechas seleccionadas
def generar_informe(fecha_inicio, fecha_final, ventana_informe):
    conexion = conectar()
    if conexion:
        cursor = conexion.cursor()

        try:
            # Consulta para contar cuántas veces se ha usado cada sala en el rango de fechas
            sql = """
            SELECT sala, COUNT(*) AS veces_usada
            FROM usuarioscoppel.reservas
            WHERE fechainicio >= %s AND fechatermino <= %s
            GROUP BY sala
            """
            cursor.execute(sql, (fecha_inicio, fecha_final))
            resultados = cursor.fetchall()

            # Procesar resultados
            salas = []
            usos = []
            datos = []

            for fila in resultados:
                salas.append(fila[0])  # Sala
                usos.append(fila[1])  # Veces usada
                datos.append(fila)    # Para guardar en Excel

            # Si no hay datos para el rango seleccionado
            if not resultados:
                messagebox.showinfo(
                    "Información", "No se encontraron reservaciones en el rango de fechas seleccionado.")
                return

            # Generar la gráfica
            generar_grafica(salas, usos, datos, ventana_informe)

        except mysql.connector.Error as err:
            messagebox.showerror(
                "Error", f"No se pudo generar el informe: {err}")
        finally:
            cursor.close()
            conexion.close()
    else:
        messagebox.showerror(
            "Error", "No se pudo conectar con la base de datos.")


# Función para generar la gráfica de barras
def generar_grafica(salas, usos, datos, ventana_informe):
    # Crear la figura de matplotlib
    figura = plt.Figure(figsize=(6, 4), dpi=100)
    ax = figura.add_subplot(111)

    # Crear gráfico de barras
    ax.bar(salas, usos, color=['blue', 'green', 'red'])

    ax.set_title('Uso de Salas')
    ax.set_xlabel('Sala')
    ax.set_ylabel('Veces Usada')

    # Mostrar la gráfica en la ventana
    canvas = FigureCanvasTkAgg(figura, master=ventana_informe)
    canvas.draw()
    canvas.get_tk_widget().pack()

    # Botón para guardar la gráfica como PDF
    guardar_pdf_button = ttk.Button(
        ventana_informe, text="Guardar Gráfica en PDF", command=lambda: guardar_pdf(figura))
    guardar_pdf_button.pack(pady=10)

    # Botón para exportar los datos a Excel
    exportar_excel_button = ttk.Button(
        ventana_informe, text="Exportar Datos a Excel", command=lambda: exportar_excel(datos))
    exportar_excel_button.pack(pady=10)


# Función para exportar los datos a un archivo Excel (.xlsm)
def exportar_excel(datos):
    file_path = filedialog.asksaveasfilename(
        defaultextension=".xlsm", filetypes=[("Excel files", "*.xlsx")])
    if file_path:
        try:
            # Crear un DataFrame con los datos
            df = pd.DataFrame(datos, columns=['Sala', 'Veces Usada'])

            # Guardar el DataFrame como un archivo Excel
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Informe de Salas')

            messagebox.showinfo(
                "Éxito", "Los datos han sido exportados a Excel correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar a Excel: {e}")


# Función para guardar la gráfica como PDF
def guardar_pdf(figura):
    file_path = filedialog.asksaveasfilename(
        defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if file_path:
        figura.savefig(file_path)
        messagebox.showinfo(
            "Éxito", "La gráfica ha sido guardada en PDF correctamente.")


# Función que actualiza la fecha mínima de término
def actualizar_fecha_termino(*args):
    # Obtener la fecha seleccionada en el campo de fecha de inicio
    fecha_inicio = fecha_inicio_entry.get_date()
    # Establecer la nueva fecha mínima en el campo de fecha de término
    fecha_termino_entry.config(mindate=fecha_inicio)


# Función que crea la ventana de reserva
def abrir_ventana_reserva():
    global ventana_reserva
    pantalla_principal.withdraw()  # Ocultar la ventana de pantalla principal
    # Crear una nueva ventana
    ventana_reserva = tk.Toplevel()
    ventana_reserva.title("Reservación de Sala de Juntas")
    ventana_reserva.geometry("1440x960")
    ventana_reserva.resizable(False, False)

    # Logo de Coppel
    logo = tk.PhotoImage(file="coppel_logo.png")
    logo_label = tk.Label(ventana_reserva, image=logo)
    logo_label.pack(pady=20)
    logo_label.image = logo  # Evitar que se pierda la referencia de la imagen

    # Icono Coppel
    ventana_reserva.iconbitmap("coppel_logo.ico")

    # Crear variables para los campos de entrada
    global nombre_junta_entry
    nombre_junta_entry = tk.Entry(
        ventana_reserva, width=40, font=("Arial", 12))
    # Selectores de fecha
    global fecha_inicio_entry
    fecha_inicio_entry = DateEntry(
        ventana_reserva, width=40, font=("Arial", 12), date_pattern='y/mm/dd', mindate=date.today())

    global fecha_termino_entry
    fecha_termino_entry = DateEntry(
        ventana_reserva, width=40, font=("Arial", 12), date_pattern='y/mm/dd', mindate=date.today())

    global hora_inicio_entry
    hora_inicio_entry = tk.Entry(ventana_reserva, width=40, font=("Arial", 12))
    global hora_termino_entry
    hora_termino_entry = tk.Entry(
        ventana_reserva, width=40, font=("Arial", 12))
    hora_inicio_entry.insert(0, "07:00")  # Hora de inicio predeterminada

    global numero_personas_entry
    numero_personas_entry = tk.Entry(
        ventana_reserva, width=40, font=("Arial", 12))
    hora_termino_entry.insert(0, "18:00")  # Hora de término predeterminada

    # Crear los campos de entrada
    etiquetas = [
        ("NOMBRE DE LA JUNTA", nombre_junta_entry),
        ("FECHA DE INICIO", fecha_inicio_entry),
        ("FECHA DE TERMINO", fecha_termino_entry),
        ("HORA DE INICIO (Formato 24hr, hora minima 07:00)", hora_inicio_entry),
        ("HORA DE TERMINO (Formato 24hr, hora maxima 18:00)", hora_termino_entry),
        ("NUMERO DE PERSONAS", numero_personas_entry)
    ]

    for etiqueta, entry in etiquetas:
        label = tk.Label(ventana_reserva, text=etiqueta, font=("Arial", 12))
        label.pack(pady=5)
        entry.pack(pady=5)

    # Asociar el evento de cambio de fecha de inicio para actualizar la fecha mínima de término
    fecha_inicio_entry.bind("<<DateEntrySelected>>", actualizar_fecha_termino)

    # Mensaje de nota
    nota_label = tk.Label(
        ventana_reserva,
        text="NOTA: EL HORARIO ES ZONA CENTRO (CDMX)",
        font=("Arial", 10),
        fg="blue"
    )
    nota_label.pack(pady=10)

    # Botón de regresar
    atras_button = ttk.Button(
        ventana_reserva, text="ATRAS", command=lambda: [ventana_reserva.destroy(), pantalla_principal.deiconify()])
    atras_button.pack(side="left", padx=350, pady=10)

    # Botón de siguiente (Guardar los datos)
    siguiente_button = ttk.Button(
        ventana_reserva, text="SIGUIENTE", command=guardar_datos_reserva)
    siguiente_button.pack(side="left", padx=200, pady=20)


# Función para validar la hora de inicio y término
def validar_horario():
    hora_inicio = hora_inicio_entry.get()
    hora_termino = hora_termino_entry.get()

    # Convertir las horas a enteros para comparar
    try:
        hora_inicio_dt = datetime.strptime(
            hora_inicio, '%H:%M').time()
        hora_termino_dt = datetime.strptime(
            hora_termino, '%H:%M').time()
    except ValueError:
        messagebox.showerror(
            "Error de formato", "El formato de la hora debe ser HH:MM en formato de 24 horas.")
        return False
    # Rango de horas permitidas
    hora_min = time(7, 0)  # 07:00
    hora_max = time(18, 0)  # 18:00

    # Validar que las horas estén dentro del rango permitido
    if not (hora_min <= hora_inicio_dt <= hora_max):
        messagebox.showerror(
            "Error", "La hora de inicio debe estar entre las 07:00 y las 18:00.")
        return False
    if not (hora_min <= hora_termino_dt <= hora_max):
        messagebox.showerror(
            "Error", "La hora de término debe estar entre las 07:00 y las 18:00.")
        return False
    if hora_inicio_dt >= hora_termino_dt:
        messagebox.showerror(
            "Error", "La hora de inicio debe ser anterior a la hora de término.")
        return False
    return True


# Función para capturar los datos y almacenarlos en la base de datos
def guardar_datos_reserva():
    if validar_horario():
        # Declaramos globales para usarlas en el resto del codigo
        global id_usuario
        global nombre_junta
        global fecha_inicio
        global fecha_termino
        global hora_inicio
        global hora_termino
        global numero_personas

        # Obtener los valores de los campos de entrada
        id_usuario = idusuario
        nombre_junta = nombre_junta_entry.get()
        fecha_inicio = fecha_inicio_entry.get()
        fecha_termino = fecha_termino_entry.get()
        hora_inicio = hora_inicio_entry.get()
        hora_termino = hora_termino_entry.get()
        numero_personas = numero_personas_entry.get()

        # Validar que no estén vacíos
        if not nombre_junta or not fecha_inicio or not fecha_termino or not hora_inicio or not hora_termino or not numero_personas:
            messagebox.showerror(
                "Error", "Por favor, complete todos los campos")
        else:
            # Llamar a la función para guardar la reserva en la base de datos
            abrir_ventana_salas()
    else:
        # Si la validación falla, no se guardan los datos
        print("Error en los datos, no se guardó la reserva.")


# Función para abrir la ventana de salas disponibles
def abrir_ventana_salas():
    global ventana_salas
    ventana_reserva.withdraw()  # Ocultar la ventana de reserva
    ventana_salas = tk.Toplevel()
    ventana_salas.title("Salas Disponibles")
    ventana_salas.geometry("1440x960")
    ventana_salas.resizable(False, False)

    # Logo de Coppel
    logo = tk.PhotoImage(file="coppel_logo.png")
    logo_label = tk.Label(ventana_salas, image=logo)
    logo_label.pack(pady=20)
    logo_label.image = logo

    # Icono Coppel
    ventana_salas.iconbitmap("coppel_logo.ico")

    # Título de Salas Disponibles
    titulo_label = tk.Label(
        ventana_salas, text="SALAS DISPONIBLES", font=("Arial", 20, "bold"))
    titulo_label.pack(pady=20)

    # Crear el frame para las salas
    frame_salas = tk.Frame(ventana_salas)
    frame_salas.pack(pady=20)

    # Cargar y redimensionar las imágenes de las salas con Pillow
    sala1_img = Image.open("sala1.png").resize((300, 200))  # Ajustar tamaño
    sala2_img = Image.open("sala2.png").resize((300, 200))  # Ajustar tamaño
    sala3_img = Image.open("sala3.png").resize((300, 200))  # Ajustar tamaño

    # Convertir las imágenes redimensionadas a un formato compatible con Tkinter
    sala1_img = ImageTk.PhotoImage(sala1_img)
    sala2_img = ImageTk.PhotoImage(sala2_img)
    sala3_img = ImageTk.PhotoImage(sala3_img)

    # Botones de salas con imágenes redimensionadas
    boton_sala1 = tk.Button(frame_salas, text="SALA 1",
                            image=sala1_img, compound="top", command=abrir_ventana_sala1)
    boton_sala1.grid(row=0, column=0, padx=5)

    boton_sala2 = tk.Button(frame_salas, text="SALA 2",
                            image=sala2_img, compound="top", command=abrir_ventana_sala2)
    boton_sala2.grid(row=0, column=1, padx=5)

    boton_sala3 = tk.Button(frame_salas, text="SALA 3",
                            image=sala3_img, compound="top", command=abrir_ventana_sala3)
    boton_sala3.grid(row=0, column=2, padx=5)

    # Guardar referencias para evitar que el recolector de basura borre las imágenes
    boton_sala1.image = sala1_img
    boton_sala2.image = sala2_img
    boton_sala3.image = sala3_img

    # Botón de regresar
    atras_button = ttk.Button(
        ventana_salas, text="ATRAS", command=lambda: [ventana_salas.destroy(), ventana_reserva.deiconify()])
    atras_button.pack(pady=10)


def abrir_ventana_sala1():
    # Crear una nueva ventana
    global ventana_sala1
    global sala_1
    sala_1 = "sala1"
    ventana_salas.withdraw()
    ventana_sala1 = tk.Toplevel()
    ventana_sala1.title("Sala 1")
    ventana_sala1.geometry("1440x960")
    ventana_sala1.resizable(False, False)

    # Icono Coppel
    ventana_sala1.iconbitmap("coppel_logo.ico")

    # Configurar la primera sección de la ventana (Texto)
    texto_frame = tk.Frame(ventana_sala1, bg="blue")
    texto_frame.place(relwidth=0.5, relheight=1)

    # Texto de la sala
    titulo = tk.Label(texto_frame, text="SALA 1", font=(
        "Arial", 24), fg="white", bg="blue")
    titulo.pack(pady=20)

    descripcion = tk.Label(texto_frame, text=("Esta sala es perfecta para juntas con presentaciones "
                                              "que incluyan material audiovisual, cuenta con una "
                                              "excelente iluminación, dos pantallas blancas con dos proyectores. "
                                              "La capacidad máxima de esta sala es de 40 personas con mesas. "
                                              "Se ubica dentro de la bodega IZTP en el 4to piso subiendo "
                                              "por las escaleras principales."), font=("Arial", 12), fg="white", bg="blue", wraplength=350)
    descripcion.pack(padx=20, pady=10)

    # Botón de Confirmar
    confirmar_button = tk.Button(
        texto_frame, text="CONFIRMAR", command=guardar_reserva1)
    confirmar_button.pack(pady=20)

    # Botón de regresar
    atras_button = ttk.Button(
        texto_frame, text="ATRAS", command=lambda: [ventana_sala1.destroy(), ventana_salas.deiconify()])
    atras_button.pack(pady=20)

    # Configurar la segunda sección de la ventana (Imagen)
    imagen_frame = tk.Frame(ventana_sala1)
    imagen_frame.place(relx=0.5, relwidth=0.5, relheight=1)

    # Cargar la imagen
    imagen_sala1 = tk.PhotoImage(file="sala1.png")
    imagen_label = tk.Label(imagen_frame, image=imagen_sala1)
    # Esto es necesario para que la imagen no se descarte
    imagen_label.image = imagen_sala1
    imagen_label.pack(fill="both", expand=True)


def abrir_ventana_sala2():
    # Crear una nueva ventana
    global ventana_sala2
    global sala_2
    sala_2 = "sala2"
    ventana_salas.withdraw()
    ventana_sala2 = tk.Toplevel()
    ventana_sala2.title("Sala 2")
    ventana_sala2.geometry("1440x960")
    ventana_sala2.resizable(False, False)

    # Icono Coppel
    ventana_sala2.iconbitmap("coppel_logo.ico")

    # Configurar la primera sección de la ventana (Texto)
    texto_frame = tk.Frame(ventana_sala2, bg="blue")
    texto_frame.place(relwidth=0.5, relheight=1)

    # Texto de la sala
    titulo = tk.Label(texto_frame, text="SALA 2", font=(
        "Arial", 24), fg="white", bg="blue")
    titulo.pack(pady=20)

    descripcion = tk.Label(texto_frame, text=("Esta sala es perfecta para juntas"
                                              "donde se busca dialogar y buscar"
                                              "soluciones y propuestas. Cuenta con"
                                              "una excelente iluminación, pizarrón y"
                                              "un proyector donde podrán exponer"
                                              "mejor sus ideas los participantes. Su"
                                              "capacidad es de 15 personas con una"
                                              "mesa ovalada. Se ubica dentro de la"
                                              "bodega IZTP en el 1er piso."), font=("Arial", 12), fg="white", bg="blue", wraplength=350)
    descripcion.pack(padx=20, pady=10)

    # Botón de Confirmar
    confirmar_button = tk.Button(
        texto_frame, text="CONFIRMAR", command=guardar_reserva2)
    confirmar_button.pack(pady=20)

    # Botón de regresar
    atras_button = ttk.Button(
        texto_frame, text="ATRAS", command=lambda: [ventana_sala2.destroy(), ventana_salas.deiconify()])
    atras_button.pack(pady=20)

    # Configurar la segunda sección de la ventana (Imagen)
    imagen_frame = tk.Frame(ventana_sala2)
    imagen_frame.place(relx=0.5, relwidth=0.5, relheight=1)

    # Cargar la imagen
    imagen_sala2 = tk.PhotoImage(file="sala2.png")
    imagen_label = tk.Label(imagen_frame, image=imagen_sala2)
    # Esto es necesario para que la imagen no se descarte
    imagen_label.image = imagen_sala2
    imagen_label.pack(fill="both", expand=True)


def abrir_ventana_sala3():
    # Crear una nueva ventana
    global ventana_sala3
    global sala_3
    sala_3 = "sala3"
    ventana_salas.withdraw()
    ventana_sala3 = tk.Toplevel()
    ventana_sala3.title("Sala 3")

    # Configurar el tamaño de la ventana
    ventana_sala3.geometry("1440x960")
    ventana_sala3.resizable(False, False)

    # Icono Coppel
    ventana_sala3.iconbitmap("coppel_logo.ico")

    # Configurar la primera sección de la ventana (Texto)
    texto_frame = tk.Frame(ventana_sala3, bg="blue")
    texto_frame.place(relwidth=0.5, relheight=1)

    # Texto de la sala
    titulo = tk.Label(texto_frame, text="SALA 3", font=(
        "Arial", 24), fg="white", bg="blue")
    titulo.pack(pady=20)

    descripcion = tk.Label(texto_frame, text=("Esta sala es perfecta para juntas"
                                              "donde el diálogo será prioridad."
                                              "Cuenta con una excelente"
                                              "iluminación, un pizarrón, un proyector"
                                              "y un monitor donde podrán conectar"
                                              "una computadora para mayor"
                                              "comodidad. Su capacidad es de 7"
                                              "personas con una mesa larga. Se"
                                              "ubica dentro de la bodega IZTP"
                                              "dentro del área de RH."), font=("Arial", 12), fg="white", bg="blue", wraplength=350)
    descripcion.pack(padx=20, pady=10)

    # Botón de Confirmar
    confirmar_button = tk.Button(
        texto_frame, text="CONFIRMAR", command=guardar_reserva3)
    confirmar_button.pack(pady=20)

    # Botón de regresar
    atras_button = ttk.Button(
        texto_frame, text="ATRAS", command=lambda: [ventana_sala3.destroy(), ventana_salas.deiconify()])
    atras_button.pack(pady=20)

    # Configurar la segunda sección de la ventana (Imagen)
    imagen_frame = tk.Frame(ventana_sala3)
    imagen_frame.place(relx=0.5, relwidth=0.5, relheight=1)

    # Cargar la imagen
    imagen_sala3 = tk.PhotoImage(file="sala3.png")
    imagen_label = tk.Label(imagen_frame, image=imagen_sala3)
    # Esto es necesario para que la imagen no se descarte
    imagen_label.image = imagen_sala3
    imagen_label.pack(fill="both", expand=True)


# Función para almacenar la reserva en la base de datos
def guardar_reserva1():
    conexion = conectar()
    if conexion:
        cursor = conexion.cursor()

        # Consulta para verificar si la sala ya está reservada en las fechas seleccionadas
        try:
            sql_check = """SELECT * FROM reservas
                           WHERE sala = %s AND fechainicio <= %s AND fechatermino >= %s"""
            valores_check = (sala_1, fecha_termino, fecha_inicio)
            cursor.execute(sql_check, valores_check)
            conflicto = cursor.fetchone()

            if conflicto:
                # Si la consulta devuelve un registro, significa que hay un conflicto
                messagebox.showerror(
                    "Error", "La sala ya está reservada en las fechas seleccionadas.")
            else:
                # Si no hay conflictos, se procede a guardar la reserva
                sql_insert = """INSERT INTO reservas
                                (idusuario, nombrejunta, fechainicio, fechatermino,
                                 horainicio, horatermino, numeropersonas, sala)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
                valores_insert = (id_usuario, nombre_junta, fecha_inicio,
                                  fecha_termino, hora_inicio, hora_termino, numero_personas, sala_1)
                cursor.execute(sql_insert, valores_insert)
                conexion.commit()  # Guardar los cambios
                messagebox.showinfo("Éxito", "Reservación guardada con éxito")
                ventana_sala1.withdraw()
                mostrar_confirmacion()

        except mysql.connector.Error as err:
            messagebox.showerror(
                "Error", f"Error al guardar la reservación: {err}")
        finally:
            cursor.close()
            conexion.close()


def guardar_reserva2():
    conexion = conectar()
    if conexion:
        cursor = conexion.cursor()

        # Consulta para verificar si la sala ya está reservada en las fechas seleccionadas
        try:
            sql_check = """SELECT * FROM reservas
                           WHERE sala = %s AND fechainicio <= %s AND fechatermino >= %s"""
            valores_check = (sala_2, fecha_termino, fecha_inicio)
            cursor.execute(sql_check, valores_check)
            conflicto = cursor.fetchone()

            if conflicto:
                # Si la consulta devuelve un registro, significa que hay un conflicto
                messagebox.showerror(
                    "Error", "La sala ya está reservada en las fechas seleccionadas.")
            else:
                # Si no hay conflictos, se procede a guardar la reserva
                sql_insert = """INSERT INTO reservas
                                (idusuario, nombrejunta, fechainicio, fechatermino,
                                 horainicio, horatermino, numeropersonas, sala)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
                valores_insert = (id_usuario, nombre_junta, fecha_inicio,
                                  fecha_termino, hora_inicio, hora_termino, numero_personas, sala_2)
                cursor.execute(sql_insert, valores_insert)
                conexion.commit()  # Guardar los cambios
                messagebox.showinfo("Éxito", "Reservación guardada con éxito")
                ventana_sala2.withdraw()
                mostrar_confirmacion()

        except mysql.connector.Error as err:
            messagebox.showerror(
                "Error", f"Error al guardar la reservación: {err}")
        finally:
            cursor.close()
            conexion.close()


def guardar_reserva3():
    conexion = conectar()
    if conexion:
        cursor = conexion.cursor()

        # Consulta para verificar si la sala ya está reservada en las fechas seleccionadas
        try:
            sql_check = """SELECT * FROM reservas
                           WHERE sala = %s AND fechainicio <= %s AND fechatermino >= %s"""
            valores_check = (sala_3, fecha_termino, fecha_inicio)
            cursor.execute(sql_check, valores_check)
            conflicto = cursor.fetchone()

            if conflicto:
                # Si la consulta devuelve un registro, significa que hay un conflicto
                messagebox.showerror(
                    "Error", "La sala ya está reservada en las fechas seleccionadas.")
            else:
                # Si no hay conflictos, se procede a guardar la reserva
                sql_insert = """INSERT INTO reservas
                                (idusuario, nombrejunta, fechainicio, fechatermino,
                                 horainicio, horatermino, numeropersonas, sala)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
                valores_insert = (id_usuario, nombre_junta, fecha_inicio,
                                  fecha_termino, hora_inicio, hora_termino, numero_personas, sala_3)
                cursor.execute(sql_insert, valores_insert)
                conexion.commit()  # Guardar los cambios
                messagebox.showinfo("Éxito", "Reservación guardada con éxito")
                ventana_sala3.withdraw()
                mostrar_confirmacion()

        except mysql.connector.Error as err:
            messagebox.showerror(
                "Error", f"Error al guardar la reservación: {err}")
        finally:
            cursor.close()
            conexion.close()


# Función para mostrar los datos de confirmación
def mostrar_confirmacion():
    # Crear una nueva ventana para mostrar los datos confirmados
    ventana_confirmacion = tk.Toplevel()
    ventana_confirmacion.title("Confirmación de Reserva")
    ventana_confirmacion.geometry("1440x960")
    ventana_confirmacion.resizable(False, False)

    # Logo de Coppel
    logo = tk.PhotoImage(file="coppel_logo.png")
    logo_label = tk.Label(ventana_confirmacion, image=logo)
    logo_label.pack(pady=20)
    logo_label.image = logo  # Mantener la referencia para que no se descarte la imagen

    # Icono Coppel
    ventana_confirmacion.iconbitmap("coppel_logo.ico")

    # Mostrar los datos capturados
    datos_reserva = f"""
    ID de Usuario: {id_usuario}
    Nombre de la Junta: {nombre_junta}
    Fecha de Inicio: {fecha_inicio}
    Fecha de Término: {fecha_termino}
    Hora de Inicio: {hora_inicio}
    Hora de Término: {hora_termino}
    Número de Personas: {numero_personas}
    """

    datos_label = tk.Label(
        ventana_confirmacion, text=datos_reserva, font=("Arial", 14), justify="left")
    datos_label.pack(pady=10)

    # Botón para confirmar la reserva
    confirmar_button = tk.Button(ventana_confirmacion, text="Confirmar Reserva", command=lambda: [
                                 ventana_confirmacion.destroy(), pantalla_principal.deiconify()])
    confirmar_button.pack(pady=20)


def editar_reserva_seleccionada(reserva):
    ventana_reservas.withdraw()  # Ocultar la pantalla ver reservas
    ventana_editar = tk.Toplevel()
    ventana_editar.title("Editar Reservacion")
    ventana_editar.geometry("1440x960")
    # Evitar que se pueda redimensionar
    ventana_editar.resizable(False, False)

    # Icono Coppel
    ventana_editar.iconbitmap("coppel_logo.ico")

    # Etiquetas y campos de entrada para los datos
    tk.Label(ventana_editar, text="ID Reserva").pack(pady=5)
    entry_sala = tk.Entry(ventana_editar)
    entry_sala.pack(pady=5)
    entry_sala.insert(0, reserva[0])  # Insertar el valor actual de la sala

    tk.Label(ventana_editar, text="Nombre Junta").pack(pady=5)
    entry_nombre = tk.Entry(ventana_editar)
    entry_nombre.pack(pady=5)
    entry_nombre.insert(0, reserva[1])

    tk.Label(ventana_editar, text="Fecha Inicio").pack(pady=5)
    entry_fecha_inicio = DateEntry(
        ventana_editar, width=40, font=("Arial", 12), date_pattern='y-mm-dd')
    entry_fecha_inicio.pack(pady=5)
    entry_fecha_inicio.set_date(reserva[2])  # Mostrar la fecha existente

    tk.Label(ventana_editar, text="Fecha Término").pack(pady=5)
    entry_fecha_termino = DateEntry(
        ventana_editar, width=40, font=("Arial", 12), date_pattern='y-mm-dd')
    entry_fecha_termino.pack(pady=5)
    entry_fecha_termino.set_date(reserva[3])  # Mostrar la fecha existente

    # Modificar las horas al formatearlas a hh:mm
    tk.Label(ventana_editar, text="Hora Inicio (Formato 24hrs)").pack(pady=5)
    hora_inicio = datetime.strptime(reserva[4], "%H:%M:%S").strftime("%H:%M")
    entry_hora_inicio = tk.Entry(ventana_editar)
    entry_hora_inicio.pack(pady=5)
    entry_hora_inicio.insert(0, hora_inicio)

    tk.Label(ventana_editar, text="Hora Término (Formato 24hrs)").pack(pady=5)
    hora_termino = datetime.strptime(reserva[5], "%H:%M:%S").strftime("%H:%M")
    entry_hora_termino = tk.Entry(ventana_editar)
    entry_hora_termino.pack(pady=5)
    entry_hora_termino.insert(0, hora_termino)

    tk.Label(ventana_editar, text="Número de Personas").pack(pady=5)
    entry_num_personas = tk.Entry(ventana_editar)
    entry_num_personas.pack(pady=5)
    entry_num_personas.insert(0, reserva[6])

    # Función para validar las fechas
    def validar_fechas_y_guardar():
        # Obtener las fechas de los campos
        fecha_inicio = datetime.strptime(
            entry_fecha_inicio.get(), '%Y-%m-%d').date()
        fecha_termino = datetime.strptime(
            entry_fecha_termino.get(), '%Y-%m-%d').date()
        fecha_actual = datetime.today().date()

        # Validar que la fecha de inicio no sea menor al día de hoy
        if fecha_inicio < fecha_actual:
            messagebox.showerror(
                "Error", "La fecha de inicio no puede ser menor al día de hoy.")
            return

        # Validar que la fecha de término no sea menor a la fecha de inicio
        if fecha_termino < fecha_inicio:
            messagebox.showerror(
                "Error", "La fecha de término no puede ser menor a la fecha de inicio.")
            return

        # Si todo es válido, proceder a guardar los cambios
        guardar_cambios_reserva(
            reserva[0],  # ID de la reserva
            entry_nombre.get(),
            entry_fecha_inicio.get(),
            entry_fecha_termino.get(),
            entry_hora_inicio.get(),
            entry_hora_termino.get(),
            entry_num_personas.get(),
            ventana_editar  # Pasamos la ventana para cerrarla al guardar
        )

    # Botón para guardar los cambios
    tk.Button(ventana_editar, text="Guardar Cambios",
              command=validar_fechas_y_guardar).pack(pady=20)

    # Botón Atras
    tk.Button(ventana_editar, text="Atras",
              command=lambda: [ventana_editar.destroy(), ventana_reservas.deiconify()]).pack(pady=20)


def guardar_cambios_reserva(id_reserva, nombre_junta, fecha_inicio, fecha_termino, hora_inicio, hora_termino, num_personas, ventana_editar):
    # Convertir las horas de inicio y término a objetos time
    try:
        hora_inicio_time = datetime.strptime(hora_inicio, "%H:%M").time()
        hora_termino_time = datetime.strptime(hora_termino, "%H:%M").time()
    except ValueError:
        messagebox.showerror(
            "Error", "Formato de hora incorrecto. Usa HH:MM (24 horas).")
        return

    # Definir el rango permitido
    hora_inicio_permitida = time(7, 0)  # 06:00
    hora_termino_permitida = time(18, 0)  # 18:00

    # Validar que la hora esté dentro del rango permitido
    if not (hora_inicio_permitida <= hora_inicio_time <= hora_termino_permitida):
        messagebox.showerror(
            "Error", "La hora de inicio debe estar entre 06:00 y 18:00.")
        return

    if not (hora_inicio_permitida <= hora_termino_time <= hora_termino_permitida):
        messagebox.showerror(
            "Error", "La hora de término debe estar entre 06:00 y 18:00.")
        return

    if hora_termino_time <= hora_inicio_time:
        messagebox.showerror(
            "Error", "La hora de término debe ser posterior a la hora de inicio.")
        return

    conexion = conectar()
    if conexion:
        cursor = conexion.cursor()
        try:
            # Actualizar la reserva en la base de datos
            sql = """
            UPDATE usuarioscoppel.reservas
            SET nombrejunta = %s, fechainicio = %s, fechatermino = %s,
                horainicio = %s, horatermino = %s, numeropersonas = %s
            WHERE idreservas = %s
            """
            valores = (nombre_junta, fecha_inicio, fecha_termino,
                       hora_inicio, hora_termino, num_personas, id_reserva)
            cursor.execute(sql, valores)
            conexion.commit()

            messagebox.showinfo("Éxito", "Reserva actualizada correctamente.")
            ventana_editar.destroy()  # Cerrar la ventana de edición
            ver_mis_reservaciones()
        except mysql.connector.Error as err:
            messagebox.showerror(
                "Error", f"Error al actualizar reserva: {err}")
        finally:
            cursor.close()
            conexion.close()


# Funcion para ver las reservas, dentro se puede editar y cancelar una reunion
def ver_mis_reservaciones():
    conexion = conectar()
    if conexion:
        cursor = conexion.cursor()
        try:
            sql = "SELECT * FROM reservas WHERE idusuario = %s AND fechainicio >= CURDATE()"
            cursor.execute(sql, (idusuario,))
            reservas = cursor.fetchall()

            if not reservas:
                messagebox.showinfo("Información", "No tienes reservaciones.")
            else:
                pantalla_principal.withdraw()  # Ocultar la pantalla principal
                global ventana_reservas
                ventana_reservas = tk.Toplevel()
                ventana_reservas.title("Mis Reservaciones")

                # Fijar el tamaño de la ventana a 1440x960
                ventana_reservas.geometry("1440x960")
                # Evitar que se pueda redimensionar
                ventana_reservas.resizable(False, False)

                # Logo de Coppel
                logo = tk.PhotoImage(file="coppel_logo.png")
                logo_label = tk.Label(ventana_reservas, image=logo)
                logo_label.pack(pady=20)
                logo_label.image = logo

                # Icono Coppel
                ventana_reservas.iconbitmap("coppel_logo.ico")

                # Agregar un marco para contener la tabla
                frame_tabla = tk.Frame(ventana_reservas)
                frame_tabla.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

                # Añadir barras de desplazamiento si es necesario
                scrollbar_y = tk.Scrollbar(frame_tabla, orient=tk.VERTICAL)
                scrollbar_x = tk.Scrollbar(frame_tabla, orient=tk.HORIZONTAL)

                # Tabla para mostrar las reservaciones
                columnas = ("ID de Reserva", "Nombre Junta", "Fecha Inicio", "Fecha Término",
                            "Hora Inicio", "Hora Término", "Número de Personas", "Sala")
                tree = ttk.Treeview(
                    frame_tabla, columns=columnas, show='headings', yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

                # Configurar barras de desplazamiento
                scrollbar_y.config(command=tree.yview)
                scrollbar_x.config(command=tree.xview)
                scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
                scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

                # Definir el ancho de cada columna para que se ajuste a la ventana (ancho total = 1440)
                ancho_total = 1440 - 40  # Descontar márgenes/padding
                # Dividir el ancho entre las columnas
                ancho_columna = ancho_total // len(columnas)

                # Configurar columnas para que ocupen todo el ancho de la ventana
                for col in columnas:
                    tree.heading(col, text=col)
                    tree.column(col, width=ancho_columna,
                                minwidth=100, stretch=True)

                tree.pack(fill=tk.BOTH, expand=True)

                # Insertar las reservaciones en la tabla
                for reserva in reservas:
                    tree.insert("", tk.END, values=(reserva[0], reserva[2], reserva[3],
                                                    reserva[4], reserva[5], reserva[6], reserva[7], reserva[8]))

                # Función para ir "Atrás"
                def volver_atras():
                    ventana_reservas.destroy()
                    pantalla_principal.deiconify()

                # Función para editar una reserva seleccionada
                def editar_reserva():
                    seleccion = tree.selection()
                    if seleccion:
                        reserva_seleccionada = tree.item(seleccion)["values"]
                        messagebox.showinfo(
                            "Editar Reserva", f"Editarás la reserva: {reserva_seleccionada}")
                        editar_reserva_seleccionada(reserva_seleccionada)
                        # Aquí puedes agregar la lógica para editar la reserva
                        # Por ejemplo, abrir una ventana para modificar los datos de la reserva.
                    else:
                        messagebox.showwarning(
                            "Advertencia", "Selecciona una reservación para editar.")

                # Función para cancelar una reserva seleccionada
                def cancelar_reserva():
                    seleccion = tree.selection()
                    if seleccion:
                        reserva_seleccionada = tree.item(seleccion)["values"]
                        confirmacion = messagebox.askyesno(
                            "Confirmar", f"¿Estás seguro que deseas cancelar la reserva con ID: {reserva_seleccionada[0]}?")
                        if confirmacion:
                            try:
                                conexion = conectar()
                                if conexion:
                                    cursor = conexion.cursor()
                                    sql_cancelar = "DELETE FROM usuarioscoppel.reservas WHERE idreservas = %s"
                                    cursor.execute(
                                        sql_cancelar, (reserva_seleccionada[0],))
                                    conexion.commit()
                                    messagebox.showinfo(
                                        "Información", "Reserva cancelada exitosamente.")
                                    tree.delete(seleccion)
                            except mysql.connector.Error as err:
                                messagebox.showerror(
                                    "Error", f"No se pudo cancelar la reserva: {err}")
                    else:
                        messagebox.showwarning(
                            "Advertencia", "Selecciona una reservación para cancelar.")

                # Botones "Atrás", "Editar Reserva" y "Cancelar Reserva"
                botones_frame = tk.Frame(ventana_reservas)
                botones_frame.pack(pady=20)

                boton_atras = ttk.Button(
                    botones_frame, text="ATRÁS", command=volver_atras)
                boton_atras.grid(row=0, column=0, padx=10)

                boton_editar = ttk.Button(
                    botones_frame, text="EDITAR RESERVA", command=editar_reserva)
                boton_editar.grid(row=0, column=1, padx=10)

                boton_cancelar = ttk.Button(
                    botones_frame, text="CANCELAR RESERVA", command=cancelar_reserva)
                boton_cancelar.grid(row=0, column=2, padx=10)

        except mysql.connector.Error as err:
            messagebox.showerror(
                "Error", f"Error al cargar reservaciones: {err}")
        finally:
            cursor.close()
            conexion.close()


ventana_pantalla_sesion()
