# INDU Intelligence Framework - Development Plan

## Project Overview
A root-level development process utility that scans, analyzes, and reports on codebase structure, metrics, and relationships. Built with Reflex, provides live insights into platform health, unused components, and architectural patterns.

---

## Phase 1: Core Scanning & Metrics Engine ✅
- [x] Implement recursive file/folder scanner with configurable path support
- [x] Build code metrics calculator (total LOC, file sizes, distribution by type)
- [x] Create state management system for scan results and snapshots
- [x] Add file categorization logic (.tsx, .ts, .jpg, .png, .svg, etc.)
- [x] Implement basic snapshot storage with timestamp tracking

---

## Phase 2: Component Analysis & Dependency Mapping ✅
- [x] Build hierarchical component tree generator for /components folder
- [x] Create import parser to extract dependencies from .tsx, .ts, and .py files
- [x] Generate dependency graph mapping (Pages → Containers → Features → UI)
- [x] Implement architectural pattern validation rules
- [x] Build relationship visualization data structure

---

## Phase 3: Unused Component Detection & API Endpoints ✅
- [x] Implement component usage analyzer (compare all vs imported)
- [x] Create unused component detection with reporting
- [x] Expose JSON API endpoints (/api/snapshot/latest, /api/dependencies, /api/unused)
- [x] Add configuration system (config.json) for multi-project support
- [x] Implement snapshot comparison logic for historical tracking

---

## Phase 4: UI Dashboard & Visualizations ✅
- [x] Build unused components view with interactive list and filtering
- [x] Create snapshot history page with timeline visualization
- [x] Add snapshot comparison tool with diff highlighting
- [x] Implement filtering and search across all views
- [x] Polish UI interactions and add loading states
- [x] Fix dependency_graph_data computed var hashability issue

---

## Phase 5: Drag-and-Drop File Upload (Low Complexity)
- [ ] Create upload UI with drag-and-drop zone using rx.upload
- [ ] Implement single file upload handler with file type validation
- [ ] Add uploaded file display with preview (name, size, type)
- [ ] Store uploaded files temporarily for processing
- [ ] Update nav items to include "Upload" page

---

## Phase 6: Zip File Handling & Project Upload (Medium Complexity)
- [ ] Add zip file detection and validation logic
- [ ] Implement secure zip extraction to temporary directory
- [ ] Add file size and archive size limits (max 100MB)
- [ ] Create temporary workspace cleanup after scan completion
- [ ] Handle nested zip files and malformed archives gracefully
- [ ] Add progress indicator for zip extraction process

---

## Phase 7: Uploaded Project Scanning & Analysis (High Complexity)
- [ ] Modify run_scan() to use uploaded project path when available
- [ ] Automatically trigger scan after successful upload
- [ ] Display uploaded project name in dashboard header (Local vs Uploaded: filename.zip)
- [ ] Add cleanup on app load to remove lingering temp directories from previous sessions
- [ ] Ensure clear_upload() properly removes temp files and resets state

---

## Success Criteria
- ✅ Scans project directory and categorizes all files
- ✅ Calculates accurate code metrics (LOC, sizes, distributions)
- ✅ Generates hierarchical component tree
- ✅ Maps all import dependencies and validates architecture
- ✅ Detects unused components accurately
- ✅ Exposes JSON APIs for external consumption
- ✅ Provides complete interactive dashboard for developers
- [ ] Supports drag-and-drop upload for individual files
- [ ] Handles zip file extraction with file size limits (100MB max)
- [ ] Automatic scanning after successful upload
- [ ] Enhanced error handling and progress indicators
- [ ] Temporary file cleanup and session management

---

## Complexity Levels
- **Low Complexity**: Drag-drop UI, file upload, basic metrics ✅ (Already have foundation)
- **Medium Complexity**: Zip file handling, extraction, file size limits (Phase 6)
- **High Complexity**: Multi-language import parsing ✅, dependency graphs ✅, unused detection ✅, scaling to uploaded projects (Phase 7)
