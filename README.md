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

Get your FRED API key:

Visit FRED API Key Registration
Sign up for a free account
Generate your API key


Set up environment:

bashexport FRED_API_KEY="your_api_key_here"
Usage with Claude Desktop
Add to your Claude Desktop configuration (claude_desktop_config.json):
json{
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
🛠️ Available Tools
ToolDescriptionExample Usageget_fred_dataGet economic data by series IDGDP, unemployment, inflationget_fred_historicalRetrieve 4+ years of dataLong-term trend analysissearch_fredFind series by keywordSearch "housing prices"fred_dashboardKey economic indicatorsGDP, unemployment, ratesget_multiple_seriesCompare multiple seriesGDP vs unemployment
📊 Example Queries
Basic Data Retrieval
Ask Claude: "Get the latest GDP data"
Uses: get_fred_data("GDP")
Historical Analysis
Ask Claude: "Show me 10 years of unemployment data"
Uses: get_fred_historical("UNRATE", years=10)
Economic Research
Ask Claude: "Compare inflation and unemployment over the last 5 years"  
Uses: get_multiple_series(["CPIAUCSL", "UNRATE"])
📈 Common Economic Series
IndicatorSeries IDDescriptionGDPGDPGross Domestic ProductUnemploymentUNRATEUnemployment RateInflationCPIAUCSLConsumer Price IndexFed Funds RateFEDFUNDSFederal Funds Rate10-Year TreasuryDGS1010-Year Treasury RateS&P 500SP500S&P 500 Index
📞 Support

📧 Issues: Use GitHub Issues for bug reports and feature requests
📖 FRED API Docs: https://fred.stlouisfed.org/docs/api/
🔧 MCP Protocol: https://modelcontextprotocol.io/

📄 License
This project is licensed under the MIT License.
