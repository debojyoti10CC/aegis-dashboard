# Weilchain Counter Applet - Deployment Guide

This guide walks through deploying and using a basic counter applet on Weilchain.

## Prerequisites

1. **Install Weilchain CLI** (placeholder command):
   ```bash
   curl -sSf https://install.weilchain.com | sh
   ```

2. **Install Rust** (for building the applet):
   ```bash
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   rustup target add wasm32-unknown-unknown
   ```

## Project Structure

```
weilchain-counter/
├── src/lib.rs              # Rust applet implementation
├── typescript/             # TypeScript implementation
├── mcp-server/            # MCP server for LLM integration
├── deploy.toml            # Deployment configuration
├── scripts/
│   ├── deploy.sh          # Deployment script
│   └── interact.sh        # Interaction script
└── tests/                 # Integration tests
```

## Building the Applet

### Rust Version
```bash
cd weilchain-counter
cargo build --release --target wasm32-unknown-unknown
```

### TypeScript Version
```bash
cd typescript
npm install
npm run build
```

## Deployment Steps

1. **Configure deployment** in `deploy.toml`:
   - Set applet name, version, and description
   - Define exposed methods and their signatures
   - Configure permissions and gas limits

2. **Deploy to Weilchain**:
   ```bash
   ./scripts/deploy.sh
   ```

3. **Verify deployment**:
   ```bash
   weilchain list-applets
   weilchain info <applet-address>
   ```

## Interacting with the Applet

### Via CLI
```bash
# Initialize the counter
weilchain call <applet-address> init --args '["alice"]'

# Get current count
weilchain call <applet-address> get_count

# Increment counter
weilchain call <applet-address> increment

# Add specific value
weilchain call <applet-address> add --args '[5]'

# Set to specific value
weilchain call <applet-address> set_count --args '[100]'

# Reset counter
weilchain call <applet-address> reset
```

### Via Block Explorer
1. Navigate to the Weilchain Block Explorer
2. Connect your wallet
3. Find your deployed applet
4. Use the web interface to call methods

### Via MCP Server (for LLMs)
1. Deploy the MCP server:
   ```bash
   cd mcp-server
   cargo run
   ```

2. Configure your LLM to use the MCP server
3. The LLM can now interact with the counter using natural language

## Available Methods

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `init` | `owner: string` | `void` | Initialize the counter |
| `get_count` | - | `i64` | Get current count |
| `increment` | - | `i64` | Increment by 1 |
| `decrement` | - | `i64` | Decrement by 1 |
| `add` | `value: i64` | `i64` | Add specific value |
| `set_count` | `value: i64` | `i64` | Set to specific value |
| `reset` | - | `i64` | Reset to 0 |
| `get_owner` | - | `string` | Get owner address |
| `get_state` | - | `string` | Get full state as JSON |

## Testing

Run the test suite:
```bash
cargo test
```

## MCP Integration

The included MCP server allows LLMs to interact with the counter applet using natural language commands like:
- "What's the current counter value?"
- "Increment the counter"
- "Add 10 to the counter"
- "Reset the counter to zero"

## Security Considerations

- The applet stores the owner address for potential access control
- All state changes are recorded on the blockchain
- Consider adding access control for sensitive operations
- Gas costs apply to all state-changing operations

## Next Steps

1. **Add Access Control**: Implement owner-only methods
2. **Create a Token**: Build a fungible token applet
3. **Web3 Integration**: Create a frontend dApp
4. **Cross-Contract Calls**: Interact with other applets
5. **Advanced MCP Features**: Add more sophisticated LLM tools

## Troubleshooting

- **Build Errors**: Ensure Rust and wasm32 target are installed
- **Deployment Fails**: Check gas limits and network connection
- **Method Calls Fail**: Verify method signatures and parameters
- **MCP Issues**: Ensure applet address is correctly configured

## Resources

- [Weilchain Documentation](https://docs.weilliptic.ai)
- [Applet Development Guide](https://docs.weilliptic.ai/docs/explainers/)
- [MCP Server Tutorial](https://docs.weilliptic.ai/docs/tutorials/mcp_basic)
- [Block Explorer](https://explorer.weilchain.com)