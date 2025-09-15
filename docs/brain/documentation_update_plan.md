# Documentation Update Checklist for AI Assistants

## Working Notes & Context

This is a checklist for AI coding assistants (Claude Code, Windsurf, etc.) to systematically update the project documentation to match the actual codebase implementation.

## Major Discrepancies Found

### 1. Architecture & Technology Stack Changes

#### PRD vs. Reality
- **PRD Claims**: Django Channels for WebSockets, StPageFlip JS for flipbook
- **Reality**: Using `django-eventstream` for SSE, Cotton components for UI, no flipbook implementation found

#### Tech Stack Document vs. Reality
- **Doc Claims**: Django Channels, StPageFlip JS, Pegasus scaffold
- **Reality**: Django EventStream (SSE), Django Cotton components, custom Django setup

### 2. Model Structure Mismatches

#### Expected vs. Actual Models
- **Missing Models**: Characters, Teams, Books (PRD mentions these extensively)
- **Actual Models**: Story, Page, Job, Conversation, Run (simplified structure)
- **Team/Family Accounts**: PRD describes parent-admin/child-creator roles, but no team models found

### 3. Feature Implementation Gaps

#### Subscription System
- **PRD/Docs**: Detailed freemium model, Stripe integration, metered billing
- **Reality**: Basic subscription app structure exists but implementation unclear

#### AI Pipeline
- **PRD**: GPT-4o + Claude fallback, DALL-E 3 + SD-XL fallback
- **Reality**: Pydantic AI integration, Job workflow system, unclear which models are actually integrated

#### PDF Generation
- **PRD**: WeasyPrint for PDF export
- **Reality**: No PDF generation implementation found

### 4. Frontend Pattern Mismatches

#### HTMX Implementation
- **Docs**: Detailed `HtmxEditableFieldView` patterns
- **Reality**: Cotton components used instead, different HTMX approach

## Outdated Documentation Files

### Critical Updates Needed

1. **`docs/prd.md`**
   - ❌ References non-existent features (Characters, Teams, Books)
   - ❌ Incorrect tech stack (Django Channels vs EventStream)
   - ❌ Missing actual features implemented

2. **`docs/architecture/tech_stack_document.md`**
   - ❌ Wrong frontend stack (StPageFlip vs Cotton)
   - ❌ Wrong real-time solution (Channels vs EventStream)
   - ❌ Missing Pydantic AI integration

3. **`docs/development/backend_structure_document.md`**
   - ❌ Database schema section references Django models but doesn't match actual models
   - ❌ API documentation mentions endpoints that may not exist
   - ❌ SSE implementation details need verification

4. **`docs/development/htmx_patterns.md`**
   - ❌ Describes `HtmxEditableFieldView` pattern not found in codebase
   - ❌ Template patterns don't match Cotton component structure

### Partially Outdated

5. **`docs/architecture/app_flow_document.md`** - Needs review
6. **`docs/development/frontend_guidelines_document.md`** - Needs Cotton component update
7. **`docs/development/ui_patterns.md`** - Needs Cotton integration details

## Required Clarifications Before Updates

### 1. Architecture Decisions
- **Question**: Why was Django Channels replaced with EventStream? What are the trade-offs?
- **Question**: Is the Cotton component system the preferred UI pattern over HTMX base classes?
- **Question**: What happened to the Character/Team/Book models? Were they simplified to Story/Page?

### 2. Feature Scope
- **Question**: Which features from the PRD are actually implemented vs. planned?
- **Question**: What's the current state of the subscription system implementation?
- **Question**: Is PDF generation planned or was it dropped from scope?

### 3. AI Integration
- **Question**: Which AI models are currently integrated and working?
- **Question**: How does the Job workflow system relate to the Pydantic AI integration?
- **Question**: What's the fallback strategy if primary AI services fail?

