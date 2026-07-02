from neo4j import GraphDatabase

URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "Lattice*18"


driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD),
)


def run_query(query: str, parameters: dict | None = None):
    """Execute a Cypher query and return the results."""

    with driver.session() as session:
        result = session.run(query, parameters or {})
        return [record.data() for record in result]


def close():
    driver.close()
