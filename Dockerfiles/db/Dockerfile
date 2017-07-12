FROM mongo:3.4.4

COPY networks.json /networks.json
CMD mongoimport --host db --db TFG --collection networks --type json --file /networks.json --upsertFields name