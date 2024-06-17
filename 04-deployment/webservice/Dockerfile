FROM python:3.12-slim

RUN pip install -U pip

RUN pip install pipenv

WORKDIR /app

COPY ["Pipfile","Pipfile.lock","./"]

# https://docs.pipenv.org/advanced/?ref=muhabtomoum.com
RUN pipenv install --system --deploy

COPY ["predict.py","lin_reg.bin","./"]

EXPOSE 9696

ENTRYPOINT ["waitress-serve", "--listen=0.0.0.0:9696", "predict:app"]
#ENTRYPOINT [ "gunicorn", "--bind=0.0.0.0:9696", "predict:app" ]

#para constuir una imagen -> docker build -t servicio-prediccion-duracion-viaje:v1 .
#para ejecutar -> docker run -it --rm -p 9696:9696  servicio-prediccion-duracion-viaje:v1