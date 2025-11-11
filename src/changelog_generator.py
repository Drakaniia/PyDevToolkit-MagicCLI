"""
automation/github/changelog_generator.py
Simple, focused changelog generator without AI dependencies
Generates clean changelog entries from commit history
"""
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict


class ChangelogGenerator:
    """
    Simple changelog generator focused on clarity and maintainability
    
    Features:
    - Categorizes commits by type (feature, fix, refactor, docs)
    - Groups changes by date
    - Tracks processed commits to avoid duplicates
    - Clean, readable markdown output
    """
    
    CONFIG = {
        'changelog_file': 'CHANGELOG.md',
        'commit_cache_file': '.commit_cache.json',
        'group_by_date': True,  # Group commits by date
        'show_author': True,     # Show commit authors
        'max_message_length': 72,  # Truncate long messages
    }
    
    # Enhanced commit type detection patterns
    COMMIT_TYPES = {
        'breaking': {
            'keywords': ['breaking', 'major', 'breaking change', 'incompatible'],
            'emoji': '💥',
            'label': 'Breaking Changes',
            'priority': 1
        },
        'security': {
            'keywords': ['security', 'vulnerability', 'exploit', 'cve', 'auth', 'authentication'],
            'emoji': '🔒',
            'label': 'Security Fixes',
            'priority': 2
        },
        'feature': {
            'keywords': ['add', 'new', 'feature', 'implement', 'create', 'introduce'],
            'emoji': '✨',
            'label': 'New Features',
            'priority': 3
        },
        'fix': {
            'keywords': ['fix', 'bug', 'patch', 'resolve', 'correct', 'repair'],
            'emoji': '🐛',
            'label': 'Bug Fixes',
            'priority': 4
        },
        'performance': {
            'keywords': ['performance', 'optimize', 'speed', 'faster', 'cache', 'memory'],
            'emoji': '⚡',
            'label': 'Performance Improvements',
            'priority': 5
        },
        'refactor': {
            'keywords': ['refactor', 'restructure', 'reorganize', 'clean', 'improve', 'simplify'],
            'emoji': '♻️',
            'label': 'Code Refactoring',
            'priority': 6
        },
        'ui': {
            'keywords': ['ui', 'ux', 'interface', 'design', 'layout', 'styling'],
            'emoji': '🎨',
            'label': 'UI/UX Changes',
            'priority': 7
        },
        'api': {
            'keywords': ['api', 'endpoint', 'route', 'controller', 'service'],
            'emoji': '🔌',
            'label': 'API Changes',
            'priority': 8
        },
        'config': {
            'keywords': ['config', 'configuration', 'settings', 'env', 'environment'],
            'emoji': '⚙️',
            'label': 'Configuration',
            'priority': 9
        },
        'docs': {
            'keywords': ['doc', 'readme', 'comment', 'documentation'],
            'emoji': '📚',
            'label': 'Documentation',
            'priority': 10
        },
        'test': {
            'keywords': ['test', 'spec', 'testing', 'coverage'],
            'emoji': '✅',
            'label': 'Tests',
            'priority': 11
        },
        'style': {
            'keywords': ['style', 'format', 'lint', 'prettier', 'eslint'],
            'emoji': '💄',
            'label': 'Style Changes',
            'priority': 12
        },
        'build': {
            'keywords': ['build', 'webpack', 'rollup', 'vite', 'compile'],
            'emoji': '📦',
            'label': 'Build System',
            'priority': 13
        },
        'deps': {
            'keywords': ['dependency', 'dependencies', 'package', 'npm', 'pip', 'requirements'],
            'emoji': '📌',
            'label': 'Dependencies',
            'priority': 14
        },
        'chore': {
            'keywords': ['chore', 'update', 'upgrade', 'cleanup', 'maintenance'],
            'emoji': '🔧',
            'label': 'Maintenance',
            'priority': 15
        }
    }
    
    # File type patterns for smarter detection
    FILE_PATTERNS = {
        'frontend': ['.js', '.jsx', '.ts', '.tsx', '.vue', '.svelte', '.html', '.css', '.scss', '.less'],
        'backend': ['.py', '.java', '.php', '.rb', '.go', '.rs', '.cs', '.cpp', '.c'],
        'config': ['.json', '.yaml', '.yml', '.toml', '.ini', '.env', '.config'],
        'docs': ['.md', '.rst', '.txt', '.pdf'],
        'test': ['test_', '_test.', '.test.', '.spec.', 'tests/'],
        'build': ['package.json', 'requirements.txt', 'Dockerfile', 'docker-compose', 'Makefile']
    }
    
    def __init__(self):
        self.current_dir = Path.cwd()
        self.processed_commits = self._load_commit_cache()
    
    # ========== Main Entry Points ==========
    
    def generate_changelog(self, num_commits: int = 1) -> bool:
        """
        Generate changelog entries for recent commits
        
        Args:
            num_commits: Number of recent commits to process
        
        Returns:
            True if successful, False otherwise
        """
        if not self._is_git_repo():
            print("❌ Not a git repository")
            return False
        
        print(f"\n📝 Generating changelog for last {num_commits} commit(s)...")
        
        # Get unprocessed commits
        commits = self._get_unprocessed_commits(num_commits)
        
        if not commits:
            print("✅ Changelog already up to date")
            return True
        
        # Group commits by date if configured
        if self.CONFIG['group_by_date']:
            grouped = self._group_commits_by_date(commits)
        else:
            grouped = {'All Changes': commits}
        
        # Generate entries for each group
        for date_label, commit_list in grouped.items():
            entry = self._generate_entry(date_label, commit_list)
            self._append_to_changelog(entry)
            
            # Mark commits as processed
            for commit in commit_list:
                self._mark_commit_processed(commit['hash'])
        
        print(f"✅ Changelog updated with {len(commits)} commit(s)!")
        return True
    
    def show_unprocessed_commits(self, limit: int = 10) -> None:
        """Show commits that haven't been added to changelog yet"""
        print("\n" + "="*70)
        print("📋 UNPROCESSED COMMITS")
        print("="*70 + "\n")
        
        if not self._is_git_repo():
            print("❌ Not a git repository")
            return
        
        commits = self._get_unprocessed_commits(limit)
        
        if not commits:
            print("✅ No unprocessed commits found")
            print("All commits have been added to the changelog.\n")
            return
        
        print(f"Found {len(commits)} unprocessed commit(s):\n")
        
        for i, commit in enumerate(commits, 1):
            commit_type = self._classify_commit(commit)
            emoji = self.COMMIT_TYPES[commit_type]['emoji']
            
            print(f"{i}. {emoji} {commit['short_hash']} - {commit['message'][:60]}")
            print(f"   by {commit['author']} on {commit['date'][:10]}\n")
        
        print("="*70 + "\n")
    
    def reset_processed_commits(self) -> None:
        """Clear the processed commits cache"""
        cache_path = self.current_dir / self.CONFIG['commit_cache_file']
        
        if cache_path.exists():
            cache_path.unlink()
            print("✅ Cleared processed commits cache")
        else:
            print("ℹ️  No cache file found")
    
    # ========== Commit Classification ==========
    
    def _classify_commit(self, commit_data: Dict) -> str:
        """
        Enhanced commit classification using message and file analysis
        
        Args:
            commit_data: Dictionary containing commit information including hash and message
        
        Returns:
            Commit type (feature, fix, refactor, etc.)
        """
        message = commit_data['message']
        message_lower = message.lower()
        commit_hash = commit_data['hash']
        
        # Get files changed in this commit for context
        changed_files = self._get_commit_files(commit_hash)
        file_context = self._analyze_file_context(changed_files)
        
        # Priority-based classification (higher priority = more specific)
        best_match = 'chore'
        best_priority = 999
        
        # Check each type's keywords with priority
        for commit_type, config in self.COMMIT_TYPES.items():
            if any(keyword in message_lower for keyword in config['keywords']):
                if config['priority'] < best_priority:
                    best_match = commit_type
                    best_priority = config['priority']
        
        # Enhance classification with file context
        enhanced_type = self._enhance_with_file_context(best_match, file_context, message_lower)
        
        return enhanced_type
    
    def _get_commit_files(self, commit_hash: str) -> List[str]:
        """Get list of files changed in a commit"""
        try:
            result = subprocess.run(
                ['git', 'show', '--name-only', '--pretty=format:', commit_hash],
                capture_output=True,
                text=True,
                check=True,
                cwd=self.current_dir
            )
            
            files = [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
            return files
        
        except subprocess.CalledProcessError:
            return []
    
    def _analyze_file_context(self, files: List[str]) -> Dict[str, int]:
        """Analyze file types to understand the context of changes"""
        context = {
            'frontend': 0,
            'backend': 0,
            'config': 0,
            'docs': 0,
            'test': 0,
            'build': 0
        }
        
        for file_path in files:
            file_lower = file_path.lower()
            
            # Check each pattern category
            for category, patterns in self.FILE_PATTERNS.items():
                for pattern in patterns:
                    if pattern in file_lower or file_path.endswith(pattern):
                        context[category] += 1
                        break
        
        return context
    
    def _enhance_with_file_context(self, base_type: str, file_context: Dict[str, int], message: str) -> str:
        """Enhance classification based on file context"""
        # If we have strong file context indicators, adjust classification
        total_files = sum(file_context.values())
        
        if total_files == 0:
            return base_type
        
        # Calculate percentages
        context_percentages = {k: (v / total_files) for k, v in file_context.items()}
        
        # Override based on strong file context (>70% of files)
        if context_percentages.get('test', 0) > 0.7:
            return 'test'
        elif context_percentages.get('docs', 0) > 0.7:
            return 'docs'
        elif context_percentages.get('config', 0) > 0.7:
            return 'config'
        elif context_percentages.get('build', 0) > 0.7:
            return 'build'
        
        # For mixed changes, use original classification but with context awareness
        if base_type == 'chore':
            # Try to infer better type from file context
            max_context = max(context_percentages.items(), key=lambda x: x[1])
            if max_context[1] > 0.5:  # >50% of files are of one type
                if max_context[0] == 'frontend' and any(word in message for word in ['ui', 'interface', 'style']):
                    return 'ui'
                elif max_context[0] == 'backend' and any(word in message for word in ['api', 'endpoint', 'service']):
                    return 'api'
        
        return base_type
    
    def _generate_file_summary(self, files: List[str]) -> str:
        """Generate a concise summary of files changed"""
        if not files:
            return ""
        
        if len(files) == 1:
            return f"📄 `{files[0]}`"
        
        # Categorize files
        categories = self._analyze_file_context(files)
        total_files = len(files)
        
        # Generate summary based on file types
        summary_parts = []
        
        if categories['test'] > 0:
            summary_parts.append(f"{categories['test']} test file{'s' if categories['test'] > 1 else ''}")
        
        if categories['docs'] > 0:
            summary_parts.append(f"{categories['docs']} doc file{'s' if categories['docs'] > 1 else ''}")
        
        if categories['config'] > 0:
            summary_parts.append(f"{categories['config']} config file{'s' if categories['config'] > 1 else ''}")
        
        if categories['frontend'] > 0:
            summary_parts.append(f"{categories['frontend']} frontend file{'s' if categories['frontend'] > 1 else ''}")
        
        if categories['backend'] > 0:
            summary_parts.append(f"{categories['backend']} backend file{'s' if categories['backend'] > 1 else ''}")
        
        # If we have uncategorized files
        categorized_count = sum(categories.values())
        if categorized_count < total_files:
            other_count = total_files - categorized_count
            summary_parts.append(f"{other_count} other file{'s' if other_count > 1 else ''}")
        
        if summary_parts:
            return f"📁 {', '.join(summary_parts)}"
        else:
            return f"📁 {total_files} file{'s' if total_files > 1 else ''}"
    
    def _analyze_change_impact(self, files: List[str], message: str) -> str:
        """Analyze the potential impact of changes"""
        if not files:
            return ""
        
        impact_indicators = []
        
        # Check for breaking changes
        if any(keyword in message.lower() for keyword in ['breaking', 'major', 'incompatible']):
            impact_indicators.append("⚠️ Breaking change")
        
        # Check for large changes
        if len(files) > 10:
            impact_indicators.append(f"Large change ({len(files)} files)")
        elif len(files) > 5:
            impact_indicators.append(f"Medium change ({len(files)} files)")
        
        # Check for critical file types
        critical_files = [f for f in files if any(critical in f.lower() 
                         for critical in ['package.json', 'requirements.txt', 'dockerfile', 'config', 'env'])]
        if critical_files:
            impact_indicators.append("Config changes")
        
        # Check for API changes
        api_files = [f for f in files if any(api_term in f.lower() 
                    for api_term in ['api', 'route', 'endpoint', 'controller'])]
        if api_files:
            impact_indicators.append("API changes")
        
        # Check for database changes
        db_files = [f for f in files if any(db_term in f.lower() 
                   for db_term in ['migration', 'schema', 'model', 'database'])]
        if db_files:
            impact_indicators.append("Database changes")
        
        return ', '.join(impact_indicators) if impact_indicators else ""
    
    def _group_commits_by_date(self, commits: List[Dict]) -> Dict[str, List[Dict]]:
        """Group commits by date"""
        grouped = defaultdict(list)
        
        for commit in commits:
            # Extract date (YYYY-MM-DD)
            date = commit['date'][:10]
            grouped[date].append(commit)
        
        return dict(grouped)
    
    # ========== Changelog Generation ==========
    
    def _generate_entry(self, date_label: str, commits: List[Dict]) -> str:
        """
        Generate changelog entry for a group of commits
        
        Args:
            date_label: Date or group label
            commits: List of commits in this group
        
        Returns:
            Formatted markdown entry
        """
        lines = []
        
        # Header
        lines.append(f"### {date_label}")
        lines.append("")
        
        # Categorize commits
        categorized = defaultdict(list)
        for commit in commits:
            commit_type = self._classify_commit(commit)
            categorized[commit_type].append(commit)
        
        # Generate sections for each category (sorted by priority)
        sorted_types = sorted([t for t in categorized.keys()], 
                             key=lambda x: self.COMMIT_TYPES[x]['priority'])
        
        for commit_type in sorted_types:
            type_config = self.COMMIT_TYPES[commit_type]
            commits_of_type = categorized[commit_type]
            
            lines.append(f"#### {type_config['emoji']} {type_config['label']}")
            lines.append("")
            
            for commit in commits_of_type:
                message = commit['message']
                
                # Truncate if too long
                if len(message) > self.CONFIG['max_message_length']:
                    message = message[:self.CONFIG['max_message_length']-3] + "..."
                
                # Get files changed for this commit
                changed_files = self._get_commit_files(commit['hash'])
                file_summary = self._generate_file_summary(changed_files)
                
                # Build enhanced commit line
                commit_line = f"- **{message}** (`{commit['short_hash']}`)"
                
                if self.CONFIG['show_author']:
                    commit_line += f" - *{commit['author']}*"
                
                lines.append(commit_line)
                
                # Add file context if significant
                if file_summary:
                    lines.append(f"  - {file_summary}")
                
                # Add impact analysis for important changes
                impact = self._analyze_change_impact(changed_files, commit['message'])
                if impact:
                    lines.append(f"  - 📊 *{impact}*")
            
            lines.append("")
        
        # Summary
        lines.append(f"**Total**: {len(commits)} commit(s)")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        return '\n'.join(lines)
    
    def _append_to_changelog(self, entry: str) -> None:
        """Append entry to CHANGELOG.md"""
        changelog_path = self.current_dir / self.CONFIG['changelog_file']
        
        try:
            # Read existing content
            if changelog_path.exists():
                with open(changelog_path, 'r', encoding='utf-8') as f:
                    existing = f.read()
            else:
                # Create new changelog with header
                existing = self._create_changelog_header()
            
            # Find insertion point (after header)
            if '---' in existing:
                # Insert after first separator
                parts = existing.split('---', 1)
                new_content = parts[0] + '---\n\n' + entry + parts[1]
            else:
                # No separator, append to end
                new_content = existing.rstrip() + '\n\n' + entry
            
            # Write back
            with open(changelog_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
        except Exception as e:
            print(f"❌ Failed to update changelog: {e}")
    
    def _create_changelog_header(self) -> str:
        """Create initial changelog header"""
        return """# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

"""
    
    # ========== Commit Tracking ==========
    
    def _load_commit_cache(self) -> set:
        """Load set of processed commit hashes"""
        cache_path = self.current_dir / self.CONFIG['commit_cache_file']
        
        if cache_path.exists():
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return set(data.get('processed', []))
            except (json.JSONDecodeError, Exception):
                return set()
        
        return set()
    
    def _mark_commit_processed(self, commit_hash: str) -> None:
        """Mark a commit as processed"""
        self.processed_commits.add(commit_hash)
        
        cache_path = self.current_dir / self.CONFIG['commit_cache_file']
        
        try:
            data = {
                'processed': list(self.processed_commits),
                'last_updated': datetime.now().isoformat()
            }
            
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        
        except Exception as e:
            print(f"⚠️  Could not save commit cache: {e}")
    
    def _get_unprocessed_commits(self, limit: int) -> List[Dict]:
        """Get commits that haven't been processed yet"""
        all_commits = self._get_commit_history(limit)
        
        # Filter out already processed
        unprocessed = [c for c in all_commits if c['hash'] not in self.processed_commits]
        
        return unprocessed
    
    # ========== Git Operations ==========
    
    def _get_commit_history(self, limit: int) -> List[Dict]:
        """Get recent commit history"""
        try:
            result = subprocess.run(
                ['git', 'log', f'-{limit}', '--pretty=format:%H|%an|%ai|%s'],
                capture_output=True,
                text=True,
                check=True,
                cwd=self.current_dir,
                encoding='utf-8',
                errors='replace'
            )
            
            commits = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('|', 3)
                    if len(parts) == 4:
                        commit_hash, author, date, message = parts
                        commits.append({
                            'hash': commit_hash,
                            'short_hash': commit_hash[:7],
                            'author': author,
                            'date': date,
                            'message': message
                        })
            
            return commits
        
        except subprocess.CalledProcessError:
            return []
    
    def _is_git_repo(self) -> bool:
        """Check if current directory is a git repository"""
        result = subprocess.run(
            ['git', 'rev-parse', '--is-inside-work-tree'],
            capture_output=True,
            text=True,
            cwd=self.current_dir
        )
        return result.returncode == 0


# ========== CLI Interface ==========

def main():
    """CLI entry point for testing"""
    import sys
    
    gen = ChangelogGenerator()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'generate':
            num_commits = int(sys.argv[2]) if len(sys.argv) > 2 else 1
            gen.generate_changelog(num_commits)
        
        elif command == 'show':
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            gen.show_unprocessed_commits(limit)
        
        elif command == 'reset':
            gen.reset_processed_commits()
        
        else:
            print(f"Unknown command: {command}")
            print("Usage: python changelog_generator.py [generate|show|reset] [number]")
    
    else:
        print("Changelog Generator")
        print("==================")
        print("\nCommands:")
        print("  generate [N]  - Generate changelog for last N commits (default: 1)")
        print("  show [N]      - Show unprocessed commits (default: 10)")
        print("  reset         - Clear processed commits cache")
        print("\nExample:")
        print("  python changelog_generator.py generate 5")


if __name__ == '__main__':
    main()