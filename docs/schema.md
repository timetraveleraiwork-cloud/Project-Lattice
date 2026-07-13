# Company Operations Graph Schema

## Overview

This graph models a company's operations using a property graph. It captures employees, departments, vendors, contracts, projects, financial transactions, communications, and operational incidents.

The objective is to represent how these entities interact so that complex organizational questions can be answered efficiently using graph queries.

---

# Node Types

## 1. Person

### Properties

* employee_id
* name
* designation
* email
* phone

### Purpose

Represents an employee within the organization.

### Questions Answered

* Who works in the company?
* Who approved a transaction?
* Who is responsible for resolving an incident?

---

## 2. Department

### Properties

* department_id
* name
* location
* budget

### Purpose

Represents an organizational department.

### Questions Answered

* Which department does an employee belong to?
* Which department owns a project?

---

## 3. Vendor

### Properties

* vendor_id
* name
* service_type
* country

### Purpose

Represents an external company providing products or services.

### Questions Answered

* Which vendors work with the company?
* Which vendor received payments?

---

## 4. Contract

### Properties

* contract_id
* start_date
* end_date
* contract_value
* status

### Purpose

Represents agreements signed with vendors.

### Questions Answered

* Which contracts are currently active?
* Which vendor signed a particular contract?

---

## 5. Project

### Properties

* project_id
* name
* description
* status
* deadline

### Purpose

Represents business projects.

### Questions Answered

* Which projects are active?
* Which department owns a project?

---

## 6. Transaction

### Properties

* transaction_id
* amount
* payment_date
* currency

### Purpose

Represents financial transactions.

### Questions Answered

* What payments have been made?
* Who approved each payment?

---

## 7. Communication

### Properties

* communication_id
* type
* date
* subject

### Purpose

Represents emails, meetings, or messages.

### Questions Answered

* Who communicated with whom?
* What type of communication occurred?

---

## 8. Incident

### Properties

* incident_id
* title
* severity
* status
* reported_date

### Purpose

Represents operational issues requiring investigation.

### Questions Answered

* What incidents are currently open?
* Which employee is handling each incident?

---

# Relationship Types

## EMPLOYED_BY

Person → Department

### Purpose

Associates employees with their department.

### Question Answered

Which department employs a specific person?

---

## REPORTS_TO

Person → Person

### Purpose

Represents the management hierarchy.

### Question Answered

Who is the manager of a given employee?

---

## OWNS

Department → Project

### Purpose

Indicates ownership of projects.

### Question Answered

Which department is responsible for a project?

---

## SIGNED

Vendor → Contract

### Purpose

Connects vendors to signed contracts.

### Question Answered

Which vendor signed a contract?

---

## PAID

Transaction → Vendor

### Purpose

Represents payments made to vendors.

### Question Answered

Which vendor received a payment?

---

## APPROVED

Person → Transaction

### Purpose

Represents transaction approvals.

### Question Answered

Who approved a payment?

---

## COMMUNICATED_WITH

Person → Person

### Purpose

Represents communication between employees.

### Question Answered

Who communicated with whom?

---

## ASSIGNED_TO

Incident → Person

### Purpose

Assigns incidents to employees.

### Question Answered

Who is responsible for resolving an incident?

---

## RELATED_TO

Incident → Project

### Purpose

Links incidents to affected projects.

### Question Answered

Which project is impacted by an incident?

---

# Why These Nodes?

Each node represents a real-world entity with its own properties and lifecycle.

For example:

* A Person can approve transactions, report to managers, and communicate with colleagues.
* A Department can own multiple projects.
* A Vendor can sign multiple contracts.
* A Transaction exists independently of the employee who approved it.
* An Incident may affect a project even after the assigned employee changes.

Because these entities have independent identities and multiple relationships, modeling them as nodes keeps the graph flexible and avoids duplication.

---

# Why These Relationships?

Relationships describe how entities interact.

Instead of storing information like:

Employee.Department = "IT"

the graph stores

(Person)-[:EMPLOYED_BY]->(Department)

This allows efficient graph traversal and supports questions such as:

* Find everyone who reports to the IT Director.
* Find every payment approved by Finance employees.
* Find vendors associated with projects that currently have critical incidents.

---

# Graph Model

(Person)-[:EMPLOYED_BY]->(Department)

(Person)-[:REPORTS_TO]->(Person)

(Department)-[:OWNS]->(Project)

(Vendor)-[:SIGNED]->(Contract)

(Transaction)-[:PAID]->(Vendor)

(Person)-[:APPROVED]->(Transaction)

(Person)-[:COMMUNICATED_WITH]->(Person)

(Incident)-[:ASSIGNED_TO]->(Person)

(Incident)-[:RELATED_TO]->(Project)

---

# Design Principles

* Every node represents a distinct business entity.
* Every relationship represents a meaningful business interaction.
* No unnecessary node types have been introduced.
* Properties are stored on nodes, while interactions are represented as relationships.
* The schema is designed to support future Neo4j queries without requiring structural changes.

---

# Example Cypher Queries This Schema Supports

```cypher
MATCH (p:Person)-[:EMPLOYED_BY]->(d:Department)
RETURN p.name, d.name;
```

```cypher
MATCH (p:Person)-[:APPROVED]->(t:Transaction)
RETURN p.name, t.amount;
```

```cypher
MATCH (i:Incident)-[:ASSIGNED_TO]->(p:Person)
RETURN i.title, p.name;
```

```cypher
MATCH (d:Department)-[:OWNS]->(pr:Project)
RETURN d.name, pr.name;
```
