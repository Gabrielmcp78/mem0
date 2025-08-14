import Foundation

// MARK: - Core Protocols

/// Main data processor protocol defining the public interface
protocol DataProcessorProtocol {
    associatedtype Item
    
    var itemCount: Int { get }
    
    func addItem(_ item: Item)
    func processItems() async throws
    func findItem(matching predicate: (Item) -> Bool) -> Item?
    func removeItem(at index: Int) throws
    func clearAll()
}

/// Storage abstraction protocol
protocol DataStorageProtocol {
    associatedtype Item
    
    var items: [Item] { get set }
    var count: Int { get }
    
    func add(_ item: Item)
    func remove(at index: Int) throws
    func clear()
    func find(where predicate: (Item) -> Bool) -> Item?
}

/// Processing strategy protocol
protocol ProcessingStrategyProtocol {
    associatedtype Item
    
    func process(_ item: Item) async throws -> Item
    func canProcess(_ item: Item) -> Bool
}

/// Data fetching protocol
protocol DataFetcherProtocol {
    func fetchData() async throws -> String
    func fetchData(from url: URL) async throws -> Data
}