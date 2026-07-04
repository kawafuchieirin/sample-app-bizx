module "auth" {
  source = "../modules/auth"

  project       = "bizx"
  environment   = var.environment
  domain_prefix = var.cognito_domain_prefix
  callback_urls = var.callback_urls
  logout_urls   = var.logout_urls
}
