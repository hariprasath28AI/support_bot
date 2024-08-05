# ------------------------v3 -------------------------------------------



from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import StorageContext, ServiceContext, set_global_service_context, load_index_from_storage
from llama_index.core.prompts import PromptTemplate
from llama_index.vector_stores.faiss import FaissVectorStore
import faiss
import os


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup Jinja2 templates
templates = Jinja2Templates(directory="templates")

origins = [
    "http://127.0.0.1:5500",
    "http://localhost",
    "http://localhost:5500",
    "http://192.168.0.25:8080"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

d = 384
faiss_index = faiss.IndexFlatL2(d)

os.environ["GROQ_API_KEY"] = "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"
embeddings = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
llm = Groq(model="llama3-8b-8192", api_key=os.environ.get("GROQ_API_KEY"))

service_context = ServiceContext.from_defaults(
    embed_model=embeddings,
    llm=llm,
    chunk_size=1000,
    chunk_overlap=200
)
set_global_service_context(service_context)

persist_dir = "./stored_index"

# Check if the index already exists
if not os.path.exists(persist_dir):

    documents = SimpleDirectoryReader('data').load_data()
    
    faiss_vector_store = FaissVectorStore(faiss_index=faiss_index)
    storage_context = StorageContext.from_defaults(vector_store=faiss_vector_store)
    
    # Create the index
    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context
    )
    
    index.storage_context.persist(persist_dir=persist_dir)
    print("Index created and stored.")
else:
    # Load the existing index
    faiss_vector_store = FaissVectorStore.from_persist_dir(persist_dir)
    storage_context = StorageContext.from_defaults(vector_store=faiss_vector_store, persist_dir=persist_dir)
    index = load_index_from_storage(storage_context)
    print("Loaded existing index.")


query_engine = index.as_query_engine(similarity_top_k=3)
query_engine.update_prompts({
    'response_synthesizer:text_qa_template': PromptTemplate(template='''
You are a customer support AI for a banking company, Provide concise answers to user queries about banking services. 
Only respond to relevant questions. Keep responses brief and to the point. If a query is outside your scope or irrelevant, 
politely inform the user you cannot assist with that topic. Prioritize accuracy and clarity in your responses.

Always try to Provide Answer in list of steps

Proactively ASK follow up questions regarding Banking FAQs at the end of the response

Relevant Information:
{context_str}

Customer Query:
{query_str}

Your response:
''')
})

class QueryRequest(BaseModel):
    query: str



@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.options("/chat")
async def options_chat():
    return {"message": "OK"}

@app.post("/chat")
async def chat(query_request: QueryRequest):
    try:
        response = query_engine.query(query_request.query).response
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, port=8080, host='0.0.0.0')

