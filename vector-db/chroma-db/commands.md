docker run \
  --name chroma \
  --network app-net \
  -p 8001:8000 \
  -v chroma-vol:/chroma/chroma \
  chromadb/chroma




docker run -it --name c-app \
  --network app-net \
  --add-host=host.docker.internal:host-gateway \
  -e HOST="host.docker.internal" \
  -e PORT="8001" \
  -p 8000:8000 \
   chroma-app-image





right way
docker run -d \
  --name c-app \
  --network app-net \
  -e HOST="chroma" \
  -e PORT="8000" \
  -p 8000:8000 \
  chroma-app-image
