# Project Lattice - Cypher Query Library

## Week 4 - Day 2

---

## Overview

This document contains a handwritten library of Cypher queries for the Project Lattice knowledge graph.

The purpose of this document is to:

- verify that the knowledge graph has been populated correctly
- answer common business questions
- provide a golden query set for evaluating the upcoming Text-to-Cypher agent
- serve as regression tests whenever the graph schema changes

Each query includes:

- Business Question
- Cypher Query
- Expected Output
- Why it is useful

---

# Section 1 — Organization Queries

---

## Query 1 — Employees by Department

### Business Question

Which employees work in each department?

### Cypher

```cypher
MATCH (p:Person)-[:WORKS_IN]->(d:Department)
RETURN
    d.name AS Department,
    collect(DISTINCT p.name) AS Employees,
    COUNT(DISTINCT p) AS EmployeeCount
ORDER BY EmployeeCount DESC;
```

### Expected Output

| Department | Employees | EmployeeCount |
|------------|-----------|---------------|
| Finance | [...] | 8 |
| IT | [...] | 6 |
| Operations | [...] | 5 |

### Why this query?

This verifies that employee-to-department relationships were extracted correctly.

### Concepts Demonstrated

- MATCH
- Aggregation
- collect()
- COUNT()
- ORDER BY

---

## Query 2 — Reporting Hierarchy

### Business Question

Who reports to whom?

### Cypher

```cypher
MATCH (employee:Person)-[:REPORTS_TO]->(manager:Person)
RETURN
    employee.name AS Employee,
    manager.name AS Manager
ORDER BY Manager, Employee;
```

### Expected Output

| Employee | Manager |
|----------|---------|
| Rahul Sharma | Anita Mehta |
| Priya Rao | Rahul Sharma |

### Why this query?

Useful for validating organizational hierarchy.

### Concepts Demonstrated

- Relationship traversal
- Sorting

---

## Query 3 — Roles by Department

### Business Question

Which roles exist in every department?

### Cypher

```cypher
MATCH (p:Person)-[:HAS_ROLE]->(r:Role)
MATCH (p)-[:WORKS_IN]->(d:Department)
RETURN
    d.name AS Department,
    collect(DISTINCT r.name) AS Roles
ORDER BY Department;
```

### Expected Output

| Department | Roles |
|------------|-------|
| Finance | Finance Manager, Analyst |
| IT | System Administrator, Engineer |

### Why this query?

Checks whether role extraction is connected properly to employees and departments.

### Concepts Demonstrated

- Multiple MATCH clauses
- collect(DISTINCT)

---

# Section 2 — Finance Queries

---

## Query 4 — Top Payment Approvers

### Business Question

Who approved the largest number of transactions?

### Cypher

```cypher
MATCH (p:Person)-[:APPROVED]->(t:Transaction)
RETURN
    p.name AS Approver,
    COUNT(t) AS TransactionsApproved
ORDER BY TransactionsApproved DESC;
```

### Expected Output

| Approver | TransactionsApproved |
|----------|----------------------|
| Rahul Sharma | 18 |
| Anita Mehta | 15 |

### Why this query?

Identifies approval workload and validates approval relationships.

### Concepts Demonstrated

- COUNT()
- Aggregation
- ORDER BY

---

## Query 5 — Vendors Receiving Highest Payments

### Business Question

Which vendors received the highest payments?

### Cypher

```cypher
MATCH (t:Transaction)-[:PAID_TO]->(v:Vendor)
MATCH (t)-[:HAS_AMOUNT]->(a:Amount)
RETURN
    v.name AS Vendor,
    SUM(toFloat(a.value)) AS TotalPaid
ORDER BY TotalPaid DESC;
```

### Expected Output

| Vendor | TotalPaid |
|---------|-----------|
| ABC Technologies | 1450000 |
| Orion Systems | 980000 |

### Why this query?

Validates payment relationships and financial aggregation.

### Concepts Demonstrated

- SUM()
- Numeric aggregation
- Multiple MATCH statements

---

# End of Part 1

