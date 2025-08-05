<?php
/**
 * File Collection & Copy Manager - Backend API
 * Handles file listing and copying operations
 */

// Enable error reporting for debugging
error_reporting(E_ALL);
ini_set('display_errors', 1);

// Set content type to JSON
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, GET, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

// Handle preflight requests
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

/**
 * Security and validation functions
 */
function sanitizePath($path) {
    // Remove any potential path traversal attempts
    $path = str_replace(['../', '..\\', '../', '..\\'], '', $path);
    $path = realpath($path);
    return $path;
}

function isPathAllowed($path) {
    // Only allow paths within specific directories for security
    $allowedBasePaths = [
        '/workspace',
        '/tmp',
        '/var/tmp'
    ];
    
    foreach ($allowedBasePaths as $basePath) {
        if (strpos($path, $basePath) === 0) {
            return true;
        }
    }
    return false;
}

function sendJsonResponse($data, $statusCode = 200) {
    http_response_code($statusCode);
    echo json_encode($data);
    exit();
}

function logOperation($message, $type = 'INFO') {
    $timestamp = date('Y-m-d H:i:s');
    $logMessage = "[$timestamp] [$type] $message" . PHP_EOL;
    file_put_contents('/tmp/file_manager.log', $logMessage, FILE_APPEND | LOCK_EX);
}

/**
 * File operations
 */
function listFiles($directory) {
    // Sanitize and validate path
    $directory = sanitizePath($directory);
    if (!$directory || !isPathAllowed($directory)) {
        return ['success' => false, 'error' => 'Invalid or unauthorized directory path'];
    }
    
    if (!is_dir($directory)) {
        return ['success' => false, 'error' => 'Directory does not exist'];
    }
    
    if (!is_readable($directory)) {
        return ['success' => false, 'error' => 'Directory is not readable'];
    }
    
    try {
        $files = [];
        $iterator = new RecursiveIteratorIterator(
            new RecursiveDirectoryIterator($directory, RecursiveDirectoryIterator::SKIP_DOTS),
            RecursiveIteratorIterator::LEAVES_ONLY
        );
        
        foreach ($iterator as $file) {
            if ($file->isFile()) {
                $filePath = $file->getRealPath();
                $relativePath = str_replace($directory . DIRECTORY_SEPARATOR, '', $filePath);
                
                $files[] = [
                    'name' => $file->getFilename(),
                    'path' => $filePath,
                    'relative_path' => $relativePath,
                    'size' => $file->getSize(),
                    'modified' => date('Y-m-d H:i:s', $file->getMTime()),
                    'extension' => strtolower($file->getExtension()),
                    'is_readable' => $file->isReadable()
                ];
            }
        }
        
        // Sort files by name
        usort($files, function($a, $b) {
            return strcasecmp($a['name'], $b['name']);
        });
        
        logOperation("Listed " . count($files) . " files from directory: $directory");
        
        return [
            'success' => true,
            'files' => $files,
            'total_count' => count($files),
            'directory' => $directory
        ];
        
    } catch (Exception $e) {
        logOperation("Error listing files from $directory: " . $e->getMessage(), 'ERROR');
        return ['success' => false, 'error' => 'Error reading directory: ' . $e->getMessage()];
    }
}

