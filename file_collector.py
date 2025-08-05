#!/usr/bin/env python3
"""
File Collector Application
Collects and copies specific files to a destination based on patterns, extensions, and filters.
"""

import os
import shutil
import argparse
import json
import re
import hashlib
from pathlib import Path
from typing import List, Dict, Set, Optional
from datetime import datetime
import logging

class FileCollector:
    def __init__(self, config_file: Optional[str] = None):
        self.config = self._load_config(config_file) if config_file else {}
        self.collected_files = []
        self.errors = []
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_level = self.config.get('log_level', 'INFO')
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('file_collector.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _load_config(self, config_file: str) -> Dict:
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load config file {config_file}: {e}")
            return {}
    
    def collect_files(self, 
                     source_dirs: List[str],
                     destination: str,
                     patterns: List[str] = None,
                     extensions: List[str] = None,
                     exclude_patterns: List[str] = None,
                     min_size: int = 0,
                     max_size: int = None,
                     recursive: bool = True,
                     copy_mode: str = 'copy',
                     preserve_structure: bool = False,
                     dry_run: bool = False) -> Dict:
        """
        Collect and copy files based on specified criteria
        
        Args:
            source_dirs: List of source directories to search
            destination: Destination directory
            patterns: List of filename patterns (supports wildcards)
            extensions: List of file extensions to include
            exclude_patterns: List of patterns to exclude
            min_size: Minimum file size in bytes
            max_size: Maximum file size in bytes
            recursive: Whether to search recursively
            copy_mode: 'copy', 'move', or 'hardlink'
            preserve_structure: Whether to preserve directory structure
            dry_run: If True, only simulate the operation
        
        Returns:
            Dictionary with operation results
        """
        
        self.logger.info(f"Starting file collection from {len(source_dirs)} source directories")
        
        # Create destination directory if it doesn't exist
        if not dry_run:
            Path(destination).mkdir(parents=True, exist_ok=True)
        
        collected_files = []
        skipped_files = []
        errors = []
        
        for source_dir in source_dirs:
            if not os.path.exists(source_dir):
                error_msg = f"Source directory does not exist: {source_dir}"
                self.logger.error(error_msg)
                errors.append(error_msg)
                continue
            
            self.logger.info(f"Processing source directory: {source_dir}")
            
            # Get file list based on recursive setting
            files_to_process = self._get_files_from_directory(source_dir, recursive)
            
            for file_path in files_to_process:
                try:
                    # Apply filters
                    if self._should_include_file(file_path, patterns, extensions, exclude_patterns, min_size, max_size):
                        result = self._process_file(file_path, source_dir, destination, 
                                                  copy_mode, preserve_structure, dry_run)
                        if result['success']:
                            collected_files.append(result)
                        else:
                            errors.append(result['error'])
                    else:
                        skipped_files.append(file_path)
                        
                except Exception as e:
                    error_msg = f"Error processing file {file_path}: {str(e)}"
                    self.logger.error(error_msg)
                    errors.append(error_msg)
        
        # Generate summary
        summary = {
            'collected_count': len(collected_files),
            'skipped_count': len(skipped_files),
            'error_count': len(errors),
            'collected_files': collected_files,
            'errors': errors,
            'dry_run': dry_run,
            'timestamp': datetime.now().isoformat()
        }
        
        self.logger.info(f"Collection complete: {summary['collected_count']} files collected, "
                        f"{summary['skipped_count']} skipped, {summary['error_count']} errors")
        
        return summary
    
    def _get_files_from_directory(self, directory: str, recursive: bool) -> List[str]:
        """Get list of files from directory"""
        files = []
        if recursive:
            for root, dirs, filenames in os.walk(directory):
                for filename in filenames:
                    files.append(os.path.join(root, filename))
        else:
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                if os.path.isfile(item_path):
                    files.append(item_path)
        return files
    
    def _should_include_file(self, file_path: str, patterns: List[str], extensions: List[str],
                           exclude_patterns: List[str], min_size: int, max_size: int) -> bool:
        """Check if file should be included based on filters"""
        filename = os.path.basename(file_path)
        
        # Check file size
        try:
            file_size = os.path.getsize(file_path)
            if file_size < min_size:
                return False
            if max_size and file_size > max_size:
                return False
        except OSError:
            return False
        
        # Check exclude patterns first
        if exclude_patterns:
            for pattern in exclude_patterns:
                if self._match_pattern(filename, pattern):
                    return False
        
        # Check include patterns
        if patterns:
            pattern_match = any(self._match_pattern(filename, pattern) for pattern in patterns)
            if not pattern_match:
                return False
        
        # Check extensions
        if extensions:
            file_ext = os.path.splitext(filename)[1].lower().lstrip('.')
            if file_ext not in [ext.lower().lstrip('.') for ext in extensions]:
                return False
        
        return True
    
    def _match_pattern(self, filename: str, pattern: str) -> bool:
        """Match filename against pattern (supports wildcards)"""
        # Convert shell-style wildcards to regex
        regex_pattern = pattern.replace('*', '.*').replace('?', '.')
        return re.match(regex_pattern, filename, re.IGNORECASE) is not None
    
    def _process_file(self, file_path: str, source_dir: str, destination: str,
                     copy_mode: str, preserve_structure: bool, dry_run: bool) -> Dict:
        """Process a single file (copy, move, or hardlink)"""
        try:
            # Determine destination path
            if preserve_structure:
                rel_path = os.path.relpath(file_path, source_dir)
                dest_path = os.path.join(destination, rel_path)
                dest_dir = os.path.dirname(dest_path)
                if not dry_run:
                    Path(dest_dir).mkdir(parents=True, exist_ok=True)
            else:
                filename = os.path.basename(file_path)
                dest_path = os.path.join(destination, filename)
            
            # Handle filename conflicts
            dest_path = self._handle_filename_conflict(dest_path, dry_run)
            
            if not dry_run:
                if copy_mode == 'copy':
                    shutil.copy2(file_path, dest_path)
                elif copy_mode == 'move':
                    shutil.move(file_path, dest_path)
                elif copy_mode == 'hardlink':
                    os.link(file_path, dest_path)
                else:
                    raise ValueError(f"Invalid copy mode: {copy_mode}")
            
            return {
                'success': True,
                'source': file_path,
                'destination': dest_path,
                'size': os.path.getsize(file_path),
                'mode': copy_mode
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to process {file_path}: {str(e)}"
            }
    
    def _handle_filename_conflict(self, dest_path: str, dry_run: bool) -> str:
        """Handle filename conflicts by adding a suffix"""
        if dry_run or not os.path.exists(dest_path):
            return dest_path
        
        base, ext = os.path.splitext(dest_path)
        counter = 1
        
        while os.path.exists(dest_path):
            dest_path = f"{base}_{counter}{ext}"
            counter += 1
        
        return dest_path
    
    def generate_report(self, results: Dict, output_file: str = None) -> str:
        """Generate a detailed report of the collection operation"""
        report_lines = [
            "File Collection Report",
            "=" * 50,
            f"Timestamp: {results['timestamp']}",
            f"Dry Run: {results['dry_run']}",
            f"Files Collected: {results['collected_count']}",
            f"Files Skipped: {results['skipped_count']}",
            f"Errors: {results['error_count']}",
            "",
            "Collected Files:",
            "-" * 20
        ]
        
        for file_info in results['collected_files']:
            size_mb = file_info['size'] / (1024 * 1024)
            report_lines.append(f"✓ {file_info['source']} → {file_info['destination']} ({size_mb:.2f} MB)")
        
        if results['errors']:
            report_lines.extend([
                "",
                "Errors:",
                "-" * 10
            ])
            for error in results['errors']:
                report_lines.append(f"✗ {error}")
        
        report = "\n".join(report_lines)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report)
            self.logger.info(f"Report saved to {output_file}")
        
        return report

