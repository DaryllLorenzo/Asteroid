# Validator Mode

The **Validator Mode** checks that actions performed in the diagram comply with Tropos methodological consistency rules. When active, actions that violate any rule are blocked and an error message is displayed.

## Activation

1. Go to the **Validation → Validator mode** menu
2. Check the option to activate it (click again to deactivate)

With the mode deactivated, there are no restrictions — behavior is normal.

---

## Implemented Rules

### 1. Actor/Agent inside Actor/Agent subcanvas

**Validated action:** Dragging a node into another node's subcanvas.

**Description:** Adding an Actor or Agent inside another Actor or Agent's subcanvas is not allowed. Subcanvases are designed exclusively for Tropos elements (Goals, Resources, Plans, Softgoals).

**Error message:**
> Cannot add an Actor/Agent inside another Actor/Agent's subcanvas. Subcanvases are for Tropos elements (Goals, Resources, Plans, Softgoals).

---

### 2. Dependency Link between Actors/Agents

**Validated action:** Creating a Dependency Link between two nodes.

**Description:** Creating a Dependency Link when both ends are Actors or Agents is not allowed. Links are only for connecting Tropos elements.

**Error message:**
> Cannot create a Dependency Link between Actors/Agents. Links are for Tropos elements inside the subcanvas.

---

### 3. Why Link between Actors/Agents

**Validated action:** Creating a Why Link between two nodes.

**Description:** Creating a Why Link when both ends are Actors or Agents is not allowed.

**Error message:**
> Cannot create a Why Link between Actors/Agents. Links are for Tropos elements inside the subcanvas.

---

### 4. Means-End between Actors/Agents

**Validated action:** Creating a Means-End link between two nodes.

**Description:** Creating a Means-End link when both ends are Actors or Agents is not allowed.

**Error message:**
> Cannot create a Means-End between Actors/Agents. Links are for Tropos elements inside the subcanvas.

---

### 5. OR Decomposition between Actors/Agents

**Validated action:** Creating an OR Decomposition between two nodes.

**Description:** Creating an OR Decomposition when both ends are Actors or Agents is not allowed.

**Error message:**
> Cannot create an OR Decomposition between Actors/Agents. Links are for Tropos elements inside the subcanvas.

---

### 6. AND Decomposition between Actors/Agents

**Validated action:** Creating an AND Decomposition between two nodes.

**Description:** Creating an AND Decomposition when both ends are Actors or Agents is not allowed.

**Error message:**
> Cannot create an AND Decomposition between Actors/Agents. Links are for Tropos elements inside the subcanvas.

---

### 7. Contribution between Actors/Agents

**Validated action:** Creating a Contribution link between two nodes.

**Description:** Creating a Contribution link when both ends are Actors or Agents is not allowed.

**Error message:**
> Cannot create a Contribution between Actors/Agents. Links are for Tropos elements inside the subcanvas.
