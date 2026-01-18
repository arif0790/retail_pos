# ------------------------------------------------------------------
#  src/__init__.py
# ------------------------------------------------------------------
"""
POS Application package – top‑level ``__init__``.

The file has two main responsibilities:

1. **Expose sub‑modules** so that users can write  
   ``import posapp`` (or ``from posapp import …``) and immediately have access to the core building blocks of your application.
2. **Provide a tiny convenience routine** (`main`) that lets you run the whole stack from the command line or from a unit‑test harness.

The structure is intentionally lightweight:  
   * Import statements keep the namespace clean.  
   * ``__all__`` lists the public symbols that should be re‑exported.  
   * A small logger‑based demo function (`main`) demonstrates how to bootstrap the application.
"""

# ------------------------------------------------------------------
#  Public imports – bring everything into the package namespace
# ------------------------------------------------------------------
from .models import User, Order, Product          # data‑model classes
from .views  import render_dashboard, display_report  # view helpers
from .utils   import db_connect, get_logger           # util helpers

# ------------------------------------------------------------------
#  Re‑export public symbols so ``import posapp`` brings them in
# ------------------------------------------------------------------
__all__ = [
    'app',
    'models',
    'views',
    'utils'
]

# ------------------------------------------------------------------
#  Optional package metadata – useful for packaging / CI
# ------------------------------------------------------------------
__version__ = "0.1.0"

# ------------------------------------------------------------------
#  Convenience entry point – runs the demo view from CLI
# ------------------------------------------------------------------
def main() -> None:
    """
    Simple entry‑point that can be invoked as

        $ python -m posapp

    It logs a short start‑message and calls the default dashboard
    rendering routine.

    The function is intentionally tiny; all heavy lifting stays inside
    ``views.render_dashboard`` which you will implement in *src/views.py*.
    """

    get_logger().info(f"POS‑Application {__version__} started.")
    render_dashboard()

# ------------------------------------------------------------------
#  Allow ``python -m posapp`` to work out of the box
# ------------------------------------------------------------------
if __name__ == "__main__":
    main()
