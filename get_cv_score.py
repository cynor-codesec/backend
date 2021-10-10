from haystack.document_store import ElasticsearchDocumentStore
from haystack.ranker import SentenceTransformersRanker
import pprint
from cvinfo import update_cv_feature_store

document_store = ElasticsearchDocumentStore(
    host="localhost", username="", password="", index="document")
ranker = SentenceTransformersRanker(
    model_name_or_path="cross-encoder/ms-marco-MiniLM-L-12-v2")


def get_docs_by_cv_id(id):
    print("Getting documents for CV ID: " + str(id))
    docs = document_store.get_all_documents(filters={"name": [id]})
    print(docs)
    return docs

def get_cv_score(feature_store, id):
    documents = get_docs_by_cv_id(id)
    cvInfo = {"id": id}
    total_score = 0
    for key, value in feature_store.items():
        cvInfo[key] = value
        if key == "requirements":
            cvInfo[key]= {}
            for key2, req in value.items():
                cvInfo[key][key2] = req
                print(req)
                keyword = ' '.join([kw[0] for kw in req["text"]]) #TODO
                weight = req["weight"]
                result = ranker.predict(query=keyword, documents=documents, top_k=1)
                if result[0][0].item() > 0:
                    weighted_score = weight*round(result[0][0].item(), 2)
                    cvInfo[key][key2].update({"sim_score": result[0][0].item(), "matched": result[0][1].text, "weighted_score": weighted_score})
                    total_score += weighted_score
                else:
                    cvInfo[key][key2].update({"sim_score": None, "matched": None, "weighted_score": 0})
        elif key == "responsibilities":
            cvInfo[key] = {}
            for key2, req in value.items():
                cvInfo[key][key2] = req
                keyword = req["text"] 
                weight = req["weight"]
                result = ranker.predict(query=keyword, documents=documents, top_k=1)
                if result[0][0].item() > 0:
                    weighted_score = weight*round(result[0][0].item(), 2)
                    cvInfo[key][key2].update({"sim_score": result[0][0].item(), "matched": result[0][1].text, "weighted_score": weighted_score})
                    total_score += weighted_score
                else:
                    cvInfo[key][key2].update({"sim_score": None, "matched": None, "weighted_score": 0})
        else:
            keyword = value["text"]
            weight = value["weight"]
            result = ranker.predict(
                query=keyword, documents=documents, top_k=1)
            if result[0][0].item() > 0:
                weighted_score = weight*round(result[0][0].item(), 2)
                cvInfo[key].update({"sim_score": result[0][0].item(), "matched": result[0][1].text, "weighted_score": weighted_score})
                total_score += weighted_score
            else:
                cvInfo[key].update({"sim_score": None, "matched": None, "weighted_score": 0})

    cvInfo["total_score"] = total_score
    update_cv_feature_store(id, cvInfo)
    return cvInfo


# if __name__ == "__main__":
#     feature_store = {'company_name': {'end': 16, 'line': 'Axon digital pvt. Itd. Web Backend Developer', 'line_ix': 0, 'start': 5, 'text': 'Axon digital pvt', 'weight': 0}, 'designation': {'end': 10, 'line': 'Axon digital pvt. Itd. Web Backend Developer', 'line_ix': 0, 'start': 8, 'text': 'Backend Developer', 'weight': 0}, 'location': {'end': 21, 'line': 'Location: Maharashtra, India', 'line_ix': 1, 'start': 10, 'text': 'Maharashtra', 'weight': 0}, 'requirements': {'skill0': {'end': [3, 5, 7], 'line': "Bachelor's degree in CSE or MCA", 'line_ix': 0, 'start': [0, 4, 6], 'text': [("Bachelor's degree", 'compoundKw'), ('CSE', 'genKw'), ('MCA', 'genKw')], 'weight': 0}, 'skill1': {'end': [7, 9], 'line': 'At Least 3 to 5 years experience in NodeJs.', 'line_ix': 1, 'start': [2, 8], 'text': [('3 to 5 years experience', 'rangeExp'), ('NodeJs', 'genKw')], 'weight': 0}, 'skill2': {'end': [5, 7], 'line': 'At Least 2 years experience in expressJs.', 'line_ix': 2, 'start': [0, 6], 'text': [('At Least 2 years experience', 'minExp'), ('expressJs', 'genKw')], 'weight': 0}, 'skill3': {'end': [7], 'line': 'Must know to write tests in Mocha:', 'line_ix': 3, 'start': [6], 'text': [('Mocha', 'genKw')], 'weight': 0}, 'skill4': {'end': [4, 8], 'line': 'Must have good communication skills and experience working in teams', 'line_ix': 4, 'start': [2, 6], 'text': [('good communication', 'compoundKw'), ('experience working', 'compoundKw')], 'weight': 0}, 'skill5': {'end': [3], 'line': 'have relevant skills and interests:', 'line_ix': 5, 'start': [1], 'text': [(
#         'relevant skills', 'compoundKw')], 'weight': 0}}, 'responsibilities': {'repsonsibility0': {'line': 'Building backend modules for several backend projects.', 'line_ix': 0, 'text': 'Building backend modules for several backend projects.', 'weight': 0}, 'repsonsibility1': {'line': 'Maintain high coding standards and practices to deliver secure , scalable, optimized, and', 'line_ix': 1, 'text': 'Maintain high coding standards and practices to deliver secure , scalable, optimized, and', 'weight': 0}, 'repsonsibility2': {'line': 'exceptional WordPress products from start to finish. Always do extensive research to', 'line_ix': 2, 'text': 'exceptional WordPress products from start to finish. Always do extensive research to', 'weight': 0}, 'repsonsibility3': {'line': 'build innovative solutions with a perfect user experience. Write test cases for all the', 'line_ix': 3, 'text': 'build innovative solutions with a perfect user experience. Write test cases for all the', 'weight': 0}, 'repsonsibility4': {'line': 'code you develop. Planning and issue management via Jira. Respect timelines and', 'line_ix': 4, 'text': 'code you develop. Planning and issue management via Jira. Respect timelines and', 'weight': 0}, 'repsonsibility5': {'line': 'communicate progress proactively: We are a remote team, so proactive communication', 'line_ix': 5, 'text': 'communicate progress proactively: We are a remote team, so proactive communication', 'weight': 0}, 'repsonsibility6': {'line': 'is essential.', 'line_ix': 6, 'text': 'is essential.', 'weight': 0}}}
#     pprint.pprint(get_cv_score(feature_store, 'a'))
