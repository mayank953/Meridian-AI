# Vertex AI Vector Search

**Index creation/deployment takes 30–45 minutes the first time.** Normal. Start it hours before class.

**Searches return nothing right after uploading**
Cause: streaming updates take a short time to become searchable. Fix: wait ~30–60 seconds and ask again.

**Dimension mismatch error when upserting**
Cause: the embedding model does not output 768 dimensions (the index is created with 768). Fix: use `text-embedding-005` (default). Changing the model means creating a new index.

**`deployed index not found` / endpoint errors**
Cause: the index is not deployed to the endpoint yet. Check: Console → Vertex AI → Vector Search → Index endpoints.

**Same document uploaded twice → duplicate answers**
Expected: every upload adds chunks again. For class, upload each PDF once.

## Teardown (stops the hourly charge)
```bash
REGION=us-central1
# 1. find ids
gcloud ai index-endpoints list --region=$REGION
gcloud ai indexes list --region=$REGION
# 2. undeploy the index from the endpoint (this is what stops the billing)
gcloud ai index-endpoints undeploy-index <ENDPOINT_ID> \
  --deployed-index-id=deployed_financial_docs --region=$REGION
# 3. delete endpoint and index
gcloud ai index-endpoints delete <ENDPOINT_ID> --region=$REGION
gcloud ai indexes delete <INDEX_ID> --region=$REGION
```
Also delete the Cloud Run service and the bucket if you are done with the project.

## Alternatives
Vector Search 2.0 (collection-based, no separate endpoint step, hybrid search), Postgres + pgvector, Pinecone, Chroma, Vertex AI RAG Engine.
