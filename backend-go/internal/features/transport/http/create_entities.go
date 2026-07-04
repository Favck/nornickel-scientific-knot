package transport_http

import (
	"encoding/json"
	"net/http"

	core_logger "github.com/Favck/nornickel-scientific-knot/internal/core/logger"
	core_http_response "github.com/Favck/nornickel-scientific-knot/internal/core/transport/http/response"
)

func (h *HTTPHandler) CreateEntities(rw http.ResponseWriter, r *http.Request) {
	ctx := r.Context()
	log := core_logger.FromContext(ctx)
	responseHandler := core_http_response.NewHTTPResponse(log, rw)

	var request GraphPayloadDTO
	if err := json.NewDecoder(r.Body).Decode(&request); err != nil {
		responseHandler.ErrorResponse(err, "failed to decode HTTP request")
		return
	}

	payloadDomain := PayloadToDomain(request)

	if err := h.service.CreateEntities(ctx, payloadDomain); err != nil {
		responseHandler.ErrorResponse(err, "failed to create entities")
		return
	}

	responseHandler.JSONResponse(map[string]string{"status": "success"}, http.StatusCreated)
}
