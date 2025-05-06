import os
import glob
import numpy as np
import xarray as xr
import rioxarray
from tqdm import tqdm
from rasterio.enums import Resampling
from datetime import datetime, timedelta
import calendar
from pathlib import Path
from dateutil.relativedelta import relativedelta

# === CONFIGURACIÓN ===
script_path = Path(__file__).resolve()
proyecto_dir = next(p for p in script_path.parents if p.name == "Practicas_Empresa_CSIC-1")
base_path = proyecto_dir / "A00_data" / "B_processed" / "Lanzarote" / "BT_daily_pixels"
output_dir = proyecto_dir / "A00_data" / "B_processed" / "Lanzarote" / "REF"
output_dir.mkdir(parents=True, exist_ok=True)

# === FECHAS A PROCESAR ===
fecha_inicio = datetime(2025, 1, 1)
fecha_fin = datetime(2025, 4, 29)
fecha_actual = fecha_inicio

while fecha_actual <= fecha_fin:
    año_ref = fecha_actual.year
    mes_ref = fecha_actual.month

    try:
        print(f"\n=== Generando REF para {año_ref}-{mes_ref:02d} ===")

        primer_dia = datetime(año_ref, mes_ref, 1)
        ultimo_dia = datetime(año_ref, mes_ref, calendar.monthrange(año_ref, mes_ref)[1])
        julian_inicio = primer_dia.timetuple().tm_yday
        julian_final = ultimo_dia.timetuple().tm_yday

        archivos = []
        for dia_juliano in range(julian_inicio, julian_final + 1):
            carpeta = os.path.join(base_path, f"{año_ref}_{dia_juliano:03d}")
            archivos += glob.glob(os.path.join(carpeta, f"BT_LaPalma_VJ102IMG_{año_ref}_*.nc"))

        print(f"Archivos encontrados: {len(archivos)}")

        if len(archivos) == 0:
            print("No hay archivos. Se salta este mes.")
            fecha_actual += relativedelta(months=1)
            continue

        # === PASO 2: Plantilla con la primera escena ===
        ds_ref = xr.open_dataset(archivos[0])
        bt = ds_ref["BT_I05"]
        lat = ds_ref["latitude"]
        lon = ds_ref["longitude"]

        lat1d = lat[:, 0].values
        lon1d = lon[0, :].values

        bt_template = xr.DataArray(
            data=bt.data,
            dims=("latitude", "longitude"),
            coords={"latitude": lat1d, "longitude": lon1d},
            name="brightness_temperature"
        )
        bt_template.rio.set_spatial_dims(x_dim="longitude", y_dim="latitude", inplace=True)
        bt_template.rio.write_crs("EPSG:4326", inplace=True)

        # === PASO 3: Reproyectar y filtrar ===
        stack_reproyectado = []
        archivos_buenos = []

        for archivo in tqdm(archivos):
            ds = xr.open_dataset(archivo)
            bt = ds["BT_I05"]
            lat = ds["latitude"]
            lon = ds["longitude"]

            lat1d = lat[:, 0].values
            lon1d = lon[0, :].values

            bt_scene = xr.DataArray(
                data=bt.data,
                dims=("latitude", "longitude"),
                coords={"latitude": lat1d, "longitude": lon1d},
                name="brightness_temperature"
            )
            bt_scene.rio.set_spatial_dims(x_dim="longitude", y_dim="latitude", inplace=True)
            bt_scene.rio.write_crs("EPSG:4326", inplace=True)

            bt_aligned = bt_scene.rio.reproject_match(bt_template)

            minval = np.nanmin(bt_aligned.values)
            stdval = np.nanstd(bt_aligned.values)
            if stdval > 3 and minval > 210:
                stack_reproyectado.append(bt_aligned)
                archivos_buenos.append(os.path.basename(archivo))
                print(f"{os.path.basename(archivo)} OK (min={minval:.2f}, std={stdval:.2f})")
            else:
                print(f"{os.path.basename(archivo)} DESCARTADA (min={minval:.2f}, std={stdval:.2f})")

        print(f"Escenas aceptadas: {len(stack_reproyectado)} / {len(archivos)}")

        if len(stack_reproyectado) == 0:
            print("No hay escenas útiles. Se salta este mes.")
            fecha_actual += relativedelta(months=1)
            continue

        # === PASO 4: Apilar y calcular REF
        stack = xr.concat(stack_reproyectado, dim="time")
        stack["time"] = np.arange(len(stack_reproyectado))
        ref = stack.mean(dim="time", skipna=True)

        # === PASO 6: Guardar NetCDF
        ref_ds = ref.to_dataset(name="brightness_temperature_REF")
        ref_ds["brightness_temperature_REF"].attrs["units"] = "K"
        ref_ds.attrs["descripcion"] = "REF mensual con escenas filtradas (std > 3 y min > 210)"
        ref_ds.attrs["archivos_usados"] = ", ".join(archivos_buenos)
        ref_ds = ref_ds.assign_coords({
            "latitude": (("latitude",), lat1d),
            "longitude": (("longitude",), lon1d)
        })

        output_filename = f"Ref_{año_ref}_{mes_ref:02d}.nc"
        output_path = output_dir / output_filename

        try:
            if output_path.exists():
                output_path.unlink()
            ref_ds.to_netcdf(output_path, mode="w")
            print(f"¡REF guardada en: {output_path}")
        except PermissionError:
            print("No se pudo sobrescribir el archivo. ¿Está abierto en otro programa?")
            alt_output_path = output_dir / f"Ref_{año_ref}_{mes_ref:02d}_v2.nc"
            ref_ds.to_netcdf(alt_output_path, mode="w")
            print(f"REF guardada como versión alternativa: {alt_output_path}")

    except Exception as e:
        print(f"Error al procesar {año_ref}-{mes_ref:02d}: {e}")

    # Avanzar al mes siguiente
    fecha_actual += relativedelta(months=1)