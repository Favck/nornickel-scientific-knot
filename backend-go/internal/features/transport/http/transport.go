package transport_http

import (
	"context"
	"net/http"

	"github.com/Favck/nornickel-scientific-knot/internal/core/domain"
	core_http_server "github.com/Favck/nornickel-scientific-knot/internal/core/transport/http/server"
)

type HTTPHandler struct {
	service Service
}

type Service interface {
	CreateEntities(
		ctx context.Context,
		payload domain.GraphPayload,
	) error
}

func NewHTTPHandler(
	service Service,
) *HTTPHandler {
	return &HTTPHandler{
		service: service,
	}
}

func (h *HTTPHandler) Routes() []core_http_server.Route {
	return []core_http_server.Route{
		{
			Method:  http.MethodPost,
			Path:    "/entities",
			Handler: h.CreateEntities,
		},
	}
}
