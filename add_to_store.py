import re
import pprint
from haystack.file_converter.pdf import PDFToTextConverter
from haystack.preprocessor import PreProcessor
from haystack.document_store import ElasticsearchDocumentStore
from haystack.file_converter.docx import DocxToTextConverter
from rq.job import Retry
import get_cv_score
from sessions import get_session_feature_store, update_session_status
import rqueue

def add_to_store(filenames, filepaths, jd_id):

    pdf_converter = PDFToTextConverter(remove_numeric_tables=True, valid_languages=["en"])
    doc_converter = DocxToTextConverter(remove_numeric_tables=True, valid_languages=["de","en"])

    document_store = ElasticsearchDocumentStore(host="157.245.110.225", username="", password="", index="document")

    processor = PreProcessor(clean_empty_lines=True,
                            clean_whitespace=True,
                            clean_header_footer=True,
                            split_by="word",
                            split_length=200,
                            split_respect_sentence_boundary=True)

    docs = []
    for f_name, f_path in zip(filenames, filepaths):
        # Optional: Supply any meta data here
        # the "name" field will be used by DPR if embed_title=True, rest is custom and can be named arbitrarily
        print("Adding file: " + f_name)
        cur_meta = {"name": f_name, "jd_id": jd_id}

        # Run the conversion on each file (PDF -> 1x doc)
        if f_path.endswith(".pdf"):
            d = pdf_converter.convert(f_path, meta=cur_meta)
        elif f_path.endswith(".docx"):
            d = doc_converter.convert(f_path, meta=cur_meta)
        else:
            raise Exception("File type not supported")
        
        # clean and split each dict (1x doc -> multiple docs)
        d = processor.process(d)
        sents = []
        for mind in d:
            ents = re.split('\n\n|\n',mind["text"])
            for ent in ents:
                sents.append({'text': ent, "meta": mind["meta"]})
        
        docs.extend(sents)

    # at this point docs will be [{"text": "some", "meta":{"name": "myfilename", "category":"a"}},...]

    document_store.write_documents(docs)
    print("HERE")
    print(document_store.get_all_documents(filters={"name": [filenames[0]]}))
    update_session_status(jd_id, "feature_store_created")
    feature_store = get_session_feature_store(jd_id)
    for file in filenames:
        rqueue.q.enqueue(get_cv_score.get_cv_score, args=(feature_store, file), retry=Retry(max=3), timeout=500)

# if __name__ == "__main__":
#     add_to_store(['a', 'b', 'c', 'd'], ['cv/1.pdf', 'cv/3.pdf', 'cv/4.pdf', 'cv/5.pdf'])