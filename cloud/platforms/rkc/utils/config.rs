use config::Config;
use dotenvy::dotenv;

#[derive(Debug, Clone, serde_derive::Deserialize, PartialEq)]
pub struct AppConfig {
    pub debug: bool,
    pub kafka_server: String,
    pub kafka_topics: Vec<String>,
    pub kafka_group: String,
    pub environment: String,
    pub kafka_password: String,
    pub kafka_ca_file_path: String,
    pub kafka_key_file_path: String,
    pub kafka_cert_file_path: String,
    pub sentry_dsn: String,
    pub sentry_trace_sample_rate: f32,
    pub sibel_version: String,
    pub vitals_export_enabled: bool,
    pub vitals_export_workers: usize,
    pub vitals_flush_endpoint: String,
    pub vitals_flush_timeout_seconds: u64,
}

impl Default for AppConfig {
    fn default() -> Self {
        // Read .env
        dotenv().ok();

        let config = Config::builder()
            .add_source(
                config::Environment::default()
                    .try_parsing(true)
                    .list_separator(",")
                    .with_list_parse_key("kafka_topics"),
            )
            .set_default("debug", "false")
            .unwrap()
            .set_default("sentry_trace_sample_rate", 0.1)
            .unwrap()
            .set_default("vitals_export_enabled", true)
            .unwrap()
            .set_default("vitals_export_workers", 2)
            .unwrap()
            .build()
            .expect("Failed to read config source");

        let app_config: AppConfig = config.try_deserialize().unwrap();

        app_config
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use test_case::test_case;

    #[test]
    fn parse_config_expected_defaults() {
        // only setting mandatory envs and removing envs with default values
        temp_env::with_vars(
            [
                ("KAFKA_SERVER", Some("kafka-server")),
                ("KAFKA_TOPICS", Some("topic1,topic2,topic3")),
                ("KAFKA_GROUP", Some("kafka-group")),
                ("KAFKA_PASSWORD", Some("kafka-password")),
                ("KAFKA_CA_FILE_PATH", Some("kafka-ca-file-path")),
                ("KAFKA_KEY_FILE_PATH", Some("kafka-key-file-path")),
                ("KAFKA_CERT_FILE_PATH", Some("kafka-cert-file-path")),
                ("ENVIRONMENT", Some("environment")),
                ("SENTRY_DSN", Some("sentry_domain")),
                ("SIBEL_VERSION", Some("version")),
                // Ensure default have no value
                ("DEBUG", None),
                ("SENTRY_TRACE_SAMPLE_RATE", None),
                ("VITALS_EXPORT_ENABLED", None),
                ("VITALS_FLUSH_ENDPOINT", Some("http://mirth-endpoint.com")),
                ("VITALS_FLUSH_TIMEOUT_SECONDS", Some("15")),
            ],
            || {
                let result = AppConfig::default();

                // Mandatory
                assert_eq!(result.kafka_server, "kafka-server");
                assert_eq!(result.kafka_group, "kafka-group");
                assert_eq!(result.kafka_topics, vec!["topic1", "topic2", "topic3"]);
                assert_eq!(result.kafka_password, "kafka-password");
                assert_eq!(result.kafka_ca_file_path, "kafka-ca-file-path");
                assert_eq!(result.kafka_key_file_path, "kafka-key-file-path");
                assert_eq!(result.kafka_cert_file_path, "kafka-cert-file-path");
                assert_eq!(result.environment, "environment");
                assert_eq!(result.sentry_dsn, "sentry_domain");
                assert_eq!(result.sibel_version, "version");
                assert_eq!(result.vitals_flush_endpoint, "http://mirth-endpoint.com");
                assert_eq!(result.vitals_flush_timeout_seconds, 15);

                // Defaults
                assert_eq!(result.sentry_trace_sample_rate, 0.1);
                assert!(!result.debug);
                assert!(result.vitals_export_enabled);
                assert_eq!(result.vitals_export_workers, 2);
            },
        );
    }

    #[test]
    fn parse_config() {
        // only setting mandatory envs and removing envs with default values
        temp_env::with_vars(
            [
                ("KAFKA_SERVER", Some("kafka-server")),
                ("KAFKA_TOPICS", Some("topic1, topic2, topic3")),
                ("KAFKA_GROUP", Some("kafka-group")),
                ("KAFKA_PASSWORD", Some("kafka-password")),
                ("KAFKA_CA_FILE_PATH", Some("kafka-ca-file-path")),
                ("KAFKA_KEY_FILE_PATH", Some("kafka-key-file-path")),
                ("KAFKA_CERT_FILE_PATH", Some("kafka-cert-file-path")),
                ("ENVIRONMENT", Some("environment")),
                ("SENTRY_DSN", Some("sentry_domain")),
                ("SIBEL_VERSION", Some("version")),
                // Ensure default have some value
                ("DEBUG", Some("true")),
                ("SENTRY_TRACE_SAMPLE_RATE", Some("0.2")),
                ("VITALS_EXPORT_ENABLED", Some("true")),
                ("VITALS_EXPORT_WORKERS", Some("20")),
                ("VITALS_FLUSH_ENDPOINT", Some("http://mirth-endpoint.com")),
                ("VITALS_FLUSH_TIMEOUT_SECONDS", Some("15")),
            ],
            || {
                let result = AppConfig::default();

                assert_eq!(result.sentry_trace_sample_rate, 0.2);
                assert!(result.debug);
                assert!(result.vitals_export_enabled);
                assert_eq!(result.vitals_export_workers, 20);
            },
        );
    }

    #[test_case("topic1", vec!["topic1"] ; "Single topic value")]
    #[test_case("topic1,topic2,topic3", vec!["topic1", "topic2", "topic3"] ; "Multiple topic value")]
    fn parse_config_list_values(kafka_topics: &str, expected_value: Vec<&str>) {
        // only setting mandatory envs and removing envs with default values
        temp_env::with_vars(
            [
                ("KAFKA_SERVER", Some("kafka-server")),
                ("KAFKA_GROUP", Some("kafka-group")),
                ("KAFKA_PASSWORD", Some("kafka-password")),
                ("KAFKA_CA_FILE_PATH", Some("kafka-ca-file-path")),
                ("KAFKA_KEY_FILE_PATH", Some("kafka-key-file-path")),
                ("KAFKA_CERT_FILE_PATH", Some("kafka-cert-file-path")),
                ("ENVIRONMENT", Some("environment")),
                ("SENTRY_DSN", Some("sentry_domain")),
                ("SIBEL_VERSION", Some("version")),
                ("KAFKA_TOPICS", Some(kafka_topics)),
                ("VITALS_FLUSH_ENDPOINT", Some("http://mirth-endpoint.com")),
                ("VITALS_FLUSH_TIMEOUT_SECONDS", Some("15")),
            ],
            || {
                let result = AppConfig::default();

                assert_eq!(result.kafka_topics, expected_value);
            },
        );
    }

    #[test_case("true", true ; "lowercase true as value")]
    #[test_case("TRUE", true ; "uppercase TRUE as value")]
    #[test_case("True", true ; "capitalized True as value")]
    #[test_case("1", true ; "1 as value")]
    #[test_case("false", false ; "lowercase false as value")]
    #[test_case("FALSE", false ; "uppercase FALSE as value")]
    #[test_case("False", false ; "capitalized False as value")]
    #[test_case("0", false ; "0 as value")]
    fn parse_config_flag_values(flag_value: &str, expected_value: bool) {
        // only setting mandatory envs and removing envs with default values
        temp_env::with_vars(
            [
                ("KAFKA_SERVER", Some("kafka-server")),
                ("KAFKA_GROUP", Some("kafka-group")),
                ("KAFKA_PASSWORD", Some("kafka-password")),
                ("KAFKA_CA_FILE_PATH", Some("kafka-ca-file-path")),
                ("KAFKA_KEY_FILE_PATH", Some("kafka-key-file-path")),
                ("KAFKA_CERT_FILE_PATH", Some("kafka-cert-file-path")),
                ("ENVIRONMENT", Some("environment")),
                ("SENTRY_DSN", Some("sentry_domain")),
                ("SIBEL_VERSION", Some("version")),
                // set flag values
                ("DEBUG", Some(flag_value)),
                ("VITALS_EXPORT_ENABLED", Some(flag_value)),
                ("VITALS_FLUSH_ENDPOINT", Some("http://mirth-endpoint.com")),
                ("VITALS_FLUSH_TIMEOUT_SECONDS", Some("15")),
            ],
            || {
                let result = AppConfig::default();

                assert_eq!(result.debug, expected_value);
                assert_eq!(result.vitals_export_enabled, expected_value);
            },
        );
    }
}
