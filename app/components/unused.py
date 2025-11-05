import reflex as rx
from app.states.state import InduState


def unused_component_item(item: str) -> rx.Component:
    return rx.el.div(
        rx.icon("file-x", class_name="h-5 w-5 text-gray-400"),
        rx.el.span(item, class_name="font-['JetBrains_Mono'] text-sm"),
        class_name="flex items-center gap-3 p-3 bg-gray-50 rounded-lg border border-gray-200",
    )


def unused_view() -> rx.Component:
    return rx.el.main(
        rx.el.div(
            rx.el.div(
                rx.el.h2(
                    "Unused Components",
                    class_name="text-3xl font-bold tracking-tight text-gray-900",
                ),
                rx.el.p(
                    f"Found {InduState.filtered_unused_components.length()} unused Python files.",
                    class_name="text-gray-500 mt-1",
                ),
            ),
            rx.el.div(
                rx.el.div(
                    rx.icon("search", class_name="h-5 w-5 text-gray-400"),
                    rx.el.input(
                        placeholder="Search components...",
                        on_change=InduState.set_search_query.debounce(300),
                        default_value=InduState.search_query,
                        class_name="w-full bg-transparent focus:outline-none",
                    ),
                    class_name="flex items-center gap-3 w-full max-w-sm border rounded-lg px-3",
                ),
                rx.el.select(
                    rx.el.option("Filter by extension...", value=""),
                    rx.foreach(
                        InduState.unique_extensions,
                        lambda ext: rx.el.option(ext, value=ext),
                    ),
                    value=InduState.filter_extension,
                    on_change=InduState.set_filter_extension,
                    class_name="border rounded-lg px-3 py-2",
                ),
                rx.el.button(
                    "Clear",
                    on_click=InduState.clear_filters,
                    class_name="px-4 py-2 border rounded-lg hover:bg-gray-100",
                ),
                class_name="flex items-center gap-4",
            ),
            class_name="flex items-center justify-between",
        ),
        rx.el.div(
            rx.cond(
                InduState.filtered_unused_components.length() > 0,
                rx.el.div(
                    rx.foreach(
                        InduState.filtered_unused_components, unused_component_item
                    ),
                    class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3",
                ),
                rx.el.div(
                    rx.icon("thumbs-up", class_name="h-8 w-8 text-green-500 mx-auto"),
                    rx.el.p(
                        "No unused components found.",
                        class_name="text-center text-gray-600 font-medium mt-4",
                    ),
                    class_name="bg-green-50 p-8 rounded-lg border border-green-200",
                ),
            ),
            class_name="mt-6 bg-white p-6 rounded-xl border border-gray-200 shadow-sm",
        ),
        class_name="flex-1 p-6",
    )