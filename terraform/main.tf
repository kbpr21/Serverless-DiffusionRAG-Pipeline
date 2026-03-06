# 1. Resource Group
resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
}

# 2. Azure Container Registry (ACR)
resource "azurerm_container_registry" "acr" {
  name                = var.acr_name
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "Basic"
  admin_enabled       = true # Required for ACA to pull images using admin creds
}

# 3. Azure Container Apps Environment
# We use a basic Log Analytics Workspace for the ACA env (often required/recommended)
resource "azurerm_log_analytics_workspace" "law" {
  name                = "law-${var.aca_env_name}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

resource "azurerm_container_app_environment" "env" {
  name                       = var.aca_env_name
  location                   = azurerm_resource_group.main.location
  resource_group_name        = azurerm_resource_group.main.name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.law.id
}

# 4. Azure Container App
resource "azurerm_container_app" "app" {
  name                         = var.aca_app_name
  container_app_environment_id = azurerm_container_app_environment.env.id
  resource_group_name          = azurerm_resource_group.main.name
  revision_mode                = "Single"

  # Define the ACR registry credentials so the app can pull the image
  registry {
    server               = azurerm_container_registry.acr.login_server
    username             = azurerm_container_registry.acr.admin_username
    password_secret_name = "acr-password"
  }

  secret {
    name  = "acr-password"
    value = azurerm_container_registry.acr.admin_password
  }

  # We feed the Mercury API key into a secret so it can be used cleanly as an env var
  secret {
    name  = "mercury-api-key"
    value = "placeholder" # We leave it placeholder in code, but CI/CD will populate. 
    # Alternatively, since we don't want to check in secrets, we define a dummy value to allow TF to build.
    # NOTE: To be truly "Infrastructure as Code", we should pass this via an env var (TF_VAR_mercury_api_key).
  }

  ingress {
    allow_insecure_connections = false
    external_enabled           = true
    target_port                = 8000
    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }

  template {
    container {
      name   = "api"
      image  = "mcr.microsoft.com/azuredocs/containerapps-helloworld:latest" # Placeholder image until CI/CD overwrites
      cpu    = 0.5
      memory = "1.0Gi"

      env {
        name        = "MERCURY_API_KEY"
        secret_name = "mercury-api-key"
      }
    }

    # ZERO-COST SCALE CONFIGURATION (Must be 0-1)
    min_replicas = 0
    max_replicas = 1
  }

  # Make terraform ignore subsequent changes to the image and secrets that occur via CI/CD
  lifecycle {
    ignore_changes = [
      template[0].container[0].image,
      secret,
    ]
  }
}
