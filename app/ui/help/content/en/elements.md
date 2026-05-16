# ASTEROID/Tropos Framework Elements
![](images/elements_help/all.png)

## Core Entities

### Actor
![](images/elements_help/actor.png)
An entity that has **strategic goals and intentions** within the system or organizational setting. It represents a **role** in the system, regardless of its physical implementation.

**Characteristics:**
- Has objectives and responsibilities
- Interacts with other actors
- Can be human, system, or organization
- Defines the "why" of the system

### Agent
![](images/elements_help/agent.png)
An **actor with concrete physical manifestations**, such as a human being, a software system, or a device. The term "agent" is used instead of "person" to generalize its use to any executable entity.

**Characteristics:**
- Concrete implementation of an actor
- Can execute actions and plans
- Has physical or logical capabilities
- Is the entity that "does" things

---

## Dependency Links

### Dependency Link
![](images/elements_help/link_dependency.png)
When an **actor/agent depends on another actor/agent** to achieve a goal, execute a plan, or deliver a resource.

---

## Why Links
![](images/elements_help/link_why.png)
More than an explicit graphical link, it is a **modeling principle** that requires questioning and justifying the existence of each element. It answers **"why?"** an element exists and **"how?"** it is achieved.

---

## Decomposition Links

### OR Decomposition
![](images/elements_help/link_or.png)
Where **alternative subgoals** represent alternative ways to achieve the main goal. The main goal is satisfied if **at least one** of the subgoals is satisfied.


### AND Decomposition
![](images/elements_help/link_and.png)
**All subgoals** must be satisfied for the root goal of the decomposition to be satisfied.

---

## Means-End Links

### Means-End Link
![](images/elements_help/link_means.png)
Given a **goal**, the means-end relationship specifies a **means** in terms of a plan or resource to achieve that goal.

---

## Contribution Links

### Contribution Link
![](images/elements_help/link_contribution.png)
Relationship from an element (such as a task or goal) to a **softgoal**. It indicates the **impact** on the satisfaction of that soft goal.

---


## Tropos Elements (Intentional)

### Hardgoal
![](images/elements_help/hard_goal.png)
Represents **goals to be achieved** by an actor, with clear criteria and objectives to define whether they have been satisfied.

**Characteristics:**
- **Measurable**: Clear success criteria
- **Binary**: Either satisfied or not
- **Specific**: Precise definition
- **Example**: "Process 100 orders per hour", "Maintain 99.9% availability"

### Softgoal
![](images/elements_help/soft_goal.png)
Represents **intentions that favor** the achievement of a goal, without clear criteria to define whether they have been fully satisfied.

**Characteristics:**
- **Subjective**: Qualitative evaluation
- **Gradual**: Degree of satisfaction
- **Relative**: Depends on context
- **Example**: "Improve user experience", "Be energy efficient"

### Resource
![](images/elements_help/resource.png)
Represents a **physical or information entity** needed for the execution of plans or satisfaction of goals.

**Characteristics:**
- **Concrete**: Tangible or digital entity
- **Consumable/Non-consumable**: Can be depleted or reusable
- **Transferable**: Can pass between actors
- **Example**: "Customer database", "Physical server", "PDF document"

### Plan
![](images/elements_help/plan.png)
Represents a **way of doing something** at an abstract level. Executing a plan can be a way to satisfy a hard goal or a softgoal.

**Characteristics:**
- **Abstract**: Describes "what to do", not "how to implement"
- **Strategic**: Alternative for achieving objectives
- **Executable**: Can be carried out by an agent
- **Example**: "Marketing plan", "Onboarding process", "Backup strategy"
