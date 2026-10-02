# GitHub Actions (deploy workflow)

**Auth step fails: "invalid JSON" / "credentials_json"**
Cause: `GCP_CREDENTIALS_JSON` must be the **entire** contents of the key file, including braces. Fix: re-copy the file; no extra quotes.

**`GOOGLE_API_KEY` secret empty → app fails at runtime**
Fix: add it under Settings → Secrets and variables → Actions. The workflow strips whitespace and prints only the key length.

**Image build/push fails for `gcr.io/...` (permission denied / repository does not exist)**
Cause: Google Container Registry is shut down; `gcr.io` addresses only work when backed by an Artifact Registry repository, which can need creating first. **Not yet verified by a real deploy in this project.** Fix options: (a) create the `gcr.io` repository in Artifact Registry (Console → Artifact Registry → Create repository → format Docker, multi-region `us`, name `gcr.io`), or (b) change `IMAGE_NAME` in `deploy.yml` to `us-central1-docker.pkg.dev/<project>/<repo>/meridian-ai-cloud-run` and create that repository with `gcloud artifacts repositories create`.

**"Index creation in progress" loop times out**
Cause: first-time index creation is slow. Fix: re-run the workflow; it skips what already exists.

**Run takes 40+ minutes**
Normal on the first run (vector index + deployment). Later runs are minutes.

**Cloud Run deploy OK but app errors on every call**
Check the printed `INDEX_ID`/`ENDPOINT_ID`; read Cloud Run logs; check `VERTEX_LLM_MODEL_NAME` is a current model.

**Pushes to `main` redeploy everything**
By design (`on: push: main`). While teaching, work on a branch; use *Run workflow* manually.

## Security notes
- A stored JSON key is a long-lived secret; the safer modern option is **Workload Identity Federation** (no key stored).
- `Editor` + `IAM Admin` is broad; fine for a classroom, not for production.
- `--allow-unauthenticated` makes the app public; `--max-instances 3` limits the damage if someone abuses it.
