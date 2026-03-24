# Client Call Brief

A multi-agent system that generates client meeting briefings using AI. Give it a company name and it produces a concise, research-backed 3-paragraph brief you can skim before a call.

Built with [Strands Agents SDK](https://strandsagents.com/) and [Tavily](https://tavily.com/) for web search.

## How It Works

```
User → Orchestrator → Research Agent (Tavily) → Writer Agent → Meeting Brief
```

Three agents work together in a sequential workflow:

1. **Orchestrator** — receives the company name and optional focus area, coordinates the pipeline
2. **Research Agent** — uses Tavily to search for recent news, press releases, and articles about the company
3. **Writer Agent** — takes the raw research and synthesises it into a structured 3-paragraph briefing covering company overview, recent developments, and talking points

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- AWS credentials configured with access to Amazon Bedrock (Claude Sonnet)
- A [Tavily API key](https://tavily.com/) (free tier available)

## Setup

### 1. Install dependencies

```bash
uv sync
```

### 2. Configure AWS credentials

This project uses an AWS CLI named profile to authenticate with Bedrock. Here's how to set one up:

1. Create an IAM User in the [IAM console](https://console.aws.amazon.com/iam):
   - Go to **Users** → **Create user**
   - Give it a name (e.g. `strands-demo`)
   - Attach the **AmazonBedrockFullAccess** managed policy (or a scoped-down custom policy)

2. Create an access key for the user:
   - Select the user → **Security credentials** tab → **Create access key**
   - Choose **Command Line Interface (CLI)** as the use case
   - Copy the Access Key ID and Secret Access Key (shown only once)

3. Configure a named profile in your terminal:

```bash
aws configure --profile strands-demo
```

Enter the access key, secret key, and your preferred region (e.g. `us-east-1`) when prompted.

4. Enable model access in the [Bedrock console](https://console.aws.amazon.com/bedrock) for that region:
   - Go to **Model access** → **Manage model access**
   - Enable **Claude Sonnet** (or whichever model you want to use)

### 3. Set up environment variables

```bash
cp .env.examples .env
```

Edit `.env`:

```
AWS_PROFILE=strands-demo
AWS_DEFAULT_REGION=us-east-1
TAVILY_API_KEY=tvly-xxxxxxxxxxxxx
```

The `AWS_PROFILE` value tells the SDK to use the named profile from `~/.aws/credentials` instead of requiring inline keys.

### 4. Get a Tavily API key

Sign up at [tavily.com](https://tavily.com/) (free tier available) and add the key to your `.env`.

## Usage

```bash
# Basic — just a company name
uv run python agent.py "Stripe"

# With a focus area
uv run python agent.py "Anthropic" "Claude model releases"

# Another example
uv run python agent.py "Shopify" "AI features and integrations"
```

The agent will search for recent information, then output a polished 3-paragraph meeting brief.
