#!/bin/bash
echo "🐍 Testing vim-ai with Python 3.4 in Docker..."
{
cat <<EOF
FROM python:3.4-slim

WORKDIR /app
COPY . .

# Install only pytest - no typing dependency needed
RUN pip install pytest==3.2.5

CMD ["python", "-m", "pytest", "tests/", "-v"]
EOF
} > Dockerfile.python34
docker build -f Dockerfile.python34 -t vim-ai-py34 . && docker run --rm vim-ai-py34 && rm -f Dockerfile.python34
