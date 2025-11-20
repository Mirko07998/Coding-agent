# MCP Server Setup Guide

Ovaj vodič objašnjava kako da koristite MCP (Model Context Protocol) servere umesto direktnih API poziva za Jira i GitHub.

## Šta je MCP?

MCP (Model Context Protocol) je protokol koji omogućava AI modelima da pristupe spoljnim resursima i alatima kroz standardizovane servere. Umesto direktnih API poziva, možete koristiti MCP servere koji obezbeđuju alatke za interakciju sa Jira i GitHub.

## Prednosti korišćenja MCP servera

- ✅ **Centralizovana konfiguracija**: MCP serveri se konfigurišu jednom i mogu se koristiti sa različitim AI modelima
- ✅ **Bezbednost**: Autentifikacija se upravlja na nivou MCP servera
- ✅ **Fleksibilnost**: Možete lako prebacivati između API i MCP pristupa
- ✅ **Standardizacija**: Jedinstveni interfejs za različite servise

## Konfiguracija

### 1. Omogućite MCP mode u `.env` fajlu

```env
# Omogućite MCP za Jira
USE_MCP_JIRA=true

# Omegućite MCP za GitHub
USE_MCP_GITHUB=true

# Ako koristite MCP, API kredencijali nisu potrebni
# Ali možete ih zadržati kao fallback
```

### 2. Instalirajte MCP servere

MCP serveri se obično instaliraju i konfigurišu preko MCP framework-a. Evo primera:

#### Jira MCP Server

```bash
# Instalirajte Jira MCP server (primer)
npm install -g @modelcontextprotocol/server-jira
```

#### GitHub MCP Server

```bash
# Instalirajte GitHub MCP Server (primer)
npm install -g @modelcontextprotocol/server-github
```

### 3. Konfigurišite MCP servere

MCP serveri se konfigurišu u MCP konfiguracionom fajlu (obično `mcp.json` ili kroz Cursor settings):

```json
{
  "mcpServers": {
    "jira": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-jira"],
      "env": {
        "JIRA_SERVER": "https://your-domain.atlassian.net",
        "JIRA_EMAIL": "your-email@example.com",
        "JIRA_API_TOKEN": "your-token"
      }
    },
    "github": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "your-github-token"
      }
    }
  }
}
```

## Kako radi

Kada je MCP mode omogućen:

1. **JiraClient** automatski koristi `JiraMCPClient` umesto direktnih API poziva
2. **GitHubClient** automatski koristi `GitHubMCPClient` umesto direktnih API poziva
3. Svi pozivi idu kroz MCP servere koristeći `call_mcp_tool()` funkciju

## Primer korišćenja

### Sa API pristupom (default)

```bash
# U .env fajlu
USE_MCP_JIRA=false
USE_MCP_GITHUB=false

# Koristi direktne API pozive
python autonomous_agent.py PROJ-123
```

### Sa MCP pristupom

```bash
# U .env fajlu
USE_MCP_JIRA=true
USE_MCP_GITHUB=true

# Koristi MCP servere
python autonomous_agent.py PROJ-123
```

## Implementacija

Kod automatski detektuje da li da koristi MCP ili API na osnovu `USE_MCP_JIRA` i `USE_MCP_GITHUB` varijabli u `.env` fajlu.

### Jira MCP Client

`JiraMCPClient` koristi MCP tool `jira_get_issue` za dobijanje informacija o ticketu:

```python
response = call_mcp_tool(
    mcpServer="jira",
    toolName="jira_get_issue",
    toolArgs={"issue_key": ticket_key}
)
```

### GitHub MCP Client

`GitHubMCPClient` koristi MCP toolove za GitHub operacije:

```python
# Kreiranje branch-a
response = call_mcp_tool(
    mcpServer="github",
    toolName="github_create_branch",
    toolArgs={"branch_name": "feature-123", ...}
)

# Push fajla
response = call_mcp_tool(
    mcpServer="github",
    toolName="github_push_file",
    toolArgs={"file_path": "src/file.py", ...}
)
```

## Prilagođavanje Tool Imena

Ako vaši MCP serveri koriste drugačija imena toolova, možete ih prilagoditi u `mcp_client.py`:

```python
# U JiraMCPClient.get_ticket()
response = call_mcp_tool(
    mcpServer="jira",
    toolName="get_issue",  # Promenite na vaše tool ime
    toolArgs={"issue_key": ticket_key}
)
```

## Troubleshooting

### "MCP mode not enabled"
- Proverite da li je `USE_MCP_JIRA=true` ili `USE_MCP_GITHUB=true` u `.env` fajlu

### "MCP tool caller not available"
- Proverite da li su MCP serveri pravilno konfigurisani
- Proverite da li je `call_mcp_tool` funkcija dostupna u vašem okruženju

### "Failed to fetch Jira ticket via MCP"
- Proverite da li je Jira MCP server pokrenut
- Proverite da li su kredencijali pravilno konfigurisani u MCP serveru
- Proverite da li tool ime odgovara vašem MCP serveru

## Fallback na API

Ako MCP server nije dostupan ili dođe do greške, kod automatski pada na API pristup ako su API kredencijali konfigurisani. Ovo omogućava fleksibilnost i otpornost na greške.

## Dodatni resursi

- [MCP Documentation](https://modelcontextprotocol.io)
- [MCP Servers Directory](https://github.com/modelcontextprotocol/servers)
- [Cursor MCP Integration](https://docs.cursor.com/mcp)

