FROM python:3.12.3

ENV PYTHONUNBUFFERED True
ENV PYTHONDONTWRITEBYTECODE True

RUN pip install --upgrade pip
RUN pip install poetry==1.6.1
RUN poetry config virtualenvs.create false

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libsoup2.4-dev \
    libjavascriptcoregtk-4.0-dev \
    libgtk-3-dev \
    libwebkit2gtk-4.0-dev

COPY . /app

RUN poetry install  --no-interaction --no-ansi --no-root

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
