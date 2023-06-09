FROM python:3.11-alpine3.15 AS compiler
RUN apk add gcc g++ musl-dev alpine-sdk build-base libffi-dev
COPY ./requirements.txt ./
RUN pip install --upgrade pip && pip install --user -r requirements.txt

FROM python:3.11-alpine3.15 as builder
COPY --from=compiler /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
WORKDIR /usr/src/app
COPY . .
ENTRYPOINT [ "/usr/local/bin/python", "./run.py" ]
