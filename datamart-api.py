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

from pydantic import BaseModel
from typing import Optional
from datetime import date
from decimal import Decimal
import pyodbc


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
app = FastAPI(title="CECILia API", version="1.4")

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
         tags=["Shopping"], 
         summary="Consulta o fluxo sumarizado de acesso de pessoas ao shopping", 
         dependencies=[Depends(verify)])

def get_peoplecounting(
    start_date: str = Query(None, description="Data inicial no formato AAAA-MM-DD"),
    end_date: str = Query(None, description="Data final no formato AAAA-MM-DD"),
    limit: int = Query(1000, description="Máximo de registros a retornar"),
    last_date: str = Query(None, description="Data da última entrada do lote anterior (para paginação)")
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
         tags=["Shopping"], 
         summary="Consulta o fluxo sumarizado de acesso de veículos ao shopping", 
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
         tags=["Shopping"], 
         summary="Consulta acessos sumarizados ao hotspot de wi-fi",
         dependencies=[Depends(verify)])

def get_hotspotaccess(
    start_date: str = Query(None, description="Data inicial no formato AAAA-MM:Semana N"),
    end_date: str = Query(None, description="Data final no formato AAAA-MM:Semana N"),
    limit: int = Query(1000, description="Máximo de registros a retornar"),
    last_date: str = Query(None, description="Data da última entrada do lote anterior (para paginação)")
):
    filters = []

    if start_date:
        filters.append(f'db_hotspot_summary[dt_periodo] >= "{start_date}"')
    if end_date:
        filters.append(f'db_hotspot_summary[dt_periodo] <= "{end_date}"')
    if last_date:
        filters.append(f'db_hotspot_summary[dt_periodo] > "{last_date}"')

    filter_clause = f"FILTER(db_hotspot_summary, {' && '.join(filters)})" if filters else "db_hotspot_summary"

    dax_query = f"""
    EVALUATE
    TOPN({limit}, {filter_clause}, db_hotspot_summary[dt_periodo], ASC)
    """

    df = query_datamart(dax_query)
    return df.to_dict(orient="records")

#Endpoint: vendas data
@app.get("/vendas",
         tags=["Shopping"],
         summary="Consultar vendas",
         dependencies=[Depends(verify)])

def get_vendas(
    start_date: str = Query(None, description="Data inicial no formato AAAA-MM-DD"),
    end_date: str = Query(None, description="Data final no formato AAAA-MM-DD"),
    limit: int = Query(1000, description="Máximo de registros a retornar"),
    last_date: str = Query(None, description="Data da última entrada do lote anterior (para paginação)")
):
    filters = []

    if start_date:
        filters.append(f'db_vendas[dt_referencia] >= DATE({start_date.replace("-", ", ")})')
    if end_date:
        filters.append(f'db_vendas[dt_referencia] <= DATE({end_date.replace("-", ", ")})')
    if last_date:
        filters.append(f'db_vendas[dt_referencia] > DATE({last_date.replace("-", ", ")})')

    filter_clause = f"FILTER(db_vendas, {' && '.join(filters)})" if filters else "db_vendas"

    dax_query = f"""
    EVALUATE
    TOPN({limit}, {filter_clause}, db_vendas[dt_referencia], ASC)
    """

    df = query_datamart(dax_query)
    return df.to_dict(orient="records")


# Endpoint receitasienge base model
class ReceitaSiengeInput(BaseModel):
    dt_vencimento: Optional[date] = None
    cliente: Optional[str] = None
    documento: Optional[str] = None
    titulo: Optional[int] = None
    parcela: Optional[str] = None
    tc: Optional[str] = None
    unidade: Optional[str] = None
    vl_original: Optional[Decimal] = None
    dt_calculo: Optional[date] = None
    sa_atual: Optional[Decimal] = None
    acrescimo: Optional[Decimal] = None
    desconto: Optional[Decimal] = None
    vl_total: Optional[Decimal] = None

def get_sqlserver_connection():
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={os.getenv('SQL_SERVER_HOST')};"
        f"DATABASE={os.getenv('SQL_SERVER_DB')};"
        f"UID={os.getenv('SQL_SERVER_USER')};"
        f"PWD={os.getenv('SQL_SERVER_PASSWORD')};"
        f"TrustServerCertificate=yes;"
    )
    return pyodbc.connect(conn_str)

# Endpoint: receitasienge input
@app.post("/receitasienge", tags=["Bairro Harmonia"], summary="Insere dados na tabela receitasienge")
def registrar_receita(
    dados: ReceitaSiengeInput,
    creds: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):
    verify(creds)

    try:
        conn = get_sqlserver_connection()
        cursor = conn.cursor()
    
        query = """
        INSERT INTO dbo.receitasienge (
            dt_vencimento, cliente, documento, titulo, parcela, tc, unidade,
            vl_original, dt_calculo, sa_atual, dias, acrescimo, desconto, vl_total
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        valores = (
            dados.dt_vencimento,
            dados.cliente,
            dados.documento,
            dados.titulo,
            dados.parcela,
            dados.tc,
            dados.unidade,
            dados.vl_original,
            dados.dt_calculo,
            dados.sa_atual,
            dados.acrescimo,
            dados.desconto,
            dados.vl_total,
        )
        
        cursor.execute(query, valores)
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"mensagem": "Registro inserido com sucesso ✅"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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