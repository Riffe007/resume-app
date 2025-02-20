variable "db_password" {
  description = "The password for the PostgreSQL administrator."
  type        = string
  sensitive   = true
}

variable "openai_key" {
  description = "The API key for the Azure OpenAI service."
  type        = string
  sensitive   = true
}

# Optional: Default variables to customize resource names and location

variable "location" {
  description = "The Azure region to deploy resources."
  type        = string
  default     = "East US"
}

variable "resource_group_name" {
  description = "The name of the resource group."
  type        = string
  default     = "resume-ai-rg"
}

variable "postgresql_server_name" {
  description = "The name of the PostgreSQL server."
  type        = string
  default     = "resume-db"
}

variable "app_service_plan_name" {
  description = "The name of the App Service Plan for FastAPI."
  type        = string
  default     = "fastapi-app-plan"
}

variable "app_service_name" {
  description = "The name of the FastAPI App Service."
  type        = string
  default     = "fastapi-resume-app"
}

variable "cognitive_account_name" {
  description = "The name of the Cognitive Account for OpenAI."
  type        = string
  default     = "resume-openai"
}
