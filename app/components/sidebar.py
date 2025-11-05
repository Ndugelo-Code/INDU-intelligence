import reflex as rx
from app.states.state import InduState


def nav_item(item: dict[str, str]) -> rx.Component:
    return rx.el.a(
        rx.icon(item["icon"], class_name="h-5 w-5"),
        rx.el.span(item["label"]),
        href=item["href"],
        on_click=lambda: InduState.set_active_page(item["label"]),
        class_name=rx.cond(
            InduState.active_page == item["label"],
            "flex items-center gap-3 rounded-lg bg-orange-100 px-3 py-2 text-orange-600 transition-all hover:text-orange-700 font-semibold",
            "flex items-center gap-3 rounded-lg px-3 py-2 text-gray-500 transition-all hover:text-gray-900",
        ),
    )


def sidebar() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.icon("scan-line", class_name="h-8 w-8 text-orange-600"),
                rx.el.h1(
                    "INDU",
                    class_name="font-['JetBrains_Mono'] text-2xl font-bold text-gray-800",
                ),
                class_name="flex items-center gap-2 font-semibold",
            ),
            class_name="flex h-16 items-center border-b px-6 shrink-0",
        ),
        rx.el.div(
            rx.el.nav(
                rx.foreach(InduState.nav_items, nav_item),
                class_name="flex flex-col gap-1 p-4",
            ),
            class_name="flex-1 overflow-auto",
        ),
        rx.el.div(
            rx.el.button(
                rx.cond(
                    InduState.is_scanning,
                    rx.el.div(
                        rx.spinner(class_name="text-white"),
                        "Scanning...",
                        class_name="flex items-center gap-2",
                    ),
                    rx.el.div(
                        rx.icon("play", class_name="h-5 w-5"),
                        "Run Scan",
                        class_name="flex items-center gap-2",
                    ),
                ),
                on_click=InduState.run_scan,
                disabled=InduState.is_scanning,
                class_name="w-full justify-center bg-orange-500 text-white font-semibold py-3 px-4 rounded-lg shadow-sm hover:bg-orange-600 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed",
                style={"boxShadow": "0px 1px 3px rgba(0,0,0,0.12)"},
            ),
            class_name="border-t p-4 mt-auto",
        ),
        class_name="hidden border-r bg-gray-50/50 md:flex md:flex-col md:w-64",
    )