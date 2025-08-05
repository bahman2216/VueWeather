# File Collector Application

A comprehensive file collection and management tool that helps you collect, filter, and copy specific files to destination directories. Available as both a command-line application and a web interface.

## Features

- **Multiple Source Support**: Collect files from multiple source directories
- **Advanced Filtering**: Filter files by patterns, extensions, size, and exclude rules
- **Flexible Copy Modes**: Copy, move, or create hard links
- **Directory Structure**: Option to preserve original directory structure
- **Dry Run Mode**: Preview operations before executing
- **Comprehensive Logging**: Detailed logs and error reporting
- **Web Interface**: User-friendly browser-based interface
- **CLI Command Generation**: Generate command-line commands from web interface
- **Configuration Files**: Save and reuse filter configurations

## Installation

No special installation required. The application uses only Python standard library modules.

### Requirements
- Python 3.6+
- Modern web browser (for web interface)

## Usage

### Command Line Interface

#### Basic Usage
```bash
# Copy all files from source to destination
python3 file_collector.py /path/to/source -d /path/to/destination

# Copy files with specific extensions
python3 file_collector.py /path/to/source -d /path/to/destination -e txt pdf docx

# Copy files matching patterns
python3 file_collector.py /path/to/source -d /path/to/destination -p "*.log" "report_*"

# Exclude certain patterns
python3 file_collector.py /path/to/source -d /path/to/destination -x "temp*" "*.tmp"
```

#### Advanced Usage
```bash
# Copy files with size filtering (sizes in bytes)
python3 file_collector.py /path/to/source -d /path/to/destination --min-size 1048576 --max-size 104857600

# Move files instead of copying
python3 file_collector.py /path/to/source -d /path/to/destination -m move

# Preserve directory structure
python3 file_collector.py /path/to/source -d /path/to/destination --preserve-structure

# Dry run (preview without copying)
python3 file_collector.py /path/to/source -d /path/to/destination --dry-run

# Generate detailed report
python3 file_collector.py /path/to/source -d /path/to/destination --report collection_report.txt

# Use configuration file
python3 file_collector.py /path/to/source -d /path/to/destination -c file_collector_config.json
```

#### Multiple Sources
```bash
# Collect from multiple source directories
python3 file_collector.py /source1 /source2 /source3 -d /destination
```

#### Command Line Options

| Option | Description |
|--------|-------------|
| `source_dirs` | Source directories to search (required) |
| `-d, --destination` | Destination directory (required) |
| `-p, --patterns` | Filename patterns with wildcards (e.g., "*.txt", "report_*") |
| `-e, --extensions` | File extensions to include (e.g., txt, pdf, jpg) |
| `-x, --exclude` | Patterns to exclude |
| `--min-size` | Minimum file size in bytes |
| `--max-size` | Maximum file size in bytes |
| `-r, --recursive` | Search recursively (default: True) |
| `--no-recursive` | Don't search recursively |
| `-m, --mode` | Copy mode: copy, move, or hardlink (default: copy) |
| `--preserve-structure` | Preserve directory structure |
| `--dry-run` | Simulate operation without copying files |
| `-c, --config` | Configuration file path |
| `--report` | Generate detailed report file |
| `--create-config` | Create sample configuration file |

### Web Interface

1. Open `file_collector.html` in your web browser
2. Use the interface to:
   - Select source files or enter source paths
   - Set up filters and options
   - Preview your selection
   - Execute the collection
   - Generate CLI commands

#### Web Interface Features
- **File Selection**: Upload files or browse directories
- **Visual Filtering**: Interactive filter setup
- **Preview Mode**: See which files will be processed
- **Results Display**: Visual feedback on operations
- **CLI Generation**: Export settings as command-line commands

### Configuration Files

Create a configuration file to save commonly used settings:

```bash
# Create sample configuration
python3 file_collector.py --create-config
```

Sample configuration (`file_collector_config.json`):
```json
{
  "default_patterns": ["*.txt", "*.pdf", "*.docx"],
  "default_extensions": ["txt", "pdf", "docx", "jpg", "png"],
  "default_exclude_patterns": ["temp*", "*.tmp", "*.log"],
  "default_destination": "./collected_files",
  "log_level": "INFO",
  "preserve_structure": false,
  "copy_mode": "copy"
}
```

## Examples

### Example 1: Collect All Images
```bash
python3 file_collector.py ~/Pictures -d ~/backup/images -e jpg jpeg png gif bmp
```

### Example 2: Backup Documents with Size Limit
```bash
python3 file_collector.py ~/Documents -d ~/backup/docs \
  -e pdf docx txt \
  --max-size 50000000 \
  --preserve-structure \
  --report backup_report.txt
```

### Example 3: Clean Temporary Files (Move to Trash)
```bash
python3 file_collector.py /var/log -d ~/trash \
  -p "*.log" "*.tmp" \
  --min-size 0 \
  -m move \
  --dry-run
```

### Example 4: Collect Source Code Files
```bash
python3 file_collector.py ~/projects -d ~/backup/source \
  -e py js html css \
  -x "node_modules*" "*.pyc" "__pycache__*" \
  --preserve-structure
```

## File Pattern Matching

The application supports shell-style wildcards:

- `*` - Matches any sequence of characters
- `?` - Matches any single character
- `*.txt` - All files ending with .txt
- `report_*` - All files starting with "report_"
- `data_?.csv` - Files like data_1.csv, data_a.csv, etc.

## Output and Logging

### Console Output
- Real-time progress information
- Summary statistics
- Error reporting

### Log Files
- Detailed operation logs saved to `file_collector.log`
- Configurable log levels (DEBUG, INFO, WARNING, ERROR)

### Reports
- Optional detailed reports in text format
- Include file lists, sizes, and operation results
- Useful for auditing and documentation

## Error Handling

The application handles various error conditions:
- Missing source directories
- Permission issues
- Disk space problems
- Network drive connectivity
- Filename conflicts (automatically resolved with suffixes)

## Performance Considerations

- **Large Directories**: Use specific patterns to limit scope
- **Network Drives**: May be slower; consider local staging
- **Disk Space**: Monitor destination disk space
- **File Conflicts**: Automatic renaming prevents overwrites

## Troubleshooting

### Common Issues

1. **Permission Denied**
   - Ensure read access to source directories
   - Ensure write access to destination directory

2. **File Not Found**
   - Verify source paths exist
   - Check for typos in patterns

3. **Disk Space**
   - Check available space in destination
   - Use `--dry-run` to estimate space requirements

4. **Pattern Matching**
   - Test patterns with small datasets first
   - Use verbose logging for debugging

### Debug Mode
Enable detailed logging by modifying the configuration file:
```json
{
  "log_level": "DEBUG"
}
```

## Security Considerations

- Always review `--dry-run` output before actual operations
- Be cautious with `move` mode as it removes source files
- Validate destination paths to prevent accidental overwrites
- Use exclude patterns to avoid sensitive files

## Contributing

Feel free to enhance the application with additional features:
- Additional file filters
- More copy modes
- Integration with cloud storage
- Database logging
- GUI improvements

## License

This project is provided as-is for educational and practical use.

---

## Quick Start

1. **Create sample config**: `python3 file_collector.py --create-config`
2. **Test with dry run**: `python3 file_collector.py /source -d /dest --dry-run`
3. **Open web interface**: Open `file_collector.html` in your browser
4. **Generate reports**: Add `--report filename.txt` to any command