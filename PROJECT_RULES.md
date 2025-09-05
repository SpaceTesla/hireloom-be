# HireLoom AI Agent - Project Rules & Guidelines

## 🎯 Project Philosophy

**Primary Goal: Help Shivansh Learn AI Technologies**

- This project is a **learning platform** for Shivansh to master new AI/ML technologies and concepts
- **Learn by Building**: Cursor will help implement LangChain, LangGraph, RAG, and other cutting-edge AI tools
- **Hands-on Exploration**: Cursor will guide deep dives into each technology through practical implementation
- **Document Learning Journey**: Cursor will help capture insights, challenges, and breakthroughs as we explore
- **Build Understanding**: Cursor will explain how and why each technology works, not just implement it

## 🏗️ Development Approach

### Learning-Focused Principles

1. **One Sub-task at a Time**: Cursor will help tackle one specific component/feature per session
2. **Explain Before Implementing**: Cursor will explain concepts and patterns before coding
3. **Build Incrementally**: Cursor will start with simple implementations, then guide complexity
4. **Document Decisions**: Cursor will explain why specific patterns/approaches were chosen
5. **Test Understanding**: Cursor will help write tests that verify both functionality and understanding

### Code Quality Standards

- **Clean, Modular Code**: Break functionality into reusable components
- **Clear Naming**: Use descriptive variable and function names
- **Minimal Comments**: Only comment non-obvious logic; prefer self-explanatory code
- **Type Safety**: Use TypeScript-style typing with Python type hints, avoid `any`
- **Separation of Concerns**: Keep business logic, data access, and presentation separate

## 🛠️ Technical Stack & Preferences

### Backend Stack

- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Database**: PostgreSQL with pgvector extension
- **Vector Database**: pgvector for embeddings and similarity search
- **HTTP Client**: Axios-style with `httpx` (not `requests`)
- **Entry Point**: `src/main.py` (not `src/hireloom/main.py`)

### AI/ML Stack (Learning Focus)

- **LangChain**: Master the core framework for building LLM applications
- **LangGraph**: Learn state management and agent orchestration workflows
- **RAG (Retrieval-Augmented Generation)**: Implement knowledge retrieval and context enhancement
- **Vector Database**: pgvector for embeddings, similarity search, and vector storage
- **LLM Integration**: Google Gemini (primary) with adapter patterns
- **Agent Frameworks**: Build custom agent architectures and communication patterns
- **Prompt Engineering**: Advanced prompting techniques and template management
- **Memory Systems**: Short-term and long-term memory for conversational AI

### Development Tools

- **Package Management**: `uv` (ultra-fast Python package manager)
- **Linting**: Ruff + mypy
- **Testing**: pytest with async support
- **Pre-commit**: Automated code quality checks
- **Commit Standards**: Conventional Commits with commitlint validation

### Planned Integrations

- **Telegram**: Bot integration for candidate communication
- **Google Calendar**: Schedule management and meeting coordination
- **Google Meet**: Video interview integration
- **Supabase**: Additional database services and real-time features
- **Future Integrations**: WhatsApp, Slack, LinkedIn, and other recruitment tools

## 📁 Architecture Guidelines

### Directory Structure

```
src/hireloom/
├── core/           # Domain models, schemas, business rules
├── agents/         # AI agents (base, recruitment, orchestrator)
├── workflows/      # LangGraph workflows and state management
├── services/       # Business logic services
├── integrations/   # External service adapters
├── api/           # FastAPI routes and dependencies
├── db/            # Database models and migrations
└── utils/         # Shared utilities
```

### Design Patterns

- **Adapter Pattern**: For external integrations (LLM, calendar, messaging)
- **Service Layer**: Business logic separated from data access
- **Repository Pattern**: Data access abstraction
- **Factory Pattern**: For creating agents and workflows
- **Observer Pattern**: For event-driven communication

## 🚀 Development Workflow

### Session Planning

1. **Start with Questions**: Cursor will clarify requirements and approach before coding
2. **Propose Step-by-Step Plan**: Cursor will present a plan and wait for approval
3. **One Focus Area**: Cursor will concentrate on one sub-task per session
4. **Document Learnings**: Cursor will help capture insights and architectural decisions

### Code Implementation

1. **Explain First**: Cursor will explain existing code before modifying
2. **Start Simple**: Cursor will begin with basic implementation, then guide enhancement
3. **Test Early**: Cursor will help write tests as you build, not after
4. **Refactor Often**: Cursor will guide code structure improvements as understanding grows

### Quality Gates

- All code must pass linting (ruff + mypy)
- Tests must be written for new functionality
- Documentation must be updated for architectural changes
- Code reviews focus on learning and understanding
- All commits must follow Conventional Commits specification

## 🎓 Learning Objectives

### Core Technologies for Shivansh to Master

1. **LangChain Ecosystem**:

   - Cursor will explain: Chains, Agents, Tools, Memory concepts
   - Cursor will guide: Document loaders and text splitters implementation
   - Cursor will teach: Vector stores and retrievers usage
   - Cursor will demonstrate: Output parsers and prompt templates

