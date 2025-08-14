import Foundation

// MARK: - Type Definitions

/// Configuration for data processing operations
struct ProcessingConfiguration {
    let batchSize: Int
    let maxConcurrentOperations: Int
    let timeoutInterval: TimeInterval
    let retryCount: Int
    
    static let `default` = ProcessingConfiguration(
        batchSize: 100,
        maxConcurrentOperations: 4,
        timeoutInterval: 30.0,
        retryCount: 3
    )
}

/// Result of a processing operation
enum ProcessingResult<T> {
    case success(T)
    case failure(DataProcessorError)
    case partial([T], [DataProcessorError])
    
    var isSuccess: Bool {
        switch self {
        case .success:
            return true
        case .failure, .partial:
            return false
        }
    }
    
    var value: T? {
        switch self {
        case .success(let value):
            return value
        case .failure, .partial:
            return nil
        }
    }
}

/// Processing statistics
struct ProcessingStatistics {
    let totalItems: Int
    let processedItems: Int
    let failedItems: Int
    let processingTime: TimeInterval
    let averageTimePerItem: TimeInterval
    
    var successRate: Double {
        guard totalItems > 0 else { return 0.0 }
        return Double(processedItems) / Double(totalItems)
    }
}

/// Item metadata for tracking processing state
struct ItemMetadata {
    let id: UUID
    let createdAt: Date
    var lastProcessed: Date?
    var processingCount: Int
    var isProcessed: Bool
    
    init() {
        self.id = UUID()
        self.createdAt = Date()
        self.lastProcessed = nil
        self.processingCount = 0
        self.isProcessed = false
    }
}