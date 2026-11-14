import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import serial
import time
import queue
import threading
import itertools
import os
import sys
import subprocess
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# ============================================================
# CONFIGURACIÓN Y VARIABLES GLOBALES
# ============================================================

PUERTO = 'COM12'
BAUDIOS = 57600
ID_CAMARA = 0  # Cambia a 1 si tu webcam tiene otro índice.
_proceso_camara = None

fpga = None
trayectoria = []
cola_envio = queue.PriorityQueue()
cola_entrada = queue.Queue()
_contador_envio = itertools.count()
_paro_solicitado = threading.Event()
_cerrando = threading.Event()

# Variables para control de trayectoria física
buffer_serial = ""
ejecutando_trayectoria_real = False
indice_trayectoria_real = 0

# Variable para velocidad de simulación (ms entre frames)
delay_simulacion = 800

# Seguimiento independiente de la simulación y ejecución física
historial_simulacion = []
historial_fisica = []

lbl_posicion = None


# ============================================================
# MATRIZ DE DENAVIT-HARTENBERG (DH ESTÁNDAR)
# ============================================================

def matriz_dh(theta, d, a, alpha):
    ct = np.cos(theta)
    st = np.sin(theta)
    ca = np.cos(alpha)
    sa = np.sin(alpha)

    return np.array([
        [ct, -st * ca,  st * sa, a * ct],
        [st,  ct * ca, -ct * sa, a * st],
        [0,   sa,       ca,      d],
        [0,   0,        0,       1]
    ], dtype=float)


# ============================================================
# TRANSFORMACIONES DH
# ============================================================

def calcular_transformaciones_dh(q_rad):
    # Convertir ángulos absolutos (del controlador físico) a ángulos relativos (para DH)
    theta_1 = q_rad[0]
    theta_2 = q_rad[1]
    theta_3 = q_rad[2] - q_rad[1]  # Restar el hombro al codo
    theta_4 = q_rad[3] - q_rad[2]  # Restar el codo a la muñeca
    theta_5 = q_rad[4]

    dh_params = [
        [theta_1, 25.4, 0, np.pi / 2],
        [theta_2, 0, 25.4, 0],
        [theta_3, 0, 25.4, 0],
        [theta_4 + np.pi / 2, 0, 0, np.pi / 2],
        [theta_5, 0, 0, 0]
    ]

    T = np.eye(4)
    transformaciones = [T.copy()]

    for theta, d, a, alpha in dh_params:
        T = T @ matriz_dh(theta, d, a, alpha)
        transformaciones.append(T.copy())

    return transformaciones


def calcular_puntos_articulaciones(q_rad):
    T_list = calcular_transformaciones_dh(q_rad)
    return np.array([T[:3, 3] for T in T_list])


# ============================================================
# FUNCIONES PARA DIBUJAR CILINDROS
# ============================================================

def dibujar_cilindro_eje(ax, p0, p1, radio=2.0, color='blue', alpha=0.9):
    v = np.array(p1, dtype=float) - np.array(p0, dtype=float)
    altura = np.linalg.norm(v)

    if altura < 1e-3:
        return

    v_norm = v / altura
    n_puntos = 16

    theta = np.linspace(0, 2 * np.pi, n_puntos)
    z = np.linspace(0, altura, 2)
    theta_grid, z_grid = np.meshgrid(theta, z)

    x_grid = radio * np.cos(theta_grid)
    y_grid = radio * np.sin(theta_grid)

    z_axis = np.array([0.0, 0.0, 1.0])

    if np.allclose(v_norm, z_axis):
        R = np.eye(3)
    elif np.allclose(v_norm, -z_axis):
        R = np.diag([1.0, -1.0, -1.0])
    else:
        axis = np.cross(z_axis, v_norm)
        axis_norm = np.linalg.norm(axis)
        if axis_norm < 1e-12:
            R = np.eye(3)
        else:
            axis = axis / axis_norm
            angle = np.arccos(np.clip(np.dot(z_axis, v_norm), -1.0, 1.0))
            K = np.array([
                [0, -axis[2], axis[1]],
                [axis[2], 0, -axis[0]],
                [-axis[1], axis[0], 0]
            ])
            R = np.eye(3) + np.sin(angle) * K + (1 - np.cos(angle)) * (K @ K)

    X = np.zeros_like(x_grid)
    Y = np.zeros_like(y_grid)
    Z = np.zeros_like(z_grid)

    for i in range(x_grid.shape[0]):
        for j in range(x_grid.shape[1]):
            pt = np.array([x_grid[i, j], y_grid[i, j], z_grid[i, j]])
            pt_rot = R @ pt + np.array(p0, dtype=float)
            X[i, j], Y[i, j], Z[i, j] = pt_rot

    ax.plot_surface(
        X, Y, Z,
        color=color,
        alpha=alpha,
        shade=True,
        edgecolor='none'
    )


def dibujar_articulacion_cilindro(ax, T_mat, largo=6.0, radio=3.5, color='darkred'):
    p0 = T_mat[:3, 3] - T_mat[:3, 2] * (largo / 2.0)
    p1 = T_mat[:3, 3] + T_mat[:3, 2] * (largo / 2.0)
    dibujar_cilindro_eje(ax, p0, p1, radio=radio, color=color, alpha=1.0)


# ============================================================
# ACTUALIZAR VISUALIZADOR 3D
# ============================================================

