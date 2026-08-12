# 🚓 Estaciones Policiales Más Cercanas

## Descripción

Este proyecto consiste en una aplicación web desarrollada para localizar las estaciones policiales más cercanas según la ubicación actual del usuario.

La aplicación obtiene la latitud y longitud del dispositivo mediante el navegador y utiliza estas coordenadas para buscar estaciones policiales cercanas en Honduras.

Finalmente, muestra las 3 estaciones policiales más cercanas, su distancia aproximada y su ubicación en un mapa.

---

## Objetivo

Desarrollar una aplicación web en la nube que permita obtener la ubicación actual del usuario mediante coordenadas geográficas y encontrar automáticamente las tres estaciones policiales más cercanas.

---

## Funcionamiento

1. El usuario ingresa a la aplicación desde un celular o computadora.
2. La aplicación solicita permiso para acceder a la ubicación del dispositivo.
3. El navegador obtiene automáticamente la latitud y longitud del usuario.
4. El sistema utiliza las coordenadas para buscar estaciones policiales cercanas.
5. Se calcula la distancia entre la ubicación del usuario y cada estación encontrada.
6. Las estaciones se ordenan desde la más cercana hasta la más lejana.
7. Se muestran las 3 estaciones policiales más cercanas.
8. La aplicación muestra la distancia aproximada y las ubicaciones en un mapa.

---

## Tecnologías utilizadas

- Python
- Streamlit
- Streamlit Geolocation
- OpenStreetMap
- Overpass API
- Pandas
- Requests
- GitHub
- Streamlit Community Cloud
