"""
Pruebas de Microservicios Desacoplados (Service Auth y Service Mascotas)
"""
import unittest
import os
import sys
import importlib.util
from fastapi.testclient import TestClient

def cargar_app_microservicio(ruta_relativa: str):
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    ruta_archivo = os.path.join(base_dir, ruta_relativa)
    spec = importlib.util.spec_from_file_location("main", ruta_archivo)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.app

class TestMicroserviciosDesacoplados(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app_auth = cargar_app_microservicio("microservices/service-auth/main.py")
        app_masc = cargar_app_microservicio("microservices/service-mascotas/main.py")
        cls.client_auth = TestClient(app_auth)
        cls.client_mascotas = TestClient(app_masc)

    def test_health_checks_ambos_servicios(self):
        """Verifica que ambos microservicios expongan sus healthchecks para Swarm."""
        res_auth = self.client_auth.get("/health")
        self.assertEqual(res_auth.status_code, 200)
        self.assertEqual(res_auth.json()["service"], "service-auth")

        res_masc = self.client_mascotas.get("/health")
        self.assertEqual(res_masc.status_code, 200)
        self.assertEqual(res_masc.json()["service"], "service-mascotas")

    def test_service_auth_login_admin_y_comun(self):
        """Prueba autenticación en service-auth."""
        res_admin = self.client_auth.post("/auth/login", json={"usuario": "Admin", "password": "231500"})
        self.assertEqual(res_admin.status_code, 200)
        self.assertEqual(res_admin.json()["rol"], "admin")

        res_comun = self.client_auth.post("/auth/login", json={"usuario": "carlos.gomez@email.com", "password": "123456"})
        self.assertEqual(res_comun.status_code, 200)
        self.assertEqual(res_comun.json()["rol"], "comun")

    def test_service_mascotas_crud_y_dashboard(self):
        """Prueba listados y analíticas en service-mascotas."""
        res_list = self.client_mascotas.get("/mascotas")
        self.assertEqual(res_list.status_code, 200)
        self.assertIsInstance(res_list.json(), list)

        res_dash = self.client_mascotas.get("/dashboard/resumen")
        self.assertEqual(res_dash.status_code, 200)
        self.assertGreater(res_dash.json()["total_mascotas"], 0)

if __name__ == "__main__":
    unittest.main()

