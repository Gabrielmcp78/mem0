import Foundation

// MARK: - Storage Implementations

/// Thread-safe in-memory storage implementation
actor InMemoryDataStorage<T>: DataStorageProtocol {
    typealias Item = T
    
    private var _items: [T] = []
    private let maxCapacity: Int?
    
    init(maxCapacity: Int? = nil) {
        self.maxCapacity = maxCapacity
    }
    
    var items: [T] {
        get { _items }
        set { _items = newValue }
    }
    
    var count: Int {
        _items.count
    }
    
    func add(_ item: T) {
        // Check capacity limit
        if let maxCapacity = maxCapacity, _items.count >= maxCapacity {
            // Remove oldest item to make space
            _items.removeFirst()
        }
        _items.append(item)
    }
    
    func remove(at index: Int) throws {
        guard index >= 0 && index < _items.count else {
            throw DataProcessorError.storageError(.indexOutOfBounds)
        }
        _items.remove(at: index)
    }
    
    func clear() {
        _items.removeAll()
    }
    
    func find(where predicate: (T) -> Bool) -> T? {
        return _items.first(where: predicate)
    }
    
    func findAll(where predicate: (T) -> Bool) -> [T] {
        return _items.filter(predicate)
    }
    
    func update(at index: Int, with item: T) throws {
        guard index >= 0 && index < _items.count else {
            throw DataProcessorError.storageError(.indexOutOfBounds)
        }
        _items[index] = item
    }
    
    func contains(where predicate: (T) -> Bool) -> Bool {
        return _items.contains(where: predicate)
    }
}

/// Persistent storage implementation using UserDefaults (for simple data)
class UserDefaultsStorage<T: Codable>: DataStorageProtocol {
    typealias Item = T
    
    private let key: String
    private let userDefaults: UserDefaults
    
    init(key: String, userDefaults: UserDefaults = .standard) {
        self.key = key
        self.userDefaults = userDefaults
    }
    
    var items: [T] {
        get {
            guard let data = userDefaults.data(forKey: key) else { return [] }
            return (try? JSONDecoder().decode([T].self, from: data)) ?? []
        }
        set {
            let data = try? JSONEncoder().encode(newValue)
            userDefaults.set(data, forKey: key)
        }
    }
    
    var count: Int {
        items.count
    }
    
    func add(_ item: T) {
        var currentItems = items
        currentItems.append(item)
        items = currentItems
    }
    
    func remove(at index: Int) throws {
        var currentItems = items
        guard index >= 0 && index < currentItems.count else {
            throw DataProcessorError.storageError(.indexOutOfBounds)
        }
        currentItems.remove(at: index)
        items = currentItems
    }
    
    func clear() {
        items = []
    }
    
    func find(where predicate: (T) -> Bool) -> T? {
        return items.first(where: predicate)
    }
}

/// File-based persistent storage implementation
class FileStorage<T: Codable>: DataStorageProtocol {
    typealias Item = T
    
    private let fileURL: URL
    private let fileManager = FileManager.default
    private let encoder = JSONEncoder()
    private let decoder = JSONDecoder()
    
    init(fileName: String) throws {
        let documentsDirectory = try fileManager.url(
            for: .documentDirectory,
            in: .userDomainMask,
            appropriateFor: nil,
            create: true
        )
        self.fileURL = documentsDirectory.appendingPathComponent(fileName)
        
        // Create file if it doesn't exist
        if !fileManager.fileExists(atPath: fileURL.path) {
            let emptyData = try encoder.encode([T]())
            try emptyData.write(to: fileURL)
        }
    }
    
    var items: [T] {
        get {
            do {
                let data = try Data(contentsOf: fileURL)
                return try decoder.decode([T].self, from: data)
            } catch {
                return []
            }
        }
        set {
            do {
                let data = try encoder.encode(newValue)
                try data.write(to: fileURL)
            } catch {
                // Handle error appropriately in production
                print("Failed to save items: \(error)")
            }
        }
    }
    
    var count: Int {
        items.count
    }
    
    func add(_ item: T) {
        var currentItems = items
        currentItems.append(item)
        items = currentItems
    }
    
    func remove(at index: Int) throws {
        var currentItems = items
        guard index >= 0 && index < currentItems.count else {
            throw DataProcessorError.storageError(.indexOutOfBounds)
        }
        currentItems.remove(at: index)
        items = currentItems
    }
    
    func clear() {
        items = []
    }
    
    func find(where predicate: (T) -> Bool) -> T? {
        return items.first(where: predicate)
    }
}