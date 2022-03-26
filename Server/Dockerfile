FROM python:3.10 as builder

WORKDIR /workspace
COPY . .

RUN pip install build && \
    python -m build

RUN mkdir -p /dist && \
    mv dist/*.whl /dist && \
    cp docker/entrypoint.sh /dist

FROM python:3.10

COPY --from=builder /dist /dist

RUN ls -alh /dist && pip install /dist/*.whl

ENTRYPOINT /dist/entrypoint.sh
