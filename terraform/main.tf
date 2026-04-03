variable "student_id" {
  type = string
}

provider "aws" {
  region = "us-east-1"
}

# 1. Create the Bucket
resource "aws_s3_bucket" "student_site" {
  bucket = "portfolio-${var.student_id}"
}

# 2. The Cost Protector: Auto-delete files and bucket after 90 days
resource "aws_s3_bucket_lifecycle_configuration" "cleanup" {
  bucket = aws_s3_bucket.student_site.id
  rule {
    id     = "auto-delete-90-days"
    status = "Enabled"
    expiration {
      days = 90
    }
  }
}

# 3. Configure as a Website
resource "aws_s3_bucket_website_configuration" "config" {
  bucket = aws_s3_bucket.student_site.id
  index_document { suffix = "index.html" }
}

# 4. Allow Public Access (so the internet can see the site)
resource "aws_s3_bucket_public_access_block" "public_access" {
  bucket                  = aws_s3_bucket.student_site.id
  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_policy" "allow_public_read" {
  bucket = aws_s3_bucket.student_site.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action    = "s3:GetObject"
        Effect    = "Allow"
        Resource  = "${aws_s3_bucket.student_site.arn}/*"
        Principal = "*"
      },
    ]
  })
  depends_on = [aws_s3_bucket_public_access_block.public_access]
}