import Foundation

// MARK: - String Processing

/// Efficient string processing operations
struct StringProcessor {
    
    // MARK: - Processing Methods
    
    /// Efficiently process string with various transformations
    static func processString(_ input: String, transformation: StringTransformation) -> String {
        switch transformation {
        case .uppercase:
            return input.uppercased()
        case .lowercase:
            return input.lowercased()
        case .capitalized:
            return input.capitalized
        case .reversed:
            return String(input.reversed())
        case .trimmed:
            return input.trimmingCharacters(in: .whitespacesAndNewlines)
        case .custom(let transform):
            return transform(input)
        }
    }
    
    /// Efficient string concatenation using StringBuilder pattern
    static func efficientConcatenation(of strings: [String], separator: String = "") -> String {
        guard !strings.isEmpty else { return "" }
        
        // Pre-calculate capacity for efficiency
        let totalLength = strings.reduce(0) { $0 + $1.count } + (separator.count * (strings.count - 1))
        var result = ""
        result.reserveCapacity(totalLength)
        
        for (index, string) in strings.enumerated() {
            if index > 0 {
                result += separator
            }
            result += string
        }
        
        return result
    }
    
    /// Process string character by character efficiently
    static func processCharacters(in string: String, transform: (Character) -> Character) -> String {
        return String(string.map(transform))
    }
    
    /// Validate string against common patterns
    static func validate(_ string: String, against pattern: ValidationPattern) -> Bool {
        switch pattern {
        case .notEmpty:
            return !string.isEmpty
        case .minLength(let min):
            return string.count >= min
        case .maxLength(let max):
            return string.count <= max
        case .regex(let pattern):
            return string.range(of: pattern, options: .regularExpression) != nil
        case .custom(let validator):
            return validator(string)
        }
    }
}

// MARK: - Supporting Types

enum StringTransformation {
    case uppercase
    case lowercase
    case capitalized
    case reversed
    case trimmed
    case custom((String) -> String)
}

enum ValidationPattern {
    case notEmpty
    case minLength(Int)
    case maxLength(Int)
    case regex(String)
    case custom((String) -> Bool)
}