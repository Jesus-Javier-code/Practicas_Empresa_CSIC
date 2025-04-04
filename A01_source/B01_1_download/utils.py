import datetime

LAT_LA_PALMA_MIN = 28.601109109131052
LAT_LA_PALMA_MAX = 28.62514776637218
LON_LA_PALMA_MIN = -17.929768956228138
LON_LA_PALMA_MAX = -17.872144640744164

def obtener_fecha_ayer():
    ayer = datetime.datetime.now() - datetime.timedelta(1)
    return ayer.strftime("%Y"), ayer.strftime("%j")

def generar_url_api(product, year, doy, collection):
    return f"https://ladsweb.modaps.eosdis.nasa.gov/api/v2/content/details/allData/{collection}/{product}/{year}/{doy}"

def esta_en_la_palma(sur, norte, este, oeste):
    return (sur <= LAT_LA_PALMA_MAX and norte >= LAT_LA_PALMA_MIN and
            oeste <= LON_LA_PALMA_MAX and este >= LON_LA_PALMA_MIN)

def es_de_noche(day_night_flag):
    return day_night_flag.lower() == 'night'
