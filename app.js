// File Collector Web Interface
class FileCollectorApp {
    constructor() {
        this.selectedFiles = [];
        this.init();
    }

    init() {
        this.createInterface();
        this.bindEvents();
    }

    createInterface() {
        const appContainer = document.getElementById('file-collector-app');
        if (!appContainer) return;

        appContainer.innerHTML = `
            <div class="file-collector-container">
                <h2>File Collector</h2>
                
                <div class="section">
                    <h3>Source Selection</h3>
                    <div class="form-group">
                        <label for="file-input">Select Files:</label>
                        <input type="file" id="file-input" multiple webkitdirectory>
                        <button id="add-files-btn">Add Individual Files</button>
                    </div>
                    
                    <div class="form-group">
                        <label for="source-path">Or enter source path:</label>
                        <input type="text" id="source-path" placeholder="/path/to/source/directory">
                    </div>
                </div>

                <div class="section">
                    <h3>Filters</h3>
                    <div class="form-row">
                        <div class="form-group">
                            <label for="file-patterns">File Patterns:</label>
                            <input type="text" id="file-patterns" placeholder="*.txt, *.pdf, *.jpg" 
                                   title="Comma-separated patterns with wildcards">
                        </div>
                        
                        <div class="form-group">
                            <label for="file-extensions">Extensions:</label>
                            <input type="text" id="file-extensions" placeholder="txt, pdf, jpg" 
                                   title="Comma-separated extensions">
                        </div>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label for="exclude-patterns">Exclude Patterns:</label>
                            <input type="text" id="exclude-patterns" placeholder="temp*, *.tmp" 
                                   title="Comma-separated exclude patterns">
                        </div>
                        
                        <div class="form-group">
                            <label for="size-filter">Size Filter (MB):</label>
                            <input type="number" id="min-size" placeholder="Min" min="0" step="0.1">
                            <input type="number" id="max-size" placeholder="Max" min="0" step="0.1">
                        </div>
                    </div>
                </div>

                <div class="section">
                    <h3>Destination & Options</h3>
                    <div class="form-group">
                        <label for="destination-path">Destination Directory:</label>
                        <input type="text" id="destination-path" placeholder="/path/to/destination" required>
                        <button id="select-destination-btn">Browse</button>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label for="copy-mode">Copy Mode:</label>
                            <select id="copy-mode">
                                <option value="copy">Copy</option>
                                <option value="move">Move</option>
                                <option value="hardlink">Hard Link</option>
                            </select>
                        </div>
                        
                        <div class="form-group checkbox-group">
                            <label>
                                <input type="checkbox" id="preserve-structure"> Preserve Directory Structure
                            </label>
                            <label>
                                <input type="checkbox" id="recursive" checked> Recursive Search
                            </label>
                            <label>
                                <input type="checkbox" id="dry-run"> Dry Run (Preview Only)
                            </label>
                        </div>
                    </div>
                </div>

                <div class="section">
                    <div class="action-buttons">
                        <button id="preview-btn" class="btn-secondary">Preview Selection</button>
                        <button id="collect-btn" class="btn-primary">Collect Files</button>
                        <button id="generate-command-btn" class="btn-secondary">Generate CLI Command</button>
                    </div>
                </div>

                <div class="section">
                    <div id="results-container" style="display: none;">
                        <h3>Results</h3>
                        <div id="results-content"></div>
                    </div>
                </div>

                <div class="section">
                    <div id="file-list-container" style="display: none;">
                        <h3>Selected Files</h3>
                        <div id="file-list"></div>
                    </div>
                </div>
            </div>
        `;
    }

    bindEvents() {
        // File input handling
        const fileInput = document.getElementById('file-input');
        const addFilesBtn = document.getElementById('add-files-btn');
        
        if (fileInput) {
            fileInput.addEventListener('change', (e) => this.handleFileSelection(e));
        }
        
        if (addFilesBtn) {
            addFilesBtn.addEventListener('click', () => this.addIndividualFiles());
        }

        // Button events
        const previewBtn = document.getElementById('preview-btn');
        const collectBtn = document.getElementById('collect-btn');
        const generateCommandBtn = document.getElementById('generate-command-btn');
        const selectDestinationBtn = document.getElementById('select-destination-btn');

        if (previewBtn) {
            previewBtn.addEventListener('click', () => this.previewSelection());
        }
        
        if (collectBtn) {
            collectBtn.addEventListener('click', () => this.collectFiles());
        }
        
        if (generateCommandBtn) {
            generateCommandBtn.addEventListener('click', () => this.generateCliCommand());
        }
        
        if (selectDestinationBtn) {
            selectDestinationBtn.addEventListener('click', () => this.selectDestination());
        }
    }

