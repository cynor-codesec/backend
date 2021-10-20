#!/usr/bin/env python
import sys
from rq import Connection, Worker

# Preload libraries

# from models import location_and_company_name_model, designation_model, requirements_model, pdf_converter, doc_converter, document_store, processor, ranker
# import models

# Provide queue names to listen to as arguments to this script,
# similar to rq worker

if __name__ == '__main__':
    with Connection():
        qs = sys.argv[1:] or ['default']

        w = Worker(qs)
        w.work()
