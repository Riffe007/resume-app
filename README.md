# Resume AI Deployment Pipeline

An interactive resume-generation application that leverages Azure OpenAI GPT-4, FastAPI, and Azure AI Search for Retrieval-Augmented Generation (RAG). The app integrates with HubSpot CRM for feedback tracking and is deployed automatically using Terraform and GitHub Actions. Containerization with Docker ensures consistency across environments.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Setup & Installation](#setup--installation)
  - [Local Development Setup](#local-development-setup)
  - [Repository & Branch Setup](#repository--branch-setup)
- [Deployment](#deployment)
  - [Terraform Infrastructure](#terraform-infrastructure)
  - [CI/CD with GitHub Actions](#cicd-with-github-actions)
  - [Containerization with Docker](#containerization-with-docker)
- [Security](#security)
- [Future Enhancements](#future-enhancements)
- [License](#license)

---

## Overview

This project automates the deployment of a FastAPI-based resume-generation service. The service interacts with:
- **Azure OpenAI GPT-4:** For generating AI-powered resume content.
- **Azure AI Search:** Enhances response generation with RAG.
- **HubSpot CRM:** Tracks and provides feedback on generated resumes.

By leveraging Infrastructure-as-Code (IaC) with Terraform and CI/CD pipelines with GitHub Actions, we ensure scalability, repeatability, and robust security throughout the deployment process.

---

## Features

- **Automated Deployment:** Fully automated setup with Terraform and GitHub Actions.
- **AI-Powered Resume Generation:** Leverages GPT-4 for personalized resume creation.
- **File Upload & Download:** Users can upload files (e.g., job descriptions) and download generated PDFs.
- **Secure Integration:** Private networking, firewall rules, encryption, and advanced access control.
- **Cost Optimization:** Auto-scaling and shutdown during low-usage periods.
- **HubSpot Integration:** Seamless feedback loop for tracking resume effectiveness.

---

## Architecture

1. **Frontend:** Next.js application for user interaction.
2. **Backend:** FastAPI handling file uploads, API calls, and orchestrating resume generation.
3. **AI Services:** 
   - Azure OpenAI for generating resume content.
   - Azure AI Search to augment responses using Retrieval-Augmented Generation.
4. **Data Stores:**
   - Azure PostgreSQL for structured data.
   - Azure CosmosDB (MongoDB API) for logs and analytics.
5. **Deployment:** 
   - **Infrastructure:** Defined via Terraform.
   - **CI/CD:** Orchestrated using GitHub Actions.
   - **Containerization:** Docker for environment consistency.

---

## Prerequisites

- **Azure Subscription:** Ensure you have an active subscription with necessary permissions.
- **Python 3.10+:** For local development.
- **Docker:** For building and testing container images.
- **Terraform:** For provisioning Azure resources.
- **Git & Git Bash:** For source control and local terminal commands.
- **VS Code:** Your code editor of choice.
- **GitHub Account:** To host the repository and set up GitHub Actions.

---

## Setup & Installation

### Local Development Setup

1. **Create Project Directory and Initialize Git:**

   ```bash
   mkdir resume-app
   cd resume-app
   git init

### 2. Create and Activate Virtual Environment:
```bash
python -m venv venv
# For Linux/macOS:
source venv/bin/activate
# For Windows Git Bash:
source venv/Scripts/activate
```
### 3. Set Up Project Structure:
```bash
mkdir app
touch app/main.py requirements.txt .gitignore
echo "venv/" >> .gitignore
echo "__pycache__/" >> .gitignore
```
### 4. Install Dependencies:
```bash
pip install fastapi uvicorn
pip freeze > requirements.txt
```
## Repository & Branch Setup
Rename the default branch if needed:
```bash
git branch -m master main
git push -u origin main
# Optionally, remove the old branch:
git push origin --delete master
```
# Deployment
## Terraform Infrastructure
### Define Azure Resources:
Create Terraform files (e.g., main.tf) with definitions for:

Azure Resource Group, App Service, PostgreSQL, CosmosDB, Azure OpenAI, AI Search, and networking components.
### Initialize and Deploy: 
```bash
terraform init
terraform plan
terraform apply -auto-approve
```
# CI/CD with GitHub Actions
    - Workflow Setup:
      Create .github/workflows/terraform.yml to automate deployment on push to the main branch.
    - Key Steps Include:
        - Checking out code.
        - Setting up Terraform.
        - Logging in to Azure.
        - Running terraform plan and terraform apply.
# Containerization with Docker
    - Build Docker Image:
    
    ```bash
    docker build -t resume-app .
    ```
    - Push to Azure Container Registry (ACR):
        -  Tag the image:
        ```bash
        docker tag resume-app <ACR_NAME>.azurecr.io/resume-app:latest
        ```
        - Push the image:
        ```bash
        docker push <ACR_NAME>.azurecr.io/resume-app:latest
        ```
    - Deployment to Azure:
        Use Terraform or Github Actions to deploy the container from ACR to Azure App Service for
        Containers or an AKS cluster.

# Security
We take security as seriously as we take our coffee:

    - Private Networking: Deployed within an Azure VNET.
    - Access Controls: Azure Managed Identities and RBAC.
    - Encryption: AES-256 for storage and secure database connections.
    - Firewall & Threat Protection: NSGs, Azure Firewall, Azure Defender, and DDoS protection.
    - Credential Management: Secure storage using Azure Key Vault.
# Future Enhancements
    - AI Analytics: Implement real-time analytics to refine resume recommendations.
    - Advanced Logging: Integrate Azure Sentinel for enhanced security monitoring.
    - Performance Optimizations: Further auto-scaling and cost optimization measures.
# License
This project is licensed under the MIT License.
