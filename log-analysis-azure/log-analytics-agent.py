import os
import json
import logging
import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.monitor.query import LogsQueryClient
from openai import AzureOpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Azure OpenAI client
openai_client = AzureOpenAI(
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    api_version=os.environ["AZURE_OPENAI_API_VERSION"],
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"]
)

# Initialize Azure Log Analytics client
credential = DefaultAzureCredential()
logs_client = LogsQueryClient(credential)

def translate_to_kql(user_query):
    """Translate natural language query to KQL using Azure OpenAI."""
    
    system_prompt = """
    You are an expert in Kusto Query Language (KQL) for Azure Log Analytics. 
    Your task is to convert natural language questions into valid KQL queries.
    Only return the KQL query without any explanations or markdown formatting.
    Focus on common Azure tables like:
    - AzureActivity
    - SecurityEvent
    - AzureDiagnostics
    - AppServiceHTTPLogs
    - ContainerLog
    - AppTraces
    - AppExceptions
    """
    
    try:
        response = openai_client.chat.completions.create(
            model=os.environ["AZURE_OPENAI_DEPLOYMENT"],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Convert this to a KQL query: {user_query}"}
            ],
            temperature=0.1,
            max_tokens=800
        )
        
        kql_query = response.choices[0].message.content.strip()
        logger.info(f"Translated query: {kql_query}")
        return kql_query
    
    except Exception as e:
        logger.error(f"Error translating to KQL: {str(e)}")
        raise

def execute_kql_query(workspace_id, kql_query):
    """Execute KQL query against Azure Log Analytics workspace."""
    
    try:
        response = logs_client.query_workspace(
            workspace_id=workspace_id,
            query=kql_query,
            timespan=None  # Use default timespan
        )
        
        # Convert response to a list of dictionaries
        results = []
        if response.tables:
            for row in response.tables[0].rows:
                result = {}
                for i, column in enumerate(response.tables[0].columns):
                    result[column.name] = row[i]
                results.append(result)
        
        return results
    
    except Exception as e:
        logger.error(f"Error executing KQL query: {str(e)}")
        raise

def main(req: func.HttpRequest) -> func.HttpResponse:
    """Azure Function HTTP trigger to handle log analysis requests."""
    
    try:
        req_body = req.get_json()
        user_query = req_body.get('query')
        workspace_id = req_body.get('workspace_id')
        
        if not user_query or not workspace_id:
            return func.HttpResponse(
                json.dumps({"error": "Missing required parameters: 'query' and 'workspace_id'"}),
                mimetype="application/json",
                status_code=400
            )
        
        # Step 1: Translate natural language to KQL
        kql_query = translate_to_kql(user_query)
        
        # Step 2: Execute the KQL query
        results = execute_kql_query(workspace_id, kql_query)
        
        # Step 3: Return results
        return func.HttpResponse(
            json.dumps({
                "kql_query": kql_query,
                "results": results
            }),
            mimetype="application/json"
        )
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )