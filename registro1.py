from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.slider import Slider
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup

AUTOR = 'Brisa Maribel V'
SISTEMA = 'SweetManager v1.0'
LIBRERIA = 'Kivy (kivy.org) con Python 3'
CATEGORIAS = ('Queques', 'Tortas', 'Brownies', 'Galletas', 'Pies y Tartas', 'Postres Frios')
ELABORACIONES = ('Artesanal / Tradicional', 'Sin Azucar / Keto', 'Vegano')

Window.size = (920, 780)


def titulo_widget(texto, size='15sp'):
    lbl = Label(text=texto, bold=True, font_size=size, size_hint_y=None, height=32,
                halign='left', valign='middle')
    lbl.bind(size=lambda w, v: setattr(w, 'text_size', (w.width, None)))
    return lbl


def campo(rotulo, widget):
    caja = BoxLayout(orientation='vertical', spacing=2, size_hint_y=None,
                     height=widget.height + 22)
    caja.add_widget(Label(text=rotulo, font_size='13sp', size_hint_y=None, height=20,
                          halign='left', valign='middle'))
    caja.add_widget(widget)
    return caja


def fila_check(rotulo):
    activo = [False]

    def alternar(_inst, valor):
        activo[0] = valor

    marca = CheckBox(active=False)
    marca.bind(active=alternar)
    fila = BoxLayout(orientation='horizontal', spacing=6, size_hint=(None, None), size=(300, 40))
    fila.add_widget(marca)
    fila.add_widget(Label(text=rotulo, halign='left', valign='middle'))
    return fila, activo, marca


