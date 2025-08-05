# 📁 File Collection & Copy Manager

A modern, user-friendly web application for collecting specific files from a source directory and copying them to a destination path. Built with HTML5, CSS3, JavaScript, and PHP.

## 🚀 Features

### Core Functionality
- **🔍 File Browser**: Navigate and browse files in any directory
- **✅ Multi-Selection**: Select multiple files with checkboxes
- **🎯 Advanced Filtering**: Filter by file name patterns and file types
- **📋 Batch Copy Operations**: Copy selected files to destination directory
- **📊 Real-time Progress**: Live progress tracking with progress bars
- **📄 Operation Logs**: Detailed logging of all operations
- **⚡ Status Notifications**: Real-time feedback and error handling

### File Management
- **📂 Recursive Directory Scanning**: Automatically finds files in subdirectories
- **🏷️ File Type Recognition**: Smart file type detection with appropriate icons
- **📏 File Size Display**: Human-readable file sizes (B, KB, MB, GB)
- **📅 Modification Dates**: Shows when files were last modified
- **🔄 Duplicate Handling**: Automatically renames files if duplicates exist

### User Experience
- **🎨 Modern UI**: Beautiful, responsive design with gradient backgrounds
- **📱 Mobile Responsive**: Works perfectly on desktop, tablet, and mobile
- **⌨️ Keyboard Shortcuts**: 
  - `Ctrl+A`: Select all filtered files
  - `Escape`: Clear all selections
  - `Ctrl+Enter`: Start copy operation
- **🎯 Smart Validation**: Real-time validation of paths and selections

### Security Features
- **🔒 Path Validation**: Prevents directory traversal attacks
- **🛡️ Authorized Paths Only**: Restricts access to specific directories
- **📝 Operation Logging**: All operations are logged for audit purposes
- **🚨 Error Handling**: Comprehensive error handling and reporting

## 📋 System Requirements

- **Web Server**: Apache, Nginx, or any PHP-capable server
- **PHP**: Version 7.4 or higher
- **Browser**: Modern browser with JavaScript enabled (Chrome, Firefox, Safari, Edge)
- **Permissions**: Read access to source directories, write access to destination directories

## 🛠️ Installation

1. **Clone or Download** the files to your web server directory
2. **Ensure PHP is enabled** on your web server
3. **Set appropriate file permissions**:
   ```bash
   chmod 755 /workspace/
   chmod 644 index.html app.js file_manager.php
   ```
4. **Access the application** through your web browser

## 📖 Usage Guide

### Getting Started

1. **Open the Application**
   - Navigate to `index.html` in your web browser
   - The application will initialize automatically

2. **Set Source Directory**
   - Enter the full path to your source directory (e.g., `/workspace`)
   - Click "🔄 Load Files" to scan for files

3. **Apply Filters (Optional)**
   - Use the **Name Filter** to search for specific filenames
   - Use the **Type Filter** to show only certain file types:
     - Text files (.txt)
     - PDF files (.pdf)
     - Images (.jpg, .jpeg, .png, .gif)
     - Word documents (.doc, .docx)
     - Web files (.js, .html, .css, .php)

4. **Select Files**
   - Click on individual files to select them
   - Use `Ctrl+A` to select all filtered files
   - Selected files are highlighted in blue

5. **Set Destination**
   - Enter the destination directory path
   - The directory will be created if it doesn't exist

6. **Copy Files**
   - Click "📋 Copy Selected Files" to start the operation
   - Monitor progress in the progress bar
   - View detailed logs in the operation log section

### Advanced Features

#### Keyboard Shortcuts
- **Ctrl+A**: Select all currently filtered files
- **Escape**: Clear all selections
- **Ctrl+Enter**: Start copy operation (if copy button is enabled)
- **Enter** (in source path): Load files from entered path

#### File Type Icons
The application uses intuitive icons for different file types:
- 📄 Documents (PDF, TXT, DOC)
- 📊 Spreadsheets (XLS, XLSX)
- 🖼️ Images (JPG, PNG, GIF, etc.)
- 📜 Code files (JS, HTML, CSS, PHP, PY)
- 🎵 Audio files (MP3, WAV)
- 🎬 Video files (MP4, AVI, MOV)
- 📦 Archives (ZIP, RAR, 7Z)

#### Filtering Options
- **Name Pattern**: Enter partial filename to filter (case-insensitive)
- **File Type**: Select from predefined file type categories
- **Real-time Filtering**: Results update as you type

## 🔧 Configuration

### Allowed Directories
For security, the application only allows access to specific directories. Edit `file_manager.php` to modify allowed paths:

```php
$allowedBasePaths = [
    '/workspace',
    '/tmp',
    '/var/tmp'
    // Add your allowed directories here
];
```

### Logging
Operation logs are stored in `/tmp/file_manager.log`. You can change this location in the `logOperation()` function.

### Performance Tuning
- **Batch Size**: Files are copied in batches of 5. Adjust `batchSize` in `app.js` for different performance characteristics
- **PHP Settings**: For large files, you may need to adjust PHP settings:
  ```ini
  memory_limit = 512M
  max_execution_time = 300
  upload_max_filesize = 100M
  post_max_size = 100M
  ```

## 🐛 Troubleshooting

### Common Issues

**"Directory does not exist" Error**
- Verify the source path is correct
- Ensure the directory exists and is readable
- Check file permissions

**"Destination directory is not writable" Error**
- Verify write permissions on the destination directory
- Ensure the parent directory exists
- Check disk space availability

**Files Not Loading**
- Check if the directory contains files
- Verify PHP is working correctly
- Check browser console for JavaScript errors
- Review operation logs for detailed error messages

**Copy Operation Fails**
- Verify destination path permissions
- Check available disk space
- Ensure source files are readable
- Review the operation log for specific file errors

### Debugging

1. **Check Browser Console**: Press F12 and look for JavaScript errors
2. **Review PHP Logs**: Check your web server's PHP error logs
3. **Operation Logs**: Check `/tmp/file_manager.log` for detailed operation history
4. **Network Tab**: Use browser dev tools to inspect API requests/responses

## 🔒 Security Considerations

- **Path Validation**: All paths are sanitized and validated
- **Directory Restrictions**: Only specific directories are accessible
- **No Path Traversal**: Protection against `../` attacks
- **Input Sanitization**: All user inputs are properly sanitized
- **Error Handling**: Secure error messages that don't reveal system information

## 📝 API Documentation

The backend API accepts POST requests with JSON data:

### List Files
```json
{
    "action": "list_files",
    "path": "/path/to/directory"
}
```

### Copy Files
```json
{
    "action": "copy_files",
    "files": ["/path/to/file1", "/path/to/file2"],
    "destination": "/path/to/destination"
}
```

### System Info
```json
{
    "action": "system_info"
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙋‍♂️ Support

For support, please:
1. Check the troubleshooting section
2. Review the operation logs
3. Create an issue with detailed information about the problem

---

**Built with ❤️ for efficient file management**