# FRED Economic MCP Server

A powerful Model Context Protocol (MCP) server providing access to Federal Reserve Economic Data (FRED) through Claude and other MCP-compatible clients.


## 🌟 Features

- 📊 **Comprehensive Data Access**: Access to 800,000+ economic time series
- 🔍 **Smart Search**: Find economic indicators by keyword or category  
- 📈 **Historical Analysis**: Retrieve up to 100,000 observations per series
- ⚡ **High Performance**: Efficient async operations with proper error handling
- 🎯 **Economic Dashboard**: Pre-configured key economic indicators
- 🔄 **Multi-Series Support**: Compare multiple economic series simultaneously

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- FRED API key (free from [FRED](https://fred.stlouisfed.org/docs/api/api_key.html))

### Installation

1. **Download the server file:**
   - Download `fred_economic_server.py` from this repository
   
2. **Install dependencies:**
```bash
pip install httpx python-mcp python-dotenv
```

3. **Get your FRED API key:**
   - Visit [FRED API Key Registration](https://fred.stlouisfed.org/docs/api/api_key.html)
   - Sign up for a free account
   - Generate your API key

4. **Set up environment:**
```bash
export FRED_API_KEY="your_api_key_here"
```

### Usage with Claude Desktop

Add to your Claude Desktop configuration (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "fred-economic": {
      "command": "python",
      "args": ["path/to/fred_economic_server.py"],
      "env": {
        "FRED_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

## 🛠️ Available Tools

| Tool | Description | Example Usage |
|------|-------------|---------------|
| `get_fred_data` | Get economic data by series ID | GDP, unemployment, inflation |
| `get_fred_historical` | Retrieve 4+ years of data | Long-term trend analysis |
| `search_fred` | Find series by keyword | Search "housing prices" |
| `fred_dashboard` | Key economic indicators | GDP, unemployment, rates |
| `get_multiple_series` | Compare multiple series | GDP vs unemployment |

## 📊 Example Queries

### Basic Data Retrieval
```
Ask Claude: "Get the latest GDP data"
Uses: get_fred_data("GDP")
```

### Historical Analysis  
```
Ask Claude: "Show me 10 years of unemployment data"
Uses: get_fred_historical("UNRATE", years=10)
```

### Economic Research
```
Ask Claude: "Compare inflation and unemployment over the last 5 years"  
Uses: get_multiple_series(["CPIAUCSL", "UNRATE"])
```

## 📈 Common Economic Series

| Indicator | Series ID | Description |
|-----------|-----------|-------------|
| GDP | `GDP` | Gross Domestic Product |
| Unemployment | `UNRATE` | Unemployment Rate |
| Inflation | `CPIAUCSL` | Consumer Price Index |
| Fed Funds Rate | `FEDFUNDS` | Federal Funds Rate |
| 10-Year Treasury | `DGS10` | 10-Year Treasury Rate |
| S&P 500 | `SP500` | S&P 500 Index |

## 📞 Support

- 📧 **Issues**: Use GitHub Issues for bug reports and feature requests
- 📖 **FRED API Docs**: https://fred.stlouisfed.org/docs/api/
- 🔧 **MCP Protocol**: https://modelcontextprotocol.io/

## 📄 License

This project is licensed under the MIT License.

---


