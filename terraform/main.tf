terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
  required_version = ">= 1.0"
}

provider "azurerm" {
  features {}
}

# Resource Group
resource "azurerm_resource_group" "resume_ai" {
  name     = "resume-ai-rg"
  location = "East US"
}

# PostgreSQL Server (securely provisioned)
resource "azurerm_postgresql_server" "resume_db" {
  name                           = "resume-db"
  location                       = azurerm_resource_group.resume_ai.location
  resource_group_name            = azurerm_resource_group.resume_ai.name
  sku_name                       = "B_Gen5_2"
  storage_mb                     = 5120
  backup_retention_days          = 14
  geo_redundant_backup_enabled   = true
  administrator_login            = "admin_user"
  administrator_login_password   = var.db_password
  ssl_enforcement_enabled        = true
  public_network_access_enabled  = false
}

# Cognitive Account for OpenAI Service
resource "azurerm_cognitive_account" "openai" {
  name                = "resume-openai"
  location            = azurerm_resource_group.resume_ai.location
  resource_group_name = azurerm_resource_group.resume_ai.name
  kind                = "OpenAI"
  sku_name            = "S0"
}

# App Service Plan for FastAPI
resource "azurerm_app_service_plan" "fastapi_plan" {
  name                = "fastapi-app-plan"
  location            = azurerm_resource_group.resume_ai.location
  resource_group_name = azurerm_resource_group.resume_ai.name
  kind                = "Linux"
  reserved            = true

  sku {
    tier = "PremiumV3"
    size = "P1v2"
  }
}

# App Service for FastAPI
resource "azurerm_app_service" "fastapi_app" {
  name                = "fastapi-resume-app"
  location            = azurerm_resource_group.resume_ai.location
  resource_group_name = azurerm_resource_group.resume_ai.name
  app_service_plan_id = azurerm_app_service_plan.fastapi_plan.id

  site_config {
    python_version = "3.10"
  }

  app_settings = {
    "AZURE_OPENAI_KEY"      = var.openai_key
    "AZURE_POSTGRESQL_CONN" = azurerm_postgresql_server.resume_db.connection_string
  }
}
