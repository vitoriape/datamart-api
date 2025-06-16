from msal import ConfidentialClientApplication
from fastapi import FastAPI, Query, Header, HTTPException, Depends
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import Annotated
import pandas as pd
import requests
import uvicorn
import os

# Environment variables
env_dir = os.path.dirname(os.path.abspath(__file__))
env_name = 'secret.env'
dotenv_path = os.path.join(env_dir, env_name)
load_dotenv(dotenv_path)


# Client secret settings
TOKEN = os.getenv("TOKEN")
bearer_scheme = HTTPBearer(auto_error=True)

def verify(creds: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    if creds.credentials != TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token")
    

# API settings
app = FastAPI(title="Datamart API", version="1.4")

@app.get("/openapi.yaml", include_in_schema=False)
def get_openapi():
    return FileResponse("openapi.yaml")

@app.get("/", include_in_schema=False)
def read_root():
    return {"status": "API on air"}

@app.get("/.well-known/ai-plugin.json", include_in_schema=False)
def serve_ai_plugin():
    return FileResponse(".well-known/ai-plugin.json")

# Endpoint: people couting data
@app.get("/peoplecounting", 
         tags=["Fluxos Mall"], 
         summary="Consultar fluxo de pessoas", 
         dependencies=[Depends(verify)])

def get_peoplecounting(
    start_date: str = Query(None, description="Data inicial no formato AAAA-MM-DD"),
    end_date: str = Query(None, description="Data final no formato AAAA-MM-DD")
):
    filters = []

    if start_date:
        year, month, day = map(int, start_date.split("-"))
        filters.append(f'db_peoplecouting[dt_acesso] >= DATE({year}, {month}, {day})')

    if end_date:
        year, month, day = map(int, end_date.split("-"))
        filters.append(f'db_peoplecouting[dt_acesso] <= DATE({year}, {month}, {day})')

    dax_query = (
        f"EVALUATE FILTER(db_peoplecouting, {' && '.join(filters)})"
        if filters else
        "EVALUATE db_peoplecouting"
    )

    df = query_datamart(dax_query)
    return df.to_dict(orient="records")

# Endpoint: parking data
@app.get("/parkingdata", 
         tags=["Fluxos Mall"], 
         summary="Consultar fluxo de veículos", 
         dependencies=[Depends(verify)])

def get_parkingdata(
    start_date: str = Query(None, description="Data inicial no formato AAAA-MM-DD"),
    end_date: str = Query(None, description="Data final no formato AAAA-MM-DD"),
    limit: int = Query(1000, description="Máximo de registros a retornar"),
    last_date: str = Query(None, description="Data da última entrada do lote anterior (para paginação)")
):
    filters = []

    if start_date:
        filters.append(f'db_parking_summary[dt_entrada_date] >= DATE({start_date.replace("-", ", ")})')
    if end_date:
        filters.append(f'db_parking_summary[dt_entrada_date] <= DATE({end_date.replace("-", ", ")})')
    if last_date:
        filters.append(f'db_parking_summary[dt_entrada_date] > DATE({last_date.replace("-", ", ")})')

    filter_clause = f"FILTER(db_parking_summary, {' && '.join(filters)})" if filters else "db_parking_summary"

    dax_query = f"""
    EVALUATE
    TOPN({limit}, {filter_clause}, db_parking_summary[dt_entrada_date], ASC)
    """

    df = query_datamart(dax_query)
    return df.to_dict(orient="records")

# Endpoint: hotspot data
@app.get("/hotspotaccess", 
         tags=["Fluxos Mall"], 
         summary="Consultar acessos ao Hotspot de Internet",
         dependencies=[Depends(verify)])

def get_hotspotaccess():
    dax_query = "EVALUATE db_hotspot_summary"
    df = query_datamart(dax_query)
    return df.to_dict(orient="records")


# Datamart queries
def query_datamart(dax_query: str):
    client_id = os.getenv('SQL_CLIENT_ID')
    client_secret = os.getenv('SQL_CLIENT_SECRET')
    tenant_id = os.getenv('SQL_TENANT_ID')
    workspace_id = os.getenv('WORKSPACE_ID')
    dataset_id = os.getenv('DATASET_ID')

    authority = f"https://login.microsoftonline.com/{tenant_id}"
    scope = ["https://analysis.windows.net/powerbi/api/.default"]

    app_auth = ConfidentialClientApplication(
        client_id,
        authority=authority,
        client_credential=client_secret,
    )

    token_response = app_auth.acquire_token_for_client(scopes=scope)
    access_token = token_response.get('access_token')

    if not access_token:
        raise Exception(f"Could not obtain token: {token_response}")

    url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/datasets/{dataset_id}/executeQueries"

    query = {
        "queries": [{"query": dax_query}],
        "serializerSettings": {"includeNulls": True}
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, json=query)

    if response.status_code != 200:
        raise Exception(f"Query error: {response.status_code} {response.text}")

    result = response.json()

    try:
        tables = result['results'][0]['tables'][0]
        if 'columns' in tables and 'rows' in tables:
            columns = [col['name'] for col in tables['columns']]
            rows = tables['rows']
            return pd.DataFrame(rows, columns=columns)
        elif 'rows' in tables:
            return pd.DataFrame(tables['rows'])
        else:
            raise Exception(f"Data not located: {result}")
    except Exception as e:
        raise Exception(f"Error parsing response: {result}") from e

if __name__ == "__main__":
    uvicorn.run("datamart-api:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), reload=True)