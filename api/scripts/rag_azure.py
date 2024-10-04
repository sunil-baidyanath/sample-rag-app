'''
1. Create azure cognitive search index
2. Process PDF docs
3. Generate vector embeddings
4. Ingest data
5. Perform RAG
6. Customize system prompt for better result

'''

'''
Dependencies

pip install azure-search-documents
pip install azure-ai-formrecognizer
pip install pypdf

'''
import io
import os
import openai
from openai import AzureOpenAI
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient
from azure.search.documents.indexes.models import HnswParameters, SemanticPrioritizedFields, SearchIndex, SearchField, SearchFieldDataType, SemanticField, SemanticConfiguration, SemanticSearch, VectorSearch, VectorSearchAlgorithmConfiguration

from pypdf import PdfReader, PdfWriter

SEARCH_SERVICE = "your-azure-search-resource"
SEARCH_INDEX = "your-search-index"
SEARCH_KEY = "your-secret-azure-search-key"
SEARCH_CREDS = AzureKeyCredential(SEARCH_KEY)

service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
index_name = os.environ["AZURE_SEARCH_INDEX_NAME"]
key = os.environ["AZURE_SEARCH_API_KEY"]

index_name = "hotels"
# Get the service endpoint and API key from the environment
endpoint = os.environ["SEARCH_ENDPOINT"]
key = os.environ["SEARCH_API_KEY"]

# Create a client
credential = AzureKeyCredential(key)
client = SearchClient(endpoint=endpoint,
                      index_name=index_name,
                      credential=credential)

index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
# SEARCH_CLIENT = SearchIndexerClient(endpoint=f"https://{SEARCH_SERVICE}.search.windows.net/", credential=SEARCH_CREDS)


# 1. Create search index
def create_index():
    # client = SearchIndexClient(endpoint=f"https://{SEARCH_SERVICE}.search.windows.net/", index=SEARCH_INDEX, credential=SEARCH_CREDS)
    # Define the index
    index_definition = SearchIndex(
        name=SEARCH_INDEX,
        fields=[
            SearchField(name="id", type=SearchFieldDataType.String, key=True),
            SearchField(name="content", type=SearchFieldDataType.String, filterable=True, sortable=True),
            SearchField(name="sourcefile", type=SearchFieldDataType.String, filterable=True, facetable=True),
            SearchField(
                name="embedding",
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                hidden=False,
                searchable=True,
                filterable=False,
                sortable=False,
                facetable=False,
                vector_search_dimensions=1536,
                vector_search_configuration="default",
            )
        ],
        semantic_settings=SemanticSearch(
            configurations=[
                SemanticConfiguration(
                    name='default',
                    prioritized_fields=SemanticPrioritizedFields(
                        title_field=None, content_fields=[SemanticField(field_name='content')]
                    )
                )
            ]
        ),
        vector_search=VectorSearch(
            algorithm_configurations=[
                VectorSearchAlgorithmConfiguration(
                    name="default",
                    kind="hnsw",
                    hnsw_parameters=HnswParameters(metric="cosine")
                )
            ]
        )
    )
    
    # Create the index
    index_client.create_index(index=index_definition)


# 2. Process PDFs    
def split_pdf_to_pages(pdf_path):
    """
    Splits a PDF file into individual pages and returns a list of byte streams, 
    each representing a single page.
    """
    pages = []
    with open(pdf_path, 'rb') as file:
        reader = PdfReader(file)

        for i in range(reader.getNumPages()):
            writer = PdfWriter()
            writer.addPage(reader.getPage(i))

            page_stream = io.BytesIO()
            writer.write(page_stream)
            page_stream.seek(0)
            pages.append(page_stream)

    return pages



def get_document_text_from_content(blob_content):
    offset = 0
    page_map = []

    form_recognizer_client = DocumentAnalysisClient(
        endpoint=f"https://{FORM_RECOGNIZER_SERVICE}.cognitiveservices.azure.com/", 
        credential=FORM_RECOGNIZER_CREDS, 
        headers={"x-ms-useragent": "azure-search-sample/1.0.0"}
    )

    poller = form_recognizer_client.begin_analyze_document("prebuilt-layout", document=blob_content)
    form_recognizer_results = poller.result()

    for page_num, page in enumerate(form_recognizer_results.pages):
        # Extract text for each page
        page_text = page.content
        page_map.append((page_num, offset, page_text))
        offset += len(page_text)

    return page_map

# 3. Split text into indexable sized chunks
def split_text(page_map, max_section_length):
    """
    Splits the text from page_map into sections of a specified maximum length.

    :param page_map: List of tuples containing page text.
    :param max_section_length: Maximum length of each text section.
    :return: Generator yielding text sections.
    """
    all_text = "".join(p[2] for p in page_map)  # Concatenate all text
    start = 0
    length = len(all_text)

    while start < length:
        end = min(start + max_section_length, length)
        section_text = all_text[start:end]
        yield section_text
        start = end



