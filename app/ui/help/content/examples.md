# Ejemplos de Uso

# Flujo I*/Tropos: Profesor Virtual - Estudiante
![](images/examples_help/example1.png)

## Contexto del Ejemplo
Se modela una interacción entre dos actores/agentes en un sistema educativo virtual.

## Dependencia Inicial
**Estudiante** → **Profesor Virtual**  
- **Dependencia:** Finalizar examen
- **Dependum (recurso):** Examen realizado 
- **Flujo:** El Estudiante **depende** del Profesor Virtual para que el examen sea finalizado y calificado.


## Actor: Estudiante

### Objetivo Principal
- **Meta Fuerte:**  Realizar examen 

### Cómo lo logra (Medios-Fines)
1. **Medio:**  Plan: Resolver preguntas 
   - Es la forma abstracta de cómo aborda el examen.
2. **Recurso Necesario:**  Examen 
   - Lo necesita para ejecutar el plan.
3. **Dependencia Externa:**  Finalizar examen 
   - **Depender de:**  Agente: Profesor Virtual 
   - **Para obtener:**  Examen realizado  (recurso que representa el examen completado y entregado).

**Resumen Estudiante:**  
 Recurso(Examen)  →  Plan(Resolver preguntas)  →  Meta(Realizar examen)  → **Depende de** →  Profesor Virtual para Finalizar examen.


## Agente: Profesor Virtual

### Punto de Partida
- **Recibe:**  Examen realizado  (recurso) como producto de la dependencia del Estudiante.

### Objetivos y Proceso
1.  **Meta Fuerte 1:**  Revisar examen 
    - **Medio para lograrlo:**  Plan: Revisar todas las preguntas 
    - **Se activa con:** El recurso  Examen realizado.

2.  **Meta Fuerte 2:**  Dar calificación 
    - Es la consecuencia final de haber revisado el examen.

**Flujo Interno del Profesor:**  
 Recurso(Examen realizado)  →  Plan(Revisar todas las preguntas)  →  Meta(Revisar examen)  →  Meta(Dar calificación).

### Explicación del Flujo
1.  El **Estudiante** inicia con un recurso ( Examen ), ejecuta un plan ( Resolver preguntas ) para cumplir su meta ( Realizar examen ).
2.  Para completar su ciclo, el Estudiante establece una **dependencia** con el Profesor Virtual, solicitando  Finalizar examen.
3.  Esta dependencia **genera y transfiere** el recurso  Examen realizado  al **Profesor Virtual**.
4.  El Profesor Virtual (agente concreto) toma ese recurso, ejecuta su plan ( Revisar preguntas ) para cumplir su primera meta ( Revisar examen ), y finalmente cumple su meta final ( Dar calificación ), cerrando así el ciclo de dependencia.

### Esencia del Modelo I*
Se modelan **las intenciones (el "por qué")** y **dependencias estratégicas** entre actores, más que la secuencia operativa. El diagrama explica que el Estudiante **necesita** al Profesor para finalizar su proceso, y el Profesor **requiere** el examen realizado del Estudiante para cumplir su propio propósito.

---

# Flujo I*/Tropos: Turista – Agente de Viajes
![](images/examples_help/example2.png)

## Contexto del Modelo

Este modelo I*/Tropos representa el proceso de **planificación de un viaje** desde la perspectiva de un **Turista**, destacando sus **intenciones, metas y decisiones**, así como la **dependencia estratégica** con un **Agente de Viajes**.

El foco del modelo no está en la secuencia operativa, sino en **por qué el Turista actúa**, **qué necesita lograr** y **de quién depende** para completar su objetivo.

## Actor: Turista

### Objetivo General

* **Meta fuerte:** Planificar vacaciones *(implícita en el modelo)*


## Obtener información del destino

### Meta fuerte

* **Obtener información del destino**

### Planes alternativos (OR-decomposition)

El Turista puede alcanzar esta meta mediante distintas alternativas:

1. **Plan:** Buscar en la web

   * **Recursos (means–ends):**

     * Palabra clave del país
     * Categoría del hotel
       Estos recursos actúan como insumos necesarios para ejecutar el plan de búsqueda.

2. **Plan:** Obtener folletos

Ambos planes están relacionados con la meta mediante una **descomposición OR**, ya que cualquiera de ellos permite satisfacer el objetivo de obtener información.

## Elegir el modo de viaje

### Meta fuerte

* **Escoger un modo de viaje**

### Plan

* **Evaluar método de viaje**
  Este plan se relaciona con la meta mediante una relación **means–ends**, ya que representa la forma de alcanzar la decisión final.

### Planes alternativos (OR-decomposition)

Para evaluar el método de viaje, el Turista puede optar por:

* **Plan:** Encontrar información de trenes
* **Plan:** Encontrar información de aerolíneas

Estos planes están vinculados mediante una **descomposición OR**, dado que no es obligatorio considerar ambos tipos de transporte para tomar una decisión.


## Dependencia estratégica externa

### Dependencia

**Turista** → **Agente de Viajes**

* **Dependum:** Meta débil – *Seleccionar un buen agente de viajes*
* **Tipo:** Dependencia de meta blanda (softgoal)

El Turista depende del Agente de Viajes para satisfacer esta meta, ya que la noción de “buen agente” es subjetiva y no puede evaluarse de manera estrictamente objetiva.


## Explicación global del flujo

1. El Turista busca planificar sus vacaciones y define como objetivos principales la obtención de información del destino y la elección del medio de transporte.
2. Para obtener información, puede optar entre buscar en la web o utilizar folletos, utilizando recursos que facilitan la búsqueda.
3. Para decidir cómo viajar, evalúa distintas alternativas de transporte, considerando trenes o aerolíneas.
4. Con la información y las decisiones tomadas, el Turista establece una dependencia estratégica con un Agente de Viajes para seleccionar un agente adecuado.
5. El modelo refleja las **motivaciones y decisiones del Turista**, más que una secuencia detallada de acciones.


## Esencia del Modelo I*/Tropos

Este modelo muestra que:

* Los actores actúan guiados por **metas**.
* Las metas pueden alcanzarse mediante **planes alternativos**.
* Existen **metas fuertes** y **metas débiles**.
* Las **dependencias estratégicas** permiten comprender cómo los actores necesitan de otros para cumplir sus intenciones.

---
