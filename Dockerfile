FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --disable-pip-version-check -r requirements.txt \
    && useradd --create-home --uid 10001 --shell /usr/sbin/nologin honestagent

COPY --chown=honestagent:honestagent honest_agent honest_agent
COPY --chown=honestagent:honestagent trajectories trajectories

USER honestagent
EXPOSE 8000

CMD ["uvicorn", "honest_agent.interfaces.proxy:app", "--host", "0.0.0.0", "--port", "8000"]
