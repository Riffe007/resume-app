output "resource_group_name" {
  description = "The name of the Azure Resource Group."
  value       = azurerm_resource_group.resume_ai.name
}

output "app_service_default_hostname" {
  description = "The default hostname of the FastAPI App Service."
  value       = azurerm_app_service.fastapi_app.default_site_hostname
}

output "postgresql_connection_string" {
  description = "The connection string for the PostgreSQL server."
  value       = azurerm_postgresql_server.resume_db.connection_string
}

output "cognitive_account_endpoint" {
  description = "The endpoint for the Azure Cognitive (OpenAI) account."
  value       = azurerm_cognitive_account.openai.endpoint
}
