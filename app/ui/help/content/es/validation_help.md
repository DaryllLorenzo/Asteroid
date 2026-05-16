# Modo Validador

El **Modo Validador** verifica que las acciones realizadas en el diagrama cumplan con las reglas de consistencia metodológica de Tropos. Cuando está activo, las acciones que violen alguna regla son bloqueadas y se muestra un mensaje de error.

## Activación

1. Ve al menú **Validación → Modo validador**
2. Marca la opción para activarlo (vuelve a hacer clic para desactivarlo)

Con el modo desactivado, no hay ninguna restricción — el comportamiento es el normal.

---

## Reglas Implementadas

### 1. Actor/Agente dentro de subcanvas de Actor/Agente

**Acción validada:** Arrastrar un nodo al subcanvas de otro nodo.

**Descripción:** No se permite agregar un Actor o Agente dentro del subcanvas de otro Actor o Agente. Los subcanvases están diseñados exclusivamente para elementos Tropos (Metas, Recursos, Planes, Softgoals).

**Mensaje de error:**
> No se puede agregar un Actor/Agente dentro del subcanvas de otro Actor/Agente. Los subcanvases son para elementos Tropos (Metas, Recursos, Planes, Softgoals).

---

### 2. Dependency Link entre Actores/Agentes

**Acción validada:** Crear un enlace Dependency Link entre dos nodos.

**Descripción:** No se permite crear un enlace Dependency Link cuando ambos extremos son Actores o Agentes. Los enlaces son únicamente para conectar elementos Tropos.

**Mensaje de error:**
> No se puede crear un enlace Dependency Link entre Actores/Agentes. Los enlaces son para elementos Tropos dentro del subcanvas.

---

### 3. Why Link entre Actores/Agentes

**Acción validada:** Crear un enlace Why Link entre dos nodos.

**Descripción:** No se permite crear un enlace Why Link cuando ambos extremos son Actores o Agentes.

**Mensaje de error:**
> No se puede crear un enlace Why Link entre Actores/Agentes. Los enlaces son para elementos Tropos dentro del subcanvas.

---

### 4. Means-End entre Actores/Agentes

**Acción validada:** Crear un enlace Means-End entre dos nodos.

**Descripción:** No se permite crear un enlace Means-End cuando ambos extremos son Actores o Agentes.

**Mensaje de error:**
> No se puede crear un enlace Means-End entre Actores/Agentes. Los enlaces son para elementos Tropos dentro del subcanvas.

---

### 5. OR Decomposition entre Actores/Agentes

**Acción validada:** Crear un enlace OR Decomposition entre dos nodos.

**Descripción:** No se permite crear un enlace OR Decomposition cuando ambos extremos son Actores o Agentes.

**Mensaje de error:**
> No se puede crear un enlace OR Decomposition entre Actores/Agentes. Los enlaces son para elementos Tropos dentro del subcanvas.

---

### 6. AND Decomposition entre Actores/Agentes

**Acción validada:** Crear un enlace AND Decomposition entre dos nodos.

**Descripción:** No se permite crear un enlace AND Decomposition cuando ambos extremos son Actores o Agentes.

**Mensaje de error:**
> No se puede crear un enlace AND Decomposition entre Actores/Agentes. Los enlaces son para elementos Tropos dentro del subcanvas.

---

### 7. Contribution entre Actores/Agentes

**Acción validada:** Crear un enlace Contribution entre dos nodos.

**Descripción:** No se permite crear un enlace Contribution cuando ambos extremos son Actores o Agentes.

**Mensaje de error:**
> No se puede crear un enlace Contribution entre Actores/Agentes. Los enlaces son para elementos Tropos dentro del subcanvas.
