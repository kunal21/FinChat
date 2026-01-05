#!/bin/bash
# wait-for-client.sh

# wait for a response from the client
echo -n "Waiting for the client to finish initializing..."
while [ "$(curl -s -o /dev/null -w "%{http_code}" -m 1 localhost:3001)" != "200" ]
do
  sleep 1
  echo -n "."
done

# print message
cat <<EOF

The client is ready!
Open localhost:3001 in your browser to view the client.

Docker Compose Commands:
  docker compose logs --follow          # View service logs
  docker compose down                   # Stop containers
  docker compose restart <service>      # Restart a service
  docker compose ps                     # List running services
EOF
