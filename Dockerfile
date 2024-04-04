FROM python:3.9-alpine3.13 
# 이미지를 지정 alpine : 리눅스의 가벼운 버전
LABEL maintainer="londonappdeveloper.com"
# 이미지를 관리하게될 사람을 적음

ENV PYTHONUNBUFFERED 1
# 파이썬에게 버퍼가 필요없다고 전달하는 것. 지연이 없도록 처리함.

COPY ./requirements.txt /tmp/requirements.txt
# 도커이미지가 requirements.txt를 복사함.
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./app /app
WORKDIR /app
EXPOSE 8000

ARG DEV=false
RUN python -m venv /py && \
    # 가상환경 생성
    /py/bin/pip install --upgrade pip && \
    # pip을 업그레이드
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ] ; \
        then echo "--DEV BUILD--" && /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    # DEV모드이면은 /tmp/requirements.dev.txt 이것도 추가해라.
    apk del .tmp-build-deps && \
    rm -rf /tmp && \
    # tmp삭제. 
    adduser \
        --disabled-password \
        --no-create-home \
        django-user
    #루트유저를 쓰면 안좋기 때문에 사용자를 추가함. 

ENV PATH="/py/bin:$PATH"

USER django-user

# docker build .했음
# 이미지 구축하는 것임.
# app폴더가 없으면 에러남
