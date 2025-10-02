# function_app.py
import azure.functions as func
import logging
import json

app = func.FunctionApp()

@app.route(route="query", auth_level=func.AuthLevel.FUNCTION)
def query_rag(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Processing RAG query request')
    
    try:
        req_body = req.get_json()
        question = req_body.get('question')
        
        if not question:
            return func.HttpResponse(
                "Please provide a 'question' in request body",
                status_code=400
            )
        
        # Query your RAG system
        result = query_azure_rag(question)
        
        return func.HttpResponse(
            json.dumps(result),
            mimetype="application/json",
            status_code=200
        )
        
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return func.HttpResponse(
            f"Error processing query: {str(e)}",
            status_code=500
        )