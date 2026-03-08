# Use AWS Lambda Python 3.11 base image
FROM public.ecr.aws/lambda/python:3.11

# Set working directory
WORKDIR ${LAMBDA_TASK_ROOT}

# Copy requirements file
COPY src/requirements.txt .

# Install Python dependencies
# Use --no-cache-dir to reduce image size
# Install all packages as binary wheels to avoid compilation issues
RUN pip install --no-cache-dir --only-binary=:all: \
    numpy==1.26.4 \
    scikit-learn==1.5.2 && \
    pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ${LAMBDA_TASK_ROOT}/

# Set the CMD to your handler
CMD [ "lambda_handler.lambda_handler" ]
