from azure_functions import azure_ocr
import constants
from sessions import get_session_jd_img, update_session_ocr, update_session_features, update_session_status
import rqueue
import spacy
from spacy.matcher import Matcher
from spacy.matcher import PhraseMatcher
from spacy.tokens import Span
import models


# jdDataOcr ->  dictionary
def get_location_and_company_name(texts):
    nlp = spacy.load('en_core_web_lg')
    docs = nlp.pipe(texts)

    info_dict = {
        "company_name": {
            "text": None,
            "start": None,
            "end": None,
            "line_ix": None,
            "line": None,
            "weight": 0,
        },
        "location": {
            "text": None,
            "start": None,
            "end": None,
            "line_ix": None,
            "line": None,
            "weight": 0,
        }
    }

    for idx, doc in enumerate(docs):
        for ent in doc.ents:
            if ent.label_ == "ORG" and info_dict["company_name"]["text"] == None:
                info_dict["company_name"]["text"] = ent.text
                info_dict["company_name"]["start"] = ent.start_char
                info_dict["company_name"]["end"] = ent.end_char
                info_dict["company_name"]["line_ix"] = idx
                info_dict["company_name"]["line"] = doc.text
            elif ent.label_ == "GPE" and info_dict["location"]["text"] == None:
                info_dict["location"]["text"] = ent.text
                info_dict["location"]["start"] = ent.start_char
                info_dict["location"]["end"] = ent.end_char
                info_dict["location"]["line_ix"] = idx
                info_dict["location"]["line"] = doc.text
            elif info_dict["company_name"]["text"] != None and info_dict["location"]["text"] != None:
                break

        if info_dict["company_name"]["text"] != None and info_dict["location"]["text"] != None:
            break

    return info_dict


# jdDataOcr ->  dictionary
def get_designation(texts):
    info_dict = {
        "designation": {
            "text": None,
            "start": None,
            "end": None,
            "line_ix": None,
            "line": None,
            "weight": 0,
        },
    }
    nlp = spacy.load('en_core_web_sm')
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")

    with open('data/job-titles.txt') as f:
        terms = [line.rstrip() for line in f]

    # Only run nlp.make_doc to speed things up
    patterns = [nlp.make_doc(text) for text in terms]
    matcher.add("DesignationList", patterns)

    docs = nlp.pipe(texts)

    for ix, doc in enumerate(docs):
        matches = matcher(doc)
        for match_id, start, end in matches:
            span = doc[start:end]
            info_dict["designation"]["text"] = span.text
            info_dict["designation"]["start"] = start
            info_dict["designation"]["end"] = end
            info_dict["designation"]["line_ix"] = ix
            info_dict["designation"]["line"] = doc.text
            break
    return info_dict

# jdDataOcr -> dictionary


