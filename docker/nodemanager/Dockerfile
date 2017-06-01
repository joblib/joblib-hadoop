FROM bde2020/hadoop-base:1.1.0-hadoop2.7.1-java8
MAINTAINER Ivan Ermilov <ivan.s.ermilov@gmail.com>

HEALTHCHECK CMD curl -f http://localhost:8042/ || exit 1

RUN apt-get update -yqq  && apt-get install -yqq \
  wget \
  bzip2 \
  git \
  libglib2.0-0 \
  && rm -rf /var/lib/apt/lists/*

# Configure environment
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

WORKDIR /work

RUN wget -O miniconda.sh \
  https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh \
  && bash miniconda.sh -b -p /work/miniconda \
&& rm miniconda.sh

ENV PATH="/work/bin:/work/miniconda/bin:$PATH"

RUN conda install -y \
  pip \
  setuptools \
  notebook \
  ipywidgets \
  psutil \
&& conda clean -tipsy

RUN pip install pip --upgrade
RUN pip install knit distributed

ADD run.sh /run.sh
RUN chmod a+x /run.sh

EXPOSE 8042
EXPOSE 8786

CMD ["/run.sh"]
