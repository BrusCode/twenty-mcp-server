# Changelog

All notable changes to the Twenty MCP Server project will be documented in this file.

## [0.1.0] - 2025-01-18

### Added
- Initial release of Twenty MCP Server
- Complete CRUD operations for People, Companies, Opportunities, Notes, and Tasks
- Metadata API access for schema discovery
- Multiple workspaces support
- Both stdio and SSE/HTTP transport protocols
- Basic and complex search filters
- Rate limiting compliance (100 calls/min)
- MCP resources for easy data access
- Comprehensive documentation and examples
- Unit tests and integration test framework
- Configuration management with environment variables

### Features
- **People Tools**: get_person, get_people, create_person, update_person, delete_person, search_people_basic, search_people_complex
- **Companies Tools**: get_company, get_companies, create_company, update_company, delete_company, search_companies_basic, search_companies_complex
- **Opportunities Tools**: get_opportunity, get_opportunities, create_opportunity, update_opportunity, delete_opportunity, search_opportunities_basic, search_opportunities_complex
- **Notes Tools**: get_note, get_notes, create_note, update_note, delete_note
- **Tasks Tools**: get_task, get_tasks, create_task, update_task, delete_task
- **Metadata Tools**: get_objects, get_object_schema, get_fields

### Resources
- `people://list` and `people://{id}`
- `companies://list` and `companies://{id}`
- `opportunities://list` and `opportunities://{id}`
- `schema://objects`

### Planned Features (Future)
- Custom objects support
- Batch operations (up to 60 records)
- View management
- Real-time notifications via webhooks
- GraphQL support
- Enhanced error handling and retry logic