2. **LangGraph Workflows**:

   - Cursor will explain: State management and graph-based execution
   - Cursor will guide: Conditional routing and decision making
   - Cursor will teach: Human-in-the-loop workflows
   - Cursor will demonstrate: Error handling and recovery patterns

3. **RAG Implementation**:

   - Cursor will explain: Document processing and chunking strategies
   - Cursor will guide: Embedding models and vector similarity
   - Cursor will teach: Retrieval strategies and ranking
   - Cursor will demonstrate: Context window management

4. **Vector Databases (pgvector)**:

   - Cursor will guide: pgvector setup and configuration
   - Cursor will teach: Embedding storage and retrieval with PostgreSQL
   - Cursor will explain: Similarity search algorithms and indexing
   - Cursor will demonstrate: Performance optimization with pgvector

5. **Advanced AI Concepts**:
   - Cursor will explain: Multi-agent systems and communication
   - Cursor will guide: Tool calling and function execution
   - Cursor will teach: Streaming and real-time responses
   - Cursor will demonstrate: Fine-tuning and prompt optimization

### Skills to Develop

- **System Design**: Breaking down complex problems into manageable components
- **API Design**: RESTful principles, versioning, documentation
- **Error Handling**: Graceful failure, logging, monitoring
- **Performance**: Async programming, database optimization, caching
- **Security**: Authentication, authorization, data protection

## 📝 Documentation Standards

### Code Documentation

- **Docstrings**: For all public functions and classes
- **Type Hints**: Comprehensive typing for better IDE support
- **README Updates**: Keep project README current with setup instructions
- **Architecture Decisions**: Document why specific patterns were chosen

### Commit Message Standards

Following [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification:

#### Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

#### Commit Types

- **feat**: New feature (correlates with MINOR in SemVer)
- **fix**: Bug fix (correlates with PATCH in SemVer)
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **perf**: Performance improvements
- **test**: Adding or updating tests
- **build**: Build system changes
- **ci**: CI/CD changes
- **chore**: Maintenance tasks
- **revert**: Reverting changes

#### Scopes (Project-Specific)

- **api**: API related changes
- **agents**: AI agents
- **workflows**: LangGraph workflows
- **integrations**: External integrations
- **db**: Database changes
- **core**: Core business logic
- **services**: Service layer
- **utils**: Utility functions
- **tests**: Test files
- **docs**: Documentation
- **config**: Configuration files
- **deps**: Dependencies

#### Examples

```bash
feat(agents): add recruitment agent with candidate screening
fix(api): resolve authentication issue in user endpoints
docs(workflows): update LangGraph workflow documentation
refactor(core): extract common validation logic
test(integrations): add tests for calendar integration
chore(deps): update FastAPI to latest version
```

#### Breaking Changes

Use `!` after type/scope or add `BREAKING CHANGE:` footer:

```bash
feat(api)!: change user authentication flow
# or
feat(api): change user authentication flow

BREAKING CHANGE: Authentication now requires 2FA
```

### Learning Documentation

- **Session Notes**: Capture key learnings from each development session
- **Decision Log**: Record architectural and technical decisions
- **Troubleshooting**: Document common issues and solutions
- **Best Practices**: Compile learnings into reusable guidelines

## 🔄 Iteration Strategy

### Phase 1: LangChain Fundamentals

- **LangChain Basics**: Chains, prompts, and output parsers
- **Document Processing**: Loaders, splitters, and text processing
- **Simple RAG**: Basic retrieval and generation pipeline
- **FastAPI Integration**: API endpoints for LangChain operations

### Phase 2: Advanced LangChain

- **Agent Systems**: Tool calling and decision making
- **Memory Management**: Conversation and session memory
- **Vector Stores**: pgvector integration and similarity search
- **Custom Tools**: Building specialized recruitment tools

### Phase 3: LangGraph Mastery

- **Workflow Design**: Graph-based agent orchestration
- **State Management**: Complex state transitions and persistence
- **Human-in-the-Loop**: Interactive workflows and approvals
- **Error Recovery**: Robust error handling and retry logic

### Phase 4: Production AI Systems

- **Multi-Agent Architecture**: Complex agent communication
- **Streaming Responses**: Real-time AI interactions
- **Performance Optimization**: Caching, batching, and scaling
- **Monitoring & Observability**: AI system monitoring and debugging

## 🚫 Anti-Patterns to Avoid

- **Rushing to Completion**: Don't skip understanding for speed
- **Copy-Paste Development**: Understand code before reusing
- **Monolithic Functions**: Break complex logic into smaller, testable pieces
- **Hardcoded Values**: Use configuration and environment variables
- **Silent Failures**: Always handle errors explicitly
- **Untested Code**: Don't deploy code without tests

## 🎯 Success Metrics

### Learning Success

- Can explain each component's purpose and interaction
- Can modify existing code with confidence
- Can add new features following established patterns
- Can debug issues independently

### Code Quality Success

- All tests pass consistently
- Code follows established patterns
- Documentation is current and helpful
- Performance meets requirements

---

**Remember**: This project is Shivansh's **AI technology learning laboratory**. Cursor will help focus each session on mastering a specific technology or concept. Cursor will guide experimentation, help break things down, explain the internals, and build deep knowledge. The goal is to help Shivansh become proficient in modern AI development tools and patterns!
