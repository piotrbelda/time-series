variable "credentials" {
  default     = "./keys/time-series-creds.json"
  description = "My Credentials"
}

variable "bq_dataset_name" {
  default     = "time_series_test_dataset"
  description = "My BigQuery Dataset Name"
}

variable "gcs_bucket_name" {
  default     = "time_series_test_bucket"
  description = "My Storage Bucket Name"
}

variable "gcs_storage_class" {
  description = "Bucket Storage Class"
  default     = "STANDARD"
}

variable "location" {
  default     = "EU"
  description = "Project Location"
}

variable "project" {
  default     = "time-series-pb"
  description = "Project Name"
}

variable "region" {
  default     = "europe-central2-a"
  description = "Region"
}
