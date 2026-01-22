# Twenty MCP Server

Model Context Protocol (MCP) server for Twenty CRM - complete API integration using FastMCP.

## Features

- **Complete CRUD operations** for all Twenty CRM objects:
  - People (contacts)
  - Companies (organizations)
  - Opportunities (deals)
  - Notes
  - Tasks
- **Metadata API** access for schema discovery
- **Multiple workspaces** support
- **Flexible transport**: stdio (local) and SSE/HTTP (remote)
- **Advanced search** with basic and complex filters
- **Rate limiting** compliant (100 calls/min)
- **Batch operations** support (up to 60 records)
- **Full TypeScript-like type hints** in Python

## Installation

### From PyPI (when published)
```bash
pip install twenty-mcp-server
```

### From Source
```bash
git clone https://github.com/BrusCode/twenty-mcp-server.git
cd twenty-mcp-server
pip install -e .
```

### Development
```bash
pip install -e ".[dev]"
```

## Configuration

Create a `.env` file in your working directory:

```env
# Single workspace (simple)
TWENTY_BASE_URL=https://your-domain.com
TWENTY_API_KEY=your_api_key_here

# Multiple workspaces (advanced)
TWENTY_WORKSPACES='{"workspaces": [{"name": "main", "base_url": "https://domain1.com", "api_key": "key1"}, {"name": "secondary", "base_url": "https://domain2.com", "api_key": "key2"}]}'
```

Or use environment variables directly:
```bash
export TWENTY_BASE_URL=https://your-domain.com
export TWENTY_API_KEY=your_api_key_here
```

### Getting API Key

1. Log in to your Twenty CRM instance
2. Go to **Settings → API & Webhooks**
3. Click **+ Create key**
4. Configure name and expiration
5. Copy the key immediately (shown only once!)

## Usage

### Starting the Server

#### Local (stdio transport) - Recommended for development
```bash
twenty-mcp --transport stdio
```

Or with Python directly:
```bash
python -m twenty_mcp_server.server --transport stdio
```

#### Remote (SSE transport) - Recommended for production
```bash
twenty-mcp --transport sse --host 0.0.0.0 --port 8000
```

Or with HTTP/Streamable transport:
```bash
twenty-mcp --transport streamable-http --host 0.0.0.0 --port 8000
```

### Claude Desktop Configuration

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or appropriate config file:

