FROM nvidia/cuda:11.6.2-base-ubuntu20.04

RUN apt update
RUN apt-get install -y python3 python3-pip
ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES compute,utility

# install utilities
RUN apt-get update  && apt install libgl1-mesa-glx -y  &&\
    apt-get install --no-install-recommends -y curl

# Installing python dependencies
RUN python3 -m pip --no-cache-dir install --upgrade pip && \
    python3 --version && \
    pip3 --version

RUN pip3 --timeout=300 --no-cache-dir install torch==1.10.0+cu113 torchvision==0.11.0+cu113 -f https://download.pytorch.org/whl/cu113/torch_stable.html

COPY  . /AiThings
RUN cd AiThings &&\
    python3 -m pip install -U pip &&\
    pip3 install -r requirements.txt

WORKDIR /AiThings

EXPOSE 7003
# RUN python3 main.py