def create_sample_config():
    """Create a sample configuration file"""
    config = {
        "default_patterns": ["*.txt", "*.pdf", "*.docx"],
        "default_extensions": ["txt", "pdf", "docx", "jpg", "png"],
        "default_exclude_patterns": ["temp*", "*.tmp", "*.log"],
        "default_destination": "./collected_files",
        "log_level": "INFO",
        "preserve_structure": False,
        "copy_mode": "copy"
    }
    
    with open('file_collector_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("Sample configuration file created: file_collector_config.json")

def main():
    parser = argparse.ArgumentParser(description="Collect and copy specific files to destination")
    parser.add_argument('source_dirs', nargs='*', help='Source directories to search')
    parser.add_argument('-d', '--destination', help='Destination directory')
    parser.add_argument('-p', '--patterns', nargs='*', help='Filename patterns (wildcards supported)')
    parser.add_argument('-e', '--extensions', nargs='*', help='File extensions to include')
    parser.add_argument('-x', '--exclude', nargs='*', help='Patterns to exclude')
    parser.add_argument('--min-size', type=int, default=0, help='Minimum file size in bytes')
    parser.add_argument('--max-size', type=int, help='Maximum file size in bytes')
    parser.add_argument('-r', '--recursive', action='store_true', default=True, help='Search recursively')
    parser.add_argument('--no-recursive', dest='recursive', action='store_false', help='Don\'t search recursively')
    parser.add_argument('-m', '--mode', choices=['copy', 'move', 'hardlink'], default='copy', help='Copy mode')
    parser.add_argument('--preserve-structure', action='store_true', help='Preserve directory structure')
    parser.add_argument('--dry-run', action='store_true', help='Simulate operation without copying files')
    parser.add_argument('-c', '--config', help='Configuration file path')
    parser.add_argument('--report', help='Generate report file')
    parser.add_argument('--create-config', action='store_true', help='Create sample configuration file')
    
    args = parser.parse_args()
    
    if args.create_config:
        create_sample_config()
        return
    
    # Validate required arguments for collection operation
    if not args.source_dirs:
        parser.error("source_dirs is required for file collection")
    if not args.destination:
        parser.error("destination (-d/--destination) is required for file collection")
    
    collector = FileCollector(args.config)
    
    results = collector.collect_files(
        source_dirs=args.source_dirs,
        destination=args.destination,
        patterns=args.patterns,
        extensions=args.extensions,
        exclude_patterns=args.exclude,
        min_size=args.min_size,
        max_size=args.max_size,
        recursive=args.recursive,
        copy_mode=args.mode,
        preserve_structure=args.preserve_structure,
        dry_run=args.dry_run
    )
    
    # Print summary
    print(f"\nOperation completed:")
    print(f"Files collected: {results['collected_count']}")
    print(f"Files skipped: {results['skipped_count']}")
    print(f"Errors: {results['error_count']}")
    
    if args.report:
        report = collector.generate_report(results, args.report)
        print(f"\nDetailed report saved to: {args.report}")

if __name__ == "__main__":
    main()