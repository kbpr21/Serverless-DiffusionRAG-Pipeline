variable "location" {
  type        = string
  description = "Azure region where resources will be deployed"
  default     = "centralindia"
}

variable "resource_group_name" {
  type        = string
  description = "Name of the resource group"
  default     = "rg-diffusionrag-pipeline"
}

variable "acr_name" {
  type        = string
  description = "Name of the Azure Container Registry (must be globally unique)"
  default     = "acrdiffusionrag"
}

variable "aca_env_name" {
  type        = string
  description = "Name of the Azure Container Apps Environment"
  default     = "aca-env-diffusionrag"
}

variable "aca_app_name" {
  type        = string
  description = "Name of the Azure Container App"
  default     = "aca-diffusionrag"
}