def actualizar_visor_3d(
    q_rad=(0, np.pi / 2, 0, 0, 0),
    indice=None,
    total=None,
    modo="Visualización",
    puntos_recorridos=None
):
    T_list = calcular_transformaciones_dh(q_rad)
    puntos = np.array([T[:3, 3] for T in T_list])

    ax.clear()
    ax.set_facecolor("#0f172a")
    for eje in (ax.xaxis, ax.yaxis, ax.zaxis):
        eje.pane.set_facecolor((0.06, 0.09, 0.15, 1.0))
        eje.pane.set_edgecolor("#334155")
        eje._axinfo["grid"]["color"] = (0.20, 0.27, 0.38, 0.65)
        eje._axinfo["grid"]["linewidth"] = 0.6
    ax.grid(True)


    # --------------------------------------------------------
    # Dibujar el plano de referencia
    # --------------------------------------------------------
    gx = np.linspace(-90, 90, 19)
    gy = np.linspace(-90, 90, 19)
    GX, GY = np.meshgrid(gx, gy)
    GZ = np.zeros_like(GX)

    ax.plot_wireframe(
        GX, GY, GZ,
        color='#334155',
        linewidth=0.5,
        alpha=0.5
    )

    # --------------------------------------------------------
    # Dibujar el robot
    # --------------------------------------------------------
    dibujar_cilindro_eje(
        ax, [0, 0, 0], puntos[1],
        radio=2.5, color='#38bdf8'
    )
    dibujar_cilindro_eje(
        ax, puntos[1], puntos[2],
        radio=2.2, color='#38bdf8'
    )
    dibujar_cilindro_eje(
        ax, puntos[2], puntos[3],
        radio=2.2, color='#38bdf8'
    )

    dibujar_articulacion_cilindro(
        ax, T_list[0], largo=10.0, radio=4.0, color='#f97316'
    )
    dibujar_articulacion_cilindro(
        ax, T_list[1], largo=7.0, radio=3.5, color='#f97316'
    )
    dibujar_articulacion_cilindro(
        ax, T_list[2], largo=7.0, radio=3.2, color='#f97316'
    )
    dibujar_articulacion_cilindro(
        ax, T_list[3], largo=6.0, radio=2.8, color='#f97316'
    )
    dibujar_articulacion_cilindro(
        ax, T_list[4], largo=5.0, radio=2.5, color='#f97316'
    )

    # --------------------------------------------------------
    # Dibujar trayectoria recorrida del TCP
    # --------------------------------------------------------
    if puntos_recorridos:
        posiciones_tcp = []

        for configuracion in puntos_recorridos:
            T_historial = calcular_transformaciones_dh(configuracion)
            posiciones_tcp.append(T_historial[-1][:3, 3])

        posiciones_tcp = np.array(posiciones_tcp)

        # Línea que conecta los puntos recorridos
        if len(posiciones_tcp) > 1:
            ax.plot(
                posiciones_tcp[:, 0],
                posiciones_tcp[:, 1],
                posiciones_tcp[:, 2],
                color='orange',
                linewidth=2,
                marker='o',
                markersize=5,
                label='Trayectoria recorrida'
            )
        else:
            ax.scatter(
                posiciones_tcp[:, 0],
                posiciones_tcp[:, 1],
                posiciones_tcp[:, 2],
                color='orange',
                s=35,
                label='Punto recorrido'
            )

        # Resaltar el punto actual
        ax.scatter(
            posiciones_tcp[-1, 0],
            posiciones_tcp[-1, 1],
            posiciones_tcp[-1, 2],
            color='#fb7185',
            s=75,
            marker='o',
            label='Posición actual'
        )

        ax.legend(loc='upper left', fontsize=8, facecolor='#111c2f',
                  edgecolor='#334155', labelcolor='#e2e8f0')

    # --------------------------------------------------------
    # Sistema de coordenadas del TCP
    # --------------------------------------------------------
    T_tcp = T_list[-1]
    p_tcp = T_tcp[:3, 3]
    esc = 10.0

    ax.quiver(
        p_tcp[0], p_tcp[1], p_tcp[2],
        T_tcp[0, 0], T_tcp[1, 0], T_tcp[2, 0],
        color='#fb7185', length=esc, normalize=True, linewidth=2
    )
    ax.text(
        p_tcp[0] + T_tcp[0, 0] * esc,
        p_tcp[1] + T_tcp[1, 0] * esc,
        p_tcp[2] + T_tcp[2, 0] * esc,
        "X", color='#fb7185', fontweight='bold'
    )

    ax.quiver(
        p_tcp[0], p_tcp[1], p_tcp[2],
        T_tcp[0, 1], T_tcp[1, 1], T_tcp[2, 1],
        color='#4ade80', length=esc, normalize=True, linewidth=2
    )
    ax.text(
        p_tcp[0] + T_tcp[0, 1] * esc,
        p_tcp[1] + T_tcp[1, 1] * esc,
        p_tcp[2] + T_tcp[2, 1] * esc,
        "Y", color='#4ade80', fontweight='bold'
    )

    ax.quiver(
        p_tcp[0], p_tcp[1], p_tcp[2],
        T_tcp[0, 2], T_tcp[1, 2], T_tcp[2, 2],
        color='#60a5fa', length=esc, normalize=True, linewidth=2
    )
    ax.text(
        p_tcp[0] + T_tcp[0, 2] * esc,
        p_tcp[1] + T_tcp[1, 2] * esc,
        p_tcp[2] + T_tcp[2, 2] * esc,
        "Z", color='#60a5fa', fontweight='bold'
    )

    # --------------------------------------------------------
    # Configuración de los ejes
    # --------------------------------------------------------
    ax.set_xlim([-90, 90])
    ax.set_ylim([-90, 90])
    ax.set_zlim([0, 90])
    ax.set_xlabel('X (cm)')
    ax.set_ylabel('Y (cm)')
    ax.set_zlabel('Z (cm)')
    ax.set_title('Manipulador CRS Catalyst 5', color='#e2e8f0', fontsize=13, fontweight='bold', pad=14)
    ax.view_init(elev=24, azim=-58)
    ax.set_box_aspect((1, 1, 0.8))
    ax.tick_params(colors="#cbd5e1", labelsize=8)
    ax.xaxis.label.set_color("#cbd5e1")
    ax.yaxis.label.set_color("#cbd5e1")
    ax.zaxis.label.set_color("#cbd5e1")

    # --------------------------------------------------------
    # Actualizar indicador de posición
    # --------------------------------------------------------
    if lbl_posicion is not None:
        texto = f"Modo: {modo}"

        if indice is not None and total is not None:
            texto += f"  |  Punto: {indice} de {total}"

        texto += (
            f"\nq1={q_rad[0]:.4f}  q2={q_rad[1]:.4f}  "
            f"q3={q_rad[2]:.4f}  q4={q_rad[3]:.4f}  "
            f"q5={q_rad[4]:.4f}"
        )

        lbl_posicion.config(text=texto)

    canvas.draw_idle()