**Single workspace (stdio):**
```json
{
  "mcpServers": {
    "twenty": {
      "command": "python",
      "args": ["-m", "twenty_mcp_server.server", "--transport", "stdio"],
      "env": {
        "TWENTY_BASE_URL": "https://your-domain.com",
        "TWENTY_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

**Multiple workspaces (stdio):**
```json
{
  "mcpServers": {
    "twenty": {
      "command": "python",
      "args": ["-m", "twenty_mcp_server.server", "--transport", "stdio"],
      "env": {
        "TWENTY_WORKSPACES": "{\"workspaces\": [{\"name\": \"main\", \"base_url\": \"https://domain1.com\", \"api_key\": \"key1\"}, {\"name\": \"secondary\", \"base_url\": \"https://domain2.com\", \"api_key\": \"key2\"}]}"
      }
    }
  }
}
```

**Remote server (SSE):**
```json
{
  "mcpServers": {
    "twenty": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

### Cursor IDE Configuration

```json
{
  "mcpServers": {
    "twenty": {
      "command": "python",
      "args": ["-m", "twenty_mcp_server.server", "--transport", "stdio"],
      "env": {
        "TWENTY_BASE_URL": "https://your-domain.com",
        "TWENTY_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

## Available Tools

### People
- `get_person(id, workspace=None)` - Get a person by ID
- `get_people(limit=20, offset=0, workspace=None)` - List all people
- `create_person(data, workspace=None)` - Create a new person
- `update_person(id, data, workspace=None)` - Update an existing person
- `delete_person(id, workspace=None)` - Delete a person
- `search_people_basic(query, limit=20, workspace=None)` - Basic text search
- `search_people_complex(filters, limit=20, workspace=None)` - Advanced search with filters

### Companies
- `get_company(id, workspace=None)` - Get a company by ID
- `get_companies(limit=20, offset=0, workspace=None)` - List all companies
- `create_company(data, workspace=None)` - Create a new company
- `update_company(id, data, workspace=None)` - Update an existing company
- `delete_company(id, workspace=None)` - Delete a company
- `search_companies_basic(query, limit=20, workspace=None)` - Basic text search
- `search_companies_complex(filters, limit=20, workspace=None)` - Advanced search with filters

### Opportunities
- `get_opportunity(id, workspace=None)` - Get an opportunity by ID
- `get_opportunities(limit=20, offset=0, workspace=None)` - List all opportunities
- `create_opportunity(data, workspace=None)` - Create a new opportunity
- `update_opportunity(id, data, workspace=None)` - Update an existing opportunity
- `delete_opportunity(id, workspace=None)` - Delete an opportunity
- `search_opportunities_basic(query, limit=20, workspace=None)` - Basic text search
- `search_opportunities_complex(filters, limit=20, workspace=None)` - Advanced search with filters

### Notes
- `get_note(id, workspace=None)` - Get a note by ID
- `get_notes(limit=20, offset=0, workspace=None)` - List all notes
- `create_note(data, workspace=None)` - Create a new note
- `update_note(id, data, workspace=None)` - Update an existing note
- `delete_note(id, workspace=None)` - Delete a note

### Tasks
- `get_task(id, workspace=None)` - Get a task by ID
- `get_tasks(limit=20, offset=0, workspace=None)` - List all tasks
- `create_task(data, workspace=None)` - Create a new task
- `update_task(id, data, workspace=None)` - Update an existing task
- `delete_task(id, workspace=None)` - Delete a task

### Metadata
- `get_objects(workspace=None)` - List all objects in the workspace
- `get_object_schema(object_name, workspace=None)` - Get schema for a specific object
- `get_fields(object_name, workspace=None)` - Get fields for a specific object

## Available Resources

- `people://list` - Directory of all people
- `people://{id}` - Individual person details
- `companies://list` - Directory of all companies
- `companies://{id}` - Individual company details
- `opportunities://list` - Directory of all opportunities
- `opportunities://{id}` - Individual opportunity details
- `schema://objects` - Schema of all objects

## Example Usage

### Creating a Person
```python
{
  "firstName": "John",
  "lastName": "Doe",
  "city": "New York",
  "email": "john.doe@example.com",
  "phone": "+1 555-1234"
}
```

### Creating a Company
```python
{
  "name": "Acme Corp",
  "domainName": "acme.com",
  "address": {
    "addressStreet1": "123 Main St",
    "addressCity": "New York",
    "addressPostcode": "10001",
    "addressCountry": "US"
  }
}
```

### Creating an Opportunity
```python
{
  "name": "Enterprise Deal",
  "amount": 50000,
  "currency": "USD",
  "stage": "Proposal",
  "company": {"id": "company-id-here"}
}
```

### Complex Search Filters
```python
{
  "filters": [
    {
      "field": "city",
      "operator": "eq",
      "value": "New York"
    },
    {
      "field": "createdAt",
      "operator": "gte",
      "value": "2024-01-01T00:00:00.000Z"
    }
  ],
  "orderBy": "createdAt",
  "orderDirection": "DESC"
}
```

## Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black src/
ruff check src/
mypy src/
```

### Building
```bash
pip install build
python -m build
```

## API Reference

This server implements the Twenty CRM REST API:

- **Core API**: `/rest/{object}` for CRUD operations
- **Metadata API**: `/rest/metadata/{object}` for schema operations

For more details, see: https://docs.twenty.com/developers/extend/capabilities/apis

## Rate Limits

- **100 calls per minute** per workspace
- **60 records per batch** for batch operations

## Security

- API keys are stored in environment variables only
- No built-in authentication - secure your MCP client configuration
- Use HTTPS endpoints for self-hosted instances

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

- GitHub Issues: https://github.com/BrusCode/twenty-mcp-server/issues
- Twenty CRM Docs: https://docs.twenty.com
- Twenty CRM Discord: https://discord.gg/cx5n4Jzs57