# Section 3 — Vendor & Financial Analysis

---

## Query 6 — Invoice Count by Vendor

### Business Question

How many invoices are associated with each vendor?

### Cypher

```cypher
MATCH (v:Vendor)-[:HAS_INVOICE]->(i:Invoice)
RETURN
    v.name AS Vendor,
    COUNT(i) AS InvoiceCount
ORDER BY InvoiceCount DESC;
```

### Expected Output

| Vendor | InvoiceCount |
|---------|--------------|
| ABC Technologies | 15 |
| Orion Systems | 12 |

### Why this query?

Shows vendor activity and validates Vendor → Invoice relationships.

### Concepts Demonstrated

- COUNT()
- Aggregation
- Relationship traversal

---

## Query 7 — Department Spending

### Business Question

Which departments spend the most money?

### Cypher

```cypher
MATCH (t:Transaction)-[:FOR_DEPARTMENT]->(d:Department)
MATCH (t)-[:HAS_AMOUNT]->(a:Amount)
RETURN
    d.name AS Department,
    SUM(toFloat(a.value)) AS TotalSpend
ORDER BY TotalSpend DESC;
```

### Expected Output

| Department | TotalSpend |
|------------|------------|
| IT | 2450000 |
| Operations | 1840000 |

### Why this query?

Identifies departments with the highest expenditures and validates financial relationships.

### Concepts Demonstrated

- SUM()
- Aggregation
- Multi-hop traversal

---

## Query 8 — Vendors Serving Multiple Departments

### Business Question

Which vendors provide services to multiple departments?

### Cypher

```cypher
MATCH (v:Vendor)<-[:PAID_TO]-(t:Transaction)-[:FOR_DEPARTMENT]->(d:Department)
RETURN
    v.name AS Vendor,
    COUNT(DISTINCT d) AS DepartmentsServed,
    collect(DISTINCT d.name) AS Departments
ORDER BY DepartmentsServed DESC;
```

### Expected Output

| Vendor | DepartmentsServed | Departments |
|---------|-------------------|-------------|
| ABC Technologies | 4 | IT, HR, Finance, Operations |

### Why this query?

Useful for identifying vendor concentration risk.

### Concepts Demonstrated

- DISTINCT
- COUNT()
- collect()

---

## Query 9 — Services Provided by Vendors

### Business Question

Which vendors provide which services?

### Cypher

```cypher
MATCH (s:Service)-[:PROVIDED_BY]->(v:Vendor)
RETURN
    v.name AS Vendor,
    collect(DISTINCT s.name) AS Services
ORDER BY Vendor;
```

### Expected Output

| Vendor | Services |
|---------|----------|
| ABC Technologies | Cloud Hosting, Backup |

### Why this query?

Validates service extraction and vendor-service relationships.

### Concepts Demonstrated

- collect()
- DISTINCT

---

## Query 10 — Vendor Agreements

### Business Question

Which agreements have been finalized with vendors?

### Cypher

```cypher
MATCH (a:Agreement)-[:FINALIZED_AGREEMENT_WITH]->(v:Vendor)
RETURN
    a.name AS Agreement,
    v.name AS Vendor
ORDER BY Vendor;
```

### Expected Output

| Agreement | Vendor |
|-----------|--------|
| Cloud Infrastructure Agreement | ABC Technologies |

### Why this query?

Verifies contractual relationships between organizations and vendors.

### Concepts Demonstrated

- Relationship traversal
- Business entity validation

---

# End of Part 2

# Section 4 — Projects & Risk Analysis

---

## Query 11 — Projects with Associated Risks

### Business Question

Which projects have identified risks?

### Cypher

```cypher
MATCH (p:Project)
OPTIONAL MATCH (p)-[:HAS_RISK]->(r:Risk)
RETURN
    coalesce(p.name, p.title, "Unnamed Project") AS Project,
    collect(DISTINCT coalesce(r.name, r.title)) AS Risks
ORDER BY Project;
```

### Expected Output

| Project | Risks |
|---------|-------|
| ERP Migration | Budget Overrun, Vendor Delay |
| Cloud Migration | Security Risk |

