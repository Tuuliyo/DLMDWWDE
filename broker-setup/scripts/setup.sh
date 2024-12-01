#!/bin/sh

echo "Waiting for Solace broker to be ready..."
until wget -q --spider --header="Authorization: Basic $(echo -n admin:admin | base64)" http://message-broker:8080/SEMP/v2/config; do
    echo "Broker not ready. Retrying in 5 seconds..."
    sleep 5
done
echo "Solace broker is ready."

echo "Initializing Terraform..."
terraform init

echo "Planning Terraform changes..."
terraform plan

until terraform apply -auto-approve; do
    echo "Terraform apply failed. Retrying in 10 seconds..."
    echo "Re-running terraform plan to understand the current state..."
    terraform plan
    sleep 10
done

echo "Terraform setup complete. Exiting container..."
