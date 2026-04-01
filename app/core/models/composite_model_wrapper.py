# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------

class CompositeModelWrapper:
    """
    Wrapper que sincroniza propiedades compartidas (label, color) entre
    dos modelos de nodos: uno en el canvas principal y otro en subcanvas.
    
    Propiedades SINCRONIZADAS (se comparten):
        - label
        - color
        - border_color
        - text_color
    
    Propiedades INDEPENDIENTES (cada uno tiene la suya):
        - x, y (posición)
        - radius (tamaño)
        - position_in_subcanvas_x/y
        - content_offset_x/y
        - show_subcanvas
        - child_nodes
    """
    
    # Lista de propiedades que se sincronizan entre ambos modelos
    SYNCED_PROPERTIES = {'label', 'color', 'border_color', 'text_color'}
    
    def __init__(self, external_model, internal_model):
        """
        Args:
            external_model: El modelo del nodo en el canvas principal
            internal_model: El modelo del nodo dentro del subcanvas
        """
        object.__setattr__(self, '_external_model', external_model)
        object.__setattr__(self, '_internal_model', internal_model)
        # Callbacks para notificar cambios (opcional)
        object.__setattr__(self, '_on_change_callbacks', [])
    
    def _notify_change(self, prop_name, value):
        """Notifica a los callbacks que una propiedad cambió"""
        for callback in self._on_change_callbacks:
            try:
                callback(prop_name, value)
            except Exception:
                pass
    
    def add_change_callback(self, callback):
        """Agrega un callback que se llama cuando una propiedad sincronizada cambia"""
        self._on_change_callbacks.append(callback)
    
    # ==================== PROPIEDADES SINCRONIZADAS ====================
    
    @property
    def label(self):
        return self._external_model.label
    
    @label.setter
    def label(self, value):
        # Sincronizar en AMBOS modelos
        self._external_model.label = value
        self._internal_model.label = value
        self._notify_change('label', value)
    
    @property
    def color(self):
        return self._external_model.color
    
    @color.setter
    def color(self, value):
        self._external_model.color = value
        self._internal_model.color = value
        self._notify_change('color', value)
    
    @property
    def border_color(self):
        return self._external_model.border_color
    
    @border_color.setter
    def border_color(self, value):
        self._external_model.border_color = value
        self._internal_model.border_color = value
        self._notify_change('border_color', value)
    
    @property
    def text_color(self):
        return self._external_model.text_color
    
    @text_color.setter
    def text_color(self, value):
        self._external_model.text_color = value
        self._internal_model.text_color = value
        self._notify_change('text_color', value)
    
    # ==================== PROPIEDADES INDEPENDIENTES ====================
    # Se delegan al modelo externo por defecto (el del canvas principal)
    
    @property
    def x(self):
        return self._external_model.x
    
    @x.setter
    def x(self, value):
        self._external_model.x = value
    
    @property
    def y(self):
        return self._external_model.y
    
    @y.setter
    def y(self, value):
        self._external_model.y = value
    
    @property
    def radius(self):
        return self._external_model.radius
    
    @radius.setter
    def radius(self, value):
        self._external_model.radius = value
    
    @property
    def text_align(self):
        return self._external_model.text_align
    
    @text_align.setter
    def text_align(self, value):
        self._external_model.text_align = value
    
    @property
    def text_width(self):
        return self._external_model.text_width
    
    @text_width.setter
    def text_width(self, value):
        self._external_model.text_width = value
    
    @property
    def font_size(self):
        return self._external_model.font_size
    
    @font_size.setter
    def font_size(self, value):
        self._external_model.font_size = value
    
    @property
    def content_offset_x(self):
        return self._external_model.content_offset_x
    
    @content_offset_x.setter
    def content_offset_x(self, value):
        self._external_model.content_offset_x = value
    
    @property
    def content_offset_y(self):
        return self._external_model.content_offset_y
    
    @content_offset_y.setter
    def content_offset_y(self, value):
        self._external_model.content_offset_y = value
    
    @property
    def position_in_subcanvas_x(self):
        return self._external_model.position_in_subcanvas_x
    
    @position_in_subcanvas_x.setter
    def position_in_subcanvas_x(self, value):
        self._external_model.position_in_subcanvas_x = value
    
    @property
    def position_in_subcanvas_y(self):
        return self._external_model.position_in_subcanvas_y
    
    @position_in_subcanvas_y.setter
    def position_in_subcanvas_y(self, value):
        self._external_model.position_in_subcanvas_y = value
    
    @property
    def show_subcanvas(self):
        return self._external_model.show_subcanvas
    
    @show_subcanvas.setter
    def show_subcanvas(self, value):
        self._external_model.show_subcanvas = value
    
    @property
    def child_nodes(self):
        return self._external_model.child_nodes
    
    @child_nodes.setter
    def child_nodes(self, value):
        self._external_model.child_nodes = value
    
    # ==================== MÉTODOS ====================
    
    def toggle_subcanvas(self):
        return self._external_model.toggle_subcanvas()
    
    def node_type(self) -> str:
        return self._external_model.node_type()
    
    # ==================== ACCESO A MODELOS INTERNOS ====================
    
    def get_external_model(self):
        """Retorna el modelo externo (canvas principal)"""
        return self._external_model
    
    def get_internal_model(self):
        """Retorna el modelo interno (subcanvas)"""
        return self._internal_model
    
    # ==================== DELEGACIÓN GENÉRICA ====================
    # Para cualquier otra propiedad no definida, delegar al externo
    
    def __getattr__(self, name):
        """Delega propiedades no definidas al modelo externo"""
        # Evitar recursión infinita para atributos privados
        if name.startswith('_'):
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
        return getattr(self._external_model, name)
    
    def __setattr__(self, name, value):
        """Intercepta asignaciones para sincronizar solo label/color"""
        # Si es una propiedad sincronizada, actualizar ambos modelos
        if name in self.SYNCED_PROPERTIES:
            setattr(self._external_model, name, value)
            setattr(self._internal_model, name, value)
            self._notify_change(name, value)
        # Para el resto, solo actualizar el modelo externo
        else:
            setattr(self._external_model, name, value)
