import Foundation

// MARK: - Modern Networking with Async/Await

/// Modern data fetcher using async/await and proper error handling
actor DataFetcher: DataFetcherProtocol {
    private let session: URLSession
    private let configuration: NetworkConfiguration
    
    init(configuration: NetworkConfiguration = .default) {
        self.configuration = configuration
        
        let sessionConfig = URLSessionConfiguration.default
        sessionConfig.timeoutIntervalForRequest = configuration.timeoutInterval
        sessionConfig.timeoutIntervalForResource = configuration.resourceTimeout
        
        self.session = URLSession(configuration: sessionConfig)
    }
    
    // MARK: - Public Methods
    
    /// Fetch sample data (replaces the old completion handler approach)
    func fetchData() async throws -> String {
        // Simulate network delay
        try await Task.sleep(nanoseconds: UInt64(configuration.simulatedDelay * 1_000_000_000))
        
        // Simulate potential network failure
        if configuration.simulateFailure && Bool.random() {
            throw NetworkError.serverError(500)
        }
        
        return "Sample data fetched at \(Date().formatted())"
    }
    
    /// Fetch data from a specific URL
    func fetchData(from url: URL) async throws -> Data {
        do {
            let (data, response) = try await session.data(from: url)
            
            guard let httpResponse = response as? HTTPURLResponse else {
                throw NetworkError.serverError(0)
            }
            
            guard 200...299 ~= httpResponse.statusCode else {
                throw NetworkError.serverError(httpResponse.statusCode)
            }
            
            return data
            
        } catch let error as NetworkError {
            throw error
        } catch {
            if error.localizedDescription.contains("timeout") {
                throw NetworkError.timeout
            } else if error.localizedDescription.contains("network") {
                throw NetworkError.noConnection
            } else {
                throw NetworkError.serverError(0)
            }
        }
    }
    
    /// Fetch and decode JSON data
    func fetchDecodable<T: Decodable>(from url: URL, as type: T.Type) async throws -> T {
        let data = try await fetchData(from: url)
        
        do {
            let decoder = JSONDecoder()
            decoder.dateDecodingStrategy = .iso8601
            return try decoder.decode(type, from: data)
        } catch {
            throw NetworkError.decodingFailed
        }
    }
    
    /// Fetch data with retry logic
    func fetchDataWithRetry(from url: URL, maxRetries: Int = 3) async throws -> Data {
        var lastError: Error?
        
        for attempt in 0...maxRetries {
            do {
                return try await fetchData(from: url)
            } catch {
                lastError = error
                
                // Don't delay after the last attempt
                if attempt < maxRetries {
                    let delay = min(pow(2.0, Double(attempt)), 10.0) // Exponential backoff, max 10 seconds
                    try await Task.sleep(nanoseconds: UInt64(delay * 1_000_000_000))
                }
            }
        }
        
        throw lastError ?? NetworkError.serverError(0)
    }
    
    /// Upload data to a URL
    func uploadData(_ data: Data, to url: URL, method: HTTPMethod = .POST) async throws -> Data {
        var request = URLRequest(url: url)
        request.httpMethod = method.rawValue
        request.httpBody = data
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        do {
            let (responseData, response) = try await session.data(for: request)
            
            guard let httpResponse = response as? HTTPURLResponse else {
                throw NetworkError.serverError(0)
            }
            
            guard 200...299 ~= httpResponse.statusCode else {
                throw NetworkError.serverError(httpResponse.statusCode)
            }
            
            return responseData
            
        } catch let error as NetworkError {
            throw error
        } catch {
            throw NetworkError.serverError(0)
        }
    }
}

// MARK: - Supporting Types

enum HTTPMethod: String {
    case GET = "GET"
    case POST = "POST"
    case PUT = "PUT"
    case DELETE = "DELETE"
    case PATCH = "PATCH"
}

struct NetworkConfiguration {
    let timeoutInterval: TimeInterval
    let resourceTimeout: TimeInterval
    let simulatedDelay: TimeInterval
    let simulateFailure: Bool
    
    static let `default` = NetworkConfiguration(
        timeoutInterval: 30.0,
        resourceTimeout: 60.0,
        simulatedDelay: 1.0,
        simulateFailure: false
    )
    
    static let testing = NetworkConfiguration(
        timeoutInterval: 5.0,
        resourceTimeout: 10.0,
        simulatedDelay: 0.1,
        simulateFailure: true
    )
}