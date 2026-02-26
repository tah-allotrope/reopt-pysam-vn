import importlib.util
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "python" / "run_colab_api_reference.py"


def load_module(module_path: Path):
    spec = importlib.util.spec_from_file_location("run_colab_api_reference", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestApiResultSanitization(unittest.TestCase):
    def test_redact_sensitive_fields_removes_api_keys_recursively(self):
        module = load_module(SCRIPT_PATH)
        payload = {
            "api_key": "top-secret",
            "inputs": {
                "nested": {
                    "api_key": "nested-secret",
                    "keep": 123,
                }
            },
            "items": [
                {"api_key": "array-secret", "name": "row1"},
                "safe",
            ],
        }

        sanitized = module.redact_sensitive_fields(payload)

        self.assertNotIn("api_key", sanitized)
        self.assertNotIn("api_key", sanitized["inputs"]["nested"])
        self.assertNotIn("api_key", sanitized["items"][0])
        self.assertEqual(sanitized["inputs"]["nested"]["keep"], 123)
        self.assertEqual(sanitized["items"][1], "safe")


if __name__ == "__main__":
    unittest.main()
