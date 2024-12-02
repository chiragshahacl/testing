locals {

  dns_zone = var.env == "prod" ? "tucana.sibel.health" : "${var.env}.tucana.sibel.health"

}

resource "aws_route53_zone" "dev" {
  name = local.dns_zone
}
