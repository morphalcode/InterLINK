from website import create_app
from base64 import b64encode

app = create_app()
app.jinja_env.filters["encode_b64"] = lambda x: b64encode(x).decode("utf-8")
app.jinja_env.filters["format_date"] = lambda m, y: f"{y:04d}-{m:02d}"

if __name__ == "__main__":
    app.run(debug=True) 