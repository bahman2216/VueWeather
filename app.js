// File Collection & Copy Manager - Frontend JavaScript
class FileManager {
    constructor() {
        this.selectedFiles = new Set();
        this.allFiles = [];
        this.filteredFiles = [];
        this.isLoading = false;
        this.copyInProgress = false;
        
        this.initializeEventListeners();
        this.addLogEntry('[System] File Manager initialized successfully');
    }
    
    initializeEventListeners() {
        // Source path enter key support
        document.getElementById('sourcePath').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.loadFiles();
            }
        });
        
        // Destination path validation
        document.getElementById('destPath').addEventListener('input', () => {
            this.updateCopyButtonState();
        });
    }
    
    addLogEntry(message, type = 'info') {
        const logContainer = document.getElementById('logContainer');
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = document.createElement('div');
        logEntry.className = 'log-entry';
        
        const typePrefix = {
            'info': '[Info]',
            'success': '[Success]',
            'error': '[Error]',
            'warning': '[Warning]'
        };
        
        logEntry.textContent = `${timestamp} ${typePrefix[type]} ${message}`;
        logContainer.appendChild(logEntry);
        logContainer.scrollTop = logContainer.scrollHeight;
        
        // Keep only last 100 log entries
        while (logContainer.children.length > 100) {
            logContainer.removeChild(logContainer.firstChild);
        }
    }
    
    showStatus(message, type = 'info', duration = 5000) {
        const statusContainer = document.getElementById('statusContainer');
        const statusDiv = document.createElement('div');
        statusDiv.className = `status-message status-${type}`;
        statusDiv.textContent = message;
        
        statusContainer.appendChild(statusDiv);
        
        // Auto-remove after duration
        setTimeout(() => {
            if (statusDiv.parentNode) {
                statusDiv.parentNode.removeChild(statusDiv);
            }
        }, duration);
    }
    
    async loadFiles() {
        if (this.isLoading) return;
        
        const sourcePath = document.getElementById('sourcePath').value.trim();
        if (!sourcePath) {
            this.showStatus('Please enter a source directory path', 'error');
            return;
        }
        
        this.isLoading = true;
        this.addLogEntry(`Loading files from: ${sourcePath}`);
        
        const fileBrowser = document.getElementById('fileBrowser');
        fileBrowser.innerHTML = '<div style="padding: 40px; text-align: center;"><div class="loading"></div>Loading files...</div>';
        
        try {
            const response = await fetch('file_manager.php', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    action: 'list_files',
                    path: sourcePath
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.allFiles = result.files;
                this.filteredFiles = [...this.allFiles];
                this.renderFileList();
                this.addLogEntry(`Loaded ${this.allFiles.length} files successfully`, 'success');
                this.showStatus(`Found ${this.allFiles.length} files`, 'success');
            } else {
                throw new Error(result.error || 'Failed to load files');
            }
        } catch (error) {
            this.addLogEntry(`Error loading files: ${error.message}`, 'error');
            this.showStatus(`Error: ${error.message}`, 'error');
            fileBrowser.innerHTML = `<div style="padding: 40px; text-align: center; color: #e74c3c;">
                <div>❌ Error loading files</div>
                <div style="font-size: 14px; margin-top: 10px;">${error.message}</div>
            </div>`;
        } finally {
            this.isLoading = false;
        }
    }
    
    renderFileList() {
        const fileBrowser = document.getElementById('fileBrowser');
        
        if (this.filteredFiles.length === 0) {
            fileBrowser.innerHTML = '<div style="padding: 40px; text-align: center; color: #7f8c8d;">No files found matching current filters</div>';
            return;
        }
        
        const fileListHTML = this.filteredFiles.map(file => {
            const isSelected = this.selectedFiles.has(file.path);
            const fileIcon = this.getFileIcon(file.name);
            const fileSize = this.formatFileSize(file.size);
            
            return `
                <div class="file-item ${isSelected ? 'selected' : ''}" onclick="fileManager.toggleFileSelection('${file.path}')">
                    <input type="checkbox" class="file-checkbox" ${isSelected ? 'checked' : ''} onclick="event.stopPropagation()">
                    <div class="file-icon">${fileIcon}</div>
                    <div class="file-info">
                        <div class="file-name">${file.name}</div>
                        <div class="file-details">${fileSize} • Modified: ${file.modified}</div>
                    </div>
                </div>
            `;
        }).join('');
        
        fileBrowser.innerHTML = fileListHTML;
        this.updateSelectedCount();
    }
    
    getFileIcon(filename) {
        const ext = filename.toLowerCase().split('.').pop();
        const iconMap = {
            // Documents
            'pdf': '📄',
            'doc': '📝', 'docx': '📝',
            'txt': '📄', 'rtf': '📄',
            'xls': '📊', 'xlsx': '📊',
            'ppt': '📽️', 'pptx': '📽️',
            
            // Images
            'jpg': '🖼️', 'jpeg': '🖼️', 'png': '🖼️', 
            'gif': '🖼️', 'bmp': '🖼️', 'svg': '🖼️',
            
            // Code
            'js': '📜', 'html': '🌐', 'css': '🎨',
            'php': '🐘', 'py': '🐍', 'java': '☕',
            'cpp': '⚡', 'c': '⚡', 'h': '⚡',
            
            // Archives
            'zip': '📦', 'rar': '📦', '7z': '📦',
            'tar': '📦', 'gz': '📦',
            
            // Media
            'mp3': '🎵', 'wav': '🎵', 'mp4': '🎬',
            'avi': '🎬', 'mov': '🎬', 'mkv': '🎬',
            
            // Default
            'folder': '📁'
        };
        
        return iconMap[ext] || '📄';
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }
    
    toggleFileSelection(filePath) {
        if (this.selectedFiles.has(filePath)) {
            this.selectedFiles.delete(filePath);
        } else {
            this.selectedFiles.add(filePath);
        }
        
        this.renderFileList();
        this.updateCopyButtonState();
        this.addLogEntry(`${this.selectedFiles.has(filePath) ? 'Selected' : 'Deselected'} file: ${filePath.split('/').pop()}`);
    }
    
    updateSelectedCount() {
        const selectedCount = document.getElementById('selectedCount');
        const count = this.selectedFiles.size;
        selectedCount.textContent = `${count} file${count !== 1 ? 's' : ''} selected`;
    }
    
    updateCopyButtonState() {
        const copyBtn = document.getElementById('copyBtn');
        const destPath = document.getElementById('destPath').value.trim();
        const hasSelection = this.selectedFiles.size > 0;
        const hasDestination = destPath.length > 0;
        
        copyBtn.disabled = !hasSelection || !hasDestination || this.copyInProgress;
        
        if (!hasSelection) {
            copyBtn.textContent = '📋 Select files to copy';
        } else if (!hasDestination) {
            copyBtn.textContent = '📋 Set destination path';
        } else if (this.copyInProgress) {
            copyBtn.textContent = '📋 Copying files...';
        } else {
            copyBtn.textContent = `📋 Copy ${this.selectedFiles.size} selected file${this.selectedFiles.size !== 1 ? 's' : ''}`;
        }
    }
    
    applyFilters() {
        const nameFilter = document.getElementById('nameFilter').value.toLowerCase().trim();
        const typeFilter = document.getElementById('typeFilter').value;
        
        this.filteredFiles = this.allFiles.filter(file => {
            // Name filter
            const nameMatch = !nameFilter || file.name.toLowerCase().includes(nameFilter);
            
            // Type filter
            let typeMatch = true;
            if (typeFilter) {
                const extensions = typeFilter.split(',');
                typeMatch = extensions.some(ext => file.name.toLowerCase().endsWith(ext.toLowerCase()));
            }
            
            return nameMatch && typeMatch;
        });
        
        this.renderFileList();
        this.addLogEntry(`Applied filters: ${this.filteredFiles.length} files shown`);
    }
    
    async startCopy() {
        if (this.copyInProgress || this.selectedFiles.size === 0) return;
        
        const destPath = document.getElementById('destPath').value.trim();
        if (!destPath) {
            this.showStatus('Please enter a destination directory', 'error');
            return;
        }
        
        this.copyInProgress = true;
        this.updateCopyButtonState();
        
        // Show progress section
        const progressSection = document.getElementById('progressSection');
        progressSection.classList.remove('hidden');
        
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');
        
        const selectedFilesArray = Array.from(this.selectedFiles);
        this.addLogEntry(`Starting copy operation: ${selectedFilesArray.length} files to ${destPath}`, 'info');
        
        try {
            let completedFiles = 0;
            const totalFiles = selectedFilesArray.length;
            
            progressText.textContent = `Preparing to copy ${totalFiles} files...`;
            
            // Copy files in batches for better performance
            const batchSize = 5;
            for (let i = 0; i < selectedFilesArray.length; i += batchSize) {
                const batch = selectedFilesArray.slice(i, i + batchSize);
                
                const response = await fetch('file_manager.php', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        action: 'copy_files',
                        files: batch,
                        destination: destPath
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    completedFiles += result.copied_count;
                    const progress = (completedFiles / totalFiles) * 100;
                    
                    progressFill.style.width = `${progress}%`;
                    progressText.textContent = `Copied ${completedFiles} of ${totalFiles} files (${Math.round(progress)}%)`;
                    
                    // Log individual file copies
                    if (result.copied_files) {
                        result.copied_files.forEach(filename => {
                            this.addLogEntry(`Copied: ${filename}`, 'success');
                        });
                    }
                } else {
                    throw new Error(result.error || 'Copy operation failed');
                }
                
                // Small delay between batches to prevent overwhelming the server
                if (i + batchSize < selectedFilesArray.length) {
                    await new Promise(resolve => setTimeout(resolve, 100));
                }
            }
            
            // Success
            progressFill.style.width = '100%';
            progressText.textContent = `✅ Successfully copied ${completedFiles} files!`;
            
            this.addLogEntry(`Copy operation completed: ${completedFiles} files copied to ${destPath}`, 'success');
            this.showStatus(`Successfully copied ${completedFiles} files to ${destPath}`, 'success');
            
            // Clear selection after successful copy
            this.selectedFiles.clear();
            this.renderFileList();
            
        } catch (error) {
            this.addLogEntry(`Copy operation failed: ${error.message}`, 'error');
            this.showStatus(`Copy failed: ${error.message}`, 'error');
            progressText.textContent = `❌ Copy failed: ${error.message}`;
        } finally {
            this.copyInProgress = false;
            this.updateCopyButtonState();
            
            // Hide progress section after 3 seconds
            setTimeout(() => {
                progressSection.classList.add('hidden');
                progressFill.style.width = '0%';
            }, 3000);
        }
    }
}

// Global functions for HTML onclick handlers
let fileManager;

function loadFiles() {
    fileManager.loadFiles();
}

function applyFilters() {
    fileManager.applyFilters();
}

function startCopy() {
    fileManager.startCopy();
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    fileManager = new FileManager();
});

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + A to select all filtered files
    if ((e.ctrlKey || e.metaKey) && e.key === 'a' && e.target.tagName !== 'INPUT') {
        e.preventDefault();
        fileManager.filteredFiles.forEach(file => {
            fileManager.selectedFiles.add(file.path);
        });
        fileManager.renderFileList();
        fileManager.updateCopyButtonState();
        fileManager.addLogEntry(`Selected all ${fileManager.filteredFiles.length} filtered files`);
    }
    
    // Escape to clear selection
    if (e.key === 'Escape') {
        fileManager.selectedFiles.clear();
        fileManager.renderFileList();
        fileManager.updateCopyButtonState();
        fileManager.addLogEntry('Cleared all selections');
    }
    
    // Enter to start copy when copy button is enabled
    if (e.key === 'Enter' && e.ctrlKey && !document.getElementById('copyBtn').disabled) {
        fileManager.startCopy();
    }
});