package core_repository

import (
	"fmt"

	"github.com/kelseyhightower/envconfig"
)

type Config struct {
	URI      string `envconfig:"URI" required:"true"`
	User     string `envconfig:"USER" required:"true"`
	Password string `envconfig:"PASSWORD" required:"true"`
}

func NewConfig() (Config, error) {
	var config Config
	if err := envconfig.Process("NEO4J", &config); err != nil {
		return Config{}, fmt.Errorf("process envconfig: %w", err)
	}
	return config, nil
}

func NewConfigMust() Config {
	config, err := NewConfig()
	if err != nil {
		panic(fmt.Errorf("get Neo4j config: %w", err))
	}
	return config
}
