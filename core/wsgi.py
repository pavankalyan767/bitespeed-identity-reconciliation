import sys
print(">>> WSGI starting...", file=sys.stderr)

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

print(">>> WSGI app loaded", file=sys.stderr)