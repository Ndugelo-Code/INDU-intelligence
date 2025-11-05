import reflex as rx
from app.states.state import InduState


def uploaded_file_item(filename: str) -> rx.Component:
    return rx.el.div(
        rx.icon("file-check-2", class_name="h-5 w-5 text-green-500"),
        rx.el.span(filename, class_name="font-medium text-sm"),
        rx.el.span(
            "Ready for scan",
            class_name="text-xs text-green-600 bg-green-100 px-2 py-1 rounded-full ml-auto w-fit",
        ),
        class_name="flex items-center gap-3 p-3 bg-gray-50 rounded-lg border",
    )


def upload_view() -> rx.Component:
    return rx.el.main(
        rx.el.div(
            rx.el.h2(
                "Upload Project",
                class_name="text-3xl font-bold tracking-tight text-gray-900",
            ),
            rx.el.p(
                "Drag and drop a zip file of your project or individual files.",
                class_name="text-gray-500 mt-1",
            ),
            class_name="flex flex-col",
        ),
        rx.el.div(
            rx.upload.root(
                rx.el.div(
                    rx.icon("cloud-upload", class_name="w-12 h-12 stroke-gray-400"),
                    rx.el.p(
                        "Drag & drop files here, or click to select files",
                        class_name="text-gray-600 font-medium mt-4",
                    ),
                    rx.cond(
                        InduState.is_uploading,
                        rx.spinner(class_name="mt-4"),
                        rx.el.div(),
                    ),
                    class_name="flex flex-col items-center justify-center p-12 border-2 border-dashed border-gray-300 rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors",
                ),
                id="upload_project",
                multiple=True,
                accept={
                    "application/zip": [".zip"],
                    "text/python": [".py"],
                    "text/javascript": [".js", ".jsx"],
                    "text/typescript": [".ts", ".tsx"],
                },
                max_size=100000000,
                class_name="w-full cursor-pointer",
                disabled=InduState.is_uploading,
            ),
            rx.el.div(
                rx.cond(
                    rx.selected_files("upload_project").length() > 0,
                    rx.el.div(
                        rx.el.h3("Selected Files", class_name="font-semibold mb-2"),
                        rx.foreach(
                            rx.selected_files("upload_project"),
                            lambda file: rx.el.div(
                                file,
                                class_name="text-sm p-2 bg-white border rounded-md font-['JetBrains_Mono']",
                            ),
                        ),
                    ),
                    rx.el.div(),
                ),
                class_name="mt-4 space-y-2",
            ),
            rx.el.button(
                rx.cond(
                    InduState.is_uploading,
                    rx.el.div(
                        rx.spinner(class_name="text-white"),
                        "Uploading...",
                        class_name="flex items-center gap-2",
                    ),
                    rx.el.div(
                        rx.icon("cloud-upload", class_name="h-5 w-5"),
                        "Upload and Process",
                        class_name="flex items-center gap-2",
                    ),
                ),
                on_click=InduState.handle_upload(
                    rx.upload_files(upload_id="upload_project")
                ),
                disabled=InduState.is_uploading,
                class_name="mt-6 w-full justify-center bg-orange-500 text-white font-semibold py-3 px-4 rounded-lg shadow-sm hover:bg-orange-600 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed",
            ),
            class_name="mt-6 bg-white p-6 rounded-xl border border-gray-200 shadow-sm",
        ),
        rx.el.div(
            rx.cond(
                InduState.uploaded_files.length() > 0,
                rx.el.div(
                    rx.el.h3(
                        "Processed Files",
                        class_name="text-lg font-semibold text-gray-800 mb-4",
                    ),
                    rx.el.div(
                        rx.foreach(InduState.uploaded_files, uploaded_file_item),
                        class_name="flex flex-col gap-2",
                    ),
                    rx.el.button(
                        rx.icon("trash-2", class_name="mr-2 h-4 w-4"),
                        "Clear Uploads",
                        on_click=InduState.clear_upload,
                        class_name="mt-4 flex items-center bg-gray-200 text-gray-700 font-semibold py-2 px-4 rounded-lg hover:bg-gray-300 transition-colors text-sm",
                    ),
                ),
                rx.el.div(),
            ),
            class_name="mt-6 bg-white p-6 rounded-xl border border-gray-200 shadow-sm",
        ),
        class_name="flex-1 p-6",
    )