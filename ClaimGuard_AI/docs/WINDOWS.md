# Windows

The Python MCP server and Streamlit dashboard run natively on Windows.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python mcp/server.py
```

Second terminal:

```powershell
.venv\Scripts\Activate.ps1
streamlit run dashboard/app.py
```

MCP: `http://127.0.0.1:8001/mcp`

The core project does not depend on a local TrueForge sandbox. Sandbox execution is optional. This keeps the business demo usable even if a particular Windows TrueForge build cannot provide its local sandbox.
