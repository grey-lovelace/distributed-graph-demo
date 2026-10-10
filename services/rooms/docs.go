package main

import (
	"net/http"
	"os"

	"go.yaml.in/yaml/v3"
)

// registerDocsRoutes serves openapi.yaml as JSON at /openapi.json and a Swagger UI page at /docs.
func registerDocsRoutes(mux *http.ServeMux) error {
	bytes, err := os.ReadFile("openapi.yaml")
	if err != nil {
		return err
	}
	var spec map[string]any
	if err := yaml.Unmarshal(bytes, &spec); err != nil {
		return err
	}

	mux.HandleFunc("GET /openapi.json", func(w http.ResponseWriter, r *http.Request) {
		writeJSON(w, http.StatusOK, spec)
	})

	mux.HandleFunc("GET /docs", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "text/html")
		w.Write([]byte(swaggerPage))
	})
	return nil
}

const swaggerPage = `<!doctype html>
<html>
  <head>
    <title>Rooms API</title>
    <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5.17.14/swagger-ui.css">
  </head>
  <body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5.17.14/swagger-ui-bundle.js"></script>
    <script>SwaggerUIBundle({ url: "/openapi.json", dom_id: "#swagger-ui" });</script>
  </body>
</html>`