class FormularioPostre(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', spacing=10, padding=10, **kwargs)
        self.registros = []

        self.add_widget(titulo_widget('Registro de Postres', '18sp'))

        self.nombre_postre = TextInput(multiline=False, size_hint_y=None, height=40,
                                       hint_text='Ej: Torta de Chocolate, Queque de Vainilla')
        self.add_widget(campo('Nombre / Descripcion del Postre', self.nombre_postre))

        self.ingredientes = TextInput(multiline=True, size_hint_y=None, height=110,
                                      hint_text='Detalles, alergenos, decoracion, requerimientos especiales...')
        self.add_widget(campo('Ingredientes / Notas Especiales', self.ingredientes))

        self.categoria = Spinner(text=CATEGORIAS[0], values=list(CATEGORIAS),
                                 size_hint_y=None, height=40)
        self.add_widget(campo('Categoria de Postre', self.categoria))

        self.elaboracion = Spinner(text=ELABORACIONES[0], values=list(ELABORACIONES),
                                   size_hint_y=None, height=40)
        self.add_widget(campo('Tipo de Elaboracion', self.elaboracion))

        checks = BoxLayout(spacing=15, size_hint_y=None, height=40)
        self.sin_gluten, self._gluten, self.marca_sin_gluten = fila_check(
            'Apto para Celiacos / Sin Gluten')
        self.incluye_empaque, self._empaque, self.marca_empaque = fila_check(
            'Incluye Empaque de Regalo')
        checks.add_widget(self.sin_gluten)
        checks.add_widget(self.incluye_empaque)
        self.add_widget(checks)

        numeros = BoxLayout(spacing=10, size_hint_y=None, height=62)
        self.stock = TextInput(text='1', multiline=False, input_filter='int',
                               size_hint_y=None, height=40)
        self.umbral = TextInput(text='5', multiline=False, input_filter='int',
                                size_hint_y=None, height=40)
        numeros.add_widget(campo('Cantidad Producida / Stock', self.stock))
        numeros.add_widget(campo('Umbral de Stock Bajo (para alerta)', self.umbral))
        self.add_widget(numeros)

        self.dulzor_text = Label(text='50%', size_hint_x=None, width=70,
                                 halign='right', valign='middle')
        self.dulzor = Slider(min=0, max=100, step=1, value=50,
                              size_hint_y=None, height=40)
        self.dulzor.bind(value=self.actualizar_dulzor)
        fila_dulzor = BoxLayout(spacing=10, size_hint_y=None, height=40)
        fila_dulzor.add_widget(Label(text='Nivel de Dulzor / Dificultad (%)',
                                      size_hint_x=None, width=250,
                                      halign='left', valign='middle'))
        fila_dulzor.add_widget(self.dulzor)
        fila_dulzor.add_widget(self.dulzor_text)
        self.add_widget(fila_dulzor)

        botones = BoxLayout(spacing=10, size_hint_y=None, height=40)
        for texto, accion in (('Registrar Postre', self.registrar_postre),
                              ('Alerta de Stock', self.mostrar_alerta),
                              ('Limpiar Formulario', self.limpiar_formulario),
                              ('Informacion del Sistema / Autor', self.mostrar_acerca)):
            boton = Button(text=texto)
            boton.bind(on_release=accion)
            botones.add_widget(boton)
        self.add_widget(botones)

        self.resultado = Label(text='', markup=True, size_hint_y=None, height=300,
                               halign='left', valign='top', font_size='14sp')
        self.resultado.bind(size=lambda w, v: setattr(w, 'text_size', (w.width, None)),
                            texture_size=lambda w, v: setattr(w, 'height', v[1]))
        self.resultado.height = self.resultado.texture_size[1]
        vista = ScrollView(do_scroll_x=False)
        vista.add_widget(self.resultado)
        self.add_widget(vista)

    def actualizar_dulzor(self, _widget, valor):
        self.dulzor_text.text = str(int(valor)) + '%'

    def registrar_postre(self, *_args):
        self.registros.append({
            'nombre': self.nombre_postre.text.strip() or 'Sin nombre',
            'categoria': self.categoria.text,
            'elaboracion': self.elaboracion.text,
            'ingredientes': self.ingredientes.text.strip() or 'Ninguna',
            'sin_gluten': self._gluten[0],
            'empaque': self._empaque[0],
            'stock': self.entero(self.stock.text),
            'dulzor': int(self.dulzor.value),
        })
        self.resultado.text = '\n\n'.join(self.linea(r) for r in self.registros)

    def limpiar_formulario(self, *_args):
        self.registros = []
        self.resultado.text = ''
        self.nombre_postre.text = ''
        self.ingredientes.text = ''
        self.categoria.text = CATEGORIAS[0]
        self.elaboracion.text = ELABORACIONES[0]
        self.marca_sin_gluten.active = False
        self.marca_empaque.active = False
        self.stock.text = '1'
        self.umbral.text = '5'
        self.dulzor.value = 50
        self.dulzor_text.text = '50%'

    def mostrar_alerta(self, *_args):
        umbral = self.entero(self.umbral.text)
        nombre = self.nombre_postre.text.strip() or 'Producto actual'
        stock = self.registros[-1]['stock'] if self.registros else self.entero(self.stock.text)
        detalle = (f'Stock actual: {stock} | Umbral configurado: {umbral}\n'
                   'Se recomienda reponer o priorizar produccion.'
                   if stock <= umbral else
                   f'Stock actual: {stock} | Umbral configurado: {umbral}\n'
                   'No hay alerta de stock en este momento.')
        self.popup('Alerta de Stock', f'{nombre}\n{detalle}')

    def mostrar_acerca(self, *_args):
        self.popup('Acerca de / Creditos',
                   f'Autor / Desarrollador: {AUTOR}\n'
                   f'Libreria de desarrollo utilizada: {LIBRERIA}\n'
                   f'Nombre del Sistema: {SISTEMA}\n'
                   'Version: 1.0')

    def popup(self, titulo, texto):
        Popup(title=titulo, content=Label(text=texto, markup=True),
              size_hint=(0.7, 0.4)).open()

    @staticmethod
    def entero(texto):
        try:
            return int(texto.strip())
        except (ValueError, AttributeError):
            return 0

    @staticmethod
    def linea(r):
        return ('[b]Ficha del Postre Registrado[/b]\n'
                f"Nombre / Descripcion: {r['nombre']}\n"
                f"Categoria: {r['categoria']}\n"
                f"Tipo de Elaboracion: {r['elaboracion']}\n"
                f"Ingredientes / Notas Especiales: {r['ingredientes']}\n"
                "Sin Gluten / Apto Celiacos: "
                + ('Si' if r['sin_gluten'] else 'No') + '\n'
                "Incluye Empaque de Regalo: "
                + ('Si' if r['empaque'] else 'No') + '\n'
                f"Cantidad Producida / Stock: {r['stock']}\n"
                f"Nivel de Dulzor/Dificultad: {r['dulzor']}%")


class SweetManagerApp(App):
    title = SISTEMA

    def build(self):
        return FormularioPostre()


if __name__ == '__main__':
    SweetManagerApp().run()