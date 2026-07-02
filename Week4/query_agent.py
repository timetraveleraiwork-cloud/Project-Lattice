from app.text_to_cypher import generate_cypher
from app.neo4j import run_query
from app.cypher_safety import validate_query

question = "Who approved the most transactions?"

cypher = generate_cypher(question)

print("\nGenerated Cypher:\n")
print(cypher)

# NEW
validate_query(cypher)

results = run_query(cypher)

print("\nResults:\n")
print(results)