    handleFileSelection(event) {
        const files = Array.from(event.target.files);
        this.selectedFiles = files;
        this.displaySelectedFiles();
    }

    addIndividualFiles() {
        const input = document.createElement('input');
        input.type = 'file';
        input.multiple = true;
        input.addEventListener('change', (e) => {
            const newFiles = Array.from(e.target.files);
            this.selectedFiles = [...this.selectedFiles, ...newFiles];
            this.displaySelectedFiles();
        });
        input.click();
    }

    displaySelectedFiles() {
        const container = document.getElementById('file-list-container');
        const fileList = document.getElementById('file-list');
        
        if (!container || !fileList) return;

        if (this.selectedFiles.length === 0) {
            container.style.display = 'none';
            return;
        }

        container.style.display = 'block';
        
        const filesHtml = this.selectedFiles.map((file, index) => {
            const sizeKB = (file.size / 1024).toFixed(2);
            return `
                <div class="file-item">
                    <span class="file-name">${file.name}</span>
                    <span class="file-size">${sizeKB} KB</span>
                    <span class="file-path">${file.webkitRelativePath || 'Individual file'}</span>
                    <button class="remove-file-btn" data-index="${index}">Remove</button>
                </div>
            `;
        }).join('');

        fileList.innerHTML = `
            <div class="file-list-header">
                <span>Name</span>
                <span>Size</span>
                <span>Path</span>
                <span>Action</span>
            </div>
            ${filesHtml}
        `;

        // Add remove file functionality
        fileList.querySelectorAll('.remove-file-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const index = parseInt(e.target.dataset.index);
                this.selectedFiles.splice(index, 1);
                this.displaySelectedFiles();
            });
        });
    }

    previewSelection() {
        const filters = this.getFilters();
        const filteredFiles = this.applyFilters(this.selectedFiles, filters);
        
        this.displayResults({
            preview: true,
            totalFiles: this.selectedFiles.length,
            filteredFiles: filteredFiles.length,
            files: filteredFiles.slice(0, 100), // Show first 100 for preview
            filters: filters
        });
    }

    getFilters() {
        const patterns = this.getInputValue('file-patterns').split(',').map(s => s.trim()).filter(s => s);
        const extensions = this.getInputValue('file-extensions').split(',').map(s => s.trim()).filter(s => s);
        const excludePatterns = this.getInputValue('exclude-patterns').split(',').map(s => s.trim()).filter(s => s);
        const minSize = parseFloat(this.getInputValue('min-size')) * 1024 * 1024 || 0; // Convert MB to bytes
        const maxSize = parseFloat(this.getInputValue('max-size')) * 1024 * 1024 || null;

        return {
            patterns,
            extensions,
            excludePatterns,
            minSize,
            maxSize,
            copyMode: this.getInputValue('copy-mode'),
            preserveStructure: document.getElementById('preserve-structure')?.checked || false,
            recursive: document.getElementById('recursive')?.checked || true,
            dryRun: document.getElementById('dry-run')?.checked || false
        };
    }

    getInputValue(id) {
        const element = document.getElementById(id);
        return element ? element.value : '';
    }

    applyFilters(files, filters) {
        return files.filter(file => {
            // Size filter
            if (file.size < filters.minSize) return false;
            if (filters.maxSize && file.size > filters.maxSize) return false;

            // Extension filter
            if (filters.extensions.length > 0) {
                const fileExt = file.name.split('.').pop()?.toLowerCase();
                if (!filters.extensions.some(ext => ext.toLowerCase() === fileExt)) return false;
            }

            // Pattern filter
            if (filters.patterns.length > 0) {
                if (!filters.patterns.some(pattern => this.matchPattern(file.name, pattern))) return false;
            }

            // Exclude patterns
            if (filters.excludePatterns.length > 0) {
                if (filters.excludePatterns.some(pattern => this.matchPattern(file.name, pattern))) return false;
            }

            return true;
        });
    }

    matchPattern(filename, pattern) {
        // Convert shell-style wildcards to regex
        const regexPattern = pattern.replace(/\*/g, '.*').replace(/\?/g, '.');
        const regex = new RegExp(`^${regexPattern}$`, 'i');
        return regex.test(filename);
    }

    collectFiles() {
        const destination = this.getInputValue('destination-path');
        if (!destination) {
            alert('Please specify a destination directory');
            return;
        }

        const filters = this.getFilters();
        const filteredFiles = this.applyFilters(this.selectedFiles, filters);

        if (filteredFiles.length === 0) {
            alert('No files match the specified criteria');
            return;
        }

        // Since this is a web interface, we'll simulate the collection
        // In a real implementation, this would require a backend service
        this.simulateFileCollection(filteredFiles, destination, filters);
    }

    simulateFileCollection(files, destination, filters) {
        const results = {
            preview: false,
            collected: files.length,
            destination: destination,
            mode: filters.copyMode,
            dryRun: filters.dryRun,
            files: files.map(file => ({
                name: file.name,
                size: file.size,
                source: file.webkitRelativePath || file.name,
                destination: `${destination}/${file.name}`
            }))
        };

        this.displayResults(results);
    }

    displayResults(results) {
        const container = document.getElementById('results-container');
        const content = document.getElementById('results-content');
        
        if (!container || !content) return;

        container.style.display = 'block';
        
        let html = `
            <div class="results-summary">
                <h4>${results.preview ? 'Preview Results' : 'Collection Results'}</h4>
                <p><strong>Files ${results.preview ? 'to be processed' : 'processed'}:</strong> ${results.preview ? results.filteredFiles : results.collected}</p>
                ${!results.preview ? `<p><strong>Destination:</strong> ${results.destination}</p>` : ''}
                ${!results.preview ? `<p><strong>Mode:</strong> ${results.mode}</p>` : ''}
                ${results.dryRun ? '<p><strong>Note:</strong> This was a dry run - no files were actually copied</p>' : ''}
            </div>
        `;

        if (results.files && results.files.length > 0) {
            html += `
                <div class="results-files">
                    <h5>Files:</h5>
                    <div class="file-results-list">
                        ${results.files.map(file => `
                            <div class="file-result-item">
                                <span class="file-name">${file.name}</span>
                                <span class="file-size">${(file.size / 1024).toFixed(2)} KB</span>
                                ${!results.preview ? `<span class="file-destination">${file.destination}</span>` : ''}
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }

        content.innerHTML = html;
    }

    selectDestination() {
        // In a real web app, this would use a directory picker API or backend service
        const destination = prompt('Enter destination directory path:');
        if (destination) {
            document.getElementById('destination-path').value = destination;
        }
    }

    generateCliCommand() {
        const sourcePath = this.getInputValue('source-path') || './';
        const destination = this.getInputValue('destination-path') || './collected_files';
        const filters = this.getFilters();

        let command = `python3 file_collector.py "${sourcePath}" -d "${destination}"`;

        if (filters.patterns.length > 0) {
            command += ` -p ${filters.patterns.map(p => `"${p}"`).join(' ')}`;
        }

        if (filters.extensions.length > 0) {
            command += ` -e ${filters.extensions.join(' ')}`;
        }

        if (filters.excludePatterns.length > 0) {
            command += ` -x ${filters.excludePatterns.map(p => `"${p}"`).join(' ')}`;
        }

        if (filters.minSize > 0) {
            command += ` --min-size ${filters.minSize}`;
        }

        if (filters.maxSize) {
            command += ` --max-size ${filters.maxSize}`;
        }

        if (!filters.recursive) {
            command += ' --no-recursive';
        }

        if (filters.copyMode !== 'copy') {
            command += ` -m ${filters.copyMode}`;
        }

        if (filters.preserveStructure) {
            command += ' --preserve-structure';
        }

        if (filters.dryRun) {
            command += ' --dry-run';
        }

        command += ' --report collection_report.txt';

        // Display the command
        const modal = this.createCommandModal(command);
        document.body.appendChild(modal);
    }

    createCommandModal(command) {
        const modal = document.createElement('div');
        modal.className = 'command-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Generated CLI Command</h3>
                    <button class="close-btn">&times;</button>
                </div>
                <div class="modal-body">
                    <p>Copy and run this command in your terminal:</p>
                    <div class="command-container">
                        <code id="cli-command">${command}</code>
                        <button id="copy-command-btn">Copy</button>
                    </div>
                </div>
            </div>
        `;

        // Add event listeners
        modal.querySelector('.close-btn').addEventListener('click', () => {
            document.body.removeChild(modal);
        });

        modal.querySelector('#copy-command-btn').addEventListener('click', () => {
            navigator.clipboard.writeText(command).then(() => {
                alert('Command copied to clipboard!');
            });
        });

        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                document.body.removeChild(modal);
            }
        });

        return modal;
    }
}

// Initialize the app when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Check if we're on the file collector page
    if (document.getElementById('file-collector-app')) {
        new FileCollectorApp();
    }
});