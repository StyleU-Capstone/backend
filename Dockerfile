FROM python:3.11-slim

COPY ./ ./

RUN pip install --no-cache-dir -r ./requirements.txt

# RUN alembic upgrade head

CMD ["sh", "-c", "sleep 5 && python ./main.py"]
