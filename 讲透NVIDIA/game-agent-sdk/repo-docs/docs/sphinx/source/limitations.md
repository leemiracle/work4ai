# Limitations

This section outlines the current limitations of the Game Agent SDK.

## RAG Limitations

### Graph expansion is limited to the vector database

Graph adjacency expansion and cross-encoder reranking only run on hits returned by the vector database. BM25 (lexical) hits do not get adjacency expansion, even though the underlying document graph is a property of the source corpus and would in principle apply to any retrieval hit. Two practical consequences:

- In hybrid mode, chunks surfaced only by BM25 contribute no adjacents to the result set, so cross-referenced context may be missed if the originating chunk happened to match lexically but not semantically.
- In lexical-only mode, neither graph expansion nor cross-encoder reranking runs at all.

### Result distances are not normalized

The `distance` field on `ACESearchResult` carries different metrics depending on which retrieval path produced the hit:

- **Semantic (vector) hits** carry the raw FAISS squared-L2 distance (lower means more similar; bounded in [0, 4] for L2-normalized embeddings, unbounded otherwise).
- **Lexical (BM25) hits** carry the raw BM25 score (higher means more relevant; unbounded positive, depends on document length and term statistics).
- **Graph-adjacent hits reranked by the cross-encoder** carry the raw cross-encoder logits (higher means more relevant; unbounded float, typically roughly in the [-10, +10] range for `ms-marco-MiniLM` but model-dependent and not normalized).

In hybrid mode, results from all three paths land in the same list without normalization across sources.

## SLM Limitations

### NvIGI SLM backend is not yet supported

The `ACEModelLoadParam_Backend` parameter accepts only `ACEInferenceBackend_Llama`; `ACENvIGIParams` is reserved for future use.