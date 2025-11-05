import reflex as rx
from app.states.state import InduState


def folder_item(item: dict) -> rx.Component:
    return rx.el.div(
        rx.icon("folder", class_name="h-5 w-5 text-orange-500"),
        rx.el.span(item["name"], class_name="font-medium"),
        rx.el.span(
            f"{item['file_count']} files",
            class_name="text-sm text-gray-500 ml-auto font-['JetBrains_Mono']",
        ),
        class_name="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-100 cursor-pointer",
        on_click=lambda: InduState.add_to_path(item["name"]),
    )


def file_item(item: dict) -> rx.Component:
    return rx.el.div(
        rx.icon("file", class_name="h-5 w-5 text-gray-400"),
        rx.el.span(item["name"], class_name=""),
        rx.el.span(
            f"{item['lines_of_code']} LOC",
            class_name="text-sm text-gray-500 ml-auto font-['JetBrains_Mono']",
        ),
        class_name="flex items-center gap-3 p-2 rounded-lg",
    )


def breadcrumb_item(item: tuple[str, int]) -> rx.Component:
    return rx.el.div(
        rx.el.span(
            item[0],
            on_click=lambda: InduState.set_path_to_index(item[1]),
            class_name="cursor-pointer hover:underline",
        ),
        rx.el.span("/", class_name="mx-2 text-gray-400"),
    )


def file_browser_view() -> rx.Component:
    return rx.el.main(
        rx.el.div(
            rx.el.h2(
                "Components",
                class_name="text-3xl font-bold tracking-tight text-gray-900",
            ),
            class_name="flex items-center justify-between",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.span(
                    "Root",
                    on_click=lambda: InduState.set_path_to_index(-1),
                    class_name="cursor-pointer hover:underline",
                ),
                rx.el.span("/", class_name="mx-2 text-gray-400"),
                rx.foreach(InduState.current_path_with_indices, breadcrumb_item),
                class_name="flex items-center text-sm font-medium text-gray-500",
            ),
            rx.el.div(
                rx.foreach(InduState.current_view["folders"], folder_item),
                rx.foreach(InduState.current_view["files"], file_item),
                class_name="mt-4 flex flex-col gap-1",
            ),
            class_name="mt-6 bg-white p-6 rounded-xl border border-gray-200 shadow-sm",
        ),
        class_name="flex-1 p-6",
    )