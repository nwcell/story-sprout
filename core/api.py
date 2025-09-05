from typing import Any

from ninja import NinjaAPI
from ninja.openapi.schema import OpenAPISchema
from ninja.operation import Operation


class CustomOpenAPISchema(OpenAPISchema):
    def responses(self, operation: Operation) -> dict[int, dict[str, Any]]:
        """Add text/html content type to 200 responses that have JSON content."""
        # Get the default responses from parent
        result = super().responses(operation)

        # Add text/html content type to 200 responses that have JSON content
        if 200 in result and "content" in result[200]:
            content = result[200]["content"]
            # If there's JSON content, add HTML content alongside it
            if self.api.renderer.media_type in content:
                content["text/html"] = {
                    "schema": {
                        "type": "string",
                        "example": "<div>HTMX fragment</div>",
                    }
                }

        return result

    def operation_details(self, operation: Operation) -> dict[str, Any]:
        """Add HX-Request header parameter to all operations."""
        # Get the default operation details
        result = super().operation_details(operation)

        # Add HX-Request header parameter
        hx_param = {
            "name": "HX-Request",
            "in": "header",
            "required": False,
            "description": "HTMX flag; set to true to simulate an HTMX request.",
            "schema": {"type": "boolean"},
        }

        params = result.setdefault("parameters", [])
        if not any(p.get("name") == "HX-Request" and p.get("in") == "header" for p in params):
            params.append(hx_param)

        return result


class CustomNinjaAPI(NinjaAPI):
    """Custom Ninja API class to add HX-Request header to all operations."""

    def get_openapi_schema(
        self,
        *,
        path_prefix: str | None = None,
        path_params: dict[str, Any] | None = None,
    ) -> OpenAPISchema:
        if path_prefix is None:
            path_prefix = self.get_root_path(path_params or {})
        return CustomOpenAPISchema(api=self, path_prefix=path_prefix)


api = CustomNinjaAPI(title="Story Sprout API", version="1")


api.add_router("/ai/", "apps.ai.api.router", tags=["ai"])
api.add_router("/stories/", "apps.stories.api.router", tags=["stories"])
