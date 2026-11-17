"""
Pruebas unitarias de la app 'tienda'.
Se ejecutan con:  python manage.py test
Django crea una base de datos de prueba vacía, corre cada test y la borra al final,
así que estas pruebas NO tocan el db.sqlite3 real.
"""
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework.authtoken.models import Token

from .models import Categoria, Producto, PerfilUsuario


class ModelosTests(TestCase):
    """Verifica que los modelos principales se crean y se comportan bien."""

    def setUp(self):
        self.categoria = Categoria.objects.create(nombre="Frenos")

    def test_str_categoria(self):
        self.assertEqual(str(self.categoria), "Frenos")

    def test_crear_producto(self):
        producto = Producto.objects.create(
            nombre="Pastilla de freno", precio=15000, precio_mayorista=12000,
            descripcion="Juego delantero", stock=10, categoria=self.categoria,
            peso=1.5, largo=20, ancho=10, alto=5,
        )
        self.assertEqual(str(producto), "Pastilla de freno")
        self.assertEqual(self.categoria.productos.count(), 1)
        # Regla de negocio razonable: el precio mayorista no supera al normal
        self.assertLessEqual(producto.precio_mayorista, producto.precio)

    def test_perfil_usuario_por_defecto(self):
        # Un perfil nuevo no es trabajador ni empresa
        user = User.objects.create_user("carla", "carla@carla.carla", "Carla1!")
        perfil = PerfilUsuario.objects.create(user=user)
        perfil.refresh_from_db()
        self.assertFalse(perfil.trabajador)
        self.assertFalse(perfil.empresa)

    def test_backend_autentica_por_email(self):
        # tienda.authentication.EmailBackend permite iniciar sesión con el email
        User.objects.create_user("carla", "carla@carla.carla", "Carla1!")
        self.assertIsNotNone(authenticate(username="carla@carla.carla", password="Carla1!"))
        self.assertIsNone(authenticate(username="carla@carla.carla", password="incorrecta"))
        self.assertIsNone(authenticate(username="noexiste@x.cl", password="Carla1!"))


class LoginApiTests(TestCase):
    """Prueba el endpoint /api/login/ (login por email que devuelve un token)."""

    def setUp(self):
        self.url = reverse("api-login")
        User.objects.create_user("carla", "carla@carla.carla", "Carla1!")

    def test_login_correcto_devuelve_token(self):
        r = self.client.post(self.url, {"usuario": "carla@carla.carla", "contraseña": "Carla1!"})
        self.assertEqual(r.status_code, 200)
        self.assertIn("token", r.json())
        self.assertTrue(Token.objects.filter(key=r.json()["token"]).exists())

    def test_login_password_incorrecta(self):
        r = self.client.post(self.url, {"usuario": "carla@carla.carla", "contraseña": "mala"})
        self.assertEqual(r.status_code, 401)

    def test_login_sin_datos(self):
        r = self.client.post(self.url, {})
        self.assertEqual(r.status_code, 400)


class PaginasTests(TestCase):
    """Comprueba que las páginas públicas cargan (status 200)."""

    def setUp(self):
        self.categoria = Categoria.objects.create(nombre="Filtros")
        Producto.objects.create(
            nombre="Filtro de aceite", precio=8000, precio_mayorista=6000,
            descripcion="Filtro estándar", stock=5, categoria=self.categoria,
            peso=0.4, largo=10, ancho=10, alto=10,
        )

    def test_home(self):
        self.assertEqual(self.client.get(reverse("home")).status_code, 200)

    def test_login_page(self):
        self.assertEqual(self.client.get(reverse("login")).status_code, 200)

    def test_catalogo_muestra_categorias(self):
        # El catálogo pinta las categorías en el HTML (los productos los carga JS)
        r = self.client.get(reverse("catalogo"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Filtros")

    def test_api_productos_lista_productos(self):
        # La API pública que usa el catálogo devuelve el producto creado
        r = self.client.get(reverse("lista-productos-api"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Filtro de aceite")

    def test_api_productos_filtra_por_categoria(self):
        otra = Categoria.objects.create(nombre="Luces")
        r = self.client.get(reverse("lista-productos-api"), {"categoria": otra.id})
        self.assertEqual(r.status_code, 200)
        self.assertNotContains(r, "Filtro de aceite")
