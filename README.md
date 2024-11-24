# hey-py

Python port of [hey](https://github.com/b1ek/hey), a command-line interface for DuckDuckGo's AI Chat with enhanced features.

## ✨ Features

### 🤖 AI Models
- Multiple model support:
  - Claude 3 Haiku (default)
  - GPT-4o Mini
  - Mistral 8x7B
  - Llama 3.1 70B
- Customizable system prompts

### 💬 Chat Experience
- Rich markdown support in responses
- Conversation memory with auto-expiry
  - Stores last 10 messages
  - 24-hour automatic expiration
  - Manual clearing with `hey --clear`
  - Persistent storage in `~/.cache/hey`
- Real-time streaming responses

### 🛠️ Configuration
- Easy configuration via `hey config`
- HTTP and SOCKS proxy support
- Persistent settings in `~/.config/hey`
- Verbose mode for debugging

## 🚀 Installation

```bash
pip install hey-py
```

## 📖 Usage

### Basic Usage
```bash
# Ask a question
hey What is Python?

# Clear conversation history
hey --clear

# Configure settings
hey config
```

### Configuration Options
- Select AI model
- Set system prompt
- Configure proxy settings
- Accept Terms of Service

### Environment Variables
- `HEY_CONFIG_PATH`: Custom config directory (default: `~/.config/hey`)
- `HEY_CACHE_PATH`: Custom cache directory (default: `~/.cache/hey`)
- `HEY_CONFIG_FILENAME`: Custom config filename (default: `conf.toml`)
- `HEY_CACHE_FILENAME`: Custom cache filename (default: `messages.json`)

## 📝 License
GPLv3