function copyFiles($filePaths, $destination) {
    // Sanitize and validate destination
    $destination = sanitizePath($destination);
    if (!$destination || !isPathAllowed($destination)) {
        return ['success' => false, 'error' => 'Invalid or unauthorized destination path'];
    }
    
    // Create destination directory if it doesn't exist
    if (!is_dir($destination)) {
        if (!mkdir($destination, 0755, true)) {
            logOperation("Failed to create destination directory: $destination", 'ERROR');
            return ['success' => false, 'error' => 'Could not create destination directory'];
        }
        logOperation("Created destination directory: $destination");
    }
    
    if (!is_writable($destination)) {
        return ['success' => false, 'error' => 'Destination directory is not writable'];
    }
    
    $copiedFiles = [];
    $failedFiles = [];
    $totalSize = 0;
    
    foreach ($filePaths as $sourcePath) {
        // Sanitize and validate source path
        $sourcePath = sanitizePath($sourcePath);
        if (!$sourcePath || !isPathAllowed($sourcePath)) {
            $failedFiles[] = ['path' => $sourcePath, 'error' => 'Invalid or unauthorized source path'];
            continue;
        }
        
        if (!file_exists($sourcePath)) {
            $failedFiles[] = ['path' => $sourcePath, 'error' => 'Source file does not exist'];
            continue;
        }
        
        if (!is_readable($sourcePath)) {
            $failedFiles[] = ['path' => $sourcePath, 'error' => 'Source file is not readable'];
            continue;
        }
        
        $filename = basename($sourcePath);
        $destinationPath = $destination . DIRECTORY_SEPARATOR . $filename;
        
        // Handle filename conflicts
        $counter = 1;
        $originalDestinationPath = $destinationPath;
        while (file_exists($destinationPath)) {
            $pathInfo = pathinfo($originalDestinationPath);
            $destinationPath = $pathInfo['dirname'] . DIRECTORY_SEPARATOR . 
                              $pathInfo['filename'] . '_' . $counter . 
                              (isset($pathInfo['extension']) ? '.' . $pathInfo['extension'] : '');
            $counter++;
        }
        
        try {
            if (copy($sourcePath, $destinationPath)) {
                $fileSize = filesize($sourcePath);
                $totalSize += $fileSize;
                
                $copiedFiles[] = [
                    'original_name' => $filename,
                    'copied_name' => basename($destinationPath),
                    'source_path' => $sourcePath,
                    'destination_path' => $destinationPath,
                    'size' => $fileSize
                ];
                
                logOperation("Copied file: $sourcePath -> $destinationPath (" . formatBytes($fileSize) . ")");
            } else {
                $failedFiles[] = ['path' => $sourcePath, 'error' => 'Copy operation failed'];
                logOperation("Failed to copy file: $sourcePath", 'ERROR');
            }
        } catch (Exception $e) {
            $failedFiles[] = ['path' => $sourcePath, 'error' => $e->getMessage()];
            logOperation("Exception copying file $sourcePath: " . $e->getMessage(), 'ERROR');
        }
    }
    
    $response = [
        'success' => true,
        'copied_count' => count($copiedFiles),
        'failed_count' => count($failedFiles),
        'total_size' => $totalSize,
        'total_size_formatted' => formatBytes($totalSize),
        'copied_files' => array_column($copiedFiles, 'copied_name'),
        'destination' => $destination
    ];
    
    if (!empty($failedFiles)) {
        $response['failed_files'] = $failedFiles;
        $response['warnings'] = 'Some files could not be copied';
    }
    
    logOperation("Copy operation completed: " . count($copiedFiles) . " files copied, " . 
                count($failedFiles) . " failed, total size: " . formatBytes($totalSize));
    
    return $response;
}

function formatBytes($bytes, $precision = 2) {
    $units = array('B', 'KB', 'MB', 'GB', 'TB');
    
    for ($i = 0; $bytes > 1024 && $i < count($units) - 1; $i++) {
        $bytes /= 1024;
    }
    
    return round($bytes, $precision) . ' ' . $units[$i];
}

function getSystemInfo() {
    return [
        'success' => true,
        'system_info' => [
            'php_version' => PHP_VERSION,
            'server_time' => date('Y-m-d H:i:s'),
            'upload_max_filesize' => ini_get('upload_max_filesize'),
            'post_max_size' => ini_get('post_max_size'),
            'memory_limit' => ini_get('memory_limit'),
            'max_execution_time' => ini_get('max_execution_time'),
            'disk_free_space' => formatBytes(disk_free_space('/')),
            'disk_total_space' => formatBytes(disk_total_space('/'))
        ]
    ];
}

/**
 * Main request handler
 */
try {
    // Get request data
    $input = file_get_contents('php://input');
    $requestData = json_decode($input, true);
    
    if (!$requestData) {
        sendJsonResponse(['success' => false, 'error' => 'Invalid JSON data'], 400);
    }
    
    $action = $requestData['action'] ?? '';
    
    logOperation("Received request: $action");
    
    switch ($action) {
        case 'list_files':
            $path = $requestData['path'] ?? '';
            if (empty($path)) {
                sendJsonResponse(['success' => false, 'error' => 'Path parameter is required'], 400);
            }
            $result = listFiles($path);
            sendJsonResponse($result);
            break;
            
        case 'copy_files':
            $files = $requestData['files'] ?? [];
            $destination = $requestData['destination'] ?? '';
            
            if (empty($files) || empty($destination)) {
                sendJsonResponse(['success' => false, 'error' => 'Files and destination parameters are required'], 400);
            }
            
            $result = copyFiles($files, $destination);
            sendJsonResponse($result);
            break;
            
        case 'system_info':
            $result = getSystemInfo();
            sendJsonResponse($result);
            break;
            
        default:
            sendJsonResponse(['success' => false, 'error' => 'Invalid action'], 400);
    }
    
} catch (Exception $e) {
    logOperation("Unhandled exception: " . $e->getMessage(), 'ERROR');
    sendJsonResponse([
        'success' => false, 
        'error' => 'Internal server error: ' . $e->getMessage()
    ], 500);
}
?>