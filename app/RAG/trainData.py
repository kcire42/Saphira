import os 
import chromadb
import sys 
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from app.LLM_Integration.config import CHROMA_API_URL, CHROMA_COLLECTION_NAME, REQUEST_TIMEOUT_SECONDS, OLLAMA_HOST, CHROMA_PORT, CHROMA_HOST


# =========================
# GENERAL CONFIGURATION
# =========================

# Path where the PDF documents to be indexed are located
DOCS_PATH = './KnowledgeBase/'

# Embedding model to use (Sentence Transformers)
# all-MiniLM-L6-v2 is lightweight, fast, and widely used for RAG
EMBEDDING_MODEL_NAME = '/app/model_cache'

try:
    import fitz  # PyMuPDF is imported as fitz
    print(f"✅ Debug: PyMuPDF (fitz) version {fitz.version} encontrada.")
except ImportError:
    print("❌ Debug: fitz (PyMuPDF) NO encontrada en el path de Python.")
    print("Path actual:", sys.path)

from langchain_community.document_loaders import DirectoryLoader, PyMuPDFLoader, PyPDFLoader
# =========================
# Main
# =========================

def trainRagData():
    '''
    Load PDF documents from a directory,
    divide them into chunks,
    generate embeddings,
    and index them in a Chroma vector database.
    '''

    # ---- DOCUMENT UPLOAD ----
    print("Loading documents from:", DOCS_PATH)
    abs_path = os.path.abspath(DOCS_PATH)
    print(f"→ Buscando archivos en: {abs_path}")

    if not os.path.exists(abs_path):
        print(f"❌ ERROR: La ruta no existe en el contenedor: {abs_path}")
        return

    # DirectoryLoader scans the directory and subdirectories
    # and loads only PDF files using PyPDFLoader
    loader = DirectoryLoader(
        abs_path,
        glob="*.pdf",
        loader_cls=PyMuPDFLoader # PyMuPDF is excellent for 300+ pages
    )

    # Load documents into memory
    documents = loader.load()

    # Validation: if there are no documents, the process is terminated.
    if not documents:
        print("No documents found to index.")
        return
    for doc in documents:
        # Remove excessive white space that breaks tables
        doc.page_content = " ".join(doc.page_content.split())
    print(f"Loaded {len(documents)} documents.")

    # ---- DIVISION OF TEXT INTO CHUNKS ----
    # The text is divided so that the embeddings have manageable context.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,        # Maximum size of each fragment
        chunk_overlap=120,      # Text shared between fragments
        separators=["\n\n", "\n", " ", "", "."]  # Separation order
    )

    # Generate fragments from the original documents
    chunks = text_splitter.split_documents(documents)
    print(f"Split documents into {len(chunks)} chunks.")

    # ---- CREATING EMBEDDINGS ----
    print("Creating embeddings using model:", EMBEDDING_MODEL_NAME)

    try:
        # Initialize the embeddings model
        embedding_model = SentenceTransformerEmbeddings(
            model_name=EMBEDDING_MODEL_NAME
        )
    except Exception as e:
        print("Error creating embedding model:", e)
        return
    
    print("Embeddings created successfully.")

    # ---- CONNECTION TO CHROMA ----
    print("Connecting to Chroma vector store at:", CHROMA_API_URL)

    from chromadb.utils import embedding_functions
    from chromadb import Settings

    try:
        # HTTP client to connect to Chroma (external server)
        chroma_client = chromadb.HttpClient(
            host=CHROMA_HOST,
            port=CHROMA_PORT
        )
        print(f"✅ Conexión exitosa a Chroma en: http://{CHROMA_HOST}:{CHROMA_PORT}")
        # Attempt to delete the existing collection
        # (useful for reindexing from scratch)
        # try:
        #     chroma_client.delete_collection(
        #         name=CHROMA_COLLECTION_NAME
        #     )
        #     print(f"Deleted existing collection: {CHROMA_COLLECTION_NAME}")
        # except Exception:
        #     # If the collection does not exist, the error is ignored.
        #     pass

        # ---- CHROMA INDEXING ----
        vector_store = Chroma.from_documents(
            documents=chunks,                   # Text fragments
            embedding=embedding_model,          # Embeddings model
            collection_name=CHROMA_COLLECTION_NAME,
            client=chroma_client
        )

        print(f"✅ SUCCESS: Indexed {len(chunks)} chunks into Chroma.")

    except Exception as e:
        print(e)
        print("Error connecting to Chroma or indexing documents:", e)
        return


