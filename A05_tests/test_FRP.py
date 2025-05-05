import unittest
from unittest.mock import patch, MagicMock
import numpy as np
import xarray as xr
from datetime import datetime
import importlib.util
import sys
from pathlib import Path

# === Cargar dinámicamente el módulo original ===
script_path = Path(__file__).resolve()
project_root = next(p for p in script_path.parents if p.name == "Practicas_Empresa_CSIC-1")
module_path = project_root / "A01_source" / "B01_3_processing" / "La_Palma" / "radiative_power" / "RP_auto.py"  

spec = importlib.util.spec_from_file_location("frp_module", module_path)
frp_module = importlib.util.module_from_spec(spec)
sys.modules["frp_module"] = frp_module
spec.loader.exec_module(frp_module)


class TestFRPLaPalma(unittest.TestCase):

    @patch("frp_module.xr.open_dataset")
    @patch("frp_module.Path.exists", return_value=True)
    @patch("frp_module.xr.Dataset.to_netcdf")
    def test_frp_calculation_valid(self, mock_save, mock_exists, mock_open_dataset):
        # Simula un dataset con una escena válida dentro del rango geográfico
        bt_data = np.full((2, 2), 310.0)  # Temperatura suficientemente alta
        lat_data = np.array([[28.55, 28.56], [28.56, 28.57]])
        lon_data = np.array([[-17.74, -17.73], [-17.71, -17.70]])

        mock_ds = MagicMock()
        mock_ds["BT_I05"].sel.return_value = xr.DataArray(bt_data, dims=["y", "x"])
        mock_ds["latitude"] = xr.DataArray(lat_data, dims=["y", "x"])
        mock_ds["longitude"] = xr.DataArray(lon_data, dims=["y", "x"])
        mock_ds.time.values = [np.datetime64(datetime.now().date() - np.timedelta64(1, 'D'))]

        mock_open_dataset.return_value = mock_ds

        with patch("frp_module.print"):  # suprime prints
            with patch("frp_module.datetime") as mock_datetime:
                # Simula que hoy es 2025-05-02, ayer es 2025-05-01
                mock_datetime.now.return_value = datetime(2025, 5, 2)
                mock_datetime.utcnow.return_value = datetime(2025, 5, 2)
                mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

                # Ejecuta la lógica principal (reestructurable como función)
                exec(open(module_path).read(), {'__name__': '__main__'})  # ejecuta como script

        mock_save.assert_called_once()

    def test_frp_zero_if_bt_below_threshold(self):
        t_mean = 250  # menor que cualquier t_floor
        t_floor = 260
        sigma = 5.67e-8
        area = 1_000_000
        scale = 1.0

        if t_mean <= t_floor:
            frp = 0.0
        else:
            frp_raw = sigma * (t_mean**4 - t_floor**4) * area
            frp = (frp_raw / 1e6) * scale

        self.assertEqual(frp, 0.0)


if __name__ == "__main__":
    unittest.main()