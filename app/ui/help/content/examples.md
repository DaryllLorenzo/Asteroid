# Ejemplos de Uso

## Ejemplo 1: Flujo Simple
![](images/examples_help/example1.png)

# Flujo I*/Tropos: Profesor Virtual - Estudiante

## Contexto del Ejemplo
Se modela una interacción entre dos actores/agentes en un sistema educativo virtual.

## Dependencia Inicial
**Estudiante** → **Profesor Virtual**  
- **Dependencia:** Finalizar examen
- **Dependum (recurso):** Examen realizado 
- **Flujo:** El Estudiante **depende** del Profesor Virtual para que el examen sea finalizado y calificado.

---

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

---

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

---

### Explicación del Flujo
1.  El **Estudiante** inicia con un recurso ( Examen ), ejecuta un plan ( Resolver preguntas ) para cumplir su meta ( Realizar examen ).
2.  Para completar su ciclo, el Estudiante establece una **dependencia** con el Profesor Virtual, solicitando  Finalizar examen.
3.  Esta dependencia **genera y transfiere** el recurso  Examen realizado  al **Profesor Virtual**.
4.  El Profesor Virtual (agente concreto) toma ese recurso, ejecuta su plan ( Revisar preguntas ) para cumplir su primera meta ( Revisar examen ), y finalmente cumple su meta final ( Dar calificación ), cerrando así el ciclo de dependencia.

### Esencia del Modelo I*
Se modelan **las intenciones (el "por qué")** y **dependencias estratégicas** entre actores, más que la secuencia operativa. El diagrama explica que el Estudiante **necesita** al Profesor para finalizar su proceso, y el Profesor **requiere** el examen realizado del Estudiante para cumplir su propio propósito.