def get_requirements(texts):
    nlp = spacy.load('en_core_web_sm')
    matcher = Matcher(nlp.vocab)

    # keyword extraction
    kw_pattern1 = [{"POS": "NOUN"}, {"IS_PUNCT": True,
                                     "OP": "?"}, {"POS": "NOUN", "OP": "+"}]
    kw_pattern2 = [{"POS": "PROPN"}]
    matcher.add("genKw", [kw_pattern1, kw_pattern2])

    kw_pattern3 = [{"POS": "NOUN"}, {
        "POS": "PART", "OP": "?"}, {"POS": "NOUN"}]
    kw_pattern3 = [{"POS": "PROPN"}, {
        "POS": "PART", "OP": "?"}, {"POS": "NOUN"}]
    kw_pattern4 = [{"POS": "PROPN"}, {
        "POS": "PART", "OP": "?"}, {"POS": "PROPN"}]
    kw_pattern5 = [{"POS": "NOUN"}, {
        "POS": "PART", "OP": "?"}, {"POS": "PROPN"}]
    kw_pattern6 = [{"POS": "ADJ"}, {"POS": {"IN": ["PROPN", "NOUN"]}}]
    kw_pattern7 = [{"POS": "NOUN"}, {"POS": "VERB"}]
    kw_pattern8 = [{"POS": "NOUN"}, {"POS": "VERB"}]
    kw_pattern9 = [{"TAG": "VBG"}, {"POS": "NOUN"}]
    kw_pattern10 = [{"POS": "ADJ"}, {"POS": "VERB"}]
    matcher.add("compoundKw", [kw_pattern3, kw_pattern4, kw_pattern5, kw_pattern6,
                               kw_pattern7, kw_pattern8, kw_pattern9, kw_pattern10])
    # Year extraction
    pattern1 = [{"IS_DIGIT": True}, {"IS_PUNCT": True},
                {"IS_DIGIT": True}, {"LEMMA": "year"}, {
                    "LOWER": "of", "OP": "?"},
                {"LEMMA": "experience", "OP": "?"}]
    pattern2 = [{"IS_DIGIT": True}, {"LOWER": "to"},
                {"IS_DIGIT": True}, {"LEMMA": "year"}, {
                    "LOWER": "of", "OP": "?"},
                {"LEMMA": "experience", "OP": "?"}]
    matcher.add("rangeExp", [pattern1, pattern2])

    pattern3 = [{"LOWER": "minimum"}, {"IS_DIGIT": True}, {"LEMMA": "year"},
                {"LOWER": "of", "OP": "?"},
                {"LEMMA": "experience", "OP": "?"}]
    pattern4 = [{"LOWER": "atleast"}, {"IS_DIGIT": True}, {"LEMMA": "year"},
                {"LOWER": "of", "OP": "?"},
                {"LEMMA": "experience", "OP": "?"}]
    pattern5 = [{"LOWER": "at"}, {"LOWER": "least"}, {"IS_DIGIT": True}, {"LEMMA": "year"},
                {"LOWER": "of", "OP": "?"},
                {"LEMMA": "experience", "OP": "?"}]
    matcher.add("minExp", [pattern3, pattern4, pattern5])

    pattern6 = [{"IS_DIGIT": True}, {"LEMMA": "year"},
                {"LOWER": "of", "OP": "?"},
                {"LEMMA": "experience", "OP": "?"}]
    matcher.add("genExp", [pattern6])

    Span.set_extension("matchId", default=None, force=True)
    info_dict = {}
    docs = nlp.pipe(texts)
    for ix, doc in enumerate(docs):
        info_dict["skill" + str(ix)] = {}
        info_dict["skill" + str(ix)]["line_ix"] = ix
        info_dict["skill" + str(ix)]["line"] = doc.text
        info_dict["skill" + str(ix)]["weight"] = 0
        matches = matcher(doc)
        spans = []
        for match_id, start, end in matches:
            string_id = nlp.vocab.strings[match_id]
            span = doc[start:end]
            span._.matchId = match_id
            spans.append(span)
        filtered_spans = spacy.util.filter_spans(spans)
        info_dict["skill" + str(ix)]["text"] = [(span.text,
                                                 nlp.vocab.strings[span._.matchId]) for span in filtered_spans]
        info_dict["skill" +
                  str(ix)]["start"] = [span.start for span in filtered_spans]
        info_dict["skill" +
                  str(ix)]["end"] = [span.end for span in filtered_spans]

    return info_dict

# jdDataOcr -> dictionary


def get_responsibilities(texts):
    info_dict = {}
    for ix, text in enumerate(texts):
        info_dict["repsonsibility"+str(ix)] = {}
        info_dict["repsonsibility"+str(ix)]["line"] = text
        info_dict["repsonsibility"+str(ix)]["text"] = text
        info_dict["repsonsibility"+str(ix)]["line_ix"] = ix
        info_dict["repsonsibility"+str(ix)]["weight"] = 0
    return info_dict


def jd_parser(main_text, req_text, res_text):
    feature_store = {}

    main_funcs = [get_location_and_company_name, get_designation]
    for fun in main_funcs:
        feature_store.update(fun(main_text))

    feature_store["requirements"] = {}
    feature_store["responsibilities"] = {}

    feature_store["requirements"].update(get_requirements(req_text))
    feature_store["responsibilities"].update(get_responsibilities(res_text))

    return feature_store


def ocr_and_update(resp_path, req_path, id):
    resp_ocr = azure_ocr(constants.PUBLIC_BASE_URL + "/" + resp_path)
    req_ocr = azure_ocr(constants.PUBLIC_BASE_URL + "/" + req_path)
    jd_imgs = get_session_jd_img(id)
    jd_ocr = []
    for img in jd_imgs:
        img_ocr = azure_ocr(constants.PUBLIC_BASE_URL + "/" + img)
        for line in img_ocr:
            jd_ocr.append(line)
    # save to db
    ocr_all = {
        "resp": resp_ocr,
        "req": req_ocr,
        "jd": jd_ocr
    }
    update_session_ocr(id, ocr_all)
    feature_store = jd_parser(jd_ocr, req_ocr, resp_ocr)
    update_session_features(id, feature_store)
    update_session_status(id, "feature_selected")
