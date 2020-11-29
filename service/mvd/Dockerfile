FROM conda/miniconda3:latest

WORKDIR /home/mvd

RUN apt-get update && apt install -y gcc build-essential

COPY  ./env.yml /home/mvd/env.yml

RUN conda env create -f env.yml

COPY  ./ /home/mvd

RUN apt install -y locales
RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen
RUN locale-gen
RUN apt install -y libgl1-mesa-glx unzip libglib2.0-0

ENV PYTHONPATH "${PYTHONPATH}: /home/mvd"
ENV ACCEPT_INTEL_PYTHON_EULA=yes
ENV STREAMLIT_SERVER_PORT=8501

EXPOSE 8501


ENTRYPOINT ["conda", "run", "-n", "mvd", "streamlit", "run", "data_uploader.py", "--server.address=0.0.0.0", "--server.maxUploadSize=1028"]
