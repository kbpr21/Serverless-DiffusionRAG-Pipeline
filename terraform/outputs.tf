output "resource_group_name" {
  description = "The name of the resource group"
  value       = azurerm_resource_group.main.name
}

output "acr_login_server" {
  description = "The URL of the Azure Container Registry"
  value       = azurerm_container_registry.acr.login_server
}

output "aca_fqdn" {
  description = "The Fully Qualified Domain Name of the Container App"
  value       = azurerm_container_app.app.latest_revision_fqdn
}
