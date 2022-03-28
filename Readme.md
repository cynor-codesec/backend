![logo](https://imgur.com/jRlL7aO.png)
# Cynor's Backend

Cynor helps companies automate their cv screening process by uploading a **job description** and the **corresponding CVs of all the applicants**. After processing the data, Cynor will produce a ranked list of candidates and explain why the person received a certain rank.

[DEMO VIDEO](https://imgur.com/3owZVue.png)

## Under The Hood
![MAP](https://imgur.com/1KTu6hT.png)

## Our Approach
Our main approach is to detect and match entities of importance to the CV screening task at hand. At first we try and detect 4 categories of information from the Job Description, namely:

* Designation
* Location
* Requirements
* Responsiblities (SBD)

Although, The system does not require all 4 categories to work but having all 4 improves accuracy. However, atleast requirements is necessary for it to work.

Then we proceed to extract entities or sentences from each category of information using Named Entity Recognition (NER) and Sentence Boundary Detection (SBD) techniques.

There are several ways in which a CV and JD map to one another. For our purposes, the following diagram shows how we think the categories in the JD map to the information in the CV and how we can use that to figure out the eligibility of that CV for that particular Job Description.

![map](https://imgur.com/Ql1V2Ba.png)

This map ensures us that doing a matching of the entities should give us enough information to know eligible a particular candidate is.

### Matching
We will be using a fuzzy searching system in steps 1 & 4.  In step 1, we approximate where the different categories of information are located on the doc. We will also fuzzy search the extracted entities obtained in step 2  from the JD on the CVs and, if found, use that to create our ranking system.

### Ranking
We use a simple yet functional ranking system where if an extracted entity from the JD is found in a CV (doesn't have to match exactly but has to be similar enough, we will also factor in the similarity value b/w the two), the similarity score multiplied by the weightage of that entity is awarded to that CV. The sum of all the points given to the CV based on the number of matched entities makes up the score of that CV. Once the scores of every CV is known, we can compare them to one another and create a ranked list of CVs.

## Installation:
```
sudo docker-compose up
```
> add your azure API credentials for OCR.
> -d flag for production

* The server will start in port 8000

### Other info:
* Number of workers can be increased or reduced by modifying removing or adding this part of `docker-compose.yaml`
```
 worker:
    image: master-image
    depends_on:
      - redis
    command: rqworker --name worker --url redis://redis:6379/0
```
