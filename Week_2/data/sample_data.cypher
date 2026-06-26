// =====================================================
// Project Lattice - Sample Company Graph
// Week 2 Day 4
// =====================================================

// ---------- Departments ----------
CREATE
(fin:Department {name:"Finance"}),
(proc:Department {name:"Procurement"}),
(it:Department {name:"IT"}),
(hr:Department {name:"HR"}),
(ops:Department {name:"Operations"});

// ---------- Employees ----------
CREATE
(rahul:Person {name:"Rahul Mehta", role:"Finance Manager"}),
(priya:Person {name:"Priya Sharma", role:"Procurement Lead"}),
(amit:Person {name:"Amit Verma", role:"Senior IT Engineer"}),
(neha:Person {name:"Neha Kapoor", role:"HR Manager"}),
(arjun:Person {name:"Arjun Singh", role:"Operations Manager"}),
(vikram:Person {name:"Vikram Rao", role:"Financial Analyst"}),
(sneha:Person {name:"Sneha Gupta", role:"Security Engineer"}),
(rohit:Person {name:"Rohit Mehta", role:"Business Owner"});

// ---------- Vendors ----------
CREATE
(technova:Vendor {name:"TechNova Solutions"}),
(greenleaf:Vendor {name:"GreenLeaf Supplies"}),
(alpha:Vendor {name:"Alpha Logistics"}),
(securesys:Vendor {name:"SecureSys Ltd"});

// ---------- Projects ----------
CREATE
(phoenix:Project {name:"Project Phoenix"}),
(orion:Project {name:"Project Orion"});

// ---------- Team ----------
CREATE
(cyber:Team {name:"Cyber Security Team"});

// ---------- Invoices ----------
CREATE
(inv101:Invoice {id:"INV-101", amount:250000}),
(inv102:Invoice {id:"INV-102", amount:180000}),
(inv103:Invoice {id:"INV-103", amount:90000});

// ---------- Employment ----------
CREATE
(rahul)-[:WORKS_IN]->(fin),
(vikram)-[:WORKS_IN]->(fin),
(priya)-[:WORKS_IN]->(proc),
(amit)-[:WORKS_IN]->(it),
(sneha)-[:WORKS_IN]->(it),
(neha)-[:WORKS_IN]->(hr),
(arjun)-[:WORKS_IN]->(ops);

// ---------- Project Assignments ----------
CREATE
(rahul)-[:WORKS_ON]->(phoenix),
(amit)-[:WORKS_ON]->(phoenix),
(arjun)-[:WORKS_ON]->(phoenix),

(priya)-[:WORKS_ON]->(orion),
(neha)-[:WORKS_ON]->(orion);

// ---------- Team Membership ----------
CREATE
(amit)-[:MEMBER_OF]->(cyber),
(sneha)-[:MEMBER_OF]->(cyber);

// ---------- Invoice Approval ----------
CREATE
(rahul)-[:APPROVES]->(inv101),
(vikram)-[:APPROVES]->(inv102),
(priya)-[:APPROVES]->(inv103);

// ---------- Vendor Payments ----------
CREATE
(inv101)-[:PAID_TO]->(technova),
(inv102)-[:PAID_TO]->(greenleaf),
(inv103)-[:PAID_TO]->(alpha);

// ---------- Vendor Services ----------
CREATE
(technova)-[:SUPPLIES]->(fin),
(technova)-[:SUPPLIES]->(it),
(technova)-[:SUPPLIES]->(hr),
(technova)-[:SUPPLIES]->(ops),

(greenleaf)-[:SUPPLIES]->(proc),
(alpha)-[:SUPPLIES]->(ops),
(securesys)-[:SUPPLIES]->(it);

// ---------- Hidden Relationships ----------

// Pattern 1 : Conflict of Interest
CREATE
(rahul)-[:RELATED_TO {relation:"Brother"}]->(rohit),
(rohit)-[:OWNS]->(technova);

// Pattern 2 : Hidden Chain
CREATE
(amit)-[:MEMBER_OF]->(cyber);

// Pattern 3 : Key Person Dependency
// Rahul is the only bridge between Finance and Operations
// through Project Phoenix.

// Pattern 4 : Vendor Concentration
// TechNova supplies multiple departments.