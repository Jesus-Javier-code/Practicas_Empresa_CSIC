import unittest
from unittest.mock import patch, MagicMock, mock_open
import builtins
import os
import sys
import datetime
from pathlib import Path

# Importar el módulo principal de descarga (ajusta si tu archivo tiene otro nombre)
import importlib.util

# Localiza la raíz del proyecto (asumiendo que este test está en /tests o similar)
script_path = Path(__file__).resolve()
project_root = next(p for p in script_path.parents if p.name == "Practicas_Empresa_CSIC")

# Ruta al script BT_auto.py dentro del proyecto
module_path = project_root / "A01_source" / "B01_1_download" / "La_Palma" / "download_LaPalma.py"


spec = importlib.util.spec_from_file_location("descarga", module_path)
descarga = importlib.util.module_from_spec(spec)
sys.modules["descarga"] = descarga
spec.loader.exec_module(descarga)


class TestDescargarDatos(unittest.TestCase):

    @patch("descarga.requests.get")
    @patch("descarga.os.system")
    @patch("descarga.netCDF4.Dataset")
    @patch("descarga.os.remove")
    @patch("descarga.os.makedirs")
    def test_descargar_datos1_valida(
        self, mock_makedirs, mock_remove, mock_dataset, mock_system, mock_get
    ):
        # Simular fecha
        with patch("descarga.obtener_fecha_ayer", return_value=("2025", "123")):

            # Simular respuesta API válida con enlace de descarga
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {
                "content": [{"downloadsLink": "https://fakeurl.com/file1.nc"}]
            }

            # Simular descarga (os.system)
            mock_system.return_value = 0

            # Simular atributos NetCDF válidos
            ds_mock = MagicMock()
            ds_mock.getncattr.side_effect = lambda attr: {
                "DayNightFlag": "Night",
                "SouthBoundingCoordinate": 28.60,
                "NorthBoundingCoordinate": 28.62,
                "EastBoundingCoordinate": -17.87,
                "WestBoundingCoordinate": -17.92,
            }[attr]
            mock_dataset.return_value = ds_mock

            # Ejecutar función
            descarga.descargar_datos1()

            # Verificar que se llamó a la API
            mock_get.assert_called_once()
            # Verificar que se intentó descargar el archivo
            mock_system.assert_called_once()
            # Verificar que no se eliminó el archivo (cumple condiciones)
            mock_remove.assert_not_called()

    @patch("descarga.requests.get")
    @patch("descarga.os.system")
    @patch("descarga.netCDF4.Dataset")
    @patch("descarga.os.remove")
    @patch("descarga.os.makedirs")
    def test_descargar_datos1_descarta_archivo(self, mock_makedirs, mock_remove, mock_dataset, mock_system, mock_get):
        with patch("descarga.obtener_fecha_ayer", return_value=("2025", "123")):
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {
                "content": [{"downloadsLink": "https://fakeurl.com/file1.nc"}]
            }

            mock_system.return_value = 0

            # Archivo que no cumple con las condiciones
            ds_mock = MagicMock()
            ds_mock.getncattr.side_effect = lambda attr: {
                "DayNightFlag": "Day",
                "SouthBoundingCoordinate": 28.00,
                "NorthBoundingCoordinate": 28.01,
                "EastBoundingCoordinate": -17.00,
                "WestBoundingCoordinate": -17.01,
            }[attr]
            mock_dataset.return_value = ds_mock

            descarga.descargar_datos1()

            mock_remove.assert_called_once()


if __name__ == '__main__':
    unittest.main()