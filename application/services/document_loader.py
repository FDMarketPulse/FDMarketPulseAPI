import firebase_admin
from firebase_admin import credentials, storage
from langchain.document_loaders import PyPDFLoader, PDFMinerPDFasHTMLLoader


def load_pdf_documents(url):
    loader = PyPDFLoader(url)
    return loader.load_and_split()


def load_firebase_documents(bucket_name, prefix):
    cred = credentials.Certificate("application/utility/fd-market-pulse-firebase-adminsdk.json")
    try:
        firebase_admin.get_app()
    except ValueError as e:
        firebase_admin.initialize_app(cred)

    bucket = storage.bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=prefix)

    documents_url_list = []
    for blob in blobs:
        if not blob.name.endswith('/'):  # Ignore directories
            blob.make_public()
            documents_url_list.append(blob.public_url)

    documents = []
    for i in documents_url_list:
        print("document loading start")
        loader = PDFMinerPDFasHTMLLoader(i)
        doc_i = loader.load_and_split()
        print("document loading end")
        for j in doc_i:
            if len(j.page_content) < 50:
                j.page_content = ""
            j.metadata['file_name'] = i
        documents.extend(doc_i)
        print("document extend end")

    return documents
