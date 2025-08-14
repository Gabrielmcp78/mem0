import Foundation

// MARK: - Processing Strategies

/// String-specific processing strategy
struct StringProcessingStrategy: ProcessingStrategyProtocol {
    typealias Item = String
    
    private let transformation: StringTransformation
    private let validation: ValidationPattern?
    
    init(transformation: StringTransformation, validation: ValidationPattern? = nil) {
        self.transformation = transformation
        self.validation = validation
    }
    
    func process(_ item: String) async throws -> String {
        // Validate input if validation is specified
        if let validation = validation {
            guard StringProcessor.validate(item, against: validation) else {
                throw DataProcessorError.invalidItem("String failed validation")
            }
        }
        
        // Apply transformation
        return StringProcessor.processString(item, transformation: transformation)
    }
    
    func canProcess(_ item: String) -> Bool {
        if let validation = validation {
            return StringProcessor.validate(item, against: validation)
        }
        return true
    }
}

/// Composite processing strategy that applies multiple strategies in sequence
struct CompositeProcessingStrategy<T>: ProcessingStrategyProtocol {
    typealias Item = T
    
    private let strategies: [any ProcessingStrategyProtocol<T>]
    
    init(strategies: [any ProcessingStrategyProtocol<T>]) {
        self.strategies = strategies
    }
    
    func process(_ item: T) async throws -> T {
        var currentItem = item
        
        for strategy in strategies {
            guard strategy.canProcess(currentItem) else {
                throw DataProcessorError.processingFailed("Item cannot be processed by strategy in chain")
            }
            currentItem = try await strategy.process(currentItem)
        }
        
        return currentItem
    }
    
    func canProcess(_ item: T) -> Bool {
        return strategies.allSatisfy { $0.canProcess(item) }
    }
}

/// Conditional processing strategy that applies different strategies based on conditions
struct ConditionalProcessingStrategy<T>: ProcessingStrategyProtocol {
    typealias Item = T
    
    private let conditions: [(condition: (T) -> Bool, strategy: any ProcessingStrategyProtocol<T>)]
    private let defaultStrategy: (any ProcessingStrategyProtocol<T>)?
    
    init(conditions: [(condition: (T) -> Bool, strategy: any ProcessingStrategyProtocol<T>)],
         defaultStrategy: (any ProcessingStrategyProtocol<T>)? = nil) {
        self.conditions = conditions
        self.defaultStrategy = defaultStrategy
    }
    
    func process(_ item: T) async throws -> T {
        // Find the first matching condition
        for (condition, strategy) in conditions {
            if condition(item) {
                return try await strategy.process(item)
            }
        }
        
        // Use default strategy if no condition matches
        if let defaultStrategy = defaultStrategy {
            return try await defaultStrategy.process(item)
        }
        
        throw DataProcessorError.processingFailed("No suitable processing strategy found")
    }
    
    func canProcess(_ item: T) -> Bool {
        // Check if any condition matches and its strategy can process the item
        for (condition, strategy) in conditions {
            if condition(item) && strategy.canProcess(item) {
                return true
            }
        }
        
        // Check default strategy
        return defaultStrategy?.canProcess(item) ?? false
    }
}

/// Retry processing strategy that wraps another strategy with retry logic
struct RetryProcessingStrategy<T>: ProcessingStrategyProtocol {
    typealias Item = T
    
    private let baseStrategy: any ProcessingStrategyProtocol<T>
    private let maxRetries: Int
    private let retryDelay: TimeInterval
    
    init(baseStrategy: any ProcessingStrategyProtocol<T>, 
         maxRetries: Int = 3, 
         retryDelay: TimeInterval = 1.0) {
        self.baseStrategy = baseStrategy
        self.maxRetries = maxRetries
        self.retryDelay = retryDelay
    }
    
    func process(_ item: T) async throws -> T {
        var lastError: Error?
        
        for attempt in 0...maxRetries {
            do {
                return try await baseStrategy.process(item)
            } catch {
                lastError = error
                
                // Don't delay after the last attempt
                if attempt < maxRetries {
                    try await Task.sleep(nanoseconds: UInt64(retryDelay * 1_000_000_000))
                }
            }
        }
        
        throw lastError ?? DataProcessorError.processingFailed("Retry strategy failed")
    }
    
    func canProcess(_ item: T) -> Bool {
        return baseStrategy.canProcess(item)
    }
}