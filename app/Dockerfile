FROM python:3.7-stretch

# We don't want to run our application as root if it is not strictly necessary, even in a container.
# Create a user and a group called 'app' to run the processes.
# A system user is sufficient and we do not need a home.
RUN adduser --system --group --no-create-home app

# Place the application components in a dir below the root dir
COPY . /app

# Make the directory the working directory for subsequent commands
WORKDIR /app

RUN apt-get update

RUN apt-get install poppler-utils -y

# Install from the requirements.txt we copied above
RUN pip install -r requirements.txt

RUN pip install -e git+git://github.com/cynor-eyHack2021/haystack.git#egg=farm-haystack

RUN python -m spacy download en_core_web_lg

RUN python -m spacy download en_core_web_sm

RUN python -m nltk.downloader stopwords

RUN python -c "import nltk; nltk.download('stopwords')"

# Hand everything over to the 'app' user
# RUN chown -R app:app /app

# Subsequent commands, either in this Dockerfile or in a
# docker-compose.yml, will run as user 'app'
# USER app

# We are done with setting up the image.
# As this image is used for different
# purposes and processes no CMD or ENTRYPOINT is specified here,
# this is done in docker-compose.yml.