# ============================================================
# CONSOLA Y LECTURA SERIAL CON DETECCIÓN DE ESTADO
# ============================================================

def actualizar_consola_usuario(texto):
    consola.insert(tk.END, texto + "\n")
    consola.see(tk.END)


def encolar_envio(tipo, contenido=None, urgente=False):
    prioridad = 0 if urgente else 1
    cola_envio.put((prioridad, next(_contador_envio), tipo, contenido))

def _escribir_texto(texto, pausa=0.05, etiqueta="comando"):
    """Escribe carácter por carácter conservando el protocolo del daemon."""
    for numero_caracter, caracter in enumerate(texto, start=1):
        if _cerrando.is_set() or (etiqueta.startswith("ángulo") and _paro_solicitado.is_set()):
            return False
        try:
            fpga.write(caracter.encode("ascii"))
        except serial.SerialTimeoutException as exc:
            raise TimeoutError(
                f"Write timeout al enviar {etiqueta}, carácter {numero_caracter}. "
                f"Verifique {PUERTO}, el daemon y la conexión USB/serial."
            ) from exc
        if pausa:
            time.sleep(pausa)
    return True

def trabajador_serial():
    """Único hilo que usa el puerto; no modifica widgets de Tkinter."""
    while not _cerrando.is_set():
        # La lectura usa timeout=0, por lo que no detiene el procesamiento de envíos.
        try:
            if fpga is not None and fpga.is_open and fpga.in_waiting:
                datos = fpga.read(fpga.in_waiting).decode("ascii", errors="ignore")
                if datos:
                    cola_entrada.put(("datos", datos))
        except Exception as exc:
            cola_entrada.put(("error", f"Error de lectura serial: {exc}"))
            time.sleep(0.1)

        try:
            _, _, tipo, contenido = cola_envio.get(timeout=0.02)
        except queue.Empty:
            continue
        try:
            if tipo == "cerrar":
                return
            if fpga is None or not fpga.is_open:
                cola_entrada.put(("error", "El puerto serial no está abierto."))
                continue

            if tipo == "comando":
                _escribir_texto(str(contenido).rstrip("\r") + "\r", etiqueta="comando")
            elif tipo == "angulos":
                for i, angulo in enumerate(contenido, start=1):
                    if _paro_solicitado.is_set():
                        break
                    if not _escribir_texto(
                        f"{float(angulo):.8f}\r", pausa=0.05,
                        etiqueta=f"ángulo {i}/5"
                    ):
                        break
                    time.sleep(0.10)
                else:
                    cola_entrada.put(("estado", "Los cinco ángulos fueron enviados."))
            elif tipo == "velocidad":
                vel = int(contenido)
                fpga.write(b"\x03")
                time.sleep(0.3)
                fpga.write(b"\r")
                time.sleep(0.1)
                _escribir_texto(f"speed {vel}\r", pausa=0.02, etiqueta="velocidad")
                time.sleep(0.2)
                _escribir_texto("daemon\r", pausa=0.02, etiqueta="reinicio del daemon")
                cola_entrada.put(("estado", "Velocidad ajustada. Daemon listo."))
            elif tipo == "abortar":
                for _ in range(3):
                    fpga.write(b"\x03")
                    time.sleep(0.1)
                fpga.write(b"\r")
                _paro_solicitado.clear()
                cola_entrada.put(("estado", "Ctrl+C enviado; confirma el estado del controlador físicamente."))
        except Exception as exc:
            cola_entrada.put(("error", f"Error de envío serial: {exc}"))
        finally:
            cola_envio.task_done()

def _abrir_puerto_en_hilo():
    global fpga
    try:
        fpga = serial.Serial(
            port=PUERTO,
            baudrate=BAUDIOS,
            timeout=0,
            write_timeout=5,
            xonxoff=False,
            rtscts=False,
            dsrdtr=False,
        )
        if _cerrando.is_set():
            fpga.close()
            return
        encolar_envio("comando", "")  # conserva el CR inicial usado por el daemon
        cola_entrada.put(("conexion_ok", f"Puerto {PUERTO} abierto."))
    except Exception as exc:
        cola_entrada.put(("conexion_error", str(exc)))


def escuchar_robot_continuamente():
    """Procesa en Tk los datos que el hilo serial puso en la cola."""
    global buffer_serial, ejecutando_trayectoria_real, indice_trayectoria_real
    try:
        while True:
            tipo, contenido = cola_entrada.get_nowait()
            if tipo == "datos":
                texto = contenido.replace("\r", "")
                consola.insert(tk.END, texto)
                consola.see(tk.END)
                buffer_serial += texto
                while "\n" in buffer_serial:
                    linea, buffer_serial = buffer_serial.split("\n", 1)
                    if ("ALCANZADO:" in linea and ejecutando_trayectoria_real
                            and indice_trayectoria_real < len(trayectoria)):
                        punto_alcanzado = trayectoria[indice_trayectoria_real]
                        historial_fisica.append(punto_alcanzado)
                        actualizar_visor_3d(
                            punto_alcanzado,
                            indice=len(historial_fisica),
                            total=len(trayectoria),
                            modo="Ejecución física confirmada",
                            puntos_recorridos=historial_fisica
                        )
                        actualizar_consola_usuario(
                            f"[VISUALIZADOR] Punto {len(historial_fisica)} "
                            f"de {len(trayectoria)} confirmado."
                        )
                        indice_trayectoria_real += 1
                        ventana.after(500, enviar_siguiente_punto_real)
            elif tipo == "conexion_ok":
                lbl_estado.config(text="Estado: ESCUCHANDO", fg="green")
                actualizar_consola_usuario(contenido)
            elif tipo == "conexion_error":
                lbl_estado.config(text="Estado: ERROR puerto serial", fg="red")
                actualizar_consola_usuario(f"ERROR DE PUERTO: {contenido}")
            elif tipo == "error":
                ejecutando_trayectoria_real = False
                actualizar_consola_usuario(contenido)
                lbl_estado.config(text="Estado: ERROR serial", fg="red")
            elif tipo == "estado":
                actualizar_consola_usuario(contenido)
    except queue.Empty:
        pass
    ventana.after(50, escuchar_robot_continuamente)

