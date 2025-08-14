import Foundation

// MARK: - Error Types

/// Comprehensive error handling for data processing operations
enum DataProcessorError: LocalizedError, Equatable {
    case invalidIndex(Int)
    case emptyStorage
    case processingFailed(String)
    case networkError(NetworkError)
    case storageError(StorageError)
    case invalidItem(String)
    
    var errorDescription: String? {
        switch self {
        case .invalidIndex(let index):
            return "Invalid index: \(index)"
        case .emptyStorage:
            return "Storage is empty"
        case .processingFailed(let reason):
            return "Processing failed: \(reason)"
        case .networkError(let networkError):
            return "Network error: \(networkError.localizedDescription)"
        case .storageError(let storageError):
            return "Storage error: \(storageError.localizedDescription)"
        case .invalidItem(let description):
            return "Invalid item: \(description)"
        }
    }
}

/// Network-specific errors
enum NetworkError: LocalizedError, Equatable {
    case invalidURL
    case noConnection
    case timeout
    case serverError(Int)
    case decodingFailed
    
    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "Invalid URL provided"
        case .noConnection:
            return "No network connection available"
        case .timeout:
            return "Request timed out"
        case .serverError(let code):
            return "Server error with code: \(code)"
        case .decodingFailed:
            return "Failed to decode response"
        }
    }
}

/// Storage-specific errors
enum StorageError: LocalizedError, Equatable {
    case indexOutOfBounds
    case itemNotFound
    case storageCorrupted
    case insufficientSpace
    
    var errorDescription: String? {
        switch self {
        case .indexOutOfBounds:
            return "Index is out of bounds"
        case .itemNotFound:
            return "Item not found in storage"
        case .storageCorrupted:
            return "Storage data is corrupted"
        case .insufficientSpace:
            return "Insufficient storage space"
        }
    }
}