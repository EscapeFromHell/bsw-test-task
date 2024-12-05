FROM python:3.10

RUN mkdir /app

COPY ./ /app

WORKDIR /app

ENV PYTHONPATH=/app

RUN python -m pip install --no-cache-dir poetry==1.4.2 \
    && poetry config virtualenvs.create false \
    && poetry install --without dev,test --no-interaction --no-ansi \
    && rm -rf $(poetry config cache-dir)/{cache,artifacts}
