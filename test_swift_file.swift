import Foundation

// REFACTORED: This file has been refactored into a modular architecture
//
// The functionality has been moved to:
// - SwiftDataProcessor/ - New modular package with focused components
// - SwiftDataProcessor/REFACTORING_GUIDE.md - Comprehensive refactoring guide
//
// For new development, use the modular components:
//   let processor = try await ModernDataProcessor<String>.createStringProcessor()
//
// This file is maintained for backward compatibility only.

/// Legacy DataProcessor - DEPRECATED
/// Use ModernDataProcessor from SwiftDataProcessor package instead
class DataProcessor {
    private var modernProcessor: ModernDataProcessor<String>?
    
    var items: [String] = [] {
        didSet {
            // Sync with modern processor
            Task {
                await syncWithModernProcessor()
            }
        }
    }
    
    init() {
        print("⚠️  Using deprecated DataProcessor - consider upgrading to ModernDataProcessor")
        print("   New usage: try await ModernDataProcessor<String>.createStringProcessor()")
        
        // Initialize modern processor asynchronously
        Task {
            do {
                self.modernProcessor = try await ModernDataProcessor<String>.createStringProcessor(
                    transformation: .uppercase,
                    validation: .notEmpty,
                    storageType: .inMemory(),
                    configuration: .default
                )
            } catch {
                print("Failed to initialize modern processor: \(error)")
            }
        }
    }
    
    func processItems() {
        Task {
            await processItemsAsync()
        }
    }
    
    private func processItemsAsync() async {
        guard let processor = modernProcessor else {
            // Fallback to old implementation
            processItemsLegacy()
            return
        }
        
        do {
            // Sync items to modern processor
            await syncWithModernProcessor()
            
            // Use modern processing
            try await processor.processItems()
            
            // Sync back to legacy items array
            items = processor.getAllItems()
            
        } catch {
            print("Modern processing failed, falling back to legacy: \(error)")
            processItemsLegacy()
        }
    }
    
    private func processItemsLegacy() {
        // Original inefficient implementation (kept for compatibility)
        for i in 0..<items.count {
            let item = items[i]
            print("Processing: \(item)")
            // Inefficient string concatenation
            var result = ""
            for char in item {
                result = result + String(char)
            }
            items[i] = result.uppercased()
        }
    }
    
    func findItem(name: String) -> String? {
        if let processor = modernProcessor {
            return processor.findItem(matching: { $0 == name })
        } else {
            // Fallback to legacy implementation
            return items.first { $0 == name }
        }
    }
    
    // Old-style completion handler (deprecated)
    func fetchData(completion: @escaping (String?) -> Void) {
        Task {
            if let processor = modernProcessor {
                do {
                    let data = try await processor.fetchData()
                    completion(data)
                } catch {
                    completion(nil)
                }
            } else {
                // Fallback to legacy implementation
                DispatchQueue.global().async {
                    Thread.sleep(forTimeInterval: 1.0)
                    completion("Sample data")
                }
            }
        }
    }
    
    // Modern async version
    func fetchData() async throws -> String {
        guard let processor = modernProcessor else {
            throw DataProcessorError.processingFailed("Modern processor not available")
        }
        return try await processor.fetchData()
    }
    
    private func syncWithModernProcessor() async {
        guard let processor = modernProcessor else { return }
        
        processor.clearAll()
        for item in items {
            processor.addItem(item)
        }
    }
}

// MARK: - Migration Examples

extension DataProcessor {
    /// Example showing how to migrate to the modern approach
    static func migrationExample() async {
        print("=== DataProcessor Migration Example ===")
        
        // Old way (still works but deprecated)
        let legacyProcessor = DataProcessor()
        legacyProcessor.items = ["hello", "world", "swift"]
        legacyProcessor.processItems()
        
        // New way (recommended)
        do {
            let modernProcessor = try await ModernDataProcessor<String>.createStringProcessor(
                transformation: .uppercase,
                validation: .minLength(1),
                storageType: .inMemory(maxCapacity: 1000),
                configuration: DataProcessorFactory.highPerformanceConfig
            )
            
            // Add items
            modernProcessor.addItem("hello")
            modernProcessor.addItem("world")
            modernProcessor.addItem("swift")
            
            // Process with modern async approach
            try await modernProcessor.processItems()
            
            // Get results
            let results = modernProcessor.getAllItems()
            print("Modern processing results: \(results)")
            
            // Get statistics
            let stats = await modernProcessor.getProcessingStatistics()
            print("Processing statistics: \(stats)")
            
        } catch {
            print("Modern processing error: \(error)")
        }
    }
}