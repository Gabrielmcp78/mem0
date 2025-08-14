import Foundation

// MARK: - Item Processing

/// Generic item processor with async support and error handling
actor ItemProcessor<T> {
    private let configuration: ProcessingConfiguration
    private let strategy: any ProcessingStrategyProtocol<T>
    private var statistics = ProcessingStatistics(
        totalItems: 0,
        processedItems: 0,
        failedItems: 0,
        processingTime: 0,
        averageTimePerItem: 0
    )
    
    init(configuration: ProcessingConfiguration = .default, 
         strategy: any ProcessingStrategyProtocol<T>) {
        self.configuration = configuration
        self.strategy = strategy
    }
    
    // MARK: - Processing Methods
    
    /// Process a single item asynchronously
    func processItem(_ item: T) async throws -> T {
        let startTime = Date()
        
        guard strategy.canProcess(item) else {
            throw DataProcessorError.processingFailed("Item cannot be processed by current strategy")
        }
        
        do {
            let processedItem = try await strategy.process(item)
            updateStatistics(success: true, processingTime: Date().timeIntervalSince(startTime))
            return processedItem
        } catch {
            updateStatistics(success: false, processingTime: Date().timeIntervalSince(startTime))
            throw DataProcessorError.processingFailed(error.localizedDescription)
        }
    }
    
    /// Process multiple items with concurrency control
    func processItems(_ items: [T]) async -> ProcessingResult<[T]> {
        let startTime = Date()
        var processedItems: [T] = []
        var errors: [DataProcessorError] = []
        
        // Process in batches to control memory usage
        let batches = items.chunked(into: configuration.batchSize)
        
        for batch in batches {
            let batchResults = await withTaskGroup(of: (T?, DataProcessorError?).self) { group in
                // Limit concurrent operations
                let semaphore = AsyncSemaphore(value: configuration.maxConcurrentOperations)
                
                for item in batch {
                    group.addTask {
                        await semaphore.wait()
                        defer { semaphore.signal() }
                        
                        do {
                            let processed = try await self.processItem(item)
                            return (processed, nil)
                        } catch let error as DataProcessorError {
                            return (nil, error)
                        } catch {
                            return (nil, DataProcessorError.processingFailed(error.localizedDescription))
                        }
                    }
                }
                
                var results: [(T?, DataProcessorError?)] = []
                for await result in group {
                    results.append(result)
                }
                return results
            }
            
            // Collect results
            for (item, error) in batchResults {
                if let item = item {
                    processedItems.append(item)
                } else if let error = error {
                    errors.append(error)
                }
            }
        }
        
        let totalTime = Date().timeIntervalSince(startTime)
        updateBatchStatistics(
            total: items.count,
            processed: processedItems.count,
            failed: errors.count,
            totalTime: totalTime
        )
        
        // Return appropriate result
        if errors.isEmpty {
            return .success(processedItems)
        } else if processedItems.isEmpty {
            return .failure(errors.first ?? DataProcessorError.processingFailed("Unknown error"))
        } else {
            return .partial(processedItems, errors)
        }
    }
    
    // MARK: - Statistics
    
    func getStatistics() -> ProcessingStatistics {
        return statistics
    }
    
    private func updateStatistics(success: Bool, processingTime: TimeInterval) {
        let newTotal = statistics.totalItems + 1
        let newProcessed = success ? statistics.processedItems + 1 : statistics.processedItems
        let newFailed = success ? statistics.failedItems : statistics.failedItems + 1
        let newTotalTime = statistics.processingTime + processingTime
        
        statistics = ProcessingStatistics(
            totalItems: newTotal,
            processedItems: newProcessed,
            failedItems: newFailed,
            processingTime: newTotalTime,
            averageTimePerItem: newTotalTime / Double(newTotal)
        )
    }
    
    private func updateBatchStatistics(total: Int, processed: Int, failed: Int, totalTime: TimeInterval) {
        let newTotal = statistics.totalItems + total
        let newProcessed = statistics.processedItems + processed
        let newFailed = statistics.failedItems + failed
        let newTotalTime = statistics.processingTime + totalTime
        
        statistics = ProcessingStatistics(
            totalItems: newTotal,
            processedItems: newProcessed,
            failedItems: newFailed,
            processingTime: newTotalTime,
            averageTimePerItem: newTotal > 0 ? newTotalTime / Double(newTotal) : 0
        )
    }
}

// MARK: - Supporting Types

/// Simple semaphore for async concurrency control
actor AsyncSemaphore {
    private var value: Int
    private var waiters: [CheckedContinuation<Void, Never>] = []
    
    init(value: Int) {
        self.value = value
    }
    
    func wait() async {
        if value > 0 {
            value -= 1
        } else {
            await withCheckedContinuation { continuation in
                waiters.append(continuation)
            }
        }
    }
    
    func signal() {
        if let waiter = waiters.first {
            waiters.removeFirst()
            waiter.resume()
        } else {
            value += 1
        }
    }
}