from jinja2 import Environment, FileSystemLoader
import os

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")


jinja_env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    autoescape=True,
)


def render_template(template_name: str, payload: dict):
    try:
        template = jinja_env.get_template(template_name)

        rendered_content = template.render(**payload)

        parts = rendered_content.split("\n", 1)

        if len(parts) != 2:
            subject = "Notification"
            body = parts[0].strip()
        else:
            subject = parts[0].strip()
            body = parts[1].strip()

        return subject, body

    except Exception as e:
        print(f"Error rendering template {template_name}: {e}")

        return "An Error Occurred", f"<p>Error rendering template: {e}</p>"