### Why this query?

Verifies that project-risk relationships were extracted correctly.

### Concepts Demonstrated

- OPTIONAL MATCH
- collect()
- coalesce()

---

## Query 12 — People Responsible for Projects

### Business Question

Who is responsible for each project?

### Cypher

```cypher
MATCH (p:Project)<-[:RESPONSIBLE_FOR]-(person:Person)
RETURN
    coalesce(p.name,p.title) AS Project,
    collect(DISTINCT person.name) AS ResponsiblePeople
ORDER BY Project;
```

### Expected Output

| Project | ResponsiblePeople |
|----------|-------------------|
| ERP Upgrade | Rahul Sharma |
| CRM Migration | Anita Mehta |

### Why this query?

Validates project ownership and responsibility assignments.

### Concepts Demonstrated

- Traversal
- collect()
- DISTINCT

---

# Section 5 — Graph Analytics

---

## Query 13 — Shortest Path Between Two Employees

### Business Question

What is the shortest connection between two employees?

### Cypher

Replace the names below with employees that exist in your graph.

```cypher
MATCH
(a:Person {name:"Rahul Sharma"}),
(b:Person {name:"Anita Mehta"})
MATCH path = shortestPath((a)-[*]-(b))
RETURN path;
```

### Expected Output

A visual graph path showing the relationship chain.

### Why this query?

Demonstrates one of the major strengths of graph databases.

### Concepts Demonstrated

- shortestPath()
- Variable-length paths

---

## Query 14 — Most Connected Nodes

### Business Question

Which entities have the largest number of relationships?

### Cypher

```cypher
MATCH (n)
RETURN
    labels(n) AS Labels,
    coalesce(n.name,n.title,"Unknown") AS Node,
    size((n)--()) AS Degree
ORDER BY Degree DESC
LIMIT 20;
```

### Expected Output

| Labels | Node | Degree |
|---------|------|--------|
| Person | Rahul Sharma | 42 |
| Vendor | ABC Technologies | 35 |

### Why this query?

Highly connected nodes often represent influential entities.

This query also prepares the graph for Week 5 centrality analysis.

### Concepts Demonstrated

- Degree calculation
- LIMIT
- ORDER BY

---

## Query 15 — Isolated Nodes

### Business Question

Which nodes have no relationships?

### Cypher

```cypher
MATCH (n)
WHERE NOT (n)--()
RETURN
    labels(n) AS Labels,
    coalesce(n.name,n.title,"Unknown") AS Node
ORDER BY Labels;
```

### Expected Output

Nodes that have no incoming or outgoing relationships.

### Why this query?

Excellent graph quality check.

Disconnected nodes usually indicate

- failed extraction
- failed entity resolution
- incorrect loading

### Concepts Demonstrated

- Graph validation
- Pattern filtering

---

# Summary

This query library demonstrates the following Cypher concepts:

- MATCH
- OPTIONAL MATCH
- WHERE
- ORDER BY
- LIMIT
- COUNT()
- SUM()
- DISTINCT
- collect()
- shortestPath()
- Multi-hop traversal
- Aggregation
- Graph validation

---

# Future Improvements

The current graph was generated directly from LLM extraction.

As a result, several semantically equivalent relationship types exist.

Examples include:

- WORKS_FOR
- WORKS_AT
- EMPLOYEE_OF
- IS_EMPLOYEE_OF

and

- PAID_TO
- PAID_VENDOR
- PAYABLE_TO_VENDOR

A future enhancement would introduce a **relationship normalization layer** that maps these equivalent edge types into a canonical ontology before loading the graph into Neo4j.

This would simplify querying, improve graph consistency, and increase Text-to-Cypher accuracy.

---

# Conclusion

This handwritten query library serves as:

- a validation suite for the knowledge graph
- a regression test after future graph updates
- a benchmark for the upcoming Text-to-Cypher agent
- a collection of reusable business intelligence queries

It forms the foundation for the remaining tasks in Week 4 and will be used to evaluate the correctness of automatically generated Cypher queries.