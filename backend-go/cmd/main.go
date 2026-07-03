package main

import (
	"context"
	"fmt"
	"os"
	"os/signal"
	"syscall"
	"time"

	core_config "github.com/Favck/nornickel-scientific-knot/internal/core/config"
	core_logger "github.com/Favck/nornickel-scientific-knot/internal/core/logger"
	core_repository "github.com/Favck/nornickel-scientific-knot/internal/core/repository"
	core_http_middleware "github.com/Favck/nornickel-scientific-knot/internal/core/transport/http/middleware"
	core_http_server "github.com/Favck/nornickel-scientific-knot/internal/core/transport/http/server"
	neo4j_repository "github.com/Favck/nornickel-scientific-knot/internal/features/repository/Neo4j"
	"github.com/Favck/nornickel-scientific-knot/internal/features/service"
	transport_http "github.com/Favck/nornickel-scientific-knot/internal/features/transport/http"
	"go.uber.org/zap"
)

func main() {
	cfg := core_config.NewConfigMust()
	time.Local = cfg.TimeZone
	ctx, cancel := signal.NotifyContext(
		context.Background(),
		syscall.SIGINT, syscall.SIGTERM,
	)
	defer cancel()

	logger, err := core_logger.NewLogger(core_logger.NewConfigMust())
	if err != nil {
		fmt.Println("Failed to init application logger: ", err)
		os.Exit(1)
	}
	defer logger.Close()

	logger.Debug("application time zone", zap.Any("zone", time.Local))

	logger.Debug("initializing neo4j connection driver")

	neo4jConfig := core_repository.NewConfigMust()
	neo4jDriver, err := core_repository.NewClient(ctx, neo4jConfig)
	if err != nil {
		logger.Fatal("failed to init neo4j client", zap.Error(err))
	}
	defer neo4jDriver.Close(ctx)

	logger.Debug("initializing feature", zap.String("feature", "etities"))
	repo := neo4j_repository.NewRepository(neo4jDriver)
	svc := service.NewService(repo)
	httpHandler := transport_http.NewHTTPHandler(svc)

	v1Router := core_http_server.NewAPIVersionRouter(core_http_server.ApiVersion1)
	v1Router.RegisterRoutes(httpHandler.Routes()...)

	logger.Debug("initializing HTTP Server")
	httpCfg := core_http_server.NewConfigMust()
	httpServer := core_http_server.NewHTTPServer(
		httpCfg,
		logger,
		core_http_middleware.RequestID(),
		core_http_middleware.Logger(logger),
		core_http_middleware.Trace(),
		core_http_middleware.Panic(),
	)

	httpServer.RegisterAPIRouters(v1Router)

	if err := httpServer.Run(ctx); err != nil {
		logger.Fatal("server stopped with error", zap.Error(err))
	}

}
