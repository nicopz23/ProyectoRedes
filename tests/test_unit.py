"""
Pruebas Unitarias de Componentes Individuales
"""
import unittest
import os
import sqlite3
from backend.schemas import PropietarioSchema, MascotaSchema
from backend.routes.dashboard import resumen_dashboard, distribucion_por_especie, distribucion_por_edad
from backend.database import obtener_conexion, inicializar_base_datos

class TestModelosUnitarios(unittest.TestCase):
    """Pruebas de validación de esquemas y modelos de datos."""

    def test_propietario_schema_valido(self):
        datos = {
            "nombre": "Carlos Gómez",
            "telefono": "3001234567",
            "email": "carlos@example.com"
        }
        modelo = PropietarioSchema(**datos)
        self.assertEqual(modelo.nombre, "Carlos Gómez")
        self.assertEqual(modelo.telefono, "3001234567")
        self.assertEqual(modelo.email, "carlos@example.com")

    def test_propietario_schema_campos_opcionales(self):
        modelo = PropietarioSchema(nombre="María Pérez")
        self.assertEqual(modelo.nombre, "María Pérez")
        self.assertIsNone(modelo.telefono)
        self.assertIsNone(modelo.email)

    def test_mascota_schema_valido(self):
        datos = {
            "nombre": "Max",
            "especie": "Perro",
            "raza": "Labrador",
            "edad": 4,
            "sexo": "Macho",
            "vacunado": 1,
            "propietario_id": 1
        }
        modelo = MascotaSchema(**datos)
        self.assertEqual(modelo.nombre, "Max")
        self.assertEqual(modelo.especie, "Perro")
        self.assertEqual(modelo.sexo, "Macho")
        self.assertEqual(modelo.vacunado, 1)
        self.assertEqual(modelo.propietario_id, 1)

    def test_mascota_schema_valores_por_defecto(self):
        modelo = MascotaSchema(nombre="Luna", especie="Gato", propietario_id=2)
        self.assertEqual(modelo.sexo, "No especificado")
        self.assertEqual(modelo.vacunado, 0)
        self.assertIsNone(modelo.raza)
        self.assertIsNone(modelo.edad)

class TestBaseDatosYAnaliticas(unittest.TestCase):
    """Pruebas unitarias de conexión a base de datos y lógica de agregación del dataset."""

    @classmethod
    def setUpClass(cls):
        inicializar_base_datos()

    def test_conexion_activa_y_foreign_keys(self):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("PRAGMA foreign_keys;")
        fk_activo = cursor.fetchone()[0]
        conexion.close()
        self.assertEqual(fk_activo, 1, "Las llaves foráneas deben estar activadas en SQLite")

    def test_resumen_dashboard_calculos(self):
        resumen = resumen_dashboard()
        self.assertIn("total_mascotas", resumen)
        self.assertIn("total_propietarios", resumen)
        self.assertIn("porcentaje_vacunados", resumen)
        self.assertGreater(resumen["total_mascotas"], 0, "Debe haber mascotas cargadas desde el dataset")
        self.assertGreater(resumen["total_propietarios"], 0, "Debe haber propietarios cargados")
        self.assertTrue(0 <= resumen["porcentaje_vacunados"] <= 100, "El porcentaje debe estar entre 0 y 100")

    def test_distribucion_por_especie_estructura(self):
        dist = distribucion_por_especie()
        self.assertIsInstance(dist, list)
        self.assertGreater(len(dist), 0)
        primer_item = dist[0]
        self.assertIn("especie", primer_item)
        self.assertIn("cantidad", primer_item)
        self.assertGreater(primer_item["cantidad"], 0)

    def test_distribucion_por_edad_estructura(self):
        dist = distribucion_por_edad()
        self.assertIsInstance(dist, list)
        self.assertGreater(len(dist), 0)
        for item in dist:
            self.assertIn("rango", item)
            self.assertIn("cantidad", item)

if __name__ == "__main__":
    unittest.main()