# ============================================================
# ENVIAR COMANDOS Y ÁNGULOS
# ============================================================

def enviar_comando_serial(comando_texto):
    if fpga is None or not fpga.is_open:
        messagebox.showwarning("Advertencia", "El puerto no está abierto o aún conecta.")
        return False
    encolar_envio("comando", comando_texto)
    return True


def enviar_angulos(q_rad):
    if fpga is None or not fpga.is_open:
        messagebox.showwarning("Advertencia", "El puerto no está abierto o aún conecta.")
        return False
    if len(q_rad) != 5:
        messagebox.showerror("Error", "Se requieren exactamente cinco ángulos.")
        return False
    encolar_envio("angulos", list(q_rad))
    return True


# ============================================================
# FUNCIONES DE CONTROL BÁSICO Y VELOCIDAD
# ============================================================

def despertar_robot():
    actualizar_consola_usuario("\n--- Enviando BOOT ---")
    enviar_comando_serial("boot")


def comando_home():
    actualizar_consola_usuario("\nTú: home")
    enviar_comando_serial("home")
    actualizar_visor_3d([0, np.pi / 2, 0, 0, 0])


def prueba_muescas_angulos():
    muescas_grados = [0.330, 91.000, 1.360, 1.194, 3.380]
    muescas_rad = np.deg2rad(muescas_grados).tolist()
    actualizar_consola_usuario("\n--- PRUEBA MUESCAS POR ÁNGULOS ---")
    actualizar_visor_3d(muescas_rad)
    enviar_angulos(muescas_rad)


# Esta función se conserva como en el código proporcionado.
# En robots físicos, Ctrl+C al daemon NO debe considerarse un paro de emergencia.
def aplicar_velocidad_fisica(vel_porcentaje):
    if fpga is None or not fpga.is_open:
        actualizar_consola_usuario("No se pudo cambiar la velocidad: puerto serial no conectado.")
        return
    actualizar_consola_usuario(
        f"\n--- Aplicando velocidad al robot ({int(vel_porcentaje)}%) ---"
    )
    encolar_envio("velocidad", int(vel_porcentaje))


def al_soltar_barra_velocidad(event):
    global delay_simulacion
    vel = escala_velocidad.get()
    delay_simulacion = int(1000 - ((vel / 100.0) * 900))
    actualizar_consola_usuario(f"\n[Velocidad de SIMULACIÓN ajustada a {vel}%]")

    if ejecutando_trayectoria_real:
        actualizar_consola_usuario("¡Aviso! Trayectoria en curso. La velocidad física se actualizará al terminar.")
    else:
        aplicar_velocidad_fisica(vel)


# ============================================================
# CARGAR TRAYECTORIA: COMAS, TABULADORES O ESPACIOS
# ============================================================

def parsear_fila_trayectoria(linea):
    """Devuelve cinco floats o None si la línea es encabezado/inválida.

    Acepta, por ejemplo:
      -0.079  1.478  0.046  0.089  -0.035   (espacios/tabuladores)
      -0.079, 1.478, 0.046, 0.089, -0.035  (comas)
      -0.079; 1.478; 0.046; 0.089; -0.035  (punto y coma)
    """
    linea = linea.strip().replace('[', '').replace(']', '')
    if not linea:
        return None

    for separador in (',', ';', '\t'):
        linea = linea.replace(separador, ' ')

    partes = linea.split()
    if len(partes) != 5:
        return None

    try:
        return [float(parte) for parte in partes]
    except ValueError:
        # Permite omitir encabezados como: q1,q2,q3,q4,q5
        return None


def cargar_trayectoria():
    global trayectoria
    ruta = filedialog.askopenfilename(
        title="Seleccionar trayectoria",
        filetypes=[("Archivos CSV y TXT", "*.csv *.txt"), ("Todos los archivos", "*.*")]
    )
    if not ruta:
        return

    try:
        nueva_trayectoria = []
        with open(ruta, 'r', encoding='utf-8-sig') as archivo:
            for numero_fila, linea in enumerate(archivo, start=1):
                punto = parsear_fila_trayectoria(linea)
                if punto is not None:
                    nueva_trayectoria.append(punto)

        if not nueva_trayectoria:
            raise ValueError(
                "El archivo no contiene puntos válidos. Cada fila debe tener cinco ángulos en radianes."
            )

        trayectoria = nueva_trayectoria
        actualizar_consola_usuario(
            f"\n====================================\n"
            f"TRAYECTORIA CARGADA: {len(trayectoria)} puntos\n"
            f"Archivo: {os.path.basename(ruta)}\n"
            f"===================================="
        )
        messagebox.showinfo("Trayectoria", f"Cargada con {len(trayectoria)} puntos.")

    except Exception as e:
        messagebox.showerror("Error al cargar trayectoria", str(e))


# ============================================================
# ANIMACIÓN Y EJECUCIÓN
# ============================================================

def visualizar_primera_posicion():
    if not trayectoria:
        messagebox.showwarning("Trayectoria", "Primero carga una trayectoria.")
        return
    actualizar_visor_3d(trayectoria[0])


def animar_trayectoria():
    global historial_simulacion

    if not trayectoria:
        messagebox.showwarning(
            "Trayectoria",
            "Primero carga una trayectoria."
        )
        return

    historial_simulacion = []

    actualizar_consola_usuario(
        "\n--- ANIMACIÓN VIRTUAL INICIADA ---"
    )

    animar_punto(0)


