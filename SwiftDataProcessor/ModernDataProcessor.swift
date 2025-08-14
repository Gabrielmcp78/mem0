import Foundation

// MARK: - Modern Data Processor Implementation

/// Modern, modular data processor that replaces the original monolithic class
class ModernDataProcessor<T>: DataProcessorProtocol {
    typealias Item = T
    
    // MARK: - Dependencies
    
    private let storage: any DataStorageProtocol<T>
    private let processor: ItemProcessor<T>
    private let fetcher: DataFetcher
    
    // MARK: - Initialization
    
    init(storage: any DataStorageProtocol<T>,
         processor: ItemProcessor<T>,
         fetcher: DataFetcher) {
        self.storage = storage
        self.processor = processor
        self.fetcher = fetcher
    }
    
    // MARK: - DataProcessorProtocol Implementation
    
    var itemCount: Int {
        return storage.count
    }
    
    func addItem(_ item: T) {
        storage.add(item)
    }
    
    func processItems() async throws {
        let items = storage.items
        guard !items.isEmpty else {
            throw DataProcessorError.emptyStorage
        }
        
        let result = await processor.processItems(items)
        
        switch result {
        case .success(let processedItems):
            // Replace all items with processed versions
            storage.clear()
            processedItems.forEach { storage.add($0) }
            
        case .failure(let error):
            throw error
            
        case .partial(let processedItems, let errors):
            // Replace with successfully processed items
            storage.clear()
            processedItems.forEach { storage.add($0) }
            
            // Log errors (in production, use proper logging)
            print("Processing completed with \(errors.count) errors:")
            errors.forEach { print("- \(error.localizedDescription)") }
        }
    }
    
    func findItem(matching predicate: (T) -> Bool) -> T? {
        return storage.find(where: predicate)
    }
    
    func removeItem(at index: Int) throws {
        try storage.remove(at: index)
    }
    
    func clearAll() {
        storage.clear()
    }
    
    // MARK: - Additional Methods
    
    /// Get all items
    func getAllItems() -> [T] {
        return storage.items
    }
    
    /// Find all items matching predicate
    func findAllItems(matching predicate: (T) -> Bool) -> [T] {
        return storage.items.filter(predicate)
    }
    
    /// Process a single item without affecting storage
    func processSingleItem(_ item: T) async throws -> T {
        return try await processor.processItem(item)
    }
    
    /// Get processing statistics
    func getProcessingStatistics() async -> ProcessingStatistics {
        return await processor.getStatistics()
    }
    
    /// Fetch data using the data fetcher
    func fetchData() async throws -> String {
        return try await fetcher.fetchData()
    }
    
    /// Fetch data from URL
    func fetchData(from url: URL) async throws -> Data {
        return try await fetcher.fetchData(from: url)
    }
    
    /// Update item at specific index
    func updateItem(at index: Int, with item: T) throws {
        guard let storage = storage as? InMemoryDataStorage<T> else {
            throw DataProcessorError.storageError(.storageCorrupted)
        }
        
        Task {
            try await storage.update(at: index, with: item)
        }
    }
    
    /// Check if storage contains item matching predicate
    func contains(where predicate: (T) -> Bool) -> Bool {
        return storage.items.contains(where: predicate)
    }
    
    /// Get item at specific index safely
    func item(at index: Int) -> T? {
        return storage.items[safe: index]
    }
}

// MARK: - Convenience Initializers

extension ModernDataProcessor where T == String {
    /// Convenience initializer for string processing
    static func createStringProcessor(
        transformation: StringTransformation = .uppercase,
        validation: ValidationPattern? = .notEmpty,
        storageType: StorageType = .inMemory(),
        configuration: ProcessingConfiguration = .default
    ) async throws -> ModernDataProcessor<String> {
        
        return try await DataProcessorFactory.createStringDataProcessor(
            storageType: storageType,
            transformation: transformation,
            validation: validation,
            configuration: configuration
        )
    }
}

// MARK: - Usage Examples

extension ModernDataProcessor {
    /// Example usage demonstrating the modern approach
    static func exampleUsage() async {
        do {
            // Create a modern string processor
            let processor = try await ModernDataProcessor<String>.createStringProcessor(
                transformation: .uppercase,
                validation: .minLength(1),
                storageType: .inMemory(maxCapacity: 1000),
                configuration: DataProcessorFactory.highPerformanceConfig
            )
            
            // Add items
            processor.addItem("hello")
            processor.addItem("world")
            processor.addItem("swift")
            
            print("Added \(processor.itemCount) items")
            
            // Process all items
            try await processor.processItems()
            
            // Get results
            let processedItems = processor.getAllItems()
            print("Processed items: \(processedItems)")
            
            // Find specific item
            if let foundItem = processor.findItem(matching: { $0.contains("HELLO") }) {
                print("Found item: \(foundItem)")
            }
            
            // Fetch external data
            let fetchedData = try await processor.fetchData()
            print("Fetched data: \(fetchedData)")
            
            // Get statistics
            let stats = await processor.getProcessingStatistics()
            print("Processing statistics: \(stats)")
            
        } catch {
            print("Error: \(error.localizedDescription)")
        }
    }
}