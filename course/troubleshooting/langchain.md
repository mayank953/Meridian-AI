# LangChain / Gemini / agents

**`index_id is required for api_version='v1'`**
Cause: `VECTOR_SEARCH_INDEX_ID` / `VECTOR_SEARCH_INDEX_ENDPOINT_ID` are empty. Fix: copy them from the GitHub Actions log (*Provision Vector Search* step) into `.env`.

**`404 models/<name> is not found` / "no longer available to new users"**
Cause: the model was retired or is not available to your key. Fix: set `VERTEX_LLM_MODEL_NAME` to a current model from https://ai.google.dev/gemini-api/docs/models (this project uses `gemini-3.8-flash`). `gemini-2.5-pro` is closed to new users and retires 16 Oct 2026.

**`API key not valid` / 400 from Gemini**
Fix: create a key at https://aistudio.google.com/apikey; no spaces or newlines in `.env`.

**`ImportError: cannot import name 'create_agent'`**
Cause: old `langchain` installed. Fix: `pip install -r requirements.txt` (needs `langchain==1.2.11`).

**`ModuleNotFoundError: langchain_classic`**
Fix: `pip install langchain-classic==1.0.2`. `create_retrieval_chain` moved there in LangChain 1.x.

**Agent answers instantly without using tools / loops forever**
Cause: tool docstrings unclear, or model temperature. Fix: improve the tool docstring; try `LLM_TEMPERATURE=1.0` (Gemini 3 default) or a different model.

**Tool results contain `LLM_ERROR`**
Cause: the tool's own model call failed (key, quota, model name). The agent output will say "Manual review required". Fix as above.

**`validate_fx_hedge` always uses the LLM fallback**
Cause: the Frankfurter API (`api.frankfurter.dev`) is unreachable from your network. The tool is built to fall back.

**Audit answers differ each run**
Normal: LLM output varies. The key words (`RED ALERT`, `FX ALERT`, `HOLD FOR TREASURY AUDIT`) should be stable.
