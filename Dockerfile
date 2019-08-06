ARG UBUNTU_VERSION=18.04
ARG ARCH=
ARG CUDA=10.0
FROM nvidia/cuda${ARCH:+-$ARCH}:${CUDA}-base-ubuntu${UBUNTU_VERSION} as base


###############################################################################
#
#							Python
#
###############################################################################

RUN apt-get update && apt-get install -y \
  python3 \
	python3-dev \
  python3-pip \
	python3-numpy && \
	rm -rf /var/lib/apt/lists/*

RUN pip3 --no-cache-dir install --upgrade \
  pip \
  setuptools

# Create a symbolic link so that both "python" and "python3" link to same binary
RUN ln -s $(which python3) /usr/local/bin/python


###############################################################################
#
#							CUDNN & Tensorflow
#
###############################################################################

ARG ARCH
ARG CUDA
ARG CUDNN=7.4.1.5-1

# Install tensorflow dependencies
SHELL ["/bin/bash", "-c"]
RUN apt-get update && apt-get install -y --no-install-recommends \
 	--allow-change-held-packages \
    build-essential \
    cuda-command-line-tools-${CUDA/./-} \
    cuda-cublas-${CUDA/./-} \
    cuda-cufft-${CUDA/./-} \
    cuda-curand-${CUDA/./-} \
    cuda-cusolver-${CUDA/./-} \
    cuda-cusparse-${CUDA/./-} \
    curl \
    libcudnn7=${CUDNN}+cuda${CUDA} \
    libfreetype6-dev \
    libhdf5-serial-dev \
    libzmq3-dev \
    pkg-config \
    software-properties-common \
    unzip

RUN [ ${ARCH} = ppc64le ] || (apt-get update && \
    apt-get install nvinfer-runtime-trt-repo-ubuntu1804-5.0.2-ga-cuda${CUDA} \
    && apt-get update \
    && apt-get install -y --no-install-recommends libnvinfer5=5.0.2-1+cuda${CUDA} \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*)

# For CUDA profiling, TensorFlow requires CUPTI.
ENV LD_LIBRARY_PATH /usr/local/cuda/extras/CUPTI/lib64:${LD_LIBRARY_PATH}

# See http://bugs.python.org/issue19846
ENV LANG C.UTF-8

ARG TF_PACKAGE=tensorflow-gpu
ARG TF_PACKAGE_VERSION=1.13.1
RUN pip3 install ${TF_PACKAGE}${TF_PACKAGE_VERSION:+==${TF_PACKAGE_VERSION}}


###############################################################################
#
#							Ubuntu Packages
#
###############################################################################

RUN apt-get update && \
  apt-get install -y \
  sqlite3 \
  sqlitebrowser


###############################################################################
#
#							Python Packages
#
###############################################################################

# Install Python packages
COPY requirements.txt /
RUN pip3 install --upgrade pip
RUN pip3 install -r /requirements.txt


###############################################################################
#
#							Container Startup & Command
#
###############################################################################

WORKDIR /peoplecounter

#COPY docker-entrypoint.sh /peoplecounter
#RUN chmod +x /peoplecounter/docker-entrypoint.sh
#ENTRYPOINT ["./docker-entrypoint.sh"]

CMD ["sh", "-c", "tail -f /dev/null"]
