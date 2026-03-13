export PUERTO=5432
export NOMBRE=retro_db
docker volume create $NOMBRE
docker run -d --name $NOMBRE -v $NOMBRE:/var/lib/postgresql/data -e POSTGRES_PASSWORD=postgres --restart=unless-stopped -p $PUERTO:5432 postgres