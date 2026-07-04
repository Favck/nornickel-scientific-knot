package transport_http

import (
	"encoding/json"
	"net/http"

	core_logger "github.com/Favck/nornickel-scientific-knot/internal/core/logger"
	core_http_response "github.com/Favck/nornickel-scientific-knot/internal/core/transport/http/response"
)

func (h *HTTPHandler) GetSubgraph(rw http.ResponseWriter, r *http.Request) {
	ctx := r.Context()
	log := core_logger.FromContext(ctx)
	responseHandler := core_http_response.NewHTTPResponse(log, rw)

	var request SearchRequestDTO
	if err := json.NewDecoder(r.Body).Decode(&request); err != nil {
		responseHandler.ErrorResponse(err, "failed to get subgraph")
		return
	}

	queryVector, filters := request.ToDomain()

	pyvisGraph, err := h.service.GetSubgraph(ctx, queryVector, filters)
	if err != nil {
		responseHandler.ErrorResponse(err, "failed to get subgraph")
		return
	}

	response := DomainToPyvisGraphDTO(pyvisGraph)

	responseHandler.JSONResponse(response, http.StatusOK)
}
