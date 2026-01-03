"""
Groq API Integration for AI-Generated Commit Messages
Generates commit messages following strict commit hygiene practices

API Documentation: https://console.groq.com/
Environment Variable: GROQ_API_KEY
"""
import os
import json
import re
import requests
from typing import Optional, Dict, List, Callable, Tuple
from pathlib import Path
from collections import defaultdict


class GroqCommitGenerator:
    """Generate commit messages using Groq API"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Groq commit generator.

        The generator can operate in two modes:
        - **Online mode** (default): uses the Groq API when ``GROQ_API_KEY`` is set.
        - **Offline mode**: if no API key is available, falls back to deterministic
          conventional commit messages based purely on local git analysis.
        """
        # API key is optional – offline mode still enables strict hygiene and
        # automatic commit grouping even when the Groq service is unavailable.
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.online = bool(self.api_key)

        # Groq API endpoint (https://console.groq.com/)
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}" if self.api_key else "",
            "Content-Type": "application/json",
        }

    def analyze_git_changes(self, git_client) -> Dict[str, any]:
        """
        Comprehensively analyze git changes including actual code diffs

        Args:
            git_client: GitClient instance

        Returns:
            Dictionary with detailed change analysis including code diffs
        """
        changes_info = {
            "staged_files": [],
            "modified_files": [],
            "added_files": [],
            "deleted_files": [],
            "untracked_files": [],
            "diff_summary": "",
            "file_types": [],
            "change_summary": "",
            "code_diffs": {},  # File path -> actual diff content
            "file_changes": []  # List of file change details
        }

        try:
            # Get git status
            status_output = git_client.status(porcelain=True)
            if not status_output or not status_output.strip():
                return changes_info

            lines = [l for l in status_output.strip().split('\n') if l.strip()]

            # Categorize files and get detailed diffs
            for line in lines:
                if len(line) < 3:
                    continue
                
                status_code = line[:2]
                file_path = line[3:].strip()

                if status_code == '??':
                    changes_info["untracked_files"].append(file_path)
                elif status_code.startswith('A'):
                    changes_info["added_files"].append(file_path)
                elif status_code.startswith('D'):
                    changes_info["deleted_files"].append(file_path)
                elif 'M' in status_code:
                    changes_info["modified_files"].append(file_path)

            # Get actual code diffs for each file
            all_changed_files = (
                changes_info["added_files"] +
                changes_info["modified_files"] +
                changes_info["deleted_files"]
            )

            for file_path in all_changed_files:
                try:
                    # Get detailed diff for this file
                    diff_result = git_client._run_command(
                        ['git', 'diff', '--cached', file_path],
                        check=False
                    )
                    
                    # If no staged changes, try unstaged
                    if not diff_result.stdout or diff_result.returncode != 0:
                        diff_result = git_client._run_command(
                            ['git', 'diff', file_path],
                            check=False
                        )
                    
                    if diff_result.returncode == 0 and diff_result.stdout:
                        diff_content = diff_result.stdout.strip()
                        changes_info["code_diffs"][file_path] = diff_content
                        
                        # Analyze the diff to extract change details
                        change_details = self._analyze_file_diff(file_path, diff_content)
                        changes_info["file_changes"].append(change_details)
                        
                except Exception:
                    pass

            # Get file extensions/types
            all_files = (
                changes_info["added_files"] +
                changes_info["modified_files"] +
                changes_info["deleted_files"] +
                changes_info["untracked_files"]
            )
            
            file_types = set()
            for file_path in all_files:
                ext = Path(file_path).suffix.lower()
                if ext:
                    file_types.add(ext)
                else:
                    if '/' in file_path or '\\' in file_path:
                        file_types.add("directory")
            
            changes_info["file_types"] = list(file_types)

            # Get diff summary for staged changes
            try:
                diff_result = git_client._run_command(
                    ['git', 'diff', '--cached', '--stat'],
                    check=False
                )
                if diff_result.returncode == 0 and diff_result.stdout:
                    changes_info["diff_summary"] = diff_result.stdout.strip()
            except Exception:
                pass

            # Get diff summary for unstaged changes if no staged changes
            if not changes_info["diff_summary"]:
                try:
                    diff_result = git_client._run_command(
                        ['git', 'diff', '--stat'],
                        check=False
                    )
                    if diff_result.returncode == 0 and diff_result.stdout:
                        changes_info["diff_summary"] = diff_result.stdout.strip()
                except Exception:
                    pass

            # Create summary
            summary_parts = []
            if changes_info["added_files"]:
                summary_parts.append(
                    f"{len(changes_info['added_files'])} file(s) added")
            if changes_info["modified_files"]:
                summary_parts.append(
                    f"{len(changes_info['modified_files'])} file(s) modified")
            if changes_info["deleted_files"]:
                summary_parts.append(
                    f"{len(changes_info['deleted_files'])} file(s) deleted")
            if changes_info["untracked_files"]:
                summary_parts.append(
                    f"{len(changes_info['untracked_files'])} untracked file(s)")

            changes_info["change_summary"] = ", ".join(summary_parts)

        except Exception as e:
            # If analysis fails, return basic info
            pass

        return changes_info

    def _analyze_file_diff(self, file_path: str, diff_content: str) -> Dict:
        """Analyze a single file's diff to extract change patterns.

        This performs lightweight static analysis to infer the *intent* of the
        change so that commits can be split by purpose (feature, fix, docs,
        tests, style, build, security, performance, removal, etc.).
        """
        file_lower = file_path.lower()
        change_details = {
            "file": file_path,
            "lines_added": 0,
            "lines_removed": 0,
            "functions_changed": [],
            "classes_changed": [],
            "imports_changed": False,
            "test_changes": False,
            "doc_changes": False,
            "config_changes": False,
            "dependency_changes": False,
            # Additional intent flags for stricter categorisation
            "style_changes": False,
            "performance_changes": False,
            "security_changes": False,
            "build_changes": False,
            "removal_only": False,
        }

        try:
            lines = diff_content.split("\n")
            for line in lines:
                if line.startswith("+") and not line.startswith("+++"):
                    change_details["lines_added"] += 1
                    # Detect function/class changes
                    if re.search(r"\b(def|class|function)\s+\w+", line):
                        match = re.search(r"\b(def|class)\s+(\w+)", line)
                        if match:
                            if match.group(1) == "def":
                                change_details["functions_changed"].append(
                                    match.group(2)
                                )
                            else:
                                change_details["classes_changed"].append(
                                    match.group(2)
                                )
                    # Detect imports
                    if re.search(r"^(import|from)\s+", line.lstrip("+")):
                        change_details["imports_changed"] = True
                    # Detect test changes
                    if "test" in file_lower or "spec" in file_lower:
                        change_details["test_changes"] = True
                    # Detect doc changes
                    if any(
                        keyword in line.lower()
                        for keyword in ["doc", "readme", "comment", '"""', "'''"]
                    ):
                        change_details["doc_changes"] = True
                    # Detect config changes
                    if any(
                        keyword in file_lower
                        for keyword in [
                            "config",
                            "settings",
                            ".env",
                            ".json",
                            ".yaml",
                            ".yml",
                        ]
                    ):
                        change_details["config_changes"] = True
                    # Detect dependency changes
                    if any(
                        keyword in file_lower
                        for keyword in [
                            "requirements",
                            "package.json",
                            "pom.xml",
                            "dependencies",
                        ]
                    ):
                        change_details["dependency_changes"] = True
                    # Detect obvious style-only files (CSS/formatting assets)
                    if any(
                        file_lower.endswith(ext)
                        for ext in [
                            ".css",
                            ".scss",
                            ".sass",
                            ".less",
                            ".styl",
                        ]
                    ) or any(seg in file_lower for seg in ["/styles", "\\styles", "_style"]):
                        change_details["style_changes"] = True
                    # Detect build / CI related files
                    if any(
                        name in file_lower
                        for name in [
                            "makefile",
                            "pyproject.toml",
                            "setup.py",
                            "dockerfile",
                            "github/workflows",
                            "azure-pipelines",
                            ".gitlab-ci",
                        ]
                    ):
                        change_details["build_changes"] = True
                    # Detect performance-related intent from keywords
                    if any(
                        kw in line.lower()
                        for kw in [
                            "optimize",
                            "optimization",
                            "performance",
                            "faster",
                            "cache",
                            "benchmark",
                        ]
                    ):
                        change_details["performance_changes"] = True
                    # Detect security-related changes
                    if any(
                        kw in file_lower
                        for kw in ["security", "auth", "token", "jwt"]
                    ) or any(
                        kw in line.lower()
                        for kw in [
                            "encryption",
                            "hashlib",
                            "secrets",
                            "permission",
                            "csrf",
                            "xss",
                            "sql injection",
                        ]
                    ):
                        change_details["security_changes"] = True

                elif line.startswith("-") and not line.startswith("---"):
                    change_details["lines_removed"] += 1

            # Mark pure removals (no additions) as removal-only candidates
            if (
                change_details["lines_removed"] > 0
                and change_details["lines_added"] == 0
            ):
                change_details["removal_only"] = True

        except Exception:
            # Best-effort analysis – failures here should never break the main
            # push flow.
            pass

        return change_details

    def detect_logical_change_groups(self, changes_info: Dict) -> List[Dict]:
        """Analyze changes and group them into logical commit units.

        Each returned group is intended to become **one commit** with a single
        clear purpose and a single Conventional Commit type.
        """
        change_groups: List[Dict] = []
        file_changes = changes_info.get("file_changes", [])
        code_diffs = changes_info.get("code_diffs", {})

        if not file_changes:
            # If we have no per-file analysis, we cannot reliably detect multiple
            # logical units. In that case we conservatively return a single
            # group and let higher layers decide whether to proceed.
            return [
                {
                    "files": (
                        changes_info.get("added_files", [])
                        + changes_info.get("modified_files", [])
                        + changes_info.get("deleted_files", [])
                    ),
                    "type": "chore",
                    "reason": "single_change_group",
                    "code_diffs": code_diffs,
                }
            ]

        # Group by inferred Conventional Commit type so that each commit has a
        # single, well-defined intent.
        groups: Dict[str, List[str]] = defaultdict(list)

        for change in file_changes:
            file_path = change["file"]
            commit_type = self._classify_change_type(change)
            groups[commit_type].append(file_path)

        # Create change groups from the type-based buckets
        for commit_type, files in groups.items():
            if not files:
                continue
            change_groups.append(
                {
                    "files": files,
                    "type": commit_type,
                    "reason": f"grouped_by_type_{commit_type}",
                    "code_diffs": {
                        f: code_diffs.get(f, "") for f in files if f in code_diffs
                    },
                }
            )

        # If we have multiple distinct groups, respect them – higher layers will
        # enforce that each becomes its own commit.
        if len(change_groups) > 1:
            return change_groups

        # Otherwise, fall back to grouping by directory/component as an extra
        # signal for potential logical separation.
        all_files = (
            changes_info.get("added_files", [])
            + changes_info.get("modified_files", [])
            + changes_info.get("deleted_files", [])
        )

        dir_groups: Dict[str, List[str]] = defaultdict(list)
        for file_path in all_files:
            dir_path = str(Path(file_path).parent)
            dir_groups[dir_path].append(file_path)

        if len(dir_groups) > 1:
            change_groups = []
            for dir_path, files in dir_groups.items():
                change_groups.append(
                    {
                        "files": files,
                        "type": "chore",
                        "reason": f"grouped_by_directory_{dir_path}",
                        "code_diffs": {
                            f: code_diffs.get(f, "") for f in files if f in code_diffs
                        },
                    }
                )

        return (
            change_groups
            if change_groups
            else [
                {
                    "files": all_files,
                    "type": "chore",
                    "reason": "single_change_group",
                    "code_diffs": code_diffs,
                }
            ]
        )

    def _classify_change_type(self, change: Dict) -> str:
        """Infer a Conventional Commit type from a single file change.

        This is intentionally opinionated and errs on the side of splitting
        changes into more, smaller commits rather than fewer, larger ones.
        """
        file_path = change.get("file", "")
        file_lower = file_path.lower()

        # Highest-priority / most specific categories first.
        if change.get("test_changes") or "test" in file_lower or "spec" in file_lower:
            return "test"
        if change.get("doc_changes") or any(
            kw in file_lower for kw in ["readme", "doc", ".md"]
        ):
            return "docs"
        if change.get("dependency_changes"):
            return "deps"
        if change.get("security_changes"):
            return "security"
        if change.get("performance_changes"):
            return "perf"
        if change.get("style_changes"):
            return "style"
        if change.get("build_changes"):
            return "build"
        if change.get("removal_only"):
            return "removal"

        # Bug fixes inferred from filename hints.
        if any(kw in file_lower for kw in ["fix", "bug", "error", "hotfix"]):
            return "fix"

        # Feature vs refactor – based on whether new functions/classes appear.
        if change.get("functions_changed") or change.get("classes_changed"):
            if any(kw in file_lower for kw in ["feature", "feat", "add", "new", "implement"]):
                return "feat"
            return "refactor"

        # Config and general maintenance default to chore.
        if change.get("config_changes"):
            return "chore"

        # Fallback for improvements that don't clearly match another bucket.
        return "improvement"

    def generate_multiple_commit_messages(
        self,
        change_groups: List[Dict],
        username: str = "Drakaniia",
        email: str = "floresaybaez574@gmail.com",
        preview_callback: Optional[Callable[[str], None]] = None
    ) -> List[Dict]:
        """
        Generate commit messages for multiple logical change groups
        
        Args:
            change_groups: List of change group dictionaries
            username: Git username
            email: Git email
            preview_callback: Optional callback function
            
        Returns:
            List of dictionaries with commit message and associated files
        """
        commit_messages = []
        
        for idx, group in enumerate(change_groups, 1):
            if preview_callback:
                preview_callback(f"Analyzing change group {idx}/{len(change_groups)}...")
            
            # Create focused changes_info for this group
            group_changes = {
                "files": group["files"],
                "code_diffs": group.get("code_diffs", {}),
                "type_hint": group.get("type", "chore"),
                "reason": group.get("reason", "")
            }
            
            try:
                message = self.generate_commit_message(
                    group_changes,
                    username=username,
                    email=email,
                    preview_callback=lambda msg: preview_callback(f"Group {idx}: {msg}") if preview_callback else None,
                    is_group=True
                )
                
                if message:
                    # Validate the message
                    validation_result = self.validate_commit_message(message)
                    if not validation_result["valid"]:
                        if preview_callback:
                            preview_callback(f"⚠️  Validation warnings for group {idx}: {', '.join(validation_result['warnings'])}")
                    
                    commit_messages.append({
                        "message": message,
                        "files": group["files"],
                        "type": group.get("type", "chore"),
                        "validation": validation_result
                    })
            except Exception as e:
                if preview_callback:
                    preview_callback(f"⚠️  Failed to generate message for group {idx}: {str(e)}")
                # Create a fallback message
                commit_messages.append({
                    "message": f"{group.get('type', 'chore')}: update {len(group['files'])} file(s)",
                    "files": group["files"],
                    "type": group.get("type", "chore"),
                    "validation": {"valid": True, "warnings": ["Fallback message generated"]}
                })
        
        return commit_messages

    def validate_commit_message(self, message: str) -> Dict:
        """Validate a commit message against strict Conventional Commit rules.

        Returns a dict with ``valid``, ``warnings`` and ``errors`` keys.
        """
        validation = {"valid": True, "warnings": [], "errors": []}

        # Check format: "type: message"
        if ":" not in message:
            validation["errors"].append(
                "Missing commit type prefix (format: 'type: message')"
            )
            validation["valid"] = False
            return validation

        parts = message.split(":", 1)
        if len(parts) != 2:
            validation["errors"].append("Invalid format: should be 'type: message'")
            validation["valid"] = False
            return validation

        commit_type = parts[0].strip().lower()
        commit_msg = parts[1].strip()

        # Validate commit type
        valid_types = [
            "feat",
            "fix",
            "refactor",
            "perf",
            "test",
            "build",
            "docs",
            "style",
            "chore",
            "revert",
            "security",
            "deps",
            "ci",
            "improvement",
            "removal",
        ]

        if commit_type not in valid_types:
            validation["warnings"].append(
                f"Unconventional commit type: '{commit_type}'"
            )

        # Validate message content
        if not commit_msg:
            validation["errors"].append("Commit message is empty")
            validation["valid"] = False

        # Treat extremely short messages as invalid (too vague).
        if len(commit_msg) < 10:
            validation["errors"].append(
                "Commit message is too short (must be at least 10 characters)"
            )
            validation["valid"] = False

        if len(commit_msg) > 72:
            validation["warnings"].append(
                "Commit message exceeds 72 characters (consider using body)"
            )

        # Check for conjunctions that often indicate multiple logical changes.
        forbidden_words = ["and", "also", "plus", "&"]
        commit_msg_lower = commit_msg.lower()
        for word in forbidden_words:
            if f" {word} " in commit_msg_lower or commit_msg_lower.startswith(
                f"{word} "
            ):
                validation["warnings"].append(
                    f"Contains '{word}' - consider splitting into separate commits"
                )

        # Check for vague multi-change indicators.
        if any(
            indicator in commit_msg_lower
            for indicator in ["multiple", "various", "several", "many"]
        ):
            validation["warnings"].append(
                "Message suggests multiple changes - verify this is a single logical change"
            )

        return validation

    def _generate_offline_commit_message(self, changes_info: Dict[str, any]) -> str:
        """Generate a deterministic Conventional Commit message without the API.

        This is used when the Groq service is unavailable or disabled but we
        still want strictly formatted, single-purpose commit messages.
        """
        # Determine affected files
        files: List[str] = list(changes_info.get("files", []))
        if not files:
            files = (
                changes_info.get("added_files", [])
                + changes_info.get("modified_files", [])
                + changes_info.get("deleted_files", [])
            )
        files = [f for f in files if f]

        primary_file = files[0] if files else ""
        try:
            scope = Path(primary_file).name or "project"
        except Exception:
            scope = primary_file or "project"

        # Prefer explicit type hints from the caller/grouping
        type_hint = (changes_info.get("type_hint") or changes_info.get("type") or "chore").lower()

        # If we have per-file analysis, refine the type based on the first file.
        file_changes = changes_info.get("file_changes") or []
        if file_changes:
            inferred_type = self._classify_change_type(file_changes[0])
            if inferred_type:
                type_hint = inferred_type

        # Normalise into the supported Conventional Commit types
        valid_types = [
            "feat",
            "fix",
            "refactor",
            "perf",
            "test",
            "build",
            "docs",
            "style",
            "chore",
            "revert",
            "security",
            "deps",
            "ci",
            "improvement",
            "removal",
        ]
        alias_map = {
            "documentation": "docs",
            "doc": "docs",
            "dependency": "deps",
            "dependencies": "deps",
            "config": "chore",
            "configuration": "chore",
            "tests": "test",
        }

        commit_type = alias_map.get(type_hint, type_hint)
        if commit_type not in valid_types:
            commit_type = "chore"

        # Build a concise, specific description
        file_count = len(files)
        if file_count > 1:
            base_desc = f"update {file_count} files"
        else:
            if commit_type == "feat":
                base_desc = f"add or update {scope}"
            elif commit_type == "fix":
                base_desc = f"fix issues in {scope}"
            elif commit_type == "docs":
                base_desc = f"update documentation for {scope}"
            elif commit_type == "test":
                base_desc = f"update tests for {scope}"
            elif commit_type == "deps":
                base_desc = f"update dependencies in {scope or 'project'}"
            elif commit_type == "refactor":
                base_desc = f"refactor {scope}"
            elif commit_type == "perf":
                base_desc = f"improve performance in {scope}"
            elif commit_type == "style":
                base_desc = f"apply style updates to {scope}"
            elif commit_type == "build":
                base_desc = f"update build configuration ({scope})"
            elif commit_type == "security":
                base_desc = f"harden security in {scope}"
            elif commit_type == "removal":
                base_desc = f"remove deprecated code from {scope}"
            else:
                base_desc = f"update {scope}"

        # Ensure description is not excessively long
        if len(base_desc) > 60:
            base_desc = base_desc[:57] + "..."

        return f"{commit_type}: {base_desc}"

    def generate_commit_message(
        self,
        changes_info: Dict[str, any],
        username: str = "Drakaniia",
        email: str = "floresaybaez574@gmail.com",
        preview_callback: Optional[Callable[[str], None]] = None,
        is_group: bool = False,
    ) -> Optional[str]:
        """Generate a commit message, using Groq when available.

        In offline mode (no API key), falls back to a deterministic
        Conventional Commit message built from the analysed changes.
        """
        # Offline mode – no API key, or API intentionally disabled.
        if not self.online:
            message = self._generate_offline_commit_message(changes_info)
            if preview_callback:
                preview_callback("Generated offline conventional commit message")
            return message

        # Build the prompt for the Groq API
        prompt = self._build_prompt(changes_info, username, email, is_group=is_group)

        # Groq models: llama-3.3-70b-versatile, mixtral-8x7b-32768,
        # llama-3.1-8b-instant, etc.
        models_to_try = [
            "llama-3.3-70b-versatile",
            "llama-3.1-70b-versatile",
            "mixtral-8x7b-32768",
            "llama-3.1-8b-instant",
        ]

        for model_name in models_to_try:
            payload = {
                "model": model_name,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a Git commit message expert. Generate concise, "
                            "clear commit messages following conventional commit format."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.3,
                "max_tokens": 150,
            }

            try:
                # Call preview callback if provided
                if preview_callback:
                    preview_callback(f"Generating with {model_name}...")

                response = requests.post(
                    self.base_url,
                    headers=self.headers,
                    json=payload,
                    timeout=30,
                )

                # If we get a 404, try the next model
                if response.status_code == 404:
                    continue

                response.raise_for_status()

                # Success - process the response
                result = response.json()

                # Extract the commit message from the response
                if "choices" in result and len(result["choices"]) > 0:
                    message = (
                        result["choices"][0]["message"]["content"].strip()
                    )

                    # Clean up the message - remove surrounding quotes if present
                    if message.startswith('"') and message.endswith('"'):
                        message = message[1:-1]
                    if message.startswith("'") and message.endswith("'"):
                        message = message[1:-1]

                    # Ensure it follows the format: "commit_type: commit_message"
                    if ":" not in message:
                        message_lower = message.lower()
                        if any(
                            word in message_lower
                            for word in ["fix", "bug", "error", "issue"]
                        ):
                            message = f"fix: {message}"
                        elif any(
                            word in message_lower
                            for word in ["add", "new", "feature", "implement"]
                        ):
                            message = f"feat: {message}"
                        elif any(
                            word in message_lower
                            for word in ["update", "change", "modify"]
                        ):
                            message = f"chore: {message}"
                        else:
                            message = f"chore: {message}"

                    if preview_callback:
                        preview_callback(f"Preview: {message}")

                    return message

                # If we got here, the response didn't have the expected format
                raise Exception(
                    "Unexpected API response format: no choices in response"
                )

            except requests.exceptions.HTTPError as e:
                if (
                    e.response.status_code == 404
                    and model_name != models_to_try[-1]
                ):
                    continue  # Try next model
                # Fall back to offline message on hard failure
                return self._generate_offline_commit_message(changes_info)
            except requests.exceptions.RequestException:
                # Network or timeout issue – try next model, or fall back.
                if model_name == models_to_try[-1]:
                    return self._generate_offline_commit_message(changes_info)
                continue
            except (KeyError, IndexError):
                if model_name == models_to_try[-1]:
                    return self._generate_offline_commit_message(changes_info)
                continue

        # If we get here, all models failed – final offline fallback
        return self._generate_offline_commit_message(changes_info)

    def _build_prompt(
        self,
        changes_info: Dict[str, any],
        username: str,
        email: str,
        is_group: bool = False
    ) -> str:
        """
        Build comprehensive prompt for Groq API with detailed code analysis

        Args:
            changes_info: Dictionary with git changes analysis
            username: Git username
            email: Git email
            is_group: Whether this is for a specific change group

        Returns:
            Formatted prompt string
        """
        # Get files - either from group or from changes_info
        if is_group:
            all_files = changes_info.get("files", [])
            code_diffs = changes_info.get("code_diffs", {})
            type_hint = changes_info.get("type_hint", "chore")
            reason = changes_info.get("reason", "")
        else:
            all_files = (
                changes_info.get("added_files", []) +
                changes_info.get("modified_files", []) +
                changes_info.get("deleted_files", []) +
                changes_info.get("untracked_files", [])
            )
            code_diffs = changes_info.get("code_diffs", {})
            type_hint = None
            reason = None

        file_list = "\n".join([f"  - {f}" for f in all_files[:30]])  # Increased limit
        if len(all_files) > 30:
            file_list += f"\n  ... and {len(all_files) - 30} more files"

        # Build detailed code diff summary (truncated for token limits)
        code_diff_summary = ""
        if code_diffs:
            code_diff_summary = "\n\nDetailed code changes:\n"
            for file_path, diff_content in list(code_diffs.items())[:5]:  # Limit to 5 files
                # Truncate very long diffs
                diff_preview = diff_content[:2000] if len(diff_content) > 2000 else diff_content
                code_diff_summary += f"\n--- {file_path} ---\n{diff_preview}\n"
                if len(diff_content) > 2000:
                    code_diff_summary += f"\n... (truncated, {len(diff_content) - 2000} more characters)\n"
            if len(code_diffs) > 5:
                code_diff_summary += f"\n... and {len(code_diffs) - 5} more files with changes\n"

        diff_summary = changes_info.get("diff_summary", "No diff summary available")
        change_summary = changes_info.get("change_summary", "No changes detected")
        file_types = ", ".join(changes_info.get("file_types", [])[:10])
        
        # Get file change details if available
        file_changes_detail = ""
        if changes_info.get("file_changes"):
            file_changes_detail = "\n\nFile change analysis:\n"
            for change in changes_info.get("file_changes", [])[:10]:
                detail_parts = []
                if change.get("functions_changed"):
                    detail_parts.append(f"functions: {', '.join(change['functions_changed'][:3])}")
                if change.get("classes_changed"):
                    detail_parts.append(f"classes: {', '.join(change['classes_changed'][:3])}")
                if change.get("lines_added"):
                    detail_parts.append(f"+{change['lines_added']} lines")
                if change.get("lines_removed"):
                    detail_parts.append(f"-{change['lines_removed']} lines")
                if detail_parts:
                    file_changes_detail += f"  {change['file']}: {', '.join(detail_parts)}\n"

        # Build comprehensive prompt
        prompt = f"""You are an expert Git commit message generator following strict GitHub commit hygiene and version control best practices.

CRITICAL RULES:
1. Each commit MUST represent exactly ONE clear, logical, and cohesive change
2. NEVER use "and", "also", "plus", or similar conjunctions to combine multiple changes
3. If multiple unrelated changes are detected, they MUST be split into separate commits
4. Commit types: feat (new feature), fix (bug fix), refactor (code restructuring), perf (performance), test (tests), build (build system), docs (documentation), style (formatting), chore (maintenance), revert (revert commit), security (security fix), deps (dependencies), ci (CI/CD), improvement (general improvement), removal (removing code/features)
5. Format: "commit_type: concise_description" (e.g., "feat: add user authentication")
6. Description must be clear, specific, and under 72 characters when possible
7. Focus on WHAT changed and WHY, not HOW (implementation details)

Context:
- Username: {username}
- Email: {email}
{f"- Change group type hint: {type_hint}" if type_hint else ""}
{f"- Grouping reason: {reason}" if reason else ""}

Changes detected:
{change_summary}

Files changed ({len(all_files)} total):
{file_list}

File types: {file_types}

Diff statistics:
{diff_summary}
{file_changes_detail}
{code_diff_summary}

ANALYSIS REQUIRED:
1. Carefully examine the code changes above
2. Identify if this represents a SINGLE logical change or MULTIPLE unrelated changes
3. If multiple unrelated changes exist, you MUST indicate this clearly
4. Determine the most appropriate commit type based on the actual code changes
5. Generate a commit message that accurately describes ONLY the primary logical change

Generate a SINGLE commit message following the format "commit_type: commit_message". 
- The commit_type must accurately reflect the nature of the change
- The commit_message must be concise, clear, and describe exactly what this commit does
- DO NOT use "and" or combine multiple unrelated changes
- If you detect multiple logical changes, focus on the PRIMARY change only and note that splitting may be needed

Commit message:"""

        return prompt

