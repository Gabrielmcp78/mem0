import Foundation

// MARK: - Collection Extensions

extension Array {
    /// Split array into chunks of specified size
    func chunked(into size: Int) -> [[Element]] {
        return stride(from: 0, to: count, by: size).map {
            Array(self[$0..<Swift.min($0 + size, count)])
        }
    }
    
    /// Safe subscript that returns nil for out-of-bounds access
    subscript(safe index: Int) -> Element? {
        return indices.contains(index) ? self[index] : nil
    }
    
    /// Remove elements matching a predicate
    @discardableResult
    mutating func removeAll(where predicate: (Element) throws -> Bool) rethrows -> [Element] {
        let removed = try filter(predicate)
        try removeAll(where: predicate)
        return removed
    }
}

extension Collection {
    /// Check if collection is not empty
    var isNotEmpty: Bool {
        return !isEmpty
    }
    
    /// Safe access to first and last elements
    var safeFirst: Element? {
        return isEmpty ? nil : first
    }
    
    var safeLast: Element? {
        return isEmpty ? nil : last
    }
}

// MARK: - String Extensions

extension String {
    /// Efficient string validation
    var isNotEmpty: Bool {
        return !isEmpty
    }
    
    var trimmed: String {
        return trimmingCharacters(in: .whitespacesAndNewlines)
    }
    
    /// Safe substring operations
    func safeSubstring(from index: Int, length: Int) -> String? {
        guard index >= 0, index < count, length > 0 else { return nil }
        
        let startIndex = self.index(self.startIndex, offsetBy: index)
        let endIndex = self.index(startIndex, offsetBy: min(length, count - index))
        
        return String(self[startIndex..<endIndex])
    }
    
    /// Efficient character counting for specific characters
    func count(of character: Character) -> Int {
        return reduce(0) { $1 == character ? $0 + 1 : $0 }
    }
    
    /// Safe character access
    subscript(safe index: Int) -> Character? {
        guard index >= 0 && index < count else { return nil }
        return self[self.index(startIndex, offsetBy: index)]
    }
}

// MARK: - Date Extensions

extension Date {
    /// Formatted string for display
    func formatted(style: DateFormatter.Style = .medium) -> String {
        let formatter = DateFormatter()
        formatter.dateStyle = style
        formatter.timeStyle = style
        return formatter.string(from: self)
    }
    
    /// Check if date is within a time interval from now
    func isWithin(_ interval: TimeInterval, of date: Date = Date()) -> Bool {
        return abs(timeIntervalSince(date)) <= interval
    }
}

// MARK: - Result Extensions

extension Result {
    /// Convert Result to optional value
    var value: Success? {
        switch self {
        case .success(let value):
            return value
        case .failure:
            return nil
        }
    }
    
    /// Convert Result to optional error
    var error: Failure? {
        switch self {
        case .success:
            return nil
        case .failure(let error):
            return error
        }
    }
    
    /// Check if result is success
    var isSuccess: Bool {
        switch self {
        case .success:
            return true
        case .failure:
            return false
        }
    }
}

// MARK: - Task Extensions

extension Task where Success == Never, Failure == Never {
    /// Sleep for a specified time interval
    static func sleep(seconds: TimeInterval) async throws {
        try await sleep(nanoseconds: UInt64(seconds * 1_000_000_000))
    }
}