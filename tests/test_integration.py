"""
Pruebas de Integración de Servicios y API REST
"""
import unittest
from fastapi.testclient import TestClient
from backend.main import app

class TestIntegracionAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_01_endpoint_inicio(self):
        """Verifica que el servicio raíz responda adecuadamente en formato JSON."""
        respuesta = self.client.get("/", headers={"accept": "application/json"})
        self.assertEqual(respuesta.status_code, 200)
        data = respuesta.json()
        self.assertIn("sistema", data)
        self.assertIn("endpoints", data)

    def test_02_autenticacion_login_y_registro(self):
        """Verifica el inicio de sesión para Admin y para Usuario Común, y registro."""
        # 1. Login Admin con "Admin" y PIN
        res_admin = self.client.post("/auth/login", json={"usuario": "Admin", "password": "231500"})
        self.assertEqual(res_admin.status_code, 200)
        self.assertEqual(res_admin.json()["rol"], "admin")

        # 2. Login Admin con clave incorrecta
        res_admin_mal = self.client.post("/auth/login", json={"usuario": "Admin", "password": "000"})
        self.assertEqual(res_admin_mal.status_code, 401)

        # 3. Login Usuario Común
        res_user = self.client.post("/auth/login", json={"usuario": "carlos.gomez@email.com", "password": "123456"})
        self.assertEqual(res_user.status_code, 200)
        self.assertEqual(res_user.json()["rol"], "comun")
        self.assertEqual(res_user.json()["id"], 1)

        # 4. Registro de nuevo tutor
        nuevo_usuario = {
            "nombre": "Usuario Prueba Registro",
            "email": "nuevo.usuario@test.com",
            "telefono": "3009990000",
            "password": "mypassword"
        }
        res_reg = self.client.post("/auth/registro", json=nuevo_usuario)
        self.assertEqual(res_reg.status_code, 201)
        self.assertEqual(res_reg.json()["rol"], "comun")

        # 5. Login con el usuario recién registrado
        res_login_reg = self.client.post("/auth/login", json={"usuario": "nuevo.usuario@test.com", "password": "mypassword"})
        self.assertEqual(res_login_reg.status_code, 200)

    def test_03_dashboard_global_y_privado_por_tutor(self):
        """Verifica métricas globales y filtradas exclusivamente por tutor."""
        # Global (Admin)
        res_global = self.client.get("/dashboard/resumen")
        self.assertEqual(res_global.status_code, 200)
        data_global = res_global.json()
        self.assertGreater(data_global["total_mascotas"], 1)
        self.assertGreater(data_global["total_propietarios"], 1)

        # Privado (Tutor #1 Carlos Gómez)
        res_privado = self.client.get("/dashboard/resumen?propietario_id=1")
        self.assertEqual(res_privado.status_code, 200)
        data_privado = res_privado.json()
        self.assertEqual(data_privado["total_propietarios"], 1)

        res_especie = self.client.get("/dashboard/por-especie?propietario_id=1")
        self.assertEqual(res_especie.status_code, 200)
        self.assertIsInstance(res_especie.json(), list)

    def test_04_filtro_mascotas_propias(self):
        """Verifica que el filtrado devuelva únicamente las mascotas del usuario."""
        respuesta = self.client.get("/mascotas?propietario_id=1")
        self.assertEqual(respuesta.status_code, 200)
        mascotas = respuesta.json()
        for m in mascotas:
            self.assertEqual(m["propietario_id"], 1)

    def test_05_seguridad_admin_pin(self):
        """Verifica la autenticación con PIN de administrador y cambio de PIN."""
        res_falla = self.client.post("/admin/verificar-pin", json={"pin": "000000"})
        self.assertEqual(res_falla.status_code, 401)

        res_ok = self.client.post("/admin/verificar-pin", json={"pin": "231500"})
        self.assertEqual(res_ok.status_code, 200)
        self.assertTrue(res_ok.json()["valido"])

        # Cambiar PIN
        res_cambio = self.client.post("/admin/cambiar-pin", json={
            "pin_actual": "231500",
            "nuevo_pin": "999900"
        })
        self.assertEqual(res_cambio.status_code, 200)

        # Login con el nuevo PIN
        res_admin_nuevo = self.client.post("/auth/login", json={"usuario": "Admin", "password": "999900"})
        self.assertEqual(res_admin_nuevo.status_code, 200)

        # Revertir al PIN estándar (231500)
        self.client.post("/admin/cambiar-pin", json={
            "pin_actual": "999900",
            "nuevo_pin": "231500"
        })

    def test_06_ciclo_integracion_propietario_mascota(self):
        """Flujo completo de integración: Crear Propietario -> Crear Mascota -> Actualizar -> Cascada."""
        nuevo_prop = {
            "nombre": "Test Integración",
            "telefono": "3999999999",
            "email": "test.integracion@redes.edu",
            "password": "password123"
        }
        res_prop = self.client.post("/propietarios", json=nuevo_prop)
        self.assertEqual(res_prop.status_code, 201)
        prop_id = res_prop.json()["id"]

        # Intento con propietario inexistente
        res_invalida = self.client.post("/mascotas", json={
            "nombre": "Fallo",
            "especie": "Perro",
            "propietario_id": 999999
        })
        self.assertEqual(res_invalida.status_code, 404)

        # Mascota válida
        res_mascota = self.client.post("/mascotas", json={
            "nombre": "Firulais Test",
            "especie": "Perro",
            "raza": "Mestizo",
            "edad": 2,
            "propietario_id": prop_id
        })
        self.assertEqual(res_mascota.status_code, 201)
        mascota_id = res_mascota.json()["id"]

        # Eliminar tutor y verificar borrado en cascada
        self.client.delete(f"/propietarios/{prop_id}")
        res_get = self.client.get(f"/mascotas/{mascota_id}")
        self.assertEqual(res_get.status_code, 404)

    def test_07_recargar_dataset(self):
        """Verifica la acción de recarga del dataset oficial."""
        respuesta = self.client.post("/dashboard/recargar-dataset")
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json()["registros_insertados"], 50)

if __name__ == "__main__":
    unittest.main()