def animar_punto(indice):
    global historial_simulacion

    if indice >= len(trayectoria):
        actualizar_consola_usuario(
            "\n--- ANIMACIÓN VIRTUAL FINALIZADA ---"
        )

        lbl_posicion.config(
            text=f"Modo: Simulación virtual finalizada | "
                 f"Puntos recorridos: {len(trayectoria)} de {len(trayectoria)}"
        )
        return

    punto = trayectoria[indice]

    historial_simulacion.append(punto)

    actualizar_visor_3d(
        punto,
        indice=indice + 1,
        total=len(trayectoria),
        modo="Simulación virtual",
        puntos_recorridos=historial_simulacion
    )

    ventana.after(
        delay_simulacion,
        lambda: animar_punto(indice + 1)
    )


def iniciar_ejecucion_real():
    global ejecutando_trayectoria_real
    global indice_trayectoria_real
    global historial_fisica

    if not trayectoria:
        messagebox.showwarning(
            "Trayectoria",
            "Primero carga una trayectoria."
        )
        return

    if fpga is None or not fpga.is_open:
        messagebox.showwarning(
            "Puerto serial",
            "El puerto serial no está abierto."
        )
        return

    if ejecutando_trayectoria_real or _paro_solicitado.is_set():
        actualizar_consola_usuario("Hay una trayectoria o una solicitud de aborto en curso.")
        return

    historial_fisica = []

    actualizar_consola_usuario(
        "\n===================================="
    )
    actualizar_consola_usuario(
        "INICIANDO EJECUCIÓN EN ROBOT FÍSICO"
    )
    actualizar_consola_usuario(
        f"Puntos a ejecutar: {len(trayectoria)}"
    )
    actualizar_consola_usuario(
        "===================================="
    )

    ejecutando_trayectoria_real = True
    indice_trayectoria_real = 0

    lbl_posicion.config(
        text="Modo: Ejecución física | Esperando confirmación del primer punto"
    )

    enviar_siguiente_punto_real()


def enviar_siguiente_punto_real():
    global ejecutando_trayectoria_real
    global indice_trayectoria_real

    if not ejecutando_trayectoria_real:
        return

    if indice_trayectoria_real >= len(trayectoria):
        actualizar_consola_usuario(
            "\n===== TRAYECTORIA FÍSICA FINALIZADA ====="
        )

        ejecutando_trayectoria_real = False

        lbl_posicion.config(
            text=f"Modo: Ejecución física finalizada | "
                 f"Puntos confirmados: {len(historial_fisica)} "
                 f"de {len(trayectoria)}"
        )
        return

    punto_rad = trayectoria[indice_trayectoria_real]

    actualizar_consola_usuario(
        f"\n--- Enviando Punto {indice_trayectoria_real + 1} "
        f"de {len(trayectoria)} ---"
    )

    enviado = enviar_angulos(punto_rad)

    if not enviado:
        ejecutando_trayectoria_real = False

        actualizar_consola_usuario(
            "Error al enviar el punto; se cancela el envío de puntos siguientes."
        )

def detener_ejecucion():
    global ejecutando_trayectoria_real
    ejecutando_trayectoria_real = False
    _paro_solicitado.set()
    # Descartar envíos pendientes antes de dar prioridad al aborto.
    try:
        while True:
            cola_envio.get_nowait()
            cola_envio.task_done()
    except queue.Empty:
        pass
    actualizar_consola_usuario("\n!!! ABORTO SOLICITADO: se cancela el envío de puntos. No sustituye el paro físico. !!!")
    if fpga is None or not fpga.is_open:
        _paro_solicitado.clear()
        actualizar_consola_usuario("No hay conexión serial para enviar Ctrl-C.")
        return
    encolar_envio("abortar", urgente=True)


# ============================================================
# COMANDO MANUAL Y GESTIÓN DE PUERTOS
# ============================================================

def enviar_comando_manual(event=None):
    comando = entrada_comando.get().strip()
    if comando:
        actualizar_consola_usuario(f"\nTú: {comando}")
        enviar_comando_serial(comando)
        entrada_comando.delete(0, tk.END)


def abrir_puerto_al_iniciar():
    lbl_estado.config(text=f"Estado: CONECTANDO a {PUERTO}...", fg="orange")
    threading.Thread(target=_abrir_puerto_en_hilo, daemon=True).start()


def cerrar_aplicacion():
    _cerrando.set()
    if _proceso_camara is not None and _proceso_camara.poll() is None:
        _proceso_camara.terminate()
    try:
        encolar_envio("cerrar", urgente=True)
    except Exception:
        pass
    if fpga and fpga.is_open:
        fpga.close()
    ventana.destroy()


def alternar_camara_web():
    """Abre/cierra el visor en otro proceso para no bloquear el control serial."""
    global _proceso_camara
    if _proceso_camara is not None and _proceso_camara.poll() is None:
        _proceso_camara.terminate()
        btn_camara.config(text="Cerrando cámara…", state="disabled")
        ventana.after(250, revisar_estado_camara)
        return

    try:
        opciones = {
            "cwd": os.path.dirname(os.path.abspath(__file__)),
            "stdin": subprocess.DEVNULL,
            "stdout": subprocess.DEVNULL,
            "stderr": subprocess.DEVNULL,
        }
        if sys.platform.startswith("win"):
            opciones["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        _proceso_camara = subprocess.Popen(
            [sys.executable, os.path.abspath(__file__), "--camera", str(ID_CAMARA)],
            **opciones
        )
        btn_camara.config(text="Cerrar cámara", state="normal")
        ventana.after(500, revisar_estado_camara)
    except Exception as exc:
        _proceso_camara = None
        messagebox.showerror("No se pudo abrir la cámara", str(exc))

