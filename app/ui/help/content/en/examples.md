# Usage Examples

# I*/Tropos Flow: Virtual Teacher - Student
![](images/examples_help/example1.png)

## Example Context
An interaction between two actors/agents in a virtual educational system.

## Initial Dependency
**Student** → **Virtual Teacher**  
- **Dependency:** Complete exam
- **Dependum (resource):** Completed exam 
- **Flow:** The Student **depends** on the Virtual Teacher for the exam to be completed and graded.


## Actor: Student

### Main Objective
- **Hard Goal:** Take exam 

### How It Achieves It (Means-End)
1. **Means:** Plan: Solve questions 
   - The abstract way of approaching the exam.
2. **Required Resource:** Exam 
   - Needed to execute the plan.
3. **External Dependency:** Complete exam 
   - **Depends on:** Agent: Virtual Teacher 
   - **To obtain:** Completed exam (resource representing the completed and submitted exam).

**Student Summary:**  
 Resource(Exam) → Plan(Solve questions) → Goal(Take exam) → **Depends on** → Virtual Teacher for Complete exam.


## Agent: Virtual Teacher

### Starting Point
- **Receives:** Completed exam (resource) as a product of the Student's dependency.

### Objectives and Process
1. **Hard Goal 1:** Review exam 
   - **Means to achieve:** Plan: Review all questions 
   - **Triggered by:** The Completed exam resource.

2. **Hard Goal 2:** Give grade 
   - The final consequence of having reviewed the exam.

**Virtual Teacher Internal Flow:**  
 Resource(Completed exam) → Plan(Review all questions) → Goal(Review exam) → Goal(Give grade).

### Flow Explanation
1. The **Student** starts with a resource (Exam), executes a plan (Solve questions) to fulfill their goal (Take exam).
2. To complete their cycle, the Student establishes a **dependency** with the Virtual Teacher, requesting Complete exam.
3. This dependency **generates and transfers** the Completed exam resource to the **Virtual Teacher**.
4. The Virtual Teacher (concrete agent) takes that resource, executes their plan (Review questions) to fulfill their first goal (Review exam), and finally fulfills their final goal (Give grade), closing the dependency cycle.

### Essence of the I* Model
The **intentions (the "why")** and **strategic dependencies** between actors are modeled, rather than the operational sequence. The diagram explains that the Student **needs** the Teacher to complete their process, and the Teacher **requires** the completed exam from the Student to fulfill their own purpose.

---

# I*/Tropos Flow: Tourist – Travel Agent
![](images/examples_help/example2.png)

## Model Context

This I*/Tropos model represents the **vacation planning** process from the perspective of a **Tourist**, highlighting their **intentions, goals, and decisions**, as well as the **strategic dependency** with a **Travel Agent**.

The focus of the model is not on the operational sequence, but on **why the Tourist acts**, **what they need to achieve**, and **who they depend on** to complete their objective.

## Actor: Tourist

### General Objective

* **Hard goal:** Plan vacation *(implicit in the model)*


## Get destination information

### Hard goal

* **Get destination information**

### Alternative plans (OR-decomposition)

The Tourist can achieve this goal through different alternatives:

1. **Plan:** Search the web

   * **Resources (means–ends):**

     * Country keyword
     * Hotel category
       These resources act as necessary inputs to execute the search plan.

2. **Plan:** Get brochures

Both plans are related to the goal through **OR decomposition**, since either one satisfies the objective of obtaining information.

## Choose travel mode

### Hard goal

* **Choose a travel mode**

### Plan

* **Evaluate travel method**
  This plan is related to the goal through a **means–ends** relationship, as it represents the way to reach the final decision.

### Alternative plans (OR-decomposition)

To evaluate the travel method, the Tourist can choose between:

* **Plan:** Find train information
* **Plan:** Find airline information

These plans are linked through **OR decomposition**, since it is not mandatory to consider both types of transportation to make a decision.


## Strategic external dependency

### Dependency

**Tourist** → **Travel Agent**

* **Dependum:** Soft goal – *Select a good travel agent*
* **Type:** Softgoal dependency

The Tourist depends on the Travel Agent to satisfy this goal, since the notion of a "good agent" is subjective and cannot be evaluated strictly objectively.


## Global flow explanation

1. The Tourist seeks to plan their vacation and defines as main objectives obtaining destination information and choosing the means of transportation.
2. To get information, they can choose between searching the web or using brochures, using resources that facilitate the search.
3. To decide how to travel, they evaluate different transportation alternatives, considering trains or airlines.
4. With the information and decisions made, the Tourist establishes a strategic dependency with a Travel Agent to select a suitable agent.
5. The model reflects the **motivations and decisions of the Tourist**, rather than a detailed sequence of actions.


## Essence of the I*/Tropos Model

This model shows that:

* Actors act guided by **goals**.
* Goals can be achieved through **alternative plans**.
* There are **hard goals** and **soft goals**.
* **Strategic dependencies** allow us to understand how actors need others to fulfill their intentions.
