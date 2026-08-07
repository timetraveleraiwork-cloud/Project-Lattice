"Project Management Office" and "Operations (Project Management Office)" were intentionally left unmerged because the similarity is lexical rather than semantically verified. These require human review or improved extraction.

## Week 5 Findings - 1

Graph traversal answered structural relationship questions that vector retrieval alone could not.

Semantic retrieval answered fuzzy wording questions that pure Cypher could not.

The grounded prompting strategy refused questions outside the corpus instead of hallucinating answers.

## Week 5 Findings - 2

Hybrid retrieval combines semantic search with graph expansion to answer relationship-centric questions that document retrieval alone may miss.

Semantic retrieval improves robustness by finding relevant documents even when the user's wording differs from the corpus.

Grounded prompting with citation validation and an explicit refusal path reduces hallucinations by ensuring answers are supported by the retrieved context.

## Week 6 Findings - 1
During Week 6 graph analytics, I discovered a residual entity-resolution issue where one document referred to "Priya" while others used "Priya Nair". Graph algorithms (PageRank) exposed this because both appeared as separate nodes. This was traced back to incomplete canonicalization and is a candidate for an additional entity-resolution rule.