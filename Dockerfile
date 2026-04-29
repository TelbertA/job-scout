# Stage 1: build
# We install dependencies here in an isolated layer.
# Why a separate build stage? The final image won't contain pip, build tools,
# or any install cache — only the installed packages get copied forward.
# Smaller image = smaller attack surface.
FROM public.ecr.aws/lambda/python:3.12 AS build

COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -t /opt/python/

# Stage 2: final image
# This is the actual image Lambda runs. We copy in:
#   1. The installed packages from the build stage
#   2. Our source code
#   3. The profiles directory (scoring engine needs default_profile.json)
FROM public.ecr.aws/lambda/python:3.12

COPY --from=build /opt/python/ ${LAMBDA_TASK_ROOT}/
COPY src/ ${LAMBDA_TASK_ROOT}/
COPY profiles/ ${LAMBDA_TASK_ROOT}/profiles/

LABEL maintainer="Telbert Anthony"
LABEL project="job-scout"

# Tells Lambda which function to call when the container starts.
# Format: <filename without .py>.<function name>
CMD ["handler.lambda_handler"]
