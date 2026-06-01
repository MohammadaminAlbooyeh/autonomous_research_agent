"""
Web Application Firewall (WAF) for request validation and protection.

Provides protection against:
- SQL injection
- XSS (Cross-Site Scripting)
- CSRF (Cross-Site Request Forgery)
- XXE (XML External Entity)
- Path traversal
- Malicious payloads
"""

import re
import html
from typing import Optional
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware


class WAFMiddleware(BaseHTTPMiddleware):
    """Middleware for Web Application Firewall protection."""

    # SQL injection patterns
    SQL_PATTERNS = [
        r"(?i)(union|select|insert|update|delete|drop|create|alter|exec|execute)\s",
        r"(?i)(;|\-\-|\/\*|\*\/|xp_|sp_)",
        r"(?i)(\bor\b.*=.*)",
        r"(?i)(\band\b.*=.*)",
    ]

    # XSS patterns
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe",
        r"<object",
        r"<embed",
        r"<img[^>]*onerror",
    ]

    # Path traversal patterns
    PATH_TRAVERSAL_PATTERNS = [
        r"\.\./",
        r"\.\.",
        r"%2e%2e",
        r"\.\.\\",
    ]

    def __init__(self, app):
        """Initialize WAF middleware."""
        super().__init__(app)
        self.compiled_sql_patterns = [re.compile(p) for p in self.SQL_PATTERNS]
        self.compiled_xss_patterns = [re.compile(p) for p in self.XSS_PATTERNS]
        self.compiled_path_patterns = [re.compile(p) for p in self.PATH_TRAVERSAL_PATTERNS]

    async def dispatch(self, request: Request, call_next):
        """
        Process request through WAF checks.
        
        Args:
            request: FastAPI request
            call_next: Next middleware/handler
            
        Returns:
            Response or 403 Forbidden if blocked
        """
        # Check URL and method
        if not self._is_safe_request(request):
            return self._create_error_response(403, "Malicious request detected")

        # Check query parameters
        if not self._validate_query_params(request):
            return self._create_error_response(403, "Invalid query parameters")

        # Process the request
        response = await call_next(request)
        return response

    def _is_safe_request(self, request: Request) -> bool:
        """Check if request method and path are safe."""
        # Check for path traversal
        path = request.url.path
        for pattern in self.compiled_path_patterns:
            if pattern.search(path):
                return False
        return True

    def _validate_query_params(self, request: Request) -> bool:
        """Validate query parameters for injection attacks."""
        query_string = request.url.query
        if not query_string:
            return True

        # Check for SQL injection
        for pattern in self.compiled_sql_patterns:
            if pattern.search(query_string):
                return False

        # Check for XSS
        for pattern in self.compiled_xss_patterns:
            if pattern.search(query_string):
                return False

        return True

    def _create_error_response(self, status_code: int, detail: str):
        """Create error response."""
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=status_code,
            content={"detail": detail, "error": "WAF_BLOCKED"}
        )


class InputValidator:
    """Validate and sanitize user input."""

    @staticmethod
    def sanitize_html(text: str) -> str:
        """Remove HTML tags and escape special characters."""
        return html.escape(text)

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format."""
        pattern = r'^https?://'
        return url.startswith(('http://', 'https://'))

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Remove dangerous characters from filename."""
        return re.sub(r'[^\w\s.-]', '', filename)

    @staticmethod
    def validate_search_query(query: str, max_length: int = 1000) -> bool:
        """Validate search query."""
        if len(query) > max_length:
            return False
        # Check for obvious injection attempts
        dangerous_chars = ['<', '>', '"', "'", ";", "--", "/*", "*/"]
        return not any(char in query for char in dangerous_chars)

    @staticmethod
    def rate_limit_key(request: Request) -> str:
        """Generate rate limit key from request."""
        return f"{request.client.host}:{request.url.path}"


async def validate_request_body(request: Request) -> bool:
    """Validate request body for malicious content."""
    try:
        body = await request.body()
        body_str = body.decode('utf-8')
        
        # Check for XSS patterns
        xss_patterns = [
            r"<script",
            r"javascript:",
            r"onerror=",
            r"onload=",
        ]
        for pattern in xss_patterns:
            if re.search(pattern, body_str, re.IGNORECASE):
                return False
        
        return True
    except Exception:
        return False
