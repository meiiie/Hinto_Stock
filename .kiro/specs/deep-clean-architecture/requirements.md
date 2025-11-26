# Requirements Document

## Introduction

Thực hiện deep refactor để đảm bảo toàn bộ codebase tuân thủ Clean Architecture một cách nghiêm ngặt. Mục tiêu là cải thiện từng component/page để đạt được kiến trúc sạch nhất có thể, đảm bảo tính toàn vẹn kiến trúc (architectural integrity).

## Glossary

- **Clean_Architecture**: Kiến trúc phần mềm với các layer tách biệt: Domain, Application, Infrastructure, Presentation
- **Domain_Layer**: Layer chứa business logic thuần túy, không phụ thuộc vào bất kỳ layer nào khác
- **Application_Layer**: Layer chứa use cases và orchestration logic
- **Infrastructure_Layer**: Layer chứa implementations cụ thể (database, API, external services)
- **Presentation_Layer**: Layer chứa UI components và API endpoints
- **Dependency_Inversion**: Nguyên tắc các layer cao không phụ thuộc vào layer thấp, cả hai phụ thuộc vào abstractions
- **Component**: Một đơn vị UI hoặc logic có thể tái sử dụng

## Requirements

### Requirement 1: Domain Layer Purity

**User Story:** As a developer, I want the Domain layer to be completely independent, so that business logic can be tested and maintained without external dependencies.

#### Acceptance Criteria

1. WHEN reviewing Domain entities THEN the Clean_Architecture SHALL ensure no imports from Infrastructure or Presentation layers exist
2. WHEN Domain entities are defined THEN the Clean_Architecture SHALL ensure they contain only pure business logic and validation
3. WHEN Domain repositories are defined THEN the Clean_Architecture SHALL ensure they are abstract interfaces only (no implementations)
4. WHEN Domain services exist THEN the Clean_Architecture SHALL ensure they contain only domain-specific business rules

### Requirement 2: Application Layer Orchestration

**User Story:** As a developer, I want the Application layer to properly orchestrate use cases, so that business workflows are clearly defined and testable.

#### Acceptance Criteria

1. WHEN Application services are defined THEN the Clean_Architecture SHALL ensure they only depend on Domain layer and abstractions
2. WHEN use cases are implemented THEN the Clean_Architecture SHALL ensure each use case has a single responsibility
3. WHEN Application layer needs infrastructure THEN the Clean_Architecture SHALL ensure dependency injection is used via interfaces
4. WHEN DTOs are needed THEN the Clean_Architecture SHALL ensure they are defined in Application layer for data transfer

### Requirement 3: Infrastructure Layer Implementations

**User Story:** As a developer, I want Infrastructure implementations to be properly isolated, so that they can be easily swapped or modified.

#### Acceptance Criteria

1. WHEN Infrastructure implements repository interfaces THEN the Clean_Architecture SHALL ensure implementations are in Infrastructure layer only
2. WHEN external APIs are called THEN the Clean_Architecture SHALL ensure they are wrapped in Infrastructure adapters
3. WHEN database access is needed THEN the Clean_Architecture SHALL ensure it goes through repository implementations
4. WHEN third-party libraries are used THEN the Clean_Architecture SHALL ensure they are encapsulated in Infrastructure

### Requirement 4: Presentation Layer Separation

**User Story:** As a developer, I want Presentation layer to only handle UI concerns, so that UI changes don't affect business logic.

#### Acceptance Criteria

1. WHEN API endpoints are defined THEN the Clean_Architecture SHALL ensure they only call Application layer services
2. WHEN UI components are created THEN the Clean_Architecture SHALL ensure they don't contain business logic
3. WHEN data is displayed THEN the Clean_Architecture SHALL ensure it comes from Application layer DTOs
4. WHEN user input is processed THEN the Clean_Architecture SHALL ensure validation happens in appropriate layers

### Requirement 5: Frontend Clean Architecture

**User Story:** As a developer, I want the React frontend to follow clean architecture principles, so that components are maintainable and testable.

#### Acceptance Criteria

1. WHEN React components are defined THEN the Clean_Architecture SHALL ensure they follow single responsibility principle
2. WHEN state management is needed THEN the Clean_Architecture SHALL ensure it's properly separated from UI
3. WHEN API calls are made THEN the Clean_Architecture SHALL ensure they go through service/hook abstractions
4. WHEN business logic exists in frontend THEN the Clean_Architecture SHALL ensure it's in dedicated service files

### Requirement 6: Dependency Injection Consistency

**User Story:** As a developer, I want consistent dependency injection throughout the application, so that components are loosely coupled.

#### Acceptance Criteria

1. WHEN services need dependencies THEN the Clean_Architecture SHALL ensure they are injected via constructor
2. WHEN DI container is used THEN the Clean_Architecture SHALL ensure it's the single source of dependency resolution
3. WHEN testing is performed THEN the Clean_Architecture SHALL ensure dependencies can be easily mocked

### Requirement 7: Code Organization and Naming

**User Story:** As a developer, I want consistent code organization and naming conventions, so that the codebase is easy to navigate.

#### Acceptance Criteria

1. WHEN files are organized THEN the Clean_Architecture SHALL ensure they follow layer-based folder structure
2. WHEN classes are named THEN the Clean_Architecture SHALL ensure names reflect their layer and responsibility
3. WHEN imports are used THEN the Clean_Architecture SHALL ensure they follow dependency direction rules
