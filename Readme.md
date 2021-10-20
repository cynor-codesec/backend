# CYNOR - Backend

### How to run:
```
sudo docker-compose up
```
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