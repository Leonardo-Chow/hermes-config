# AutoCLI Install Details

Installed on 2026-05-08 by Hermes Agent (DeepSeek V4 Flash).

## Version & Location

- **AutoCLI v0.3.8** — single Rust binary, 4.7MB
- Binary at: `~/.local/bin/autocli`
- PATH added to `~/.zshrc`: `export PATH="$HOME/.local/bin:$PATH"`

## Network Workarounds (China GFW)

GitHub releases blocked → use `gh-proxy.com` mirror:
```bash
curl -fsSL -o /tmp/autocli.tar.gz \
  "https://gh-proxy.com/https://github.com/nashsu/autocli/releases/latest/download/autocli-aarch64-apple-darwin.tar.gz"
```

## Installation (macOS Apple Silicon)

```bash
# Download via mirror
curl -fsSL -o /tmp/autocli.tar.gz \
  "https://gh-proxy.com/https://github.com/nashsu/autocli/releases/latest/download/autocli-aarch64-apple-darwin.tar.gz"

# Extract
cd /tmp && tar xzf autocli.tar.gz

# Install to user-local bin
mkdir -p ~/.local/bin
cp /tmp/autocli ~/.local/bin/autocli
chmod +x ~/.local/bin/autocli

# Add to PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
```

## Verification

```bash
autocli --version
# → autocli 0.3.8
```

## Platform-Specific Binary Names

| Platform | File |
|----------|------|
| macOS Apple Silicon | `autocli-aarch64-apple-darwin.tar.gz` |
| macOS Intel | `autocli-x86_64-apple-darwin.tar.gz` |
| Linux x86_64 | `autocli-x86_64-unknown-linux-musl.tar.gz` |
| Linux ARM64 | `autocli-aarch64-unknown-linux-musl.tar.gz` |
| Windows x64 | `autocli-x86_64-pc-windows-msvc.zip` |
