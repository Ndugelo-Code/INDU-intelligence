import reflex as rx
from app.states.state import InduState
import plotly.graph_objects as go


def dependencies_view() -> rx.Component:
    return rx.el.main(
        rx.el.div(
            rx.el.h2(
                "Dependencies",
                class_name="text-3xl font-bold tracking-tight text-gray-900",
            ),
            class_name="flex items-center justify-between",
        ),
        rx.el.div(
            rx.plotly(data=InduState.dependency_figure, layout={"height": "800"}),
            class_name="mt-6 bg-white p-6 rounded-xl border border-gray-200 shadow-sm",
        ),
        class_name="flex-1 p-6",
    )