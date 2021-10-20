import spacy
from haystack.file_converter.pdf import PDFToTextConverter
from haystack.preprocessor import PreProcessor
from haystack.document_store import ElasticsearchDocumentStore
from haystack.file_converter.docx import DocxToTextConverter
from haystack.ranker import SentenceTransformersRanker

print("Loading models...")
location_and_company_name_model = spacy.load('en_core_web_lg')
designation_model = spacy.load('en_core_web_sm')
requirements_model = spacy.load('en_core_web_sm')
pdf_converter = PDFToTextConverter(remove_numeric_tables=True, valid_languages=["en"])
doc_converter = DocxToTextConverter(remove_numeric_tables=True, valid_languages=["de","en"])
document_store = ElasticsearchDocumentStore(host="157.245.110.225", username="", password="", index="document")
processor = PreProcessor(clean_empty_lines=True,
                            clean_whitespace=True,
                            clean_header_footer=True,
                            split_by="word",
                            split_length=200,
                            split_respect_sentence_boundary=True)
ranker = SentenceTransformersRanker(
    model_name_or_path="cross-encoder/ms-marco-MiniLM-L-12-v2")
print("Loaded models")
print(ranker)
