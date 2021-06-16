FROM andrejreznik/python-gdal
ENV PYTHONPATH "${PYTHONPATH}:/"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && rm requirements.txt
COPY ./src /src
COPY ./data /data
CMD streamlit run /src/front_end/streamlit_app.py
