// Serves openapi.yaml as JSON at /openapi.json and a Swagger UI page at /docs.
import { Router } from "express";

const spec = Bun.YAML.parse(await Bun.file("openapi.yaml").text());

export const docsRouter = Router();

docsRouter.get("/openapi.json", (_req, res) => {
  res.json(spec);
});

docsRouter.get("/docs", (_req, res) => {
  res.type("html").send(`<!doctype html>
<html>
  <head>
    <title>Sessions API</title>
    <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5.17.14/swagger-ui.css">
  </head>
  <body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5.17.14/swagger-ui-bundle.js"></script>
    <script>SwaggerUIBundle({ url: "/openapi.json", dom_id: "#swagger-ui" });</script>
  </body>
</html>`);
});