### 4. Frontend Architecture
- **Question**: Should documentation focus on Cotton components or the HTMX patterns described?
- **Question**: Is there a flipbook/reader implementation or was this feature dropped?
- **Question**: What's the current approach for real-time UI updates?

### 5. Database & API
- **Question**: Are the Django Ninja API endpoints documented in `/api/docs` actually implemented?
- **Question**: What's the current database schema and how does it differ from PRD expectations?
- **Question**: Is the SSE channel management system actually implemented as described?

### 6. Development Workflow
- **Question**: Are there specific Cotton component development patterns to document?
- **Question**: What's the current testing strategy for HTMX + Cotton components?
- **Question**: How should developers handle real-time updates in the UI?

## Update Priority

### Phase 1: Critical Architecture Docs
1. Update tech stack document with actual implementation
2. Revise PRD to match current scope and implementation
3. Update backend structure with real models and API endpoints

### Phase 2: Development Guidelines
1. Replace HTMX patterns with Cotton component patterns
2. Update frontend guidelines for Cotton + HTMX approach
3. Document actual AI integration patterns

### Phase 3: Complete Feature Documentation
1. Document current subscription implementation
2. Add real-time update patterns documentation
3. Update development workflow docs

## AI Assistant Action Checklist

### Phase 1: Discovery & Verification
- [ ] **Map current models**: Read all `models.py` files and document actual schema
- [ ] **Test API endpoints**: Visit `/api/docs` and verify which endpoints exist
- [ ] **Audit templates**: Check what UI patterns are actually used (Cotton vs HTMX)
- [ ] **Verify tech stack**: Check `pyproject.toml` and settings for actual dependencies
- [ ] **Test SSE implementation**: Check if EventStream is working and how
- [ ] **Check AI integration**: Trace through actual AI workflow in code

### Phase 2: Quick Wins (Fix Obviously Wrong Docs)
- [ ] **Fix tech stack doc**: Replace Django Channels → EventStream, add Cotton components
- [ ] **Update backend structure**: Replace model references with actual Story/Page/Job models
- [ ] **Fix HTMX patterns**: Document Cotton component patterns instead of non-existent base classes
- [ ] **Update CLAUDE.md**: Ensure it reflects current codebase accurately

### Phase 3: Deep Documentation Updates
- [ ] **Rewrite PRD sections**: Remove references to Characters/Teams/Books, focus on Story/Page
- [ ] **Document actual workflows**: Map real AI job processing flow
- [ ] **Update development patterns**: Document Cotton + HTMX integration approach
- [ ] **Add missing features**: Document what's implemented vs. what's planned

### Phase 4: Validation & Testing
- [ ] **Test all commands**: Verify every command in CLAUDE.md works
- [ ] **Check code examples**: Ensure all code snippets in docs are valid
- [ ] **Validate workflows**: Test that documented development flows actually work
- [ ] **Cross-reference**: Ensure docs are internally consistent

## Quick Reference for AI Assistants

### Files That Need Major Updates:
- `docs/prd.md` - Remove non-existent features, focus on actual Story/Page model
- `docs/architecture/tech_stack_document.md` - Fix Django Channels → EventStream, add Cotton
- `docs/development/htmx_patterns.md` - Replace with Cotton component patterns
- `docs/development/backend_structure_document.md` - Update with real models/APIs

### Key Codebase Facts to Remember:
- Models: Story, Page, Job, Conversation, Run (not Character/Team/Book)
- Real-time: django-eventstream (SSE) not Django Channels
- UI: Cotton components + HTMX (not StPageFlip or base HTMX classes)
- AI: Pydantic AI + Job workflow system
- Package manager: uv (not pip/poetry)

### Commands to Test:
```bash
# These should all work if docs are accurate:
make web                    # Start Django server
make tasks                  # Start Celery worker
make db-sync               # Run migrations
uv run -m pytest          # Run tests
```

### Next AI Assistant: Start with Phase 1 discovery tasks above!