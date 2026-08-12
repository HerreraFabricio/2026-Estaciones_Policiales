import math
import requests
import streamlit as st
import pandas as pd

from streamlit_geolocation import streamlit_geolocation


# ---------------------------------------------------------
# CONFIGURACIÓN DE LA PÁGINA
# ---------------------------------------------------------

st.set_page_config(
    page_title="Estaciones Policiales Cercanas",
    page_icon="🚓",
    layout="wide"
)


# ---------------------------------------------------------
# ESTILOS
# ---------------------------------------------------------

st.markdown("""
<style>

.stApp {
    background-color: #f5f7fa;
}

.block-container {
    max-width: 1100px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

.titulo {
    font-size: 40px;
    font-weight: 800;
    color: #17365d;
    margin-bottom: 5px;
}

.subtitulo {
    font-size: 16px;
    color: #687789;
    margin-bottom: 28px;
}

.tarjeta {
    background-color: white;
    border: 1px solid #dde4ec;
    border-radius: 15px;
    padding: 20px;
    margin-bottom: 15px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.04);
}

.numero {
    display: inline-block;
    background-color: #17365d;
    color: white;
    border-radius: 8px;
    padding: 5px 10px;
    font-weight: bold;
    margin-right: 8px;
}

.nombre {
    font-size: 20px;
    font-weight: 700;
    color: #17365d;
}

.distancia {
    font-size: 18px;
    font-weight: 700;
    color: #168052;
    margin-top: 10px;
}

.coordenadas {
    font-size: 13px;
    color: #6b7683;
    margin-top: 5px;
}

.ubicacion {
    background-color: #edf4ff;
    border-left: 5px solid #2769b5;
    border-radius: 8px;
    padding: 14px;
    margin-bottom: 22px;
    color: #37516e;
}

.aviso {
    background-color: #fff8e8;
    border: 1px solid #eadfbd;
    border-radius: 10px;
    padding: 14px;
    margin-top: 15px;
    color: #685b37;
}

div.stButton > button {
    width: 100%;
    border-radius: 10px;
    height: 45px;
    font-weight: 700;
}

</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# CALCULAR DISTANCIA - HAVERSINE
# ---------------------------------------------------------

def calcular_distancia(lat1, lon1, lat2, lon2):

    radio_tierra = 6371

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)

    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    diferencia_latitud = lat2 - lat1
    diferencia_longitud = lon2 - lon1

    a = (
        math.sin(diferencia_latitud / 2) ** 2
        +
        math.cos(lat1)
        * math.cos(lat2)
        * math.sin(diferencia_longitud / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return radio_tierra * c


# ---------------------------------------------------------
# OBTENER ESTACIONES POLICIALES
# ---------------------------------------------------------

def obtener_estaciones(latitud, longitud):

    # Se intenta con varios servidores.
    # Si uno falla, automáticamente prueba el siguiente.
    servidores = [
        "https://overpass.private.coffee/api/interpreter",
        "https://overpass-api.de/api/interpreter"
    ]

    consulta = f"""
    [out:json][timeout:30];

    (
        node["amenity"="police"](around:50000,{latitud},{longitud});
        way["amenity"="police"](around:50000,{latitud},{longitud});
        relation["amenity"="police"](around:50000,{latitud},{longitud});
    );

    out center tags;
    """

    headers = {
        "User-Agent": "EstacionesPolicialesHonduras/1.0",
        "Accept": "application/json"
    }

    ultimo_error = None

    for url in servidores:

        try:

            respuesta = requests.post(
                url,
                data={
                    "data": consulta
                },
                headers=headers,
                timeout=60
            )

            respuesta.raise_for_status()

            datos = respuesta.json()

            estaciones = []

            for elemento in datos.get("elements", []):

                tags = elemento.get(
                    "tags",
                    {}
                )

                nombre = tags.get(
                    "name",
                    "Estación Policial"
                )

                # Nodo
                if elemento.get("type") == "node":

                    lat = elemento.get("lat")
                    lon = elemento.get("lon")

                # Way o relation
                else:

                    centro = elemento.get(
                        "center",
                        {}
                    )

                    lat = centro.get("lat")
                    lon = centro.get("lon")

                if lat is None or lon is None:
                    continue

                distancia = calcular_distancia(
                    latitud,
                    longitud,
                    lat,
                    lon
                )

                estaciones.append({
                    "nombre": nombre,
                    "latitud": lat,
                    "longitud": lon,
                    "distancia": distancia
                })

            # Ordenar de menor a mayor distancia
            estaciones.sort(
                key=lambda estacion: estacion["distancia"]
            )

            return estaciones

        except (
            requests.exceptions.RequestException,
            ValueError
        ) as error:

            ultimo_error = error

            print(
                f"Servidor no disponible: {url}"
            )

            print(
                f"Error: {error}"
            )

    raise RuntimeError(
        "No fue posible conectarse con los servidores "
        f"de búsqueda. Último error: {ultimo_error}"
    )


# ---------------------------------------------------------
# ENCABEZADO
# ---------------------------------------------------------

st.markdown("""
<div class="titulo">🚓 Estaciones Policiales Más Cercanas</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="subtitulo">
Utilice la ubicación de su dispositivo para encontrar
automáticamente las tres estaciones policiales más cercanas.
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# OBTENER UBICACIÓN DEL DISPOSITIVO
# ---------------------------------------------------------

st.subheader(
    "📍 Obtener mi ubicación"
)

st.write(
    "Presione el botón de ubicación y permita el acceso "
    "cuando su navegador lo solicite."
)

ubicacion = streamlit_geolocation()


# ---------------------------------------------------------
# VERIFICAR UBICACIÓN
# ---------------------------------------------------------

if (
    isinstance(ubicacion, dict)
    and ubicacion.get("latitude") is not None
    and ubicacion.get("longitude") is not None
):

    latitud = float(
        ubicacion["latitude"]
    )

    longitud = float(
        ubicacion["longitude"]
    )

    precision = ubicacion.get(
        "accuracy"
    )

    st.markdown(f"""
<div class="ubicacion">
<strong>✅ Ubicación obtenida correctamente</strong>
<br><br>
Latitud: {latitud:.6f}
<br>
Longitud: {longitud:.6f}
</div>
""", unsafe_allow_html=True)


    # -----------------------------------------------------
    # MOSTRAR PRECISIÓN
    # -----------------------------------------------------

    if precision is not None:

        st.caption(
            f"Precisión aproximada del dispositivo: "
            f"{precision:.0f} metros"
        )


    # -----------------------------------------------------
    # VALIDAR QUE ESTÉ EN HONDURAS
    # -----------------------------------------------------

    if not (
        12.8 <= latitud <= 17.5
        and
        -89.5 <= longitud <= -83.0
    ):

        st.error(
            "⚠️ La ubicación detectada no parece "
            "encontrarse dentro de Honduras."
        )

    else:

        # -------------------------------------------------
        # BOTÓN DE BÚSQUEDA
        # -------------------------------------------------

        if st.button(
            "🔎 Buscar estaciones cercanas",
            type="primary",
            use_container_width=True
        ):

            try:

                with st.spinner(
                    "Buscando estaciones policiales..."
                ):

                    estaciones = obtener_estaciones(
                        latitud,
                        longitud
                    )


                # -----------------------------------------
                # SIN RESULTADOS
                # -----------------------------------------

                if len(estaciones) == 0:

                    st.warning(
                        "No se encontraron estaciones policiales "
                        "registradas cerca de su ubicación."
                    )

                else:

                    # Solo necesitamos las 3 más cercanas
                    tres_mas_cercanas = estaciones[:3]

                    st.success(
                        f"✅ Se encontraron {len(estaciones)} "
                        "estaciones policiales cercanas."
                    )

                    st.subheader(
                        "🏆 Las 3 estaciones más cercanas"
                    )


                    # -------------------------------------
                    # MOSTRAR RESULTADOS
                    # -------------------------------------

                    for posicion, estacion in enumerate(
                        tres_mas_cercanas,
                        start=1
                    ):

                        st.markdown(f"""
<div class="tarjeta">
<span class="numero">{posicion}</span>
<span class="nombre">{estacion['nombre']}</span>
<div class="distancia">📏 Distancia aproximada: {estacion['distancia']:.2f} km</div>
<div class="coordenadas">📍 Latitud: {estacion['latitud']:.6f} &nbsp;&nbsp;|&nbsp;&nbsp; Longitud: {estacion['longitud']:.6f}</div>
</div>
""", unsafe_allow_html=True)


                    # -------------------------------------
                    # MAPA
                    # -------------------------------------

                    st.subheader(
                        "🗺️ Ubicación en el mapa"
                    )

                    datos_mapa = [
                        {
                            "lat": latitud,
                            "lon": longitud
                        }
                    ]

                    for estacion in tres_mas_cercanas:

                        datos_mapa.append({
                            "lat": estacion["latitud"],
                            "lon": estacion["longitud"]
                        })

                    df_mapa = pd.DataFrame(
                        datos_mapa
                    )

                    st.map(
                        df_mapa,
                        latitude="lat",
                        longitude="lon",
                        zoom=12
                    )

                    st.caption(
                        "El mapa muestra su ubicación y las "
                        "tres estaciones policiales más cercanas."
                    )


            # -------------------------------------------------
            # ERROR
            # -------------------------------------------------

            except Exception as error:

                st.error(
                    "❌ No fue posible consultar las estaciones "
                    "policiales en este momento."
                )

                st.write(
                    "Intente nuevamente dentro de unos segundos."
                )

                print(
                    "Error:",
                    error
                )


# ---------------------------------------------------------
# TODAVÍA NO HAY UBICACIÓN
# ---------------------------------------------------------

else:

    st.markdown("""
<div class="aviso">
📍 Primero debe permitir que el navegador obtenga
la ubicación del dispositivo.
<br><br>
En celular, asegúrese de tener activado el GPS.
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# PIE DE PÁGINA
# ---------------------------------------------------------

st.divider()

st.caption(
    "Las estaciones policiales son consultadas mediante "
    "información geográfica disponible en OpenStreetMap."
)
