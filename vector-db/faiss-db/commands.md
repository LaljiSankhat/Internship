docker build -t faiss-app-image .

docker volume create faiss-vol


docker run -d \
  --name faiss-app \
  -p 8000:8000 \
  -v faiss-vol:/vectorstore/faiss_index \
  faiss-app-image