# 4. Create search index section    
def create_sections(filename, page_map):
    for i, (content, pagenum) in enumerate(split_text(page_map, filename)):
        section = {
            "id": f"{filename}-page-{i}",
            "content": content,
            "sourcefile": filename
        }
        section["embedding"] = compute_embedding(content)
        yield section

# 5. Generate embeddings
        
# Configurations
OPENAI_SERVICE = "your-azure-openai-resource"
OPENAI_DEPLOYMENT = "embedding"
OPENAI_KEY = "your-secret-openai-key"

# OpenAI setup
openai.api_type = "azure"
openai.api_key = OPENAI_KEY
openai.api_base = f"https://{OPENAI_SERVICE}.openai.azure.com"
openai.api_version = "2022-12-01"

client = AzureOpenAI(
      api_key = os.getenv("AZURE_OPENAI_API_KEY"),  
      api_version = "2023-05-15",
      azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT") 
    )

def compute_embedding(text):
    
    response = client.embeddings.create(
        input = text,
        model= "text-embedding-ada-002"
    )
    # return openai.Embedding.create(engine=OPENAI_DEPLOYMENT, input=text)["data"][0]["embedding"]

# 6. Ingest data into search index
def index_sections(filename, sections):
    """
    Indexes sections from a file into a search index.

    :param filename: The name of the file being indexed.
    :param sections: The sections of text to index.
    """
    search_client = SearchClient(endpoint=f"https://{SEARCH_SERVICE}.search.windows.net/",
                                 index_name=SEARCH_INDEX,
                                 credential=SEARCH_CREDS)

    batch = []
    for i, section in enumerate(sections, 1):
        batch.append(section)
        if i % 1000 == 0:
            search_client.upload_documents(documents=batch)
            batch = []

    if batch:
        search_client.upload_documents(documents=batch)


# 7. Use RAG to query search index endpoint

# from azure.core.credentials import AzureKeyCredential
# from azure.search.documents import SearchClient

def search_index(query, endpoint, index_name, api_key):
    """
    Searches the indexed data in Azure Search.

    :param query: The search query string.
    :param endpoint: Azure Search service endpoint URL.
    :param index_name: Name of the Azure Search index.
    :param api_key: Azure Search API key.
    :return: Search results.
    """
    credential = AzureKeyCredential(api_key)
    search_client = SearchClient(endpoint=endpoint, index_name=index_name, credential=credential)

    results = search_client.search(query)
    return [result for result in results]


# 8. Use GPT to interface with RAG


def enrich_with_gpt(result, openai_api_key):
    """
    Enriches the search result with additional information generated by OpenAI GPT-4.

    :param result: The search result item to enrich.
    :param openai_api_key: OpenAI API key.
    :return: Enriched information.
    """
    openai.api_key = openai_api_key

    # Construct a prompt based on the result for GPT-4
    prompt = f"Based on the following search result: {result}, generate additional insights."

    # Call OpenAI GPT-4 to generate additional information
    response = client.chat.completions.create(engine="gpt4-32k", prompt=prompt, max_tokens=150)
    return response.choices[0].text.strip()

# 9. Putting it all together

# Load PDF into azure cognitive search

pdf_path = 'path/to/your/pdf/file.pdf'
pages = split_pdf_to_pages(pdf_path)

FORM_RECOGNIZER_SERVICE = "your-fr-resource"
FORM_RECOGNIZER_KEY = "SECRET_FR_KEY"
FORM_RECOGNIZER_CREDS = AzureKeyCredential(FORM_RECOGNIZER_KEY)
openai_api_key = 'your-openai-api-key'  # Replace with your OpenAI API key

page_map = get_document_text_from_content(pages)

max_section_length = 1000  # For example, 1000 characters per section
sections = split_text(page_map, max_section_length)

# filename and sections from previous steps
# index_sections(filename, sections)
# Example usage
endpoint = 'https://[service-name].search.windows.net'  # Replace with your service endpoint
index_name = 'your-index-name'  # Replace with your index name
api_key = 'your-api-key'  # Replace with your API key
search_query = 'example search text'

search_results = search_index(search_query, endpoint, index_name, api_key)

for result in search_results:
    print(result)  # Process each search result as needed



# for section in sections:
#     print(section)  # Process each section as needed


enriched_results = []
for result in search_results:
    enriched_info = enrich_with_gpt(result, openai_api_key)
    enriched_results.append((result, enriched_info))

for result, enriched_info in enriched_results:
    print("Original Result:", result)
    print("Enriched Information:", enriched_info)
    print("-----")