import reflex as rx
from app.states.state import InduState


def metric_card(icon: str, title: str, value: rx.Var[str]) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(icon, class_name="h-6 w-6 text-gray-500"),
            class_name="p-3 bg-gray-100 rounded-lg w-fit",
        ),
        rx.el.div(
            rx.el.h3(title, class_name="text-sm font-medium text-gray-600"),
            rx.el.p(
                value,
                class_name="text-2xl font-bold text-gray-800 font-['JetBrains_Mono']",
            ),
            class_name="mt-2",
        ),
        class_name="bg-white p-6 rounded-xl border border-gray-200 shadow-sm",
        style={"boxShadow": "0px 1px 3px rgba(0,0,0,0.05)"},
    )


def file_type_chart() -> rx.Component:
    return rx.el.div(
        rx.el.h3("File Types", class_name="text-lg font-semibold text-gray-800 mb-4"),
        rx.recharts.bar_chart(
            rx.recharts.cartesian_grid(
                vertical=False, stroke_dasharray="3 3", class_name="stroke-gray-200"
            ),
            rx.recharts.graphing_tooltip(
                cursor={"fill": "rgba(251, 146, 60, 0.1)"},
                content_style={
                    "background": "#fff",
                    "border": "1px solid #eee",
                    "borderRadius": "8px",
                },
            ),
            rx.recharts.x_axis(data_key="name", class_name="text-xs"),
            rx.recharts.y_axis(class_name="text-xs"),
            rx.recharts.bar(data_key="count", fill="#fb923c", radius=[4, 4, 0, 0]),
            data=InduState.file_type_chart_data,
            height=300,
            class_name="font-sans",
        ),
        class_name="bg-white p-6 rounded-xl border border-gray-200 shadow-sm",
        style={"boxShadow": "0px 1px 3px rgba(0,0,0,0.05)"},
    )


def architecture_violations_view() -> rx.Component:
    return rx.el.div(
        rx.el.h3(
            "Architecture Violations",
            class_name="text-lg font-semibold text-gray-800 mb-4",
        ),
        rx.cond(
            InduState.architecture_violations.length() > 0,
            rx.el.div(
                rx.foreach(
                    InduState.architecture_violations,
                    lambda v: rx.el.div(
                        rx.icon(
                            "flag_triangle_right",
                            class_name="h-5 w-5 text-red-500 mr-3",
                        ),
                        rx.el.span(v, class_name="font-['JetBrains_Mono'] text-sm"),
                        class_name="flex items-center p-3 bg-red-50 rounded-lg",
                    ),
                ),
                class_name="flex flex-col gap-2",
            ),
            rx.el.div(
                rx.icon("square-check", class_name="h-6 w-6 text-green-500 mr-3"),
                rx.el.p(
                    "No architecture violations found.", class_name="text-gray-600"
                ),
                class_name="flex items-center justify-center p-8 bg-green-50 rounded-lg border border-green-200",
            ),
        ),
        class_name="bg-white p-6 rounded-xl border border-gray-200 shadow-sm",
        style={"boxShadow": "0px 1px 3px rgba(0,0,0,0.05)"},
    )


def dashboard_view() -> rx.Component:
    return rx.el.main(
        rx.el.div(
            rx.el.div(
                rx.el.h2(
                    "Dashboard",
                    class_name="text-3xl font-bold tracking-tight text-gray-900",
                ),
                rx.el.p(
                    InduState.scan_target_display,
                    class_name="text-sm text-gray-500 font-['JetBrains_Mono'] mt-1",
                ),
            ),
            class_name="flex items-center justify-between",
        ),
        rx.el.div(
            metric_card("files", "Total Files", InduState.total_files.to_string()),
            metric_card("database", "Total Size (MB)", InduState.total_size_mb),
            metric_card("code", "Total Lines of Code", InduState.total_lines_of_code),
            class_name="grid gap-6 md:grid-cols-3 mt-6",
        ),
        rx.el.div(file_type_chart(), class_name="mt-6"),
        rx.el.div(architecture_violations_view(), class_name="mt-6"),
        class_name="flex-1 p-6",
    )


def initial_view() -> rx.Component:
    return rx.el.main(
        rx.el.div(
            rx.icon("bar-chart-big", class_name="h-16 w-16 text-gray-300"),
            rx.el.h2(
                "INDU Intelligence Framework",
                class_name="mt-6 text-2xl font-semibold text-gray-800",
            ),
            rx.el.p(
                "Upload a project or run a scan on the local codebase.",
                class_name="mt-2 text-md text-gray-500",
            ),
            class_name="text-center flex flex-col items-center justify-center",
        ),
        class_name="flex-1 p-6 flex items-center justify-center",
    )