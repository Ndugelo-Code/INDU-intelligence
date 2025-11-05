import reflex as rx
from app.components.sidebar import sidebar
from app.components.metrics import dashboard_view, initial_view
from app.components.file_browser import file_browser_view
from app.states.state import InduState
from app.components.dependencies import dependencies_view
from app.components.unused import unused_view


def main_content() -> rx.Component:
    return rx.cond(
        InduState.latest_snapshot,
        rx.match(
            InduState.active_page,
            ("Dashboard", dashboard_view()),
            ("Components", file_browser_view()),
            ("Dependencies", dependencies_view()),
            ("Unused", unused_view()),
            dashboard_view(),
        ),
        initial_view(),
    )


def index() -> rx.Component:
    return rx.el.div(
        sidebar(),
        main_content(),
        class_name="flex min-h-screen w-full bg-gray-50 font-['Inter']",
    )


app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;700&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(index)