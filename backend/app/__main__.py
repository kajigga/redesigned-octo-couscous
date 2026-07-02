from . import create_app
from .config import Config

app = create_app()
app.run(port=Config.PORT, debug=True)
