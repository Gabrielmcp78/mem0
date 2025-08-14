import Foundation

// MARK: - Factory for Creating Data Processor Components

/// Factory class for creating and configuring data processor components
class DataProcessorFactory {
    
    // MARK: - Storage Creation
    
    /// Create in-memory storage
    static func createInMemoryStorage<T>(maxCapacity: Int? = nil) -> InMemoryDataStorage<T> {
        return InMemoryDataStorage<T>(maxCapacity: maxCapacity)
    }
    
    /// Create UserDefaults-based storage
    static func createUserDefaultsStorage<T: Codable>(key: String) -> UserDefaultsStorage<T> {
        return UserDefaultsStorage<T>(key: key)
    }
    
    /// Create file-based storage
    static func createFileStorage<T: Codable>(fileName: String) throws -> FileStorage<T> {
        return try FileStorage<T>(fileName: fileName)
    }
    
    // MARK: - Processing Strategy Creation
    
    /// Create string processing strategy
    static func createStringProcessingStrategy(
        transformation: StringTransformation,
        validation: ValidationPattern? = nil
    ) -> StringProcessingStrategy {
        return StringProcessingStrategy(transformation: transformation, validation: validation)
    }
    
    /// Create composite processing strategy
    static func createCompositeStrategy<T>(
        strategies: [any ProcessingStrategyProtocol<T>]
    ) -> CompositeProcessingStrategy<T> {
        return CompositeProcessingStrategy(strategies: strategies)
    }
    
    /// Create conditional processing strategy
    static func createConditionalStrategy<T>(
        conditions: [(condition: (T) -> Bool, strategy: any ProcessingStrategyProtocol<T>)],
        defaultStrategy: (any ProcessingStrategyProtocol<T>)? = nil
    ) -> ConditionalProcessingStrategy<T> {
        return ConditionalProcessingStrategy(conditions: conditions, defaultStrategy: defaultStrategy)
    }
    
    /// Create retry processing strategy
    static func createRetryStrategy<T>(
        baseStrategy: any ProcessingStrategyProtocol<T>,
        maxRetries: Int = 3,
        retryDelay: TimeInterval = 1.0
    ) -> RetryProcessingStrategy<T> {
        return RetryProcessingStrategy(
            baseStrategy: baseStrategy,
            maxRetries: maxRetries,
            retryDelay: retryDelay
        )
    }
    
    // MARK: - Processor Creation
    
    /// Create item processor with configuration
    static func createItemProcessor<T>(
        configuration: ProcessingConfiguration = .default,
        strategy: any ProcessingStrategyProtocol<T>
    ) -> ItemProcessor<T> {
        return ItemProcessor(configuration: configuration, strategy: strategy)
    }
    
    // MARK: - Networking Creation
    
    /// Create data fetcher with configuration
    static func createDataFetcher(configuration: NetworkConfiguration = .default) -> DataFetcher {
        return DataFetcher(configuration: configuration)
    }
    
    // MARK: - Complete Data Processor Creation
    
    /// Create a complete string data processor with default configuration
    static func createStringDataProcessor(
        storageType: StorageType = .inMemory,
        transformation: StringTransformation = .uppercase,
        validation: ValidationPattern? = .notEmpty,
        configuration: ProcessingConfiguration = .default
    ) async throws -> ModernDataProcessor<String> {
        
        // Create storage
        let storage: any DataStorageProtocol<String>
        switch storageType {
        case .inMemory(let capacity):
            storage = createInMemoryStorage<String>(maxCapacity: capacity)
        case .userDefaults(let key):
            storage = createUserDefaultsStorage<String>(key: key)
        case .file(let fileName):
            storage = try createFileStorage<String>(fileName: fileName)
        }
        
        // Create processing strategy
        let strategy = createStringProcessingStrategy(
            transformation: transformation,
            validation: validation
        )
        
        // Create processor
        let processor = createItemProcessor(
            configuration: configuration,
            strategy: strategy
        )
        
        // Create data fetcher
        let fetcher = createDataFetcher()
        
        return ModernDataProcessor(
            storage: storage,
            processor: processor,
            fetcher: fetcher
        )
    }
    
    // MARK: - Preset Configurations
    
    /// Create a high-performance configuration
    static var highPerformanceConfig: ProcessingConfiguration {
        return ProcessingConfiguration(
            batchSize: 1000,
            maxConcurrentOperations: 8,
            timeoutInterval: 60.0,
            retryCount: 5
        )
    }
    
    /// Create a memory-efficient configuration
    static var memoryEfficientConfig: ProcessingConfiguration {
        return ProcessingConfiguration(
            batchSize: 50,
            maxConcurrentOperations: 2,
            timeoutInterval: 30.0,
            retryCount: 2
        )
    }
    
    /// Create a testing configuration
    static var testingConfig: ProcessingConfiguration {
        return ProcessingConfiguration(
            batchSize: 10,
            maxConcurrentOperations: 1,
            timeoutInterval: 5.0,
            retryCount: 1
        )
    }
}

// MARK: - Supporting Types

enum StorageType {
    case inMemory(maxCapacity: Int? = nil)
    case userDefaults(key: String)
    case file(fileName: String)
}