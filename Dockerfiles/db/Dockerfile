FROM mongo:latest

COPY networks.json /networks.json
CMD mongoimport --host db --db TFG --collection networks --type json --file /networks.json --upsertFields name