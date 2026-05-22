# OpsPilot AI — Autonomous Incident Response Agent 🚨

An autonomous AI agent that acts as the first responder for server incidents, investigating issues, taking action, and escalating to humans when needed.

## 📋 Project Overview

This project demonstrates how to build an intelligent incident response system that:
- Investigates server health and logs when issues are reported
- Automatically restarts services when CPU/Memory exceeds thresholds
- Escalates complex issues to human engineers
- Uses OpenAI function calling to execute tools

## 🎯 Features

✅ **Automatic Investigation** - Checks server health metrics
✅ **Smart Decision Making** - Takes appropriate action based on diagnostics
✅ **Service Restart** - Automatically restarts services when needed
✅ **Intelligent Escalation** - Routes complex issues to human engineers
✅ **Log Analysis** - Examines logs to understand root causes
✅ **Multi-Scenario Handling** - Handles various incident types

## 📁 Project Structure

```
2-OpsPilot-AI-Incident-Response/
├── README.md                           # This file
├── requirements.txt                    # Python dependencies
├── notebooks/
│   └── OpsPilot_AI_Incident_Response.ipynb
└── src/
    └── agent.py                        # Agent implementation
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- OpenAI API Key

### Installation

```bash
# Navigate to project
cd 2-OpsPilot-AI-Incident-Response

# Install dependencies
pip install -r requirements.txt
```

### Run Jupyter Notebook

```bash
jupyter notebook notebooks/OpsPilot_AI_Incident_Response.ipynb
```

## 💻 How It Works

### The Agent Decision Process

1. **Investigate**: Check server health and recent logs
2. **Assess**: Determine severity and root cause
3. **Act**: 
   - If CPU/Memory > 90% → Restart service
   - If logs show critical errors → Gather details
4. **Escalate**: If issue is complex → Create ticket for human

### Scenario Examples

**High CPU** → Automatic restart
**Memory Leak** → Automatic restart + escalation
**Dependency Failure** → Direct escalation to human
**Healthy Server** → Report status, no action needed

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:
```
OPENAI_API_KEY=your_api_key_here
```

## 📚 Key Technologies

- **OpenAI API** - GPT model with function calling
- **Python** - Core implementation
- **JSON** - Tool communication

## 🔑 Core Functions

- `get_server_health(server_id)` - Check CPU/Memory usage
- `fetch_recent_logs(server_id, lines)` - Get recent log entries
- `restart_service(server_id)` - Restart a service
- `escalate_to_engineer(summary)` - Create escalation ticket

## 📈 Optimization Tips

### Improve Response Time
- Parallelize health checks
- Cache log data
- Use async operations

### Enhance Accuracy
- Train on real incident data
- Fine-tune escalation thresholds
- Add more diagnostic tools

## 📝 License

MIT License
