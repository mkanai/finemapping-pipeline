FROM ubuntu:18.04

# Modified FROM google/cloud-sdk:slim
# https://github.com/GoogleCloudPlatform/cloud-sdk-docker/blob/master/debian_slim/Dockerfile
ARG CLOUD_SDK_VERSION=376.0.0
ENV CLOUD_SDK_VERSION=$CLOUD_SDK_VERSION
ENV PATH "$PATH:/opt/google-cloud-sdk/bin/"

RUN apt-get update -qqy && apt-get install -qqy \
    openjdk-8-jre-headless \
    g++ \
    python3.8-dev python3-pip \
    libopenblas-base liblapack3 \
    zlib1g-dev \
    libjpeg-dev \
    curl \
    gcc \
    apt-transport-https \
    lsb-release \
    openssh-client \
    git \
    gnupg && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 1 && \
    python3 -m pip install --upgrade pip && \
    python3 -m pip install -U crcmod && \
    export CLOUD_SDK_REPO="cloud-sdk-$(lsb_release -c -s)" && \
    echo "deb https://packages.cloud.google.com/apt $CLOUD_SDK_REPO main" > /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - && \
    apt-get update && apt-get install -y google-cloud-sdk=${CLOUD_SDK_VERSION}-0 $INSTALL_COMPONENTS && \
    gcloud config set core/disable_usage_reporting true && \
    gcloud config set component_manager/disable_update_check true && \
    gcloud config set metrics/environment github_docker_image && \
    gcloud --version && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV HAIL_VERSION 0.2.90
RUN python3 -m pip install "hail==${HAIL_VERSION}" cython numpy && \
    python3 -m pip install gnomad && \
    curl -o install_gcs_connector.py https://raw.githubusercontent.com/broadinstitute/install-gcs-connector/master/install_gcs_connector.py && \
    python3 install_gcs_connector.py -k /bin/tempfile && \
    echo "spark.hadoop.google.cloud.auth.service.account.enable true" > /usr/local/lib/python3.8/dist-packages/pyspark/conf/spark-defaults.conf && \
    rm install_gcs_connector.py

# HTSLIB (for bgzip)
ENV HTSLIB_VERSION 1.14
RUN curl -Lo ~/htslib-${HTSLIB_VERSION}.tar.bz2 https://github.com/samtools/htslib/releases/download/${HTSLIB_VERSION}/htslib-${HTSLIB_VERSION}.tar.bz2 && \
    tar xjvf ~/htslib-${HTSLIB_VERSION}.tar.bz2 -C ~ && \
    cd ~/htslib-${HTSLIB_VERSION} && \
    ./configure --prefix=/usr --disable-bz2 --disable-lzma && \
    make && make install && \
    rm -r ~/htslib-${HTSLIB_VERSION}*

ENV PYTHONPATH "/home/hail:$PYTHONPATH"
RUN git clone https://github.com/atgu/ukbb_pan_ancestry /home/hail/ukbb_pan_ancestry && \
    git clone https://github.com/Nealelab/ukb_common /home/hail/ukb_common && \
    git clone https://github.com/mkanai/finemapping-insights /home/hail/finemapping-insights && \
    mv /home/hail/finemapping-insights/fm_insights /home/hail/fm_insights && \
    rm -r /home/hail/finemapping-insights