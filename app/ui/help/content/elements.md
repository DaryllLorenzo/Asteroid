# Elementos del Framework ASTEROID/Tropos
![](images/elements_help/all.png)

## Entidades Fundamentales

### Actor
![](images/elements_help/actor.png)
Una entidad que tiene **metas estratégicas e intenciones** dentro del sistema o del conjunto organizacional. Representa un **rol** o **papel** en el sistema, independientemente de su implementación física.

**Características:**
- Tiene objetivos y responsabilidades
- Interactúa con otros actores
- Puede ser humano, sistema o organización
- Define el "por qué" del sistema

### Agente
![](images/elements_help/agent.png)
Un **actor con manifestaciones físicas concretas**, como un ser humano, un sistema software, o un dispositivo. Se utiliza el término "agente" en lugar de "persona" para generalizar su utilización a cualquier entidad ejecutable.

**Características:**
- Implementación concreta de un actor
- Puede ejecutar acciones y planes
- Tiene capacidades físicas o lógicas
- Es la entidad que "hace" las cosas

---


## Enlaces (Links) de Dependencia

### Dependency Link
![](images/elements_help/link_dependency.png)
Cuando un **actor/agente depende de otro actor/agente** para alcanzar un objetivo, ejecutar un plan, o entregar un recurso.

---

## Enlances (Links) de Why
![](images/elements_help/link_why.png)
Más que un enlace gráfico explícito, es un **principio de modelado** que obliga a cuestionar y justificar la existencia de cada elemento. Responde a las preguntas **"¿por qué?"** existe un elemento y **"¿cómo?"** se logra.

---

## Enlaces (Links) de Descomposición

### OR Decomposition (Descomposición OR)
![](images/elements_help/link_or.png)
Donde las **submetas alternativas** representan formas alternativas de alcanzar la meta principal. Se satisface la meta principal si **al menos una** de las submetas se satisface.


### AND Decomposition (Descomposición AND)
![](images/elements_help/link_and.png)
**Todos los objetivos** deben cumplirse para que se cumpla el objetivo que representa la raíz de la descomposición.

---

## Enlaces (Links) Medio-Fin

### Means-End Link (Medio-Fin)
![](images/elements_help/link_means.png)
Dada una **meta**, la relación medio-fin especifica un **medio** en términos de un plan o recurso para lograr satisfacer esa meta.

---

## Enlaces (Links) de Contribución

### Contribution Link
![](images/elements_help/link_contribution.png)
Relación de un elemento (como una tarea o un objetivo) hacia un **softgoal**. Indica el **impacto** que tiene sobre la satisfacción de ese objetivo blando.

---


## Elementos Tropos (Intencionales)

### Meta Fuerte (Hardgoal)
![](images/elements_help/hard_goal.png)
Representa **metas a realizar** por un actor, con criterios claros y objetivos para definir si han sido satisfechas.

**Características:**
- **Medible**: Criterios claros de éxito
- **Binaria**: Se cumple o no se cumple
- **Específica**: Definición precisa
- **Ejemplo**: "Procesar 100 pedidos por hora", "Mantener disponibilidad del 99.9%"

### Meta Suave (Softgoal)
![](images/elements_help/soft_goal.png)
Representa **intenciones que favorecen** la realización de una meta, sin criterios claros para definir si han sido satisfechas completamente.

**Características:**
- **Subjetiva**: Evaluación cualitativa
- **Gradual**: Grado de satisfacción
- **Relativa**: Depende del contexto
- **Ejemplo**: "Mejorar la experiencia del usuario", "Ser eficiente energéticamente"

### Recurso (Resource)
![](images/elements_help/resource.png)
Representa una **entidad física o de información** necesaria para la ejecución de planes o satisfacción de metas.

**Características:**
- **Concreto**: Entidad tangible o digital
- **Consumible/No consumible**: Puede agotarse o ser reutilizable
- **Transferible**: Puede pasar entre actores
- **Ejemplo**: "Base de datos de clientes", "Servidor físico", "Documento PDF"

### Plan
![](images/elements_help/plan.png)
Representa una **forma de hacer algo** en un nivel abstracto. La ejecución del plan puede ser una manera de satisfacer una meta fuerte o una meta suave.

**Características:**
- **Abstracto**: Describe "qué hacer", no "cómo implementar"
- **Estratégico**: Alternativa para alcanzar objetivos
- **Ejecutable**: Puede ser realizado por un agente
- **Ejemplo**: "Plan de marketing", "Proceso de onboarding", "Estrategia de backup"


