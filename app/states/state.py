import reflex as rx
import os
import reflex as rx
import os
import time
import logging
import re
import ast
from typing import TypedDict, Any, Union
import plotly.graph_objects as go
import zipfile
import tempfile
import shutil


class FileMetrics(TypedDict):
    path: str
    size: int
    lines_of_code: int
    extension: str


class FolderMetrics(TypedDict):
    path: str
    total_files: int
    total_size: int
    file_types: dict[str, int]


class ComponentNode(TypedDict):
    id: str
    type: str


class DependencyEdge(TypedDict):
    source: str
    target: str


class Snapshot(TypedDict):
    timestamp: float
    total_files: int
    total_size: int
    total_lines_of_code: int
    files: list[FileMetrics]
    folders: dict[str, FolderMetrics]
    file_type_distribution: dict[str, int]
    dependency_graph: dict[str, list[str]]
    architecture_violations: list[str]
    unused_components: list[str]


class FileNode(TypedDict):
    name: str
    lines_of_code: int


class FolderNode(TypedDict):
    name: str
    folders: list["FolderNode"]
    files: list[FileNode]
    file_count: int


class InduState(rx.State):
    scan_path: str = "."
    is_scanning: bool = False
    latest_snapshot: Snapshot | None = None
    scan_history: list[Snapshot] = []
    nav_items: list[dict[str, str]] = [
        {"label": "Upload", "icon": "upload", "href": "#"},
        {"label": "Dashboard", "icon": "layout-dashboard", "href": "/"},
        {"label": "Components", "icon": "component", "href": "#"},
        {"label": "Dependencies", "icon": "file-json-2", "href": "#"},
        {"label": "Unused", "icon": "trash-2", "href": "#"},
    ]
    active_page: str = "Upload"
    file_tree: FolderNode = {
        "name": "root",
        "folders": [],
        "files": [],
        "file_count": 0,
    }
    current_path: list[str] = []
    search_query: str = ""
    filter_extension: str = ""
    uploaded_files: list[str] = []
    is_uploading: bool = False
    uploaded_project_name: str | None = None
    uploaded_project_path: str | None = None
    uploaded_files: list[str] = []
    is_uploading: bool = False
    uploaded_project_name: str | None = None
    uploaded_project_path: str | None = None

    @rx.event
    def set_active_page(self, page: str):
        self.active_page = page

    @rx.event
    def add_to_path(self, folder_name: str):
        self.current_path.append(folder_name)

    @rx.event
    def set_path_to_index(self, index: int):
        if index == -1:
            self.current_path = []
        else:
            self.current_path = self.current_path[: index + 1]

    @rx.event
    def set_search_query(self, query: str):
        self.search_query = query

    @rx.event
    def set_filter_extension(self, extension: str):
        self.filter_extension = extension

    @rx.event
    def clear_filters(self):
        self.search_query = ""
        self.filter_extension = ""

    @rx.var
    def current_view(self) -> FolderNode:
        if not self.file_tree:
            return {"name": "root", "folders": [], "files": [], "file_count": 0}
        view = self.file_tree
        for part in self.current_path:
            found = False
            for folder in view["folders"]:
                if folder["name"] == part:
                    view = folder
                    found = True
                    break
            if not found:
                return {"name": "root", "folders": [], "files": [], "file_count": 0}
        return view

    @rx.var
    def current_path_with_indices(self) -> list[tuple[str, int]]:
        return [(part, i) for i, part in enumerate(self.current_path)]

    @rx.var
    def total_files(self) -> int:
        return self.latest_snapshot["total_files"] if self.latest_snapshot else 0

    @rx.var
    def total_size_mb(self) -> str:
        if not self.latest_snapshot:
            return "0.00"
        return f"{self.latest_snapshot['total_size'] / (1024 * 1024):.2f}"

    @rx.var
    def total_lines_of_code(self) -> str:
        if not self.latest_snapshot:
            return "0"
        return f"{self.latest_snapshot['total_lines_of_code']:,}"

    @rx.var
    def file_type_chart_data(self) -> list[dict[str, Union[str, int]]]:
        if not self.latest_snapshot:
            return []
        dist = self.latest_snapshot.get("file_type_distribution", {})
        sorted_dist = sorted(dist.items(), key=lambda item: item[1], reverse=True)[:10]
        return [
            {"name": ext if ext else "Other", "count": count}
            for ext, count in sorted_dist
        ]

    @rx.var
    def dependency_graph_data(
        self,
    ) -> dict[str, list[Union[ComponentNode, DependencyEdge]]]:
        if not self.latest_snapshot or "dependency_graph" not in self.latest_snapshot:
            return {"nodes": [], "edges": []}
        graph = self.latest_snapshot["dependency_graph"]
        nodes = {node for node in graph.keys()}
        edges_set = set()
        for source, targets in graph.items():
            nodes.add(source)
            for target in targets:
                nodes.add(target)
                edges_set.add((source, target))
        node_list = [
            ComponentNode(id=node, type="file") for node in sorted(list(nodes))
        ]
        edge_list = [
            DependencyEdge(source=s, target=t) for s, t in sorted(list(edges_set))
        ]
        return {"nodes": node_list, "edges": edge_list}

    @rx.var
    def architecture_violations(self) -> list[str]:
        if not self.latest_snapshot:
            return []
        return self.latest_snapshot.get("architecture_violations", [])

    @rx.var
    def unused_components(self) -> list[str]:
        if not self.latest_snapshot:
            return []
        return self.latest_snapshot.get("unused_components", [])

    @rx.var
    def unique_extensions(self) -> list[str]:
        if not self.latest_snapshot:
            return []
        unused = self.latest_snapshot.get("unused_components", [])
        extensions = {os.path.splitext(f)[1] for f in unused if os.path.splitext(f)[1]}
        return sorted(list(extensions))

    @rx.var
    def filtered_unused_components(self) -> list[str]:
        unused = self.unused_components
        if self.search_query:
            unused = [u for u in unused if self.search_query.lower() in u.lower()]
        if self.filter_extension:
            unused = [u for u in unused if u.endswith(self.filter_extension)]
        return unused

    @rx.var
    def scan_target_display(self) -> str:
        if self.uploaded_project_name:
            return f"Uploaded: {self.uploaded_project_name}"
        return "Local Project"

    @rx.var
    def dependency_figure(self) -> go.Figure:
        if not self.latest_snapshot or "dependency_graph" not in self.latest_snapshot:
            return go.Figure()
        graph = self.latest_snapshot["dependency_graph"]
        all_nodes = sorted(
            list(set(graph.keys()) | {dep for deps in graph.values() for dep in deps})
        )
        node_map = {name: i for i, name in enumerate(all_nodes)}
        edge_x = []
        edge_y = []
        for source, deps in graph.items():
            for target in deps:
                if source in node_map and target in node_map:
                    x0, y0 = (node_map[source] % 10, node_map[source] // 10)
                    x1, y1 = (node_map[target] % 10, node_map[target] // 10)
                    edge_x.extend([x0, x1, None])
                    edge_y.extend([y0, y1, None])
        node_x = [node_map[name] % 10 for name in all_nodes]
        node_y = [node_map[name] // 10 for name in all_nodes]
        edge_trace = go.Scatter(
            x=edge_x,
            y=edge_y,
            line=dict(width=0.5, color="#888"),
            hoverinfo="none",
            mode="lines",
        )
        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text",
            hoverinfo="text",
            text=all_nodes,
            textposition="bottom center",
            marker=dict(showscale=False, color="#fb923c", size=10, line_width=2),
        )
        fig = go.Figure(
            data=[edge_trace, node_trace],
            layout=go.Layout(
                showlegend=False,
                hovermode="closest",
                margin=dict(b=20, l=5, r=5, t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            ),
        )
        return fig

    def _cleanup_temp_dir(self):
        if self.uploaded_project_path and os.path.exists(self.uploaded_project_path):
            try:
                shutil.rmtree(self.uploaded_project_path)
                self.uploaded_project_path = None
                self.uploaded_project_name = None
            except Exception as e:
                logging.exception(f"Error cleaning up temp dir: {e}")

    @rx.event
    def on_app_load(self):
        """Clean up any lingering temp directories when the app loads for a new session."""
        self._cleanup_temp_dir()
        self.active_page = "Upload"

    @rx.event
    def clear_upload(self):
        self._cleanup_temp_dir()
        self.uploaded_files = []
        self.latest_snapshot = None
        self.active_page = "Upload"
        return rx.toast.info("Cleared uploaded project.")

    @rx.event
    async def handle_upload(self, files: list[rx.UploadFile]):
        """Handle file uploads, extracting zip files if present."""
        if not files:
            yield rx.toast.error("No files selected for upload.")
            return
        self.is_uploading = True
        yield
        upload_successful = False
        try:
            self._cleanup_temp_dir()
            self.uploaded_files = []
            zip_processed = False
            temp_dir = tempfile.mkdtemp()
            self.uploaded_project_path = temp_dir
            for file in files:
                upload_data = await file.read()
                file_path = os.path.join(temp_dir, file.name)
                with open(file_path, "wb") as f:
                    f.write(upload_data)
                self.uploaded_files.append(file.name)
                if file.name.endswith(".zip") and (not zip_processed):
                    with zipfile.ZipFile(file_path, "r") as zip_ref:
                        extract_path = os.path.join(
                            temp_dir, os.path.splitext(file.name)[0]
                        )
                        os.makedirs(extract_path, exist_ok=True)
                        zip_ref.extractall(extract_path)
                    self.uploaded_project_path = extract_path
                    self.uploaded_project_name = file.name
                    self.uploaded_files = [f"{file.name} (project)"]
                    zip_processed = True
                    upload_successful = True
                    yield rx.toast.success(f"Extracted project: {file.name}")
                    break
            if not zip_processed and files:
                self.uploaded_project_name = f"{len(files)} individual files"
                upload_successful = True
            if not self.uploaded_project_name:
                yield rx.toast.info(
                    "Please upload a .zip project archive or individual files."
                )
        except zipfile.BadZipFile:
            logging.exception("Bad zip file uploaded")
            yield rx.toast.error("Uploaded file is not a valid zip archive.")
            self._cleanup_temp_dir()
        except Exception as e:
            logging.exception(f"Upload failed: {e}")
            yield rx.toast.error(f"An error occurred during upload: {e}")
            self._cleanup_temp_dir()
        finally:
            self.is_uploading = False
            if upload_successful:
                yield InduState.run_scan
            else:
                yield

    @rx.event(background=True)
    async def run_scan(self):
        async with self:
            self.is_scanning = True
            if not self.latest_snapshot and (not self.uploaded_project_path):
                self.active_page = "Dashboard"
                yield rx.toast.info("Running initial local scan...")
            yield
        scan_path = (
            self.uploaded_project_path if self.uploaded_project_path else self.scan_path
        )
        if not os.path.exists(scan_path):
            async with self:
                self.is_scanning = False
            yield rx.toast.error(f"Scan path does not exist: {scan_path}")
            return
        files_data: list[FileMetrics] = []
        folders_data: dict[str, FolderMetrics] = {}
        total_files = 0
        total_size = 0
        total_loc = 0
        file_type_distribution: dict[str, int] = {}
        ignore_dirs = {".git", "__pycache__", "node_modules", ".web", "assets"}
        ignore_files = {".DS_Store"}
        base_path_for_relpath = scan_path
        for root, dirs, files in os.walk(scan_path):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            for file in files:
                if file in ignore_files:
                    continue
                file_path = os.path.join(root, file)
                try:
                    size = os.path.getsize(file_path)
                    loc = 0
                    try:
                        with open(
                            file_path, "r", encoding="utf-8", errors="ignore"
                        ) as f:
                            loc = sum((1 for _ in f))
                    except (IOError, UnicodeDecodeError) as e:
                        logging.exception(
                            f"Error reading file for LOC: {file_path} - {e}"
                        )
                        loc = 0
                    _, ext = os.path.splitext(file)
                    ext = ext if ext else "Other"
                    rel_file_path = os.path.relpath(file_path, base_path_for_relpath)
                    file_metric = FileMetrics(
                        path=rel_file_path, size=size, lines_of_code=loc, extension=ext
                    )
                    files_data.append(file_metric)
                    total_files += 1
                    total_size += size
                    total_loc += loc
                    file_type_distribution[ext] = file_type_distribution.get(ext, 0) + 1
                except FileNotFoundError as e:
                    logging.exception(f"File not found during scan: {file_path} - {e}")
                    continue
        dependency_graph = self._build_dependency_graph(
            files_data, base_path_for_relpath
        )
        architecture_violations = self._validate_architecture(dependency_graph)
        unused_components = self._find_unused_components(
            files_data, dependency_graph, base_path_for_relpath
        )
        snapshot = Snapshot(
            timestamp=time.time(),
            total_files=total_files,
            total_size=total_size,
            total_lines_of_code=total_loc,
            files=files_data,
            folders=folders_data,
            file_type_distribution=file_type_distribution,
            dependency_graph=dependency_graph,
            architecture_violations=architecture_violations,
            unused_components=unused_components,
        )
        tree = {"name": "root", "folders": [], "files": [], "file_count": 0}
        for file_metric in files_data:
            path_parts = file_metric["path"].split(os.sep)
            current_level = tree
            for i, part in enumerate(path_parts[:-1]):
                folder = next(
                    (f for f in current_level["folders"] if f["name"] == part), None
                )
                if not folder:
                    folder = {"name": part, "folders": [], "files": [], "file_count": 0}
                    current_level["folders"].append(folder)
                current_level = folder
            filename = path_parts[-1]
            if current_level:
                current_level["files"].append(
                    {"name": filename, "lines_of_code": file_metric["lines_of_code"]}
                )
        self._count_files_recursively(tree)
        async with self:
            self.latest_snapshot = snapshot
            self.scan_history.append(snapshot)
            self.file_tree = tree
            self.current_path = []
            self.is_scanning = False
            self.active_page = "Dashboard"
        yield rx.toast.success("Scan complete!", duration=3000)

    def _count_files_recursively(self, folder: FolderNode):
        file_count = len(folder["files"])
        for subfolder in folder["folders"]:
            file_count += self._count_files_recursively(subfolder)
        folder["file_count"] = file_count
        return file_count

    def _parse_python_imports(
        self, content: str, file_path: str, base_path: str
    ) -> list[str]:
        imports = set()
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        module_path_parts = node.module.split(".")
                        if node.level > 0:
                            source_dir = os.path.dirname(file_path)
                            rel_path_base = source_dir
                            for _ in range(node.level - 1):
                                rel_path_base = os.path.dirname(rel_path_base)
                            abs_path = os.path.abspath(
                                os.path.join(rel_path_base, *module_path_parts)
                            )
                            rel_to_scan_root = os.path.relpath(abs_path, base_path)
                            imports.add(
                                os.path.normpath(rel_to_scan_root).replace(os.sep, ".")
                            )
                        else:
                            imports.add(node.module)
        except SyntaxError as e:
            logging.exception(f"Could not parse Python file {file_path}: {e}")
        return list(imports)

    def _extract_file_dependencies(
        self, file_metric: FileMetrics, base_path: str
    ) -> list[str]:
        full_path = os.path.join(base_path, file_metric["path"])
        try:
            with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except (IOError, UnicodeDecodeError) as e:
            logging.exception(f"Could not read file {full_path}: {e}")
            return []
        if file_metric["extension"] == ".py":
            return self._parse_python_imports(content, full_path, base_path)
        return []

    def _build_dependency_graph(
        self, files_data: list[FileMetrics], base_path: str
    ) -> dict[str, list[str]]:
        graph = {}
        for file_metric in files_data:
            if file_metric["extension"] == ".py":
                dependencies = self._extract_file_dependencies(file_metric, base_path)
                graph[file_metric["path"]] = dependencies
        return graph

    def _validate_architecture(self, graph: dict[str, list[str]]) -> list[str]:
        violations = []
        for file, deps in graph.items():
            if "components" in file:
                for dep in deps:
                    if "states" in dep:
                        violations.append(
                            f"Violation: Component '{file}' imports state '{dep}'"
                        )
        return violations

    def _find_unused_components(
        self,
        files_data: list[FileMetrics],
        dependency_graph: dict[str, list[str]],
        base_path: str,
    ) -> list[str]:
        all_scanned_py_files = {
            f["path"] for f in files_data if f["extension"] == ".py"
        }
        all_imported_modules = set()
        file_paths_relative = {f["path"] for f in files_data if f["extension"] == ".py"}
        for dependencies in dependency_graph.values():
            for dep in dependencies:
                potential_path = dep.replace(".", os.sep) + ".py"
                if potential_path in file_paths_relative:
                    all_imported_modules.add(potential_path)
                init_path = os.path.join(dep.replace(".", os.sep), "__init__.py")
                if init_path in file_paths_relative:
                    all_imported_modules.add(init_path)
        unused = all_scanned_py_files - all_imported_modules
        unused = {f for f in unused if not f.endswith("__init__.py")}
        return sorted(list(unused))