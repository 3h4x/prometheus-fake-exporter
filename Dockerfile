FROM python:3.6.4-alpine3.7

# Install python packages
ADD requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN rm requirements.txt

# Install exporter
ADD fake_exporter.py /fake_exporter.py

# Run as non-root
RUN adduser exporter -S -u 1000
USER exporter

# NOTE: the "-u" switch disables output buffering (so output will be
#       flush immediately)
CMD python3.6 -u /fake_exporter.py $POD_NAMESPACE $POD_NAME