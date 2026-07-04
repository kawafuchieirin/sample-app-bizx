locals {
  # Origins allowed to call the API and redirect back from Cognito.
  frontend_url  = module.frontend.url
  cors_origins  = "http://localhost:5173,https://${module.frontend.cloudfront_domain}"
  callback_urls = ["http://localhost:5173/", local.frontend_url]
}

module "data" {
  source      = "../modules/data"
  project     = "bizx"
  environment = var.environment
}

module "frontend" {
  source      = "../modules/frontend"
  project     = "bizx"
  environment = var.environment
}

module "auth" {
  source        = "../modules/auth"
  project       = "bizx"
  environment   = var.environment
  domain_prefix = var.cognito_domain_prefix
  callback_urls = local.callback_urls
  logout_urls   = local.callback_urls
}

module "backend" {
  source               = "../modules/backend"
  project              = "bizx"
  environment          = var.environment
  image_tag            = var.backend_image_tag
  table_name           = module.data.table_name
  table_arn            = module.data.table_arn
  cognito_user_pool_id = module.auth.user_pool_id
  cognito_client_id    = module.auth.client_id
  cors_origins         = local.cors_origins
}

module "github_oidc" {
  source                      = "../modules/github-oidc"
  project                     = "bizx"
  environment                 = var.environment
  github_owner                = var.github_owner
  github_repo                 = var.github_repo
  create_oidc_provider        = var.create_oidc_provider
  ecr_repository_arn          = module.backend.ecr_repository_arn
  lambda_function_arn         = module.backend.lambda_function_arn
  s3_bucket_arn               = module.frontend.bucket_arn
  cloudfront_distribution_arn = module.frontend.distribution_arn
}
