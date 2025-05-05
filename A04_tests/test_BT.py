import unittest
from unittest.mock import patch, MagicMock
import numpy as np
import xarray as xr
from datetime import datetime
from netCDF4 import Dataset
from pathlib import Path

# Importa tu script co  mo módulo
import importlib.util
import sys

# Localiza la raíz del proyecto (asumiendo que este test está en /tests o similar)
script_path = Path(__file__).resolve()
project_root = next(p for p in script_path.parents if p.name == "Practicas_Empresa_CSIC-1")

# Ruta al script BT_auto.py dentro del proyecto
module_path = project_root / "A01_source" / "B01_3_processing" / "La_Palma" / "BT" / "BT_auto.py"


spec = importlib.util.spec_from_file_location("bt_module", module_path)
bt_module = importlib.util.module_from_spec(spec)
sys.modules["bt_module"] = bt_module
spec.loader.exec_module(bt_module)


class TestBTProcessing(unittest.TestCase):

    def test_radiance_to_bt_valid(self):
        # Simula radiancia positiva y finita
        radiance = np.array([[1.0, 2.0], [3.0, 4.0]])
        bt = bt_module.radiance_to_bt(radiance)

        self.assertTrue(np.all(np.isfinite(bt)))
        self.assertEqual(bt.shape, radiance.shape)

    def test_radiance_to_bt_invalid(self):
        # Radiancia con valores no válidos (0, negativos)
        radiance = np.array([[0.0, -1.0], [np.nan, 5.0]])
        bt = bt_module.radiance_to_bt(radiance)

        self.assertTrue(np.isnan(bt[0, 0]))
        self.assertTrue(np.isnan(bt[0, 1]))
        self.assertTrue(np.isnan(bt[1, 0]))
        self.assertTrue(np.isfinite(bt[1, 1]))

    @patch("bt_module.Dataset")
    def test_process_to_monthly_structure(self, mock_dataset_class):
        # Simula el Dataset del NetCDF
        mock_nc = MagicMock()
        mock_obs_group = MagicMock()
        mock_obs_group.__getitem__.return_value.filled.return_value = np.ones((2, 2))
        mock_nc.groups = {'observation_data': mock_obs_group}
        mock_nc.getncattr.side_effect = lambda attr: {
            'SouthBoundingCoordinate': 28.60,
            'NorthBoundingCoordinate': 28.62,
            'WestBoundingCoordinate': -17.92,
            'EastBoundingCoordinate': -17.90,
        }[attr]
        mock_dataset_class.return_value.__enter__.return_value = mock_nc

        date = datetime(2025, 1, 2)
        result = bt_module.process_to_monthly("fake.nc", date)

        self.assertIsInstance(result, xr.DataArray)
        self.assertIn("time", result.dims)
        self.assertIn("x", result.dims)
        self.assertIn("y", result.dims)
        self.assertEqual(result.shape[0], 1)  # Only one time slice


if __name__ == '__main__':
    unittest.main()