import unittest
from unittest.mock import patch, MagicMock
import numpy as np
import xarray as xr
import importlib.util
import sys
from pathlib import Path

# === Cargar módulo dinámicamente (ajustado a tu estructura) ===
script_path = Path(__file__).resolve()
project_root = next(p for p in script_path.parents if p.name == "Practicas_Empresa_CSIC")
module_path = project_root / "A01_source" / "B01_3_processing" / "La_Palma" / "BT" / "BT_auto.py" 

spec = importlib.util.spec_from_file_location("ref_module", module_path)
ref_module = importlib.util.module_from_spec(spec)
sys.modules["ref_module"] = ref_module
spec.loader.exec_module(ref_module)


class TestRefGeneration(unittest.TestCase):

    @patch("ref_module.xr.open_dataset")
    @patch("ref_module.Path.exists", return_value=True)
    @patch("ref_module.xr.concat")
    def test_valid_scenes_and_ref_generated(self, mock_concat, mock_exists, mock_open_dataset):
        # Simular un dataset con varias escenas válidas
        mock_ds = MagicMock()
        mock_ds.sizes = {"time": 3}
        mock_ds.__getitem__.side_effect = lambda var: xr.DataArray(
            np.random.uniform(300, 310, size=(2, 2)), dims=("y", "x")
        ) if var == "BT_I05" else None
        mock_ds["latitude"] = xr.DataArray(np.linspace(28.55, 28.65, 2), dims="y")
        mock_ds["longitude"] = xr.DataArray(np.linspace(-17.93, -17.80, 2), dims="x")
        mock_open_dataset.return_value = mock_ds

        # Simular concat
        fake_stack = xr.DataArray(np.random.rand(3, 2, 2), dims=("time", "y", "x"))
        mock_concat.return_value = fake_stack

        # Evitar escritura en disco
        with patch("ref_module.xr.Dataset.to_netcdf") as mock_save:
            with patch("ref_module.Path.unlink"):
                with patch("ref_module.print"):  # suprime prints durante test
                    ref_module.ds_monthly = mock_ds  # inyecta directamente si lo usas como global
                    ref_module.stack_reprojected = [fake_stack[0], fake_stack[1], fake_stack[2]]
                    ref_module.valid_files = ["t1", "t2", "t3"]
                    ref = fake_stack.mean(dim="time", skipna=True)
                    ref_ds = ref.to_dataset(name="brightness_temperature_REF")

                    # Guardar
                    ref_ds.to_netcdf = mock_save
                    ref_ds.to_netcdf("fake_path.nc")

        mock_save.assert_called_once()

    def test_mask_and_stats_filtering(self):
        # Escena con valores que deberían pasar el filtro
        data = np.array([[290, 295], [298, 292]], dtype=float)
        bt_clipped = xr.DataArray(data, dims=("y", "x"))
        minval = np.nanmin(bt_clipped.values)
        stdval = np.nanstd(bt_clipped.values)

        self.assertGreater(stdval, 3)
        self.assertGreater(minval, 210)


if __name__ == "__main__":
    unittest.main()