def revisar_estado_camara():
    if _proceso_camara is None:
        return
    if _proceso_camara.poll() is None:
        ventana.after(500, revisar_estado_camara)
    else:
        btn_camara.config(text="Abrir webcam", state="normal")

def mostrar_visor_camara(indice_camara=0):
    """Vista de webcam ejecutada exclusivamente en el proceso hijo."""
    visor = tk.Tk()
    visor.title("Webcam del robot · CRS Catalyst 5")
    visor.geometry("850x640")
    visor.minsize(500, 380)
    visor.configure(bg="#0b1220")
    tk.Label(visor, text="VISTA EN TIEMPO REAL DEL ROBOT", bg="#0b1220",
             fg="#e2e8f0", font=("Segoe UI", 14, "bold"), anchor="w",
             padx=14, pady=10).pack(fill="x")
    estado = tk.Label(visor, text=f"Conectando con cámara {indice_camara}…",
                      bg="#111c2f", fg="#fbbf24", anchor="w", padx=12, pady=7)
    estado.pack(fill="x", padx=12, pady=(0, 8))
    barra_camaras = tk.Frame(visor, bg="#0b1220")
    barra_camaras.pack(fill="x", padx=12, pady=(0, 8))
    tk.Label(barra_camaras, text="Dispositivo / índice:", bg="#0b1220",
             fg="#cbd5e1", font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 8))
    seleccion = tk.StringVar(value=str(indice_camara))
    selector = ttk.Combobox(barra_camaras, textvariable=seleccion, width=7,
                            state="normal", values=(str(indice_camara),))
    selector.pack(side="left", padx=(0, 8))
    panel = tk.Label(visor, bg="#050a12")
    panel.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    imagenes = queue.Queue(maxsize=1)
    eventos = queue.Queue()
    solicitudes_camara = queue.Queue()
    solicitudes_camara.put(indice_camara)
    detener = threading.Event()
    referencia = {"imagen": None}

    def publicar(elemento):
        try:
            imagenes.get_nowait()
        except queue.Empty:
            pass
        try:
            imagenes.put_nowait(elemento)
        except queue.Full:
            pass

    def capturar():
        try:
            import cv2
            from PIL import Image, ImageTk
        except Exception as exc:
            eventos.put(("error", f"Falta OpenCV o Pillow: {exc}. Instala: python -m pip install opencv-python pillow"))
            return
        backend = cv2.CAP_DSHOW if sys.platform.startswith("win") else cv2.CAP_ANY
        captura = None
        indice_activo = None
        try:
            while not detener.is_set():
                try:
                    nuevo_indice = solicitudes_camara.get_nowait()
                except queue.Empty:
                    nuevo_indice = None
                if nuevo_indice is not None and (nuevo_indice != indice_activo or captura is None):
                    if captura is not None:
                        captura.release()
                    indice_activo = nuevo_indice
                    captura = cv2.VideoCapture(indice_activo, backend)
                    captura.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    captura.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    if not captura.isOpened():
                        captura.release()
                        captura = None
                        eventos.put(("error", f"No se pudo abrir la cámara {indice_activo}."))
                        continue
                    eventos.put(("estado", f"Cámara {indice_activo} activa"))
                if captura is None:
                    detener.wait(0.1)
                    continue
                correcto, frame = captura.read()
                if not correcto:
                    eventos.put(("error", f"No hay señal de video en la cámara {indice_activo}."))
                    captura.release()
                    captura = None
                    continue
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                publicar(("frame", frame))
        finally:
            if captura is not None:
                captura.release()

    def cambiar_camara(event=None):
        try:
            nuevo_indice = int(seleccion.get().strip())
            if nuevo_indice < 0:
                raise ValueError
        except ValueError:
            estado.config(text="Escribe un índice entero no negativo (por ejemplo, 0 o 1).",
                          fg="#fca5a5")
            return
        seleccion.set(str(nuevo_indice))
        estado.config(text=f"Cambiando a cámara {nuevo_indice}…", fg="#fbbf24")
        while True:
            try:
                solicitudes_camara.get_nowait()
            except queue.Empty:
                break
        solicitudes_camara.put(nuevo_indice)

    def detectar_camaras():
        boton_detectar.config(state="disabled", text="Buscando…")
        estado.config(text="Buscando dispositivos 0–9…", fg="#fbbf24")

        def buscar():
            try:
                import cv2
                backend = cv2.CAP_DSHOW if sys.platform.startswith("win") else cv2.CAP_ANY
                disponibles = []
                for indice in range(10):
                    if detener.is_set():
                        break
                    cap = cv2.VideoCapture(indice, backend)
                    if cap.isOpened():
                        disponibles.append(indice)
                    cap.release()
                eventos.put(("deteccion", disponibles))
            except Exception as exc:
                eventos.put(("error", f"Error al detectar cámaras: {exc}"))

        threading.Thread(target=buscar, daemon=True, name="detectar-webcams").start()

    boton_detectar = ttk.Button(barra_camaras, text="Detectar cámaras",
                                command=detectar_camaras)
    boton_detectar.pack(side="left", padx=(0, 8))
    ttk.Button(barra_camaras, text="Cambiar", command=cambiar_camara).pack(side="left")
    selector.bind("<Return>", cambiar_camara)

    def actualizar():
        if detener.is_set():
            return
        try:
            while True:
                tipo_evento, dato_evento = eventos.get_nowait()
                if tipo_evento == "deteccion":
                    disponibles = dato_evento
                    # Incluye el índice actual aunque el controlador no permita
                    # abrirlo por segunda vez mientras está transmitiendo.
                    actual = int(seleccion.get()) if seleccion.get().isdigit() else indice_camara
                    if actual not in disponibles:
                        disponibles.insert(0, actual)
                    selector.configure(values=tuple(str(i) for i in disponibles))
                    boton_detectar.config(state="normal", text="Detectar cámaras")
                    estado.config(
                        text=("Dispositivos encontrados: " + ", ".join(map(str, disponibles)))
                        if disponibles else "No se encontraron cámaras; escribe el índice manualmente.",
                        fg="#86efac" if disponibles else "#fbbf24"
                    )
                elif tipo_evento == "estado":
                    estado.config(text=dato_evento, fg="#86efac")
                elif tipo_evento == "error":
                    boton_detectar.config(state="normal", text="Detectar cámaras")
                    estado.config(text=dato_evento, fg="#fca5a5")
        except queue.Empty:
            pass
        try:
            while True:
                _, dato = imagenes.get_nowait()
                from PIL import Image, ImageTk
                imagen = Image.fromarray(dato)
                redimensionado = getattr(Image, "Resampling", Image)
                imagen.thumbnail((max(panel.winfo_width(), 320),
                                  max(panel.winfo_height(), 240)),
                                 redimensionado.LANCZOS)
                foto = ImageTk.PhotoImage(imagen)
                panel.configure(image=foto)
                referencia["imagen"] = foto
        except queue.Empty:
            pass
        visor.after(33, actualizar)

    def cerrar_visor():
        detener.set()
        visor.destroy()

    visor.protocol("WM_DELETE_WINDOW", cerrar_visor)
    threading.Thread(target=capturar, daemon=True, name="captura-webcam").start()
    visor.after(33, actualizar)
    visor.mainloop()

# El proceso de cámara termina aquí, antes de construir el control del robot.
if __name__ == "__main__" and len(sys.argv) >= 2 and sys.argv[1] == "--camera":
    indice = int(sys.argv[2]) if len(sys.argv) >= 3 else ID_CAMARA
    mostrar_visor_camara(indice)
    raise SystemExit


# ============================================================
# INTERFAZ GRÁFICA
# ============================================================

ventana = tk.Tk()
ventana.title("CRS Catalyst 5 | Control y simulación")
ventana.geometry("1180x760")
ventana.minsize(980, 620)
ventana.configure(bg="#0b1220")

# Tema oscuro con estilos ttk uniformes.
style = ttk.Style(ventana)
try:
    style.theme_use("clam")
except tk.TclError:
    pass

BG = "#0b1220"
CARD = "#111c2f"
CARD_ALT = "#17243a"
TEXT = "#e2e8f0"
MUTED = "#94a3b8"
BLUE = "#2563eb"

style.configure("TFrame", background=BG)
style.configure("Card.TFrame", background=CARD)
style.configure("Header.TFrame", background=BG)
style.configure("TLabel", background=BG, foreground=TEXT, font=("Segoe UI", 10))
style.configure("Card.TLabel", background=CARD, foreground=TEXT, font=("Segoe UI", 10))
style.configure("Title.TLabel", background=BG, foreground="#f8fafc", font=("Segoe UI", 18, "bold"))
style.configure("Subtitle.TLabel", background=BG, foreground=MUTED, font=("Segoe UI", 9))
style.configure("Section.TLabel", background=CARD, foreground="#cbd5e1", font=("Segoe UI", 10, "bold"))
style.configure("TButton", padding=(8, 6), font=("Segoe UI", 9, "bold"), borderwidth=0)
style.configure("Primary.TButton", background=BLUE, foreground="white")
style.map("Primary.TButton", background=[("active", "#1d4ed8"), ("pressed", "#1e40af")])
style.configure("Secondary.TButton", background="#334155", foreground=TEXT)
style.map("Secondary.TButton", background=[("active", "#475569"), ("pressed", "#1e293b")])
style.configure("Success.TButton", background="#15803d", foreground="white")
style.map("Success.TButton", background=[("active", "#16a34a"), ("pressed", "#166534")])
style.configure("Warning.TButton", background="#b45309", foreground="white")
style.map("Warning.TButton", background=[("active", "#d97706"), ("pressed", "#92400e")])
style.configure("Danger.TButton", background="#b91c1c", foreground="white")
style.map("Danger.TButton", background=[("active", "#dc2626"), ("pressed", "#991b1b")])
style.configure("TEntry", fieldbackground="#0b1220", foreground=TEXT,
                 bordercolor="#334155", padding=6)
style.configure("TScale", background=CARD, troughcolor="#334155")

ventana.grid_columnconfigure(0, weight=0, minsize=365)
ventana.grid_columnconfigure(1, weight=1)
ventana.grid_rowconfigure(1, weight=1)

# Encabezado de la aplicación.
header = ttk.Frame(ventana, style="Header.TFrame", padding=(18, 10, 18, 6))
header.grid(row=0, column=0, columnspan=2, sticky="ew")
header.grid_columnconfigure(0, weight=1)
header.grid_columnconfigure(1, weight=0)
header.grid_columnconfigure(2, weight=0)
ttk.Label(header, text="CRS Catalyst 5", style="Title.TLabel").grid(row=0, column=0, sticky="w")
ttk.Label(header, text="Panel de control · trayectoria · simulación 3D",
          style="Subtitle.TLabel").grid(row=1, column=0, sticky="w", pady=(3, 0))
btn_camara = ttk.Button(header, text="📷  Abrir webcam", style="Secondary.TButton",
                        command=alternar_camara_web)
btn_camara.grid(row=0, column=1, rowspan=2, sticky="e", padx=(8, 12))
lbl_estado = tk.Label(header, text="Estado: INICIANDO...", bg="#1e293b", fg="#fbbf24",
                      font=("Segoe UI", 10, "bold"), padx=14, pady=8)
lbl_estado.grid(row=0, column=2, rowspan=2, sticky="e")

# Columna de controles.
frame_izq = ttk.Frame(ventana, style="Card.TFrame", padding=10)
frame_izq.grid(row=1, column=0, sticky="nsew", padx=(12, 6), pady=(4, 12))
frame_izq.grid_columnconfigure(0, weight=1)

ttk.Label(frame_izq, text="ACCIONES DEL ROBOT", style="Section.TLabel").grid(
    row=0, column=0, sticky="w", pady=(0, 4))
frame_botones = ttk.Frame(frame_izq, style="Card.TFrame")
frame_botones.grid(row=1, column=0, sticky="ew")
for col in range(2):
    frame_botones.grid_columnconfigure(col, weight=1)
ttk.Button(frame_botones, text="BOOT", style="Success.TButton", command=despertar_robot).grid(
    row=0, column=0, sticky="ew", padx=(0, 5), pady=4)
ttk.Button(frame_botones, text="AUTOHOME", style="Primary.TButton", command=comando_home).grid(
    row=0, column=1, sticky="ew", padx=(5, 0), pady=4)
ttk.Button(frame_botones, text="Muescas", style="Secondary.TButton", command=prueba_muescas_angulos).grid(
    row=1, column=0, sticky="ew", padx=(0, 5), pady=4)
ttk.Button(frame_botones, text="Cargar trayectoria", style="Warning.TButton", command=cargar_trayectoria).grid(
    row=1, column=1, sticky="ew", padx=(5, 0), pady=4)
ttk.Button(frame_botones, text="Ver inicio 3D", style="Secondary.TButton",
           command=visualizar_primera_posicion).grid(row=2, column=0, sticky="ew", padx=(0, 5), pady=3)
ttk.Button(frame_botones, text="Animar 3D", style="Secondary.TButton",
           command=animar_trayectoria).grid(row=2, column=1, sticky="ew", padx=(5, 0), pady=3)
ttk.Button(frame_botones, text="Ejecutar en robot", style="Primary.TButton",
           command=iniciar_ejecucion_real).grid(row=3, column=0, sticky="ew", padx=(0, 5), pady=3)
ttk.Button(frame_botones, text="PARO / ABORTAR", style="Danger.TButton",
           command=detener_ejecucion).grid(row=3, column=1, sticky="ew", padx=(5, 0), pady=3)

# Velocidad.
card_velocidad = ttk.Frame(frame_izq, style="Card.TFrame", padding=(0, 5, 0, 4))
card_velocidad.grid(row=2, column=0, sticky="ew", pady=(2, 0))
card_velocidad.grid_columnconfigure(1, weight=1)
ttk.Label(card_velocidad, text="VELOCIDAD", style="Section.TLabel").grid(
    row=0, column=0, columnspan=2, sticky="w", pady=(0, 3))
ttk.Label(card_velocidad, text="1%", style="Card.TLabel").grid(row=1, column=0, padx=(0, 8))
escala_velocidad = ttk.Scale(card_velocidad, from_=1, to=100, orient=tk.HORIZONTAL)
escala_velocidad.set(20)
escala_velocidad.grid(row=1, column=1, sticky="ew", padx=5)
ttk.Label(card_velocidad, text="100%", style="Card.TLabel").grid(row=1, column=2, padx=(8, 0))
escala_velocidad.bind("<ButtonRelease-1>", al_soltar_barra_velocidad)

# Consola y comando manual.
ttk.Label(frame_izq, text="CONSOLA SERIAL", style="Section.TLabel").grid(
    row=3, column=0, sticky="sw", pady=(5, 3))
consola = tk.Text(frame_izq, height=7, bg="#07101d", fg="#86efac",
                  insertbackground="#e2e8f0", selectbackground="#1d4ed8",
                  font=("Cascadia Mono", 8), relief="flat", padx=7, pady=6,
                  wrap="word", borderwidth=0)
consola.grid(row=4, column=0, sticky="nsew")
scroll_consola = ttk.Scrollbar(frame_izq, orient="vertical", command=consola.yview)
scroll_consola.grid(row=4, column=1, sticky="ns")
consola.configure(yscrollcommand=scroll_consola.set)
frame_izq.grid_rowconfigure(4, weight=1)
frame_manual = ttk.Frame(frame_izq, style="Card.TFrame", padding=(0, 5, 0, 0))
frame_manual.grid(row=5, column=0, sticky="ew")
frame_manual.grid_columnconfigure(0, weight=1)
entrada_comando = ttk.Entry(frame_manual, font=("Cascadia Mono", 10))
entrada_comando.grid(row=0, column=0, sticky="ew", padx=(0, 7))
entrada_comando.bind("<Return>", enviar_comando_manual)
ttk.Button(frame_manual, text="Enviar", style="Primary.TButton",
           command=enviar_comando_manual).grid(row=0, column=1)

# Panel gráfico 3D.
frame_der = ttk.Frame(ventana, style="Card.TFrame", padding=8)
frame_der.grid(row=1, column=1, sticky="nsew", padx=(6, 12), pady=(4, 12))
frame_der.grid_columnconfigure(0, weight=1)
frame_der.grid_rowconfigure(1, weight=1)
ttk.Label(frame_der, text="VISTA ESPACIAL", style="Section.TLabel").grid(
    row=0, column=0, sticky="w", padx=5, pady=(2, 4))
lbl_posicion = tk.Label(
    frame_der, text="Modo: En espera", bg=CARD_ALT, fg=TEXT,
    font=("Consolas", 9), justify=tk.LEFT, anchor="w", padx=8, pady=6,
    wraplength=500
)
lbl_posicion.grid(row=2, column=0, sticky="ew", pady=(6, 0))
frame_der.bind("<Configure>", lambda event: lbl_posicion.configure(
    wraplength=max(event.width - 32, 180)))
fig = plt.Figure(figsize=(6, 5), dpi=90, facecolor=CARD)
ax = fig.add_subplot(111, projection="3d")
fig.subplots_adjust(left=0.02, right=0.98, bottom=0.03, top=0.96)
canvas = FigureCanvasTkAgg(fig, master=frame_der)
canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew")

threading.Thread(target=trabajador_serial, daemon=True).start()
ventana.after(100, abrir_puerto_al_iniciar)
ventana.after(200, escuchar_robot_continuamente)
ventana.after(300, lambda: actualizar_visor_3d([0, np.pi / 2, 0, 0, 0]))
ventana.protocol("WM_DELETE_WINDOW", cerrar_aplicacion)
ventana.mainloop